# COEUS: AI-Powered Technical Interview Platform

COEUS is a comprehensive AI-driven technical interview platform that combines multiple advanced technologies to conduct sophisticated, real-time technical interviews. The system integrates lie detection, code monitoring, voice interaction, and comprehensive candidate assessment to provide a complete interview solution.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Technical Specifications](#technical-specifications)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

COEUS represents a next-generation technical interview platform designed to address the limitations of traditional interview processes. The system combines artificial intelligence, real-time monitoring, and comprehensive assessment to provide an objective, consistent, and thorough evaluation of technical candidates.

### Key Features

**AI-Powered Interview Agents**
- Multiple specialized agents for different interview scenarios
- Real-time conversation analysis and response generation
- Adaptive questioning based on candidate responses
- Professional interview experience with configurable intensity levels

**Lie Detection System (LDA)**
- Advanced AI-powered claim verification against candidate background
- Real-time analysis of interview responses for inconsistencies
- Confidence scoring for detected discrepancies
- Comprehensive knowledge base integration

**Code Interview Engine**
- Real-time code monitoring and analysis
- Intelligent nudging system for stuck candidates
- Automated test execution and feedback
- Performance logging and assessment

**Voice-Enabled Interaction**
- Speech-to-text (STT) for candidate responses
- Text-to-speech (TTS) for natural interviewer communication
- Low-latency audio processing for seamless conversation
- Filler word caching to mask processing delays

**Comprehensive Data Integration**
- LinkedIn profile scraping and analysis
- Resume parsing and information extraction
- Job description matching and analysis
- Automated candidate background verification

**Advanced Analytics**
- Performance scoring and assessment
- Comprehensive interview logging
- Log consolidation across multiple systems
- Hirability scoring algorithm with detailed breakdown

## System Architecture

COEUS follows a modular, microservices-inspired architecture designed for scalability, maintainability, and extensibility.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│                   Next.js React Application                     │
│              - Interview Forms & UI Components                  │
│              - Real-time Code Editor                           │
│              - Status Monitoring & Progress Tracking           │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                              │
├─────────────────────────────────────────────────────────────────┤
│                     FastAPI Backend                             │
│              - RESTful API Endpoints                           │
│              - WebSocket Connections                           │
│              - Request Validation & Routing                    │
└─────────────────────────────────────────────────────────────────┘
                                   │
                     ┌─────────────┼─────────────┐
                     ▼             ▼             ▼
┌──────────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    LDA System        │ │  Code Interview │ │  Data Pipeline  │
│                      │ │     Engine      │ │                 │
│ - Lie Detection      │ │ - Real-time     │ │ - LinkedIn      │
│ - Knowledge Base     │ │   Monitoring    │ │   Scraping      │
│ - Interview Agents   │ │ - Code Analysis │ │ - Resume        │
│ - Voice Processing   │ │ - Test Execution│ │   Parsing       │
└──────────────────────┘ └─────────────────┘ └─────────────────┘
```

### Component Architecture

**Brain Module Structure**
```
Brain/
├── lda/                          # Lie Detection Agent System
│   ├── main.py                   # LDA orchestration and main loop
│   ├── agents.py                 # AI agents for interviews and lie detection
│   ├── knowledge_db.py           # Knowledge base management
│   ├── audio.py                  # Audio processing and voice interaction
│   └── config.py                 # LDA system configuration
│
├── code interview agent/         # Code Interview System
│   ├── main.py                   # Code interview orchestration
│   ├── agents.py                 # Code interview AI agents
│   ├── code_monitor.py           # Real-time code monitoring
│   ├── audio.py                  # Voice interaction for code interviews
│   ├── performance_logger.py     # Performance tracking and assessment
│   └── prompts.py                # AI prompt templates
│
└── rstt/                         # Real-time Speech-to-Text
    └── main.py                   # STT service entry point
```

## Core Components

### 1. Lie Detection Agent (LDA) System

The LDA system represents the core intelligence of COEUS, designed to verify candidate claims against their documented background and detect potential inconsistencies during interviews.

**Key Features:**
- Advanced AI-powered claim analysis using Cerebras LLM
- Real-time fact-checking against LinkedIn and resume data
- Confidence scoring for detected discrepancies
- Contextual nudging when inconsistencies are identified
- Comprehensive conversation history tracking

**Technical Implementation:**
- Langchain integration for advanced LLM interactions
- Pydantic models for structured data validation
- Asynchronous processing for real-time analysis
- Knowledge base with 143+ extracted candidate data points

### 2. Code Interview Engine

The Code Interview Engine provides comprehensive real-time monitoring and assessment of coding sessions.

**Core Capabilities:**
- Browser automation for code editor monitoring
- Real-time code change detection and analysis
- Intelligent nudging system for candidate assistance
- Automated test execution and result analysis
- Performance metrics and scoring algorithms

**Technical Stack:**
- Selenium WebDriver for browser automation
- Real-time code diff analysis
- AI-powered hint generation and delivery
- Comprehensive performance logging

### 3. Voice Interaction System

The voice system enables natural conversation between AI interviewers and candidates.

**Components:**
- **Speech-to-Text (STT):** Real-time transcription using advanced models
- **Text-to-Speech (TTS):** Natural voice synthesis with multiple providers
- **Audio Management:** Low-latency audio processing and queue management
- **Filler Words:** Pre-cached audio to mask processing delays

**Supported Providers:**
- Deepgram for high-quality STT
- Azure Cognitive Services
- OpenAI Whisper
- ElevenLabs for premium TTS

### 4. Data Integration Pipeline

Comprehensive data collection and processing system for candidate background verification.

**Data Sources:**
- **LinkedIn Profiles:** Automated scraping with Selenium
- **Resume Documents:** PDF parsing and information extraction
- **Job Descriptions:** Requirement analysis and matching
- **Interview Logs:** Historical performance data

**Processing Capabilities:**
- Automatic latest file detection
- Comprehensive data extraction (143+ data points)
- Hirability scoring algorithm
- Data consolidation across multiple sources

### 5. Web Interface

Modern, responsive web interface built with Next.js and TypeScript.

**Key Features:**
- Real-time interview status monitoring
- Comprehensive form validation
- Progress tracking with animated indicators
- Responsive design for multiple devices
- Accessibility-compliant components

**Technology Stack:**
- Next.js 15 with Turbopack
- TypeScript for type safety
- Tailwind CSS for styling
- Shadcn/UI component library
- Framer Motion for animations

## Installation and Setup

### System Requirements

**Operating System:**
- macOS (primary support)
- Linux (tested compatibility)
- Windows (with appropriate path adjustments)

**Runtime Requirements:**
- Python 3.13 or higher
- Node.js 16.0 or higher
- Chrome Browser (latest version)
- ChromeDriver (compatible version)

**Hardware Recommendations:**
- Minimum: 8GB RAM, quad-core processor
- Recommended: 16GB RAM, 8-core processor
- Audio input/output devices for voice interaction

### Prerequisites Installation

**1. Install Python Dependencies**
```bash
# Clone the repository
git clone <repository-url>
cd coeus_submission

# Install uv package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies using uv
uv sync

# Alternative: Install with pip
pip install -r requirements.txt
```

**2. Install Node.js Dependencies**
```bash
# Navigate to frontend directory
cd coeus-frontend

# Install dependencies using pnpm (recommended)
pnpm install

# Alternative: Install with npm
npm install
```

**3. Install Resume Parser Dependencies**
```bash
# Navigate to resume parser directory
cd resume_parser

# Install TypeScript dependencies
npm install
```

**4. Setup ChromeDriver**
```bash
# Download ChromeDriver from https://chromedriver.chromium.org/
# Ensure version matches your Chrome browser

# Set environment variable
export CHROMEDRIVER=/path/to/chromedriver

# Make executable (Linux/macOS)
chmod +x /path/to/chromedriver
```

### Environment Configuration

**1. Create Environment File**
```bash
# Create .env file in project root
touch .env
```

**2. Configure Required Variables**
```bash
# .env file contents
# LinkedIn Credentials (required for profile scraping)
LINKEDIN_EMAIL=your_linkedin_email@example.com
LINKEDIN_PASSW=your_linkedin_password

# AI/LLM Configuration
CEREBRAS_API_KEY=your_cerebras_api_key

# Audio Services (optional)
DEEPGRAM_API_KEY=your_deepgram_api_key
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
OPENAI_API_KEY=your_openai_api_key

# Chrome Driver Path (if not in PATH)
CHROMEDRIVER=/path/to/chromedriver
```

### Initial Setup Verification

**1. Verify Python Environment**
```bash
# Test Python installation
python --version
uv --version

# Test basic imports
python -c "import fastapi, cerebras, selenium; print('Dependencies OK')"
```

**2. Verify Node.js Environment**
```bash
# Test Node.js installation
node --version
pnpm --version

# Test frontend build
cd coeus-frontend
pnpm build
```

**3. Test Audio System**
```bash
# Test audio devices
python playground/test_local_mic.py
```

## Usage

### Quick Start Guide

**1. Start the Backend API**
```bash
# Navigate to API directory
cd api

# Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Start the Frontend Application**
```bash
# Navigate to frontend directory
cd coeus-frontend

# Start Next.js development server
pnpm dev
```

**3. Access the Application**
```
Frontend: http://localhost:3000
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health
```

### Interview Workflow

**1. Candidate Registration**
- Navigate to the interview form at `http://localhost:3000`
- Fill in required information:
  - Full name
  - Gender
  - LinkedIn profile URL
  - Resume PDF upload (max 10MB)
  - Interview duration (optional, defaults to 30 minutes)

**2. Data Processing Phase**
- System automatically processes candidate information
- LinkedIn profile scraping (if credentials configured)
- Resume parsing and information extraction
- Knowledge base population and verification

**3. Interview Initialization**
- Background processing completes
- AI interview agents initialize
- Audio systems prepare for interaction
- Code editor environment setup (for code interviews)

**4. Interview Execution**
- Real-time voice interaction with AI interviewer
- Automated question generation based on candidate background
- Live code monitoring and analysis (code interviews)
- Continuous lie detection and fact verification

**5. Assessment and Results**
- Comprehensive performance scoring
- Interview summary generation
- Log consolidation and analysis
- Hirability assessment with detailed breakdown

### Direct System Access

**LDA Interview System**
```bash
# Navigate to LDA directory
cd Brain/lda

# Start lie detection interview
python main.py
```

**Code Interview System**
```bash
# Navigate to code interview directory
cd "Brain/code interview agent"

# Start code interview with candidate name
python main.py "John Doe"

# Start with specific interview mode
python main.py "Jane Smith" --mode challenging
```

**Data Collection Tools**
```bash
# Scrape LinkedIn profile
python linkdin_scrapper.py

# Parse resume document
cd resume_parser
npx tsx parse_resume.ts /path/to/resume.pdf

# Unified data collection
python collect_candidate_data.py --linkedin-url "https://linkedin.com/in/profile" --resume-pdf "resume.pdf"
```

## API Documentation

### RESTful Endpoints

**Interview Management**

```http
POST /interview/start
Content-Type: multipart/form-data

Parameters:
- name: string (required) - Candidate's full name
- gender: string (required) - Candidate's gender
- linkedin_url: string (required) - LinkedIn profile URL
- resume: file (required) - PDF resume file (max 10MB)
- duration: integer (optional) - Interview duration in seconds

Response:
{
  "message": "Interview workflow started successfully",
  "task_id": "interview_20250928_120000_abc12345",
  "status": "started",
  "processing_status": "data_collection"
}
```

```http
GET /interview/status/{task_id}

Response:
{
  "task_id": "interview_20250928_120000_abc12345",
  "status": "ready",
  "processing_status": "interview_active",
  "message": "Interview system is active and ready",
  "ready_for_interview": true,
  "redirect_url": "/akira"
}
```

```http
POST /interview/stop/{task_id}

Response:
{
  "message": "Interview stopped successfully",
  "task_id": "interview_20250928_120000_abc12345",
  "status": "stopped"
}
```

**Task Management**

```http
GET /tasks/health
Response:
{
  "status": "healthy",
  "timestamp": "2025-09-29T12:00:00Z",
  "active_tasks": 0
}
```

**Question Management**

```http
GET /questions/available
Response:
{
  "questions": [
    {
      "id": "two_sum",
      "title": "Two Sum",
      "difficulty": "Easy",
      "tags": ["array", "hash-table"]
    }
  ],
  "total_count": 150
}
```

### WebSocket Endpoints

**Agent Communication**

```
Endpoint: ws://localhost:8000/ws/agent

Message Types:

Client → Server:
{
  "type": "start_agent",
  "candidate_name": "John Doe",
  "interview_mode": "challenging"
}

{
  "type": "stop_agent"
}

{
  "type": "ping"
}

Server → Client:
{
  "type": "connected",
  "message": "WebSocket connection established"
}

{
  "type": "agent_started",
  "pid": 12345,
  "message": "Agent subprocess started successfully"
}

{
  "type": "agent_completed",
  "reason": "completed",
  "message": "Interview completed successfully"
}

{
  "type": "subprocess_output",
  "output": "Real-time output from interview agent"
}
```

### Error Handling

**Standard Error Response Format**
```json
{
  "error": "Error type identifier",
  "message": "Human-readable error description",
  "details": "Additional error context",
  "timestamp": "2025-09-29T12:00:00Z"
}
```

**Common HTTP Status Codes**
- `200` - Success
- `400` - Bad Request (validation errors)
- `404` - Resource not found
- `422` - Unprocessable Entity (invalid data)
- `500` - Internal server error

## Configuration

### System Configuration Files

**API Configuration (api/config.py)**
```python
# Server settings
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ["application/pdf"]

# Task settings
TASK_TIMEOUT = 300  # 5 minutes
CLEANUP_INTERVAL = 3600  # 1 hour
```

**LDA Configuration (Brain/lda/config.py)**
```python
# Interview settings
MAX_INTERVIEW_DURATION = 1800  # 30 minutes
LIE_CONFIDENCE_THRESHOLD = 0.7
LISTENING_WINDOW = 10  # seconds

# Audio settings
AUDIO_CACHE_DIR = "audio_cache"
TTS_PROVIDER = "deepgram"  # deepgram, azure, openai
STT_PROVIDER = "deepgram"  # deepgram, azure, openai

# AI model settings
LLM_MODEL = "gpt-oss-120b"
LLM_TEMPERATURE = 0.8
LLM_MAX_TOKENS = 1024
```

**Code Interview Configuration (Brain/code interview agent/config.py)**
```python
# Monitoring settings
POLLING_INTERVAL = 5  # seconds
INACTIVITY_THRESHOLD = 30  # seconds
CODE_CHANGE_DETECTION = True

# Browser settings
BROWSER_URL = "http://localhost:3000"
BROWSER_TIMEOUT = 30
HEADLESS_MODE = False

# Performance settings
PERFORMANCE_LOGGING = True
DETAILED_ANALYTICS = True
```

### Environment Variables

**Required Variables**
```bash
# AI/LLM Services
CEREBRAS_API_KEY=your_cerebras_api_key

# LinkedIn Integration
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSW=your_linkedin_password
```

**Optional Variables**
```bash
# Audio Services
DEEPGRAM_API_KEY=your_deepgram_key
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=your_azure_region
OPENAI_API_KEY=your_openai_key

# Browser Automation
CHROMEDRIVER=/path/to/chromedriver
BROWSER_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Technical Specifications

### AI and Machine Learning

**Large Language Models**
- Primary: Cerebras GPT-OSS-120B for production workloads
- Fallback: OpenAI GPT-4 for enhanced reasoning
- Temperature: 0.8 for balanced creativity and consistency
- Max tokens: 1024 for comprehensive responses

**Lie Detection Algorithm**
- Confidence threshold: 0.7 (70% confidence required)
- Knowledge base matching against 143+ extracted data points
- Real-time claim verification with contextual analysis
- Multi-factor assessment including consistency, specificity, and verifiability

**Hirability Scoring Algorithm**
```
Weighted Categories:
- Technical Skills (30%): Programming languages, frameworks, tools
- AI/ML Experience (25%): Machine learning, data science expertise
- Experience Level (20%): Years of experience, seniority indicators
- Education Background (15%): Degrees, certifications, achievements
- Soft Skills (10%): Communication, teamwork, problem-solving

Scoring Logic:
- Job-relevant skills: 2 points
- Additional skills: 1 point
- Range: 0-100 with weighted averages

Recommendations:
- 80-100: Strong Hire
- 65-79: Hire
- 50-64: Weak Hire
- 35-49: Weak No Hire
- 0-34: No Hire
```

### Audio Processing

**Speech-to-Text (STT)**
- Real-time transcription with low latency
- Noise cancellation and audio enhancement
- Multi-language support (primary: English)
- Confidence scoring for transcription quality

**Text-to-Speech (TTS)**
- Natural voice synthesis with emotional inflection
- Multiple voice options and speaking rates
- SSML support for advanced speech control
- Audio caching for improved performance

**Audio Management**
- Asynchronous audio queue processing
- Filler word injection to mask processing delays
- Real-time audio level monitoring
- Cross-platform audio device compatibility

### Code Monitoring

**Real-time Analysis**
- Code change detection with 5-second intervals
- Diff analysis for incremental changes
- Syntax and style analysis
- Performance impact assessment

**Test Execution**
- Automated test running and result capture
- Real-time feedback on test outcomes
- Performance metrics collection
- Error analysis and debugging assistance

### Data Processing

**LinkedIn Scraping**
- Selenium-based automation for profile extraction
- Comprehensive data extraction: experiences, education, skills, projects
- Rate limiting and anti-detection measures
- Data validation and cleaning

**Resume Parsing**
- PDF text extraction and analysis
- Section identification and categorization
- Skill extraction and classification
- Experience timeline construction

### Security and Privacy

**Data Protection**
- Temporary file handling with automatic cleanup
- Encrypted storage for sensitive information
- Access control and authentication
- GDPR compliance measures

**System Security**
- Input validation and sanitization
- SQL injection prevention
- Cross-site scripting (XSS) protection
- Rate limiting and DDoS protection

## Development Workflow

### Code Organization

**Project Structure Principles**
- Model-Controller-Service architecture pattern
- Separation of concerns across modules
- Type-safe development with TypeScript and Python typing
- Comprehensive error handling and logging

**Python Development Guidelines**
- Type annotations for all functions and classes
- PEP 257 docstring conventions
- Pytest for testing framework
- Ruff for code formatting and linting
- Virtual environment management with uv

**TypeScript Development Guidelines**
- Strict TypeScript configuration
- Functional components with hooks
- Shadcn/UI component library
- Tailwind CSS for styling
- Next.js best practices

### Testing Strategy

**Backend Testing**
```bash
# Run API tests
cd api
python -m pytest tests/ -v

# Run specific test modules
python test_interview_api.py
python test_lie_detection_logging.py
```

**Frontend Testing**
```bash
# Run frontend tests
cd coeus-frontend
pnpm test

# Run component tests
pnpm test:components

# Run integration tests
pnpm test:integration
```

**System Integration Testing**
```bash
# Test WebSocket communication
python test_websocket_simple.py

# Test end-to-end workflow
python api/test_interview_api.py
```

### Development Environment Setup

**Backend Development**
```bash
# Start API in development mode
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

**Frontend Development**
```bash
# Start frontend with hot reload
cd coeus-frontend
pnpm dev

# Start with specific port
pnpm dev --port 3001
```

**Audio System Development**
```bash
# Test audio components
python playground/test_local_mic.py
python playground/test_beep.py
```

### Code Quality and Standards

**Python Code Standards**
- Black formatting with line length 88
- Import sorting with isort
- Type checking with mypy
- Docstring coverage validation
- Security scanning with bandit

**TypeScript Code Standards**
- ESLint with strict configuration
- Prettier formatting
- Import organization
- Component composition patterns
- Accessibility compliance (WCAG 2.1)

## Testing

### Test Suite Organization

**Unit Tests**
- Individual component testing
- Mock external dependencies
- Isolated functionality verification
- High code coverage targets (>80%)

**Integration Tests**
- Multi-component interaction testing
- Database and API integration
- File system operations
- External service integration

**End-to-End Tests**
- Complete workflow testing
- User journey validation
- Performance benchmarking
- Stress testing under load

### Testing Commands

**Comprehensive Test Execution**
```bash
# Run all tests
make test

# Run with coverage report
make test-coverage

# Run specific test categories
make test-unit
make test-integration
make test-e2e
```

**Individual Test Modules**
```bash
# API functionality tests
python api/test_interview_api.py

# LDA system tests
python Brain/lda/test_agents.py

# Code interview tests
python "Brain/code interview agent/test_main.py"

# Frontend component tests
cd coeus-frontend && pnpm test
```

### Performance Testing

**Load Testing**
```bash
# API load testing
python tests/load_test_api.py

# WebSocket connection testing
python tests/load_test_websocket.py

# Audio system performance
python tests/test_audio_performance.py
```

**Memory and Performance Profiling**
```bash
# Memory profiling
python -m memory_profiler Brain/lda/main.py

# Performance profiling
python -m cProfile -s cumulative Brain/lda/main.py
```

## Deployment

### Production Environment Setup

**Docker Deployment**
```dockerfile
# Backend Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build
EXPOSE 3000

CMD ["npm", "start"]
```

**Docker Compose Configuration**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CEREBRAS_API_KEY=${CEREBRAS_API_KEY}
      - LINKEDIN_EMAIL=${LINKEDIN_EMAIL}
      - LINKEDIN_PASSW=${LINKEDIN_PASSW}
    volumes:
      - ./logs:/app/logs
      - ./temp_uploads:/app/temp_uploads

  frontend:
    build: ./coeus-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Production Configuration

**Environment Variables for Production**
```bash
# Production environment
NODE_ENV=production
PYTHON_ENV=production

# Security
SECRET_KEY=your_production_secret_key
JWT_SECRET=your_jwt_secret

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO

# Performance
WORKERS=4
MAX_CONNECTIONS=100
```

**Security Hardening**
```bash
# SSL/TLS Configuration
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com
```

### Monitoring and Logging

**Application Monitoring**
```python
# Performance monitoring setup
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

**Health Checks**
```bash
# API health endpoint
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/tasks/health
```

**Log Aggregation**
```bash
# Centralized logging setup
python log_consolidator.py

# Log rotation configuration
logrotate -d /etc/logrotate.d/coeus
```

## Contributing

### Development Guidelines

**Code Contribution Process**
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Run the full test suite
5. Submit a pull request with description

**Code Review Checklist**
- Type annotations and documentation
- Test coverage for new functionality
- Performance impact assessment
- Security vulnerability review
- Backward compatibility verification

**Development Tools Setup**
```bash
# Install development dependencies
uv sync --group dev

# Setup pre-commit hooks
pre-commit install

# Run code quality checks
make lint
make format
make type-check
```

### Issue Reporting

**Bug Reports**
- Provide detailed reproduction steps
- Include system environment information
- Attach relevant log files
- Specify expected vs actual behavior

**Feature Requests**
- Describe the use case and benefits
- Provide implementation suggestions
- Consider backward compatibility
- Include acceptance criteria

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for detailed terms and conditions.

---

**COEUS Technical Interview Platform**
Version 1.0.0 | Documentation Last Updated: September 29, 2025

For technical support and inquiries, please refer to the project documentation or contact the development team.