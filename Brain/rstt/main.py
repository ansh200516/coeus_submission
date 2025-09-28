import logging
import os
import sys
import threading
import time
from typing import Callable, Optional

import pyaudio
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
)
from dotenv import load_dotenv

# This path modification is not ideal. Consider a better project structure.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lda.shared_state import AudioState

load_dotenv()

logger = logging.getLogger(__name__)


class RealTimeSTT:
    """Handles real-time Speech-to-Text, aware of the application's audio state."""

    def __init__(
        self,
        audio_state: AudioState,
        on_interim: Optional[Callable[[str], None]] = None,
        on_final: Optional[Callable[[str], None]] = None,
    ):
        self.audio_state = audio_state
        self.on_interim = on_interim
        self.on_final = on_final
        self.dg_connection = None
        self.audio_thread: Optional[threading.Thread] = None
        self.exit_flag = threading.Event()
        self.utterance_end_event = threading.Event()
        self.connection_active = False
        self.RATE = 16000
        self.CHUNK = 320

    def _on_message(self, _, result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        if not transcript:
            return

        if result.is_final:
            if self.on_final:
                self.on_final(transcript)
        else:
            if self.on_interim:
                self.on_interim(transcript)

    def _on_utterance_end(self, *args, **kwargs):
        logger.info("Utterance end detected.")
        self.utterance_end_event.set()

    def start(self) -> bool:
        if not self._create_connection():
            return False
        self.exit_flag.clear()
        self.utterance_end_event.clear()
        self.audio_thread = threading.Thread(target=self._audio_worker, daemon=True)
        self.audio_thread.start()
        return True

    def _create_connection(self) -> bool:
        try:
            config = DeepgramClientOptions(options={"keepalive": "true"})
            deepgram = DeepgramClient(config=config)

            self.dg_connection = deepgram.listen.websocket.v("1")
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, self._on_message)
            self.dg_connection.on(
                LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end
            )
            options = LiveOptions(
                model="nova-2",
                language="en",
                encoding="linear16",
                channels=1,
                sample_rate=self.RATE,
                smart_format=True,
                filler_words=True,
                interim_results=True,
                endpointing=300,
                utterance_end_ms=1000,
            )
            if self.dg_connection.start(options):
                self.connection_active = True
                return True
            return False
        except Exception as e:
            logger.error(f"Error creating Deepgram STT connection: {e}")
            return False

    def _close_connection(self):
        if self.dg_connection and self.connection_active:
            try:
                self.dg_connection.finish()
                self.connection_active = False
            except Exception as e:
                logger.error(f"Error closing STT connection: {e}")

    def _audio_worker(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        try:
            while not self.exit_flag.is_set():
                frame = stream.read(self.CHUNK, exception_on_overflow=False)
                if (
                    self.connection_active
                    and self.dg_connection
                    and not self.audio_state.is_speaking()
                ):
                    self.dg_connection.send(frame)
        except Exception as e:
            logger.error(f"Error in STT audio worker: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def stop(self):
        if not self.exit_flag.is_set():
            self.exit_flag.set()
        self._close_connection()
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()


def main():
    """A simple demo that prints transcription results in real-time."""
    logging.basicConfig(level=logging.INFO)
    print("Starting Real-Time STT Demo. Press Ctrl+C to stop.")

    def handle_interim(text: str):
        print(f"🎤 {text}", end="\r", flush=True)

    def handle_final(text: str):
        # Clear the line and print the final transcript
        print(" " * 80, end="\r")
        print(f"✅ {text}")

    stt = RealTimeSTT(
        audio_state=AudioState(), on_interim=handle_interim, on_final=handle_final
    )
    if not stt.start():
        logger.error("Failed to start STT engine.")
        return

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping demo...")
    finally:
        stt.stop()
        print("Demo finished.")


if __name__ == "__main__":
    main()
