import asyncio
import websockets
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
HOST = "localhost"
PORT = 8000
# Simulate 0.5 seconds of silent 16-bit PCM audio at 16kHz
# 16000 samples/sec * 1 channel * 2 bytes/sample * 0.5 sec = 16000 bytes
FAKE_AUDIO_CHUNK = b'\x00' * 16000

async def test_endpoint(endpoint: str):
    """Connects to a WebSocket endpoint, sends a fake audio chunk, and prints the response."""
    uri = f"ws://{HOST}:{PORT}/ws/{endpoint}"
    logger.info(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connection successful.")
            
            # Send the fake audio data
            logger.info(f"Sending {len(FAKE_AUDIO_CHUNK)} bytes of fake PCM audio data...")
            await websocket.send(FAKE_AUDIO_CHUNK)
            
            # Wait for and print the response from the server
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
            
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"Connection closed unexpectedly: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test WebSocket connections for the Integrator API.")
    parser.add_argument(
        "endpoint", 
        choices=["code_interview", "lda_technical", "lda_hr"], 
        help="The WebSocket endpoint to test."
    )
    args = parser.parse_args()
    
    asyncio.run(test_endpoint(args.endpoint))
