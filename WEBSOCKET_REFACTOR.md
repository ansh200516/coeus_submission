# WebSocket Refactor Documentation

## Overview

The WebSocket system has been completely refactored to provide a simplified, single-endpoint approach for managing the code interview agent subprocess.

## Changes Made

### 1. Simplified WebSocket Architecture

**Before:**

- Complex multi-router system with separate endpoints for different functionalities
- Multiple service classes and models
- Heavy logging and complex state management

**After:**

- Single WebSocket endpoint: `/ws/agent`
- Direct subprocess management within the WebSocket handler
- Minimal logging and simplified state management

### 2. Files Removed

The following files were removed as they are no longer needed:

- `app/routers/websocket.py` - Complex WebSocket router
- `app/routers/frontend.py` - Frontend-specific WebSocket router
- `app/services/websocket_service.py` - Complex WebSocket service
- `app/services/subprocess_manager.py` - Complex subprocess manager
- `app/models/websocket.py` - WebSocket data models

### 3. Files Added/Modified

**New Files:**

- `app/routers/websocket_simple.py` - Simplified WebSocket router with integrated subprocess management
- `test_websocket_simple.py` - Test script for the new WebSocket endpoint

**Modified Files:**

- `main.py` - Added completion callback functionality and argument parsing
- `app/main.py` - Updated to use the new simplified WebSocket router

## New WebSocket Endpoint

### Endpoint: `/ws/agent`

This single endpoint handles all WebSocket communication for the code interview agent.

### Message Types

#### Client to Server:

1. **start_agent**

   ```json
   {
     "type": "start_agent",
     "candidate_name": "John Doe",
     "interview_mode": "challenging"
   }
   ```

2. **stop_agent**

   ```json
   {
     "type": "stop_agent"
   }
   ```

3. **ping**
   ```json
   {
     "type": "ping"
   }
   ```

#### Server to Client:

1. **connected** - Connection confirmation
2. **agent_started** - Agent subprocess started successfully
3. **agent_stopped** - Agent subprocess stopped
4. **agent_completed** - Agent finished its task (success/error/interruption)
5. **agent_event** - Events from the agent subprocess
6. **subprocess_output** - Real-time output from the subprocess
7. **pong** - Response to ping
8. **error** - Error messages

## Completion Callback System

The `main.py` file now includes a completion callback system that notifies the WebSocket server when the agent completes its task.

### Completion Reasons:

- `completed` - Interview completed successfully
- `error` - An error occurred during the interview
- `interrupted` - Process was interrupted (SIGINT/SIGTERM)
- `timeout` - Interview exceeded maximum duration

### How It Works:

1. The WebSocket server starts the `main.py` subprocess with a `--pipe-path` argument
2. The `main.py` script writes completion events to the pipe file
3. The WebSocket server monitors the pipe and forwards events to connected clients
4. When the agent completes, clients receive an `agent_completed` message

## Usage

### Starting the Server

```bash
cd "Brain/code interview agent"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing the WebSocket

```bash
cd "D:\Projects\fun\eightfold_finals"
python test_websocket_simple.py
```

### Frontend Integration

Connect to `ws://localhost:8000/ws/agent` and send messages as documented above.

Example JavaScript:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/agent");

ws.onopen = function () {
  // Start the agent
  ws.send(
    JSON.stringify({
      type: "start_agent",
      candidate_name: "John Doe",
      interview_mode: "challenging",
    })
  );
};

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);

  if (data.type === "agent_completed") {
    console.log("Agent finished:", data.reason);
    // Handle completion - show results, enable next steps, etc.
  }
};
```

## Benefits of the Refactor

1. **Simplified Architecture** - Single endpoint instead of multiple complex routers
2. **Reduced Code Complexity** - Removed unnecessary abstractions and services
3. **Better Error Handling** - Direct error propagation without complex middleware
4. **Easier Maintenance** - Less code to maintain and debug
5. **Clear Completion Signals** - Frontend always knows when the agent is done
6. **Minimal Logging** - Only essential logs, reducing noise

## Migration Notes

If you have existing frontend code that uses the old WebSocket endpoints, you'll need to:

1. Update the WebSocket URL to `/ws/agent`
2. Update message formats to match the new simplified schema
3. Handle the new `agent_completed` message type to know when the agent is finished
4. Remove any code that depends on the old complex message types

The new system is much simpler and more reliable for managing the code interview agent subprocess.
