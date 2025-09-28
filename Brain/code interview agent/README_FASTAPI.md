# FastAPI Code Interview Agent

Basic FastAPI architecture following the Model-Controller-Service pattern for the code interview agent.

## Architecture Overview

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/
│   ├── __init__.py
│   └── config.py          # Application configuration
├── models/
│   ├── __init__.py
│   ├── interview.py       # Interview data models
│   └── websocket.py       # WebSocket data models
├── services/
│   ├── __init__.py
│   ├── interview_service.py    # Interview business logic
│   └── websocket_service.py    # WebSocket management
└── routers/
    ├── __init__.py
    ├── interview.py       # Interview API endpoints
    └── websocket.py       # WebSocket endpoints
```

## Features

- **Model-Controller-Service Architecture**: Clean separation of concerns
- **WebSocket Support**: Real-time communication for interviews
- **Interview Session Management**: Create, manage, and track interview sessions
- **Type Safety**: Full type annotations with Pydantic models
- **Configuration Management**: Environment-based configuration
- **CORS Support**: Pre-configured for frontend integration

## Quick Start

1. **Install Dependencies**:

   ```bash
   pip install -r app_requirements.txt
   ```

2. **Environment Setup**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Application**:

   ```bash
   python run.py
   ```

4. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Interview Management

- `POST /api/v1/interview/` - Create interview session
- `GET /api/v1/interview/{session_id}` - Get session details
- `PUT /api/v1/interview/{session_id}/status` - Update session status
- `DELETE /api/v1/interview/{session_id}` - Delete session
- `GET /api/v1/interview/` - List all sessions

### WebSocket

- `WS /ws/interview/{session_id}` - WebSocket connection for interview

## WebSocket Endpoints

### Frontend Connection

- `WS /ws/agent/{session_id}` - Main WebSocket connection for frontend
- `GET /ws/agent/status` - Get agent status

### System Events

- `WS /ws/interview/{session_id}` - Internal system WebSocket

## WebSocket Message Types

- `connect` - Connection established
- `disconnect` - Connection closed
- `heartbeat` - Keep-alive ping
- `interview_start` - Start interview session (triggers subprocess)
- `interview_end` - End interview session (stops subprocess)
- `code_update` - Code changes (for future implementation)
- `audio_data` - Audio data (for future implementation)
- `message` - General message
- `error` - Error message

## Code Agent Integration

The system integrates with the main.py code interview agent via:

- **Subprocess Management**: Runs main.py as a subprocess per session
- **Named Pipe Communication**: Real-time event streaming from agent to WebSocket
- **Event Broadcasting**: All agent events are forwarded to frontend via WebSocket

### Agent Events

- `interview_initializing` - System initialization started
- `interview_initialized` - System ready for interview
- `question_selecting` - Selecting interview question
- `question_selected` - Question set in code editor
- `interview_started` - Interview session active
- `submit_detected` - Code submission detected
- `inactivity_nudge` - Inactivity nudge delivered
- `interview_completing` - Generating final feedback
- `interview_completed` - Interview finished
- `error_occurred` - Error in agent process

## Usage Example

### Frontend WebSocket Connection

```javascript
// Connect to agent WebSocket
const sessionId = "your-session-id";
const ws = new WebSocket(
  `ws://localhost:8000/ws/agent/${sessionId}?candidate_name=John Doe`
);

ws.onopen = function () {
  console.log("Connected to code interview agent");

  // Start interview
  ws.send(
    JSON.stringify({
      type: "interview_start",
      session_id: sessionId,
      data: {
        candidate_name: "John Doe",
        interview_mode: "friendly",
      },
    })
  );
};

ws.onmessage = function (event) {
  const message = JSON.parse(event.data);
  console.log("Agent event:", message);

  switch (message.data.event_type) {
    case "interview_initializing":
      console.log("Interview system starting...");
      break;
    case "question_selected":
      console.log("Question selected:", message.data.question_title);
      break;
    case "interview_started":
      console.log("Interview is now active");
      break;
    case "submit_detected":
      console.log("Code submission detected");
      break;
    case "interview_completed":
      console.log("Interview finished");
      break;
    case "error_occurred":
      console.error("Agent error:", message.data.message);
      break;
  }
};

// Send heartbeat every 30 seconds
setInterval(() => {
  ws.send(
    JSON.stringify({
      type: "heartbeat",
      session_id: sessionId,
      data: {},
    })
  );
}, 30000);
```

### REST API Usage

```python
# Create interview session
import requests

response = requests.post("http://localhost:8000/api/v1/interview/", json={
    "interview_type": "technical",
    "user_id": "john_doe"
})

session_data = response.json()
session_id = session_data["session_id"]
print(f"Session created: {session_id}")

# Check agent status
status = requests.get("http://localhost:8000/ws/agent/status")
print(f"Agent status: {status.json()}")
```

## Development Notes

- Services use in-memory storage (replace with database in production)
- WebSocket connections are managed globally
- All endpoints include proper error handling
- Models use Pydantic for validation and serialization
- Configuration is environment-based with sensible defaults
