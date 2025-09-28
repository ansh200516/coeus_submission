import asyncio
import importlib.util
import json
import logging
import os
import re
import sys
import wave
from typing import Any, List, Optional, Union

import pyaudio

from config import SAMPLE_RATE, STT_MODEL, TTS_MODEL
from shared_state import AudioState

logger = logging.getLogger(__name__)


# ========== DYNAMIC IMPORTS ==========
def _import_helper(
    module_name: str, relative_path: str, class_name: str
) -> Optional[Any]:
    """Dynamically imports a class from a module at a given path."""
    module_dir = None
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir = os.path.abspath(os.path.join(script_dir, relative_path))
        module_file_path = os.path.join(module_dir, "main.py")
        if not os.path.exists(module_file_path):
            # Do not raise FileNotFoundError, just log a warning.
            logger.warning(f"Module file not found at {module_file_path}, cannot import {class_name}")
            return None
        sys.path.insert(0, module_dir)
        spec = importlib.util.spec_from_file_location(module_name, module_file_path)
        if spec is None:
            raise ImportError(f"Could not create spec for module at {module_file_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
    finally:
        if module_dir and module_dir in sys.path:
            sys.path.remove(module_dir)


ProvenDeepgramTTS = _import_helper("rtts_main", "../rtts", "DeepgramTTS")
RealTimeSTT = _import_helper("rstt_main", "../rstt", "RealTimeSTT")


# ========== AUDIO CLASSES ==========
class AudioManager:
    """Manages all audio playback through a single, queued stream."""

    def __init__(self, audio_state: AudioState):
        self.audio_state = audio_state
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE, output=True
        )
        self._playback_queue = asyncio.Queue()
        self._worker_task = asyncio.create_task(self._playback_worker())

    async def _playback_worker(self):
        """The background worker that processes audio jobs from the queue."""
        while True:
            job = await self._playback_queue.get()
            if job is None:  # Sentinel value to stop the worker
                self._playback_queue.task_done()
                break

            self.audio_state.set_speaking(True)
            if isinstance(job, str):
                await self._play_wav_file(job)
            elif isinstance(job, asyncio.Queue):
                await self._play_from_stream_queue(job)
            self.audio_state.set_speaking(False)
            self._playback_queue.task_done()

    async def _play_wav_file(self, file_path: str):
        logger.info(f"Starting WAV file playback: {os.path.basename(file_path)}")
        try:
            with wave.open(file_path, "rb") as wf:
                logger.info(f"WAV file opened successfully. Sample rate: {wf.getframerate()}, Channels: {wf.getnchannels()}, Frames: {wf.getnframes()}")
                data = wf.readframes(1024)
                frames_played = 0
                while data:
                    self._stream.write(data)
                    data = wf.readframes(1024)
                    frames_played += 1024
                    await asyncio.sleep(0.01)
                logger.info(f"WAV file playback completed. Total frames played: {frames_played}")
        except Exception as e:
            logger.error(f"Failed to play WAV file {file_path}: {e}", exc_info=True)

    async def _play_from_stream_queue(self, stream_queue: asyncio.Queue):
        logger.info("Playing audio from live stream...")
        try:
            while True:
                chunk = await stream_queue.get()
                if chunk is None:
                    break
                self._stream.write(chunk)
        except Exception as e:
            logger.error(f"Error playing from stream queue: {e}")

    async def schedule_playback(self, job: Union[str, asyncio.Queue]):
        """Adds a new audio job to the playback queue."""
        await self._playback_queue.put(job)

    async def wait_for_playback_to_finish(self):
        """Waits until all scheduled audio jobs have been played."""
        await self._playback_queue.join()

    async def close(self):
        """Closes the audio stream and terminates PyAudio."""
        if self._worker_task and not self._worker_task.done():
            # Gracefully stop the worker
            await self._playback_queue.put(None)
            # Wait for the worker to finish processing, but with a timeout
            try:
                await asyncio.wait_for(self._worker_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("AudioManager worker did not shut down gracefully.")
                self._worker_task.cancel()

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pyaudio:
            self._pyaudio.terminate()
        logger.info("AudioManager closed.")


class InterviewTTS:
    """Prepares and schedules TTS audio jobs for the AudioManager."""

    def __init__(self, audio_manager: AudioManager):
        self.audio_manager = audio_manager

    async def speak(self, text: str):
        """Schedules a full block of text to be spoken."""
        logger.info("TTS creating speak job for: '%s'...", text[:70])
        if not text:
            return
        utterance_queue = asyncio.Queue()
        await self.audio_manager.schedule_playback(utterance_queue)
        asyncio.create_task(self._stream_to_queue(text, utterance_queue))

    async def _stream_to_queue(self, text: str, queue: asyncio.Queue):
        """Connects to Deepgram, streams audio, and puts it in the queue."""
        tts_connection = ProvenDeepgramTTS()
        try:
            if not await tts_connection.connect(
                model=TTS_MODEL, sample_rate=SAMPLE_RATE
            ):
                raise ConnectionError(
                    "Failed to connect to Deepgram TTS for streaming."
                )
            await tts_connection.send_text(text)
            await tts_connection.websocket.send(json.dumps({"type": "Flush"}))
            while True:
                message = await tts_connection.websocket.recv()
                if isinstance(message, bytes):
                    await queue.put(message)
                elif json.loads(message).get("type") in ["Close", "Flushed"]:
                    break
        except Exception as e:
            logger.error(f"Error in TTS stream-to-queue: {e}", exc_info=True)
        finally:
            await queue.put(None)
            await tts_connection.close()


class InterviewSTT:
    """STT wrapper that manages a persistent connection and is aware of audio playback state."""

    def __init__(self, audio_state: AudioState):
        self.audio_state = audio_state
        self.collected_transcriptions: List[str] = []
        self.stt: Optional[RealTimeSTT] = None
        if RealTimeSTT:
            self.stt = RealTimeSTT(
                audio_state=self.audio_state, on_final=self._on_final_transcript
            )
            self.stt.start()
        else:
            logger.error("RealTimeSTT module not available. STT will be disabled.")

    def _on_final_transcript(self, transcript: str):
        """Callback to append final transcripts to the list."""
        self.collected_transcriptions.append(transcript)

    async def listen(self) -> str:
        """Waits for silence, then listens until an utterance is detected."""
        if not self.stt:
            return ""

        self.collected_transcriptions.clear()
        self.stt.utterance_end_event.clear()

        # Wait for any current audio playback to finish before listening
        while self.audio_state.is_speaking():
            await asyncio.sleep(0.1)
        logger.info("Audio playback finished. Starting STT listening period.")

        logger.info("Listening for utterance...")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: self.stt.utterance_end_event.wait())
        logger.info("Utterance end detected by VAD.")

        return " ".join(self.collected_transcriptions).strip()

    def stop(self):
        """Stops the underlying STT engine."""
        if self.stt:
            self.stt.stop()
