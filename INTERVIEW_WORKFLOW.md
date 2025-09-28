# Interview Workflow Documentation

This document describes the complete interview workflow from form submission to LDA system activation.

## Architecture Overview

The interview system follows a Model-Controller-Service architecture with the following components:

### Backend Components

1. **Interview Controller** (`api/controllers/interview_controller.py`)
   - Handles HTTP requests from the frontend
   - Validates form data and file uploads
   - Coordinates with the interview service

2. **Interview Service** (`api/services/interview_service.py`)
   - Contains business logic for interview processing
   - Manages candidate data collection and LDA system coordination
   - Handles background processing and task tracking

3. **Interview Models** (`api/models/interview_model.py`)
   - Pydantic models for request/response validation
   - Data structures for status tracking and processing states

### Frontend Components

1. **Interview Form** (`coeus-frontend/src/components/interview-form.tsx`)
   - Collects candidate information (name, gender, LinkedIn, resume)
   - Submits data to backend API
   - Shows processing animation with real-time status updates

2. **Status Hook** (`coeus-frontend/src/hooks/useInterviewStatus.ts`)
   - Polls backend for interview processing status
   - Handles automatic navigation when interview is ready
   - Manages error states and loading indicators

## Workflow Steps

### 1. Form Submission
- User fills out the interview form with:
  - Full name (required)
  - Gender (required)
  - LinkedIn profile URL (required)
  - Resume PDF file (required, max 10MB)
  - Duration (optional, defaults to 30 minutes)

### 2. Initial Processing
- Backend validates form data and saves resume file
- Returns task ID immediately for status tracking
- Starts background processing workflow

### 3. Background Data Collection
- **LinkedIn Scraping**: Extracts profile data using unified scraper
- **Resume Parsing**: Processes uploaded PDF for relevant information
- **Data Combination**: Merges LinkedIn and resume data into unified format

### 4. LDA System Initialization
- Starts the LDA (Lie Detection Agent) system with collected data
- Loads job description and candidate information
- Initializes interview agents and audio systems

### 5. Status Polling & Navigation
- Frontend polls backend every 2 seconds for status updates
- Shows progress indicators for each processing phase
- Automatically redirects to `/akira` when interview is ready

## API Endpoints

### POST `/interview/start`
Starts the interview process with form data.

**Request**: Multipart form data
- `name`: Candidate's full name
- `gender`: Candidate's gender
- `linkedin_url`: LinkedIn profile URL
- `resume`: PDF file upload
- `duration`: Interview duration in seconds (optional)

**Response**:
```json
{
  "message": "Interview workflow started successfully",
  "task_id": "interview_20250928_120000_abc12345",
  "status": "started",
  "processing_status": "data_collection"
}
```

### GET `/interview/status/{task_id}`
Gets current status of an interview task.

**Response**:
```json
{
  "task_id": "interview_20250928_120000_abc12345",
  "status": "ready",
  "processing_status": "interview_active",
  "message": "Interview system is active and ready",
  "ready_for_interview": true,
  "redirect_url": "/akira"
}
```

### POST `/interview/stop/{task_id}`
Stops an active interview and cleans up resources.

## Processing States

1. **`initializing`**: Task created, initial setup in progress
2. **`data_collection`**: Scraping LinkedIn and parsing resume
3. **`data_ready`**: Data processing complete, starting LDA system
4. **`interview_active`**: LDA system running, ready for interview
5. **`failed`**: Error occurred during processing

## Error Handling

- **Validation Errors**: Invalid form data returns 400 with details
- **File Errors**: Invalid resume format or size returns 400
- **Processing Errors**: Data collection failures tracked in task status
- **System Errors**: LDA startup failures logged and reported

## File Structure

```
api/
├── controllers/
│   ├── interview_controller.py    # HTTP request handlers
│   └── task_controller.py         # Legacy task endpoints
├── models/
│   ├── interview_model.py         # Pydantic models
│   └── task_model.py             # Legacy task models
├── services/
│   ├── interview_service.py       # Business logic
│   └── task_service.py           # Legacy task service
├── main.py                       # FastAPI application
└── test_interview_api.py         # Test suite

coeus-frontend/src/
├── components/
│   └── interview-form.tsx        # Main form component
└── hooks/
    └── useInterviewStatus.ts     # Status polling hook

Brain/lda/
├── main.py                       # LDA system entry point
└── unified_scraper.py           # Data collection script
```

## Testing

Run the test suite to verify all components:

```bash
cd /Users/shaurya/Developer/hackathon/eightfold_finals
python api/test_interview_api.py
```

## Configuration

### Environment Variables
- `LINKEDIN_EMAIL`: LinkedIn account email for scraping
- `LINKEDIN_PASSW`: LinkedIn account password for scraping
- `CEREBRAS_API_KEY`: API key for LLM services

### File Paths
- Resume uploads: `temp_uploads/` (auto-created)
- LDA logs: `Brain/lda/lda_logs/`
- Interview logs: `logs/`

## Integration Points

1. **Frontend → Backend**: Form submission via `/interview/start`
2. **Backend → Unified Scraper**: Data collection subprocess
3. **Backend → LDA System**: Interview initialization subprocess
4. **Frontend ← Backend**: Status polling via `/interview/status/{task_id}`
5. **Frontend → Akira**: Automatic navigation when ready

## Security Considerations

- File upload validation (PDF only, 10MB max)
- Input sanitization and validation
- Temporary file cleanup after processing
- CORS configuration for frontend access
- Error message sanitization to prevent information leakage
