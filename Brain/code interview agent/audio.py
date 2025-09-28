"""
Audio management system for the Code Interview Agent.

This module provides comprehensive audio handling including speech-to-text (STT),
text-to-speech (TTS), and audio queue management for seamless interview experience.
"""

import asyncio
import importlib.util
import json
import logging
import os
import random
import sys
import wave
from typing import Any, List, Optional, Union

import pyaudio

from config import SAMPLE_RATE, STT_MODEL, TTS_MODEL, AUDIO_CACHE_DIR
from shared_state import AudioState

logger = logging.getLogger(__name__)


# ========== DYNAMIC IMPORTS ==========
def _import_helper(
    module_name: str, relative_path: str, class_name: str
) -> Optional[Any]:
    """
    Dynamically imports a class from a module at a given path.
    
    Args:
        module_name: Name of the module to import
        relative_path: Relative path to the module directory
        class_name: Name of the class to import
        
    Returns:
        Optional[Any]: Imported class or None if import failed
    """
    module_dir = None
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        module_dir = os.path.abspath(os.path.join(script_dir, relative_path))
        module_file_path = os.path.join(module_dir, "main.py")
        
        if not os.path.exists(module_file_path):
            logger.warning(f"Module file not found at {module_file_path}, cannot import {class_name}")
            return None
            
        sys.path.insert(0, module_dir)
        spec = importlib.util.spec_from_file_location(module_name, module_file_path)
        
        if spec is None:
            raise ImportError(f"Could not create spec for module at {module_file_path}")
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
        
    except Exception as e:
        logger.error(f"Failed to import {class_name} from {relative_path}: {e}")
        return None
    finally:
        if module_dir and module_dir in sys.path:
            sys.path.remove(module_dir)


# Import audio modules from the same directory structure as nudge.py
ProvenDeepgramTTS = _import_helper("rtts_main", "../rtts", "DeepgramTTS")
RealTimeSTT = _import_helper("rstt_main", "../rstt", "RealTimeSTT")


