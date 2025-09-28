import asyncio
import json
import logging
import os

import pyaudio
import websockets
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DeepgramTTS:
    """A class to handle real-time Text-to-Speech with Deepgram."""

    def __init__(self):
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        self.websocket: websockets.client.WebSocketClientProtocol | None = None
        self.pyaudio_instance: pyaudio.PyAudio | None = None
        self.audio_stream = None
        self.sample_rate = 24000
        self.channels = 1
        self.format = pyaudio.paInt16

    async def connect(
        self,
        model="aura-2-thalia-en",
        encoding="linear16",
        sample_rate=24000,
    ) -> bool:
        """Establishes a WebSocket connection to the Deepgram TTS API."""
        url = "wss://api.deepgram.com/v1/speak"
        params = {
            "model": model,
            "encoding": encoding,
            "sample_rate": str(sample_rate),
            "mip_opt_out": "true",
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        headers = {"Authorization": f"token {self.api_key}"}

        try:
            self.websocket = await websockets.connect(
                full_url, additional_headers=headers
            )
            self.sample_rate = sample_rate
            return True
        except Exception as e:
            logger.error(f"TTS connection failed: {e}")
            return False

    def setup_audio_playback(self):
        """Initializes the PyAudio stream for audio output."""
        self.pyaudio_instance = pyaudio.PyAudio()
        self.audio_stream = self.pyaudio_instance.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
        )

    def stop_audio_playback(self):
        """Closes the PyAudio stream and terminates the instance."""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()

    async def _listen_for_audio(self):
        """Listens for a single utterance and writes audio data to the stream."""
        if not self.websocket:
            return False
        try:
            while True:
                message = await self.websocket.recv()
                if isinstance(message, bytes):
                    if self.audio_stream:
                        self.audio_stream.write(message)
                elif (data := json.loads(message)).get("type") in ["Close", "Flushed"]:
                    return True  # Utterance is complete
        except websockets.exceptions.ConnectionClosed:
            logger.info("TTS connection closed.")
            return True
        except Exception as e:
            logger.error(f"Error while listening for TTS audio: {e}")
            return False

    async def send_text(self, text: str) -> bool:
        """Sends a text message to the TTS WebSocket."""
        if not self.websocket:
            return False
        await self.websocket.send(json.dumps({"type": "Speak", "text": text}))
        return True

    async def close(self):
        """Closes the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()

    async def speak(self, text: str):
        """Speaks a given text by sending it to Deepgram and playing the audio."""
        try:
            await self.send_text(text)
            await self.websocket.send(json.dumps({"type": "Flush"}))
            await self._listen_for_audio()
        except Exception as e:
            logger.error(f"Error in speak method: {e}")


def demo_generator():
    """A generator that yields sentences for the TTS demo."""
    yield "Hello world! This is a test of real-time text-to-speech synthesis."
    yield "Each sentence is generated and spoken as it is received."
    yield "This demonstrates the power of streaming TTS technology."


async def main():
    """Main function to run a demo of the DeepgramTTS class."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Deepgram TTS Demo...")
    tts = DeepgramTTS()

    if not await tts.connect():
        logger.error("Failed to connect to Deepgram. Aborting demo.")
        return

    tts.setup_audio_playback()

    try:
        logger.info("Speaking a single sentence...")
        await tts.speak("First, let's test a single sentence.")
        await asyncio.sleep(1)

        logger.info("Now, speaking sentences from a generator...")
        for sentence in demo_generator():
            logger.info(f"Speaking: {sentence}")
            await tts.speak(sentence)
            # Small pause between sentences
            await asyncio.sleep(0.5)

        logger.info("TTS demo finished.")
    finally:
        # The close method in the refactored version only closes the websocket.
        # We need to manually stop the audio playback for the demo.
        await tts.close()
        tts.stop_audio_playback()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")
