import argparse
import asyncio
import logging

import pyaudio
import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HOST = "localhost"
PORT = 8000

# Audio settings - must match what the agent's STT expects
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Deepgram and most STT services prefer 16000 Hz


# --- Main Client Logic ---
async def run_test(agent_type: str, interview_mode: str, candidate_name: str) -> None:
    """Connect to the agent server, stream mic audio, and play back the response.

    Args:
        agent_type: The type of agent to connect to (e.g., 'lda').
        interview_mode: The interview mode (e.g., 'hr', 'technical').
        candidate_name: The name of the candidate.
    """
    uri = f"ws://{HOST}:{PORT}/ws/{agent_type}/{interview_mode}?candidate={candidate_name}"
    logger.info(f"Connecting to {uri}...")

    p = pyaudio.PyAudio()

    try:
        mic_stream = p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
        )
        speaker_stream = p.open(
            format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK
        )
    except OSError as e:
        logger.error(
            f"Could not open audio streams. Make sure you have a microphone and speakers. Error: {e}"
        )
        logger.error(
            "On macOS, you may need to grant terminal/IDE access to the microphone in System Settings."
        )
        p.terminate()
        return

    logger.info("Audio streams opened. Connecting to WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket connection established. Streaming audio...")
            logger.info("--- SPEAK INTO YOUR MICROPHONE (Press Ctrl+C to stop) ---")

            async def sender(ws: WebSocketClientProtocol) -> None:
                """Read from microphone and send to WebSocket."""
                try:
                    while True:
                        data = await asyncio.to_thread(mic_stream.read, CHUNK)
                        await ws.send(data)
                except asyncio.CancelledError:
                    logger.info("Sender task cancelled.")
                finally:
                    mic_stream.stop_stream()
                    mic_stream.close()

            async def receiver(ws: WebSocketClientProtocol) -> None:
                """Receive from WebSocket and play to speakers."""
                try:
                    while True:
                        data = await ws.recv()
                        if isinstance(data, bytes):
                            speaker_stream.write(data)
                except asyncio.CancelledError:
                    logger.info("Receiver task cancelled.")
                except ConnectionClosed:
                    logger.info("Connection closed by server.")
                finally:
                    speaker_stream.stop_stream()
                    speaker_stream.close()

            sender_task = asyncio.create_task(sender(websocket))
            receiver_task = asyncio.create_task(receiver(websocket))

            done, pending = await asyncio.wait(
                [sender_task, receiver_task], return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

    except ConnectionClosed as e:
        logger.error(f"Connection to server failed: {e}. Is the server running?")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up PyAudio...")
        p.terminate()
        logger.info("--- TEST COMPLETE ---")


# --- Entry Point ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test client for the Agent Runner WebSocket server."
    )
    parser.add_argument(
        "agent_type", choices=["lda", "code_interview"], help="The type of agent to connect to."
    )
    parser.add_argument(
        "interview_mode", help="The interview mode (e.g., 'hr', 'technical', 'friendly')."
    )
    parser.add_argument(
        "-n", "--name", default="Local Test Candidate", help="The candidate name to use."
    )
    args = parser.parse_args()

    try:
        asyncio.run(run_test(args.agent_type, args.interview_mode, args.name))
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user.")