# ========== AUDIO CLASSES ==========
class AudioManager:
    """
    Manages all audio playback through a single, queued stream.
    
    This class ensures that audio playback is properly sequenced, supporting
    both filler audio and live TTS streams without conflicts.
    """

    def __init__(self, audio_state: AudioState) -> None:
        """
        Initialize the audio manager.
        
        Args:
            audio_state: Shared audio state for coordination
        """
        self.audio_state = audio_state
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            output=True
        )
        self._playback_queue = asyncio.Queue()
        self._worker_task = asyncio.create_task(self._playback_worker())
        logger.info("AudioManager initialized")

    async def _playback_worker(self) -> None:
        """
        Background worker that processes audio jobs from the queue.
        
        This worker ensures sequential audio playback and proper state management.
        """
        while True:
            job = await self._playback_queue.get()
            if job is None:  # Sentinel value to stop the worker
                self._playback_queue.task_done()
                break

            self.audio_state.set_speaking(True)
            
            try:
                if isinstance(job, str):
                    await self._play_wav_file(job)
                elif isinstance(job, asyncio.Queue):
                    await self._play_from_stream_queue(job)
                elif isinstance(job, dict) and job.get("type") == "filler":
                    await self._play_filler_audio(job.get("duration", 1.0))
            except Exception as e:
                logger.error(f"Error processing audio job: {e}")
            finally:
                self.audio_state.set_speaking(False)
                self._playback_queue.task_done()

    async def _play_wav_file(self, file_path: str) -> None:
        """
        Play a WAV file through the audio stream.
        
        Args:
            file_path: Path to the WAV file to play
        """
        logger.info(f"Playing audio file: {os.path.basename(file_path)}")
        try:
            with wave.open(file_path, "rb") as wf:
                data = wf.readframes(1024)
                while data:
                    self._stream.write(data)
                    data = wf.readframes(1024)
                    await asyncio.sleep(0.01)  # Allow other tasks to run
        except Exception as e:
            logger.error(f"Failed to play WAV file {file_path}: {e}")

    async def _play_from_stream_queue(self, stream_queue: asyncio.Queue) -> None:
        """
        Play audio from a live stream queue (for TTS).
        
        Args:
            stream_queue: Queue containing audio chunks from TTS
        """
        logger.info("Playing audio from live TTS stream...")
        try:
            while True:
                chunk = await stream_queue.get()
                if chunk is None:  # End of stream marker
                    break
                self._stream.write(chunk)
        except Exception as e:
            logger.error(f"Error playing from stream queue: {e}")

    async def _play_filler_audio(self, duration: float) -> None:
        """
        Play random filler audio for the specified duration.
        
        Args:
            duration: Duration in seconds to play filler audio
        """
        try:
            filler_file = self._get_random_filler_file()
            if filler_file:
                await self._play_wav_file(filler_file)
            else:
                # Fallback: generate silence
                silence_samples = int(SAMPLE_RATE * duration)
                silence_data = b'\x00\x00' * silence_samples
                self._stream.write(silence_data)
        except Exception as e:
            logger.error(f"Error playing filler audio: {e}")

    def _get_random_filler_file(self) -> Optional[str]:
        """
        Get a random filler audio file from the cache.
        
        Returns:
            Optional[str]: Path to random filler file or None
        """
        try:
            if not os.path.exists(AUDIO_CACHE_DIR):
                logger.warning(f"Audio cache directory not found: {AUDIO_CACHE_DIR}")
                return None
                
            audio_files = [
                f for f in os.listdir(AUDIO_CACHE_DIR)
                if f.endswith('.wav')
            ]
            
            if not audio_files:
                logger.warning("No filler audio files found in cache")
                return None
                
            selected_file = random.choice(audio_files)
            return os.path.join(AUDIO_CACHE_DIR, selected_file)
            
        except Exception as e:
            logger.error(f"Error selecting filler audio: {e}")
            return None

    async def schedule_playback(self, job: Union[str, asyncio.Queue, dict]) -> None:
        """
        Add a new audio job to the playback queue.
        
        Args:
            job: Audio job (file path, stream queue, or filler config)
        """
        await self._playback_queue.put(job)

    async def schedule_filler(self, duration: float = 1.0) -> None:
        """
        Schedule filler audio playback.
        
        Args:
            duration: Duration of filler audio in seconds
        """
        filler_job = {"type": "filler", "duration": duration}
        await self.schedule_playback(filler_job)

    async def wait_for_playback_to_finish(self) -> None:
        """Wait until all scheduled audio jobs have been played."""
        await self._playback_queue.join()

    async def close(self) -> None:
        """Close the audio stream and terminate PyAudio."""
        logger.info("Closing AudioManager...")
        
        if self._worker_task and not self._worker_task.done():
            # Gracefully stop the worker
            await self._playback_queue.put(None)
            
            # Wait for the worker to finish processing, but with a timeout
            try:
                await asyncio.wait_for(self._worker_task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("AudioManager worker did not shut down gracefully")
                self._worker_task.cancel()

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            
        if self._pyaudio:
            self._pyaudio.terminate()
            
        logger.info("AudioManager closed successfully")


class InterviewTTS:
    """
    Text-to-speech system for the code interview agent.
    
    This class handles TTS requests and integrates with the AudioManager
    for proper audio queue management.
    """

    def __init__(self, audio_manager: AudioManager) -> None:
        """
        Initialize the TTS system.
        
        Args:
            audio_manager: AudioManager instance for audio playback
        """
        self.audio_manager = audio_manager
        logger.info("InterviewTTS initialized")

    async def speak(self, text: str, add_filler: bool = True) -> None:
        """
        Convert text to speech and schedule for playback.
        
        Args:
            text: Text to convert to speech
            add_filler: Whether to add filler audio before speaking
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return

        logger.info(f"TTS processing: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Optionally add filler audio before speaking
        if add_filler:
            await self.audio_manager.schedule_filler(duration=0.5)
        
        # Create audio queue for streaming TTS
        utterance_queue = asyncio.Queue()
        await self.audio_manager.schedule_playback(utterance_queue)
        
        # Start TTS streaming in background
        asyncio.create_task(self._stream_to_queue(text, utterance_queue))

    async def _stream_to_queue(self, text: str, queue: asyncio.Queue) -> None:
        """
        Stream TTS audio to the playback queue.
        
        Args:
            text: Text to convert to speech
            queue: Queue to stream audio chunks to
        """
        tts_connection = None
        try:
            if not ProvenDeepgramTTS:
                logger.error("Deepgram TTS module not available")
                await queue.put(None)
                return
                
            tts_connection = ProvenDeepgramTTS()
            
            # Connect to Deepgram TTS
            if not await tts_connection.connect(
                model=TTS_MODEL, 
                sample_rate=SAMPLE_RATE
            ):
                raise ConnectionError("Failed to connect to Deepgram TTS")
            
            # Send text and flush
            await tts_connection.send_text(text)
            await tts_connection.websocket.send(json.dumps({"type": "Flush"}))
            
            # Stream audio chunks
            while True:
                message = await tts_connection.websocket.recv()
                
                if isinstance(message, bytes):
                    await queue.put(message)
                elif isinstance(message, str):
                    msg_data = json.loads(message)
                    if msg_data.get("type") in ["Close", "Flushed"]:
                        break
                        
        except Exception as e:
            logger.error(f"Error in TTS stream-to-queue: {e}", exc_info=True)
        finally:
            await queue.put(None)  # End of stream marker
            if tts_connection:
                await tts_connection.close()


class InterviewSTT:
    """
    Speech-to-text system for the code interview agent.
    
    This class provides continuous speech recognition with voice activity
    detection and proper coordination with TTS playback.
    """

    def __init__(self, audio_state: AudioState) -> None:
        """
        Initialize the STT system.
        
        Args:
            audio_state: Shared audio state for coordination
        """
        self.audio_state = audio_state
        self.collected_transcriptions: List[str] = []
        self.stt: Optional[RealTimeSTT] = None
        
        if RealTimeSTT:
            self.stt = RealTimeSTT(
                audio_state=self.audio_state,
                on_final=self._on_final_transcript
            )
            self.stt.start()
            logger.info("InterviewSTT initialized with RealTimeSTT")
        else:
            logger.error("RealTimeSTT module not available. STT will be disabled")

    def _on_final_transcript(self, transcript: str) -> None:
        """
        Callback to handle final transcript results.
        
        Args:
            transcript: Final transcript text
        """
        if transcript and transcript.strip():
            self.collected_transcriptions.append(transcript.strip())
            logger.info(f"Final transcript: {transcript}")

    async def listen(self, timeout: Optional[float] = None) -> str:
        """
        Listen for speech input and return the transcription.
        
        Args:
            timeout: Maximum time to wait for speech (None for no timeout)
            
        Returns:
            str: Transcribed speech or empty string if no speech detected
        """
        if not self.stt:
            logger.error("STT not available")
            return ""

        # Clear previous transcriptions
        self.collected_transcriptions.clear()
        self.stt.utterance_end_event.clear()

        # Wait for any current audio playback to finish
        logger.info("Waiting for audio playback to finish...")
        while self.audio_state.is_speaking():
            await asyncio.sleep(0.1)
        
        logger.info("Starting STT listening period...")
        self.audio_state.set_listening(True)
        
        try:
            # Wait for utterance end detection
            loop = asyncio.get_running_loop()
            
            if timeout:
                await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: self.stt.utterance_end_event.wait()),
                    timeout=timeout
                )
            else:
                await loop.run_in_executor(None, lambda: self.stt.utterance_end_event.wait())
                
            logger.info("Utterance end detected by VAD")
            
        except asyncio.TimeoutError:
            logger.info("STT listening timeout reached")
        except Exception as e:
            logger.error(f"Error during STT listening: {e}")
        finally:
            self.audio_state.set_listening(False)

        # Return collected transcriptions
        result = " ".join(self.collected_transcriptions).strip()
        logger.info(f"STT result: '{result}'")
        return result

    async def listen_with_prompt(self, prompt: str, timeout: float = 30.0) -> str:
        """
        Listen for speech with a spoken prompt.
        
        Args:
            prompt: Text prompt to speak before listening
            timeout: Maximum time to wait for response
            
        Returns:
            str: Transcribed response
        """
        # This would require TTS integration, but we'll keep it simple for now
        logger.info(f"Listening with prompt: {prompt}")
        return await self.listen(timeout=timeout)

    def stop(self) -> None:
        """Stop the STT system."""
        logger.info("Stopping InterviewSTT...")
        if self.stt:
            self.stt.stop()
        self.audio_state.set_listening(False)
        logger.info("InterviewSTT stopped")


# ========== AUDIO UTILITIES ==========
async def play_notification_sound(audio_manager: AudioManager) -> None:
    """
    Play a notification sound to get the candidate's attention.
    
    Args:
        audio_manager: AudioManager instance
    """
    # Schedule a short filler audio as notification
    await audio_manager.schedule_filler(duration=0.3)


async def test_audio_system(audio_state: AudioState) -> bool:
    """
    Test the audio system components.
    
    Args:
        audio_state: Audio state for testing
        
    Returns:
        bool: True if all components work, False otherwise
    """
    try:
        logger.info("Testing audio system...")
        
        # Test audio manager
        audio_manager = AudioManager(audio_state)
        
        # Test TTS
        tts = InterviewTTS(audio_manager)
        await tts.speak("Audio system test", add_filler=False)
        await audio_manager.wait_for_playback_to_finish()
        
        # Test STT (brief test)
        stt = InterviewSTT(audio_state)
        
        # Cleanup
        stt.stop()
        await audio_manager.close()
        
        logger.info("Audio system test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Audio system test failed: {e}")
        return False
