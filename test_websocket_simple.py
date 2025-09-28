#!/usr/bin/env python3
"""
Simple WebSocket test script for the refactored code interview agent.

This script tests the new simplified WebSocket endpoint that manages
the subprocess execution of the main.py code interview agent.
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_websocket_connection() -> None:
    """Test the WebSocket connection and subprocess management."""
    uri = "ws://localhost:8000/ws/agent"
    
    try:
        logger.info(f"Connecting to WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            logger.info("✅ WebSocket connection established")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"Connection response: {data}")
            
            # Test ping/pong
            await test_ping_pong(websocket)
            
            # Test starting the agent
            await test_start_agent(websocket)
            
            # Wait for some events
            await listen_for_events(websocket, duration=30)
            
            # Test stopping the agent
            await test_stop_agent(websocket)
            
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")


async def test_ping_pong(websocket) -> None:
    """Test ping/pong functionality."""
    logger.info("Testing ping/pong...")
    
    ping_message = {
        "type": "ping",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await websocket.send(json.dumps(ping_message))
    response = await websocket.recv()
    data = json.loads(response)
    
    if data.get("type") == "pong":
        logger.info("✅ Ping/pong test successful")
    else:
        logger.warning(f"⚠️ Unexpected ping response: {data}")


async def test_start_agent(websocket) -> None:
    """Test starting the code interview agent."""
    logger.info("Testing agent start...")
    
    start_message = {
        "type": "start_agent",
        "candidate_name": "Test Candidate",
        "interview_mode": "challenging",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await websocket.send(json.dumps(start_message))
    response = await websocket.recv()
    data = json.loads(response)
    
    if data.get("type") == "agent_started":
        logger.info("✅ Agent start test successful")
        logger.info(f"Agent started for: {data.get('candidate_name')}")
    else:
        logger.warning(f"⚠️ Unexpected start response: {data}")


async def test_stop_agent(websocket) -> None:
    """Test stopping the code interview agent."""
    logger.info("Testing agent stop...")
    
    stop_message = {
        "type": "stop_agent",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await websocket.send(json.dumps(stop_message))
    response = await websocket.recv()
    data = json.loads(response)
    
    if data.get("type") == "agent_stopped":
        logger.info("✅ Agent stop test successful")
        logger.info(f"Stop success: {data.get('success')}")
    else:
        logger.warning(f"⚠️ Unexpected stop response: {data}")


async def listen_for_events(websocket, duration: int = 30) -> None:
    """Listen for events from the agent subprocess."""
    logger.info(f"Listening for events for {duration} seconds...")
    
    start_time = asyncio.get_event_loop().time()
    
    while (asyncio.get_event_loop().time() - start_time) < duration:
        try:
            # Wait for message with timeout
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            event_type = data.get("type")
            
            if event_type == "agent_event":
                agent_event = data.get("event_type")
                logger.info(f"📡 Agent event: {agent_event}")
                
                if data.get("data"):
                    logger.info(f"   Data: {data['data']}")
            
            elif event_type == "agent_completed":
                reason = data.get("reason", "unknown")
                logger.info(f"🏁 Agent completed: {reason}")
                break
            
            elif event_type == "subprocess_output":
                stream = data.get("stream", "unknown")
                output = data.get("data", "")
                logger.info(f"📝 Subprocess [{stream}]: {output}")
            
            else:
                logger.info(f"📨 Received: {event_type} - {data}")
        
        except asyncio.TimeoutError:
            logger.debug("No message received in timeout period")
            continue
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            break
    
    logger.info("Finished listening for events")


async def main() -> None:
    """Main test function."""
    logger.info("=" * 60)
    logger.info("Starting WebSocket Simple Test")
    logger.info("=" * 60)
    
    try:
        await test_websocket_connection()
        logger.info("✅ All tests completed successfully")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    
    logger.info("=" * 60)
    logger.info("Test Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
