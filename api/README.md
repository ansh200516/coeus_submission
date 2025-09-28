# Interview Task API

FastAPI backend following the **Model-Controller-Service** architecture pattern for managing interview tasks.

## Architecture

```
/api
├── controllers/          # API endpoint handlers
│   └── task_controller.py
├── models/              # Pydantic data models
│   └── task_model.py
├── services/            # Business logic
│   └── task_service.py
├── main.py             # FastAPI application
├── run.py              # Application runner
└── requirements.txt    # Dependencies
```

## Features

- **REST API** for starting interview tasks
- **Model-Controller-Service** architecture
- **Pydantic** data validation
- **CORS** support for frontend integration
- **Comprehensive logging**
- **Health check endpoints**

## API Endpoints

### Start Interview Task

```http
POST /tasks/start
Content-Type: application/json

{
  "name": "candidate_name",
  "duration": 300
}
```

**Response:**

```json
{
  "message": "Interview task started successfully with ID: task_20250927_123456_abc123",
  "task_id": "task_20250927_123456_abc123",
  "status": "started"
}
```

### Health Check

```http
GET /tasks/health
```

### API Documentation

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

## Installation

1. Install dependencies:

```bash
cd api
pip install -r requirements.txt
```

2. Run the server:

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Integration

The API integrates with:

- **Frontend:** `coeus-frontend/src/components/coding-engine/CodeEditor.tsx`

**Note:** Browser auto-launching functionality has been disabled. The API now only registers interview tasks without launching external processes or browser automation.

## Development

The API follows Python best practices:

- Type annotations
- Comprehensive docstrings
- Error handling
- Logging
- Pydantic validation
