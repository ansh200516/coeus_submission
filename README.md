# 🎯 Eightfold Finals - AI-Powered Interview Platform

## 📋 Project Overview

**Eightfold Finals** is a comprehensive AI-powered interview platform designed to automate and enhance the technical interview process. The system combines multiple sophisticated components including lie detection, code interview monitoring, resume parsing, LinkedIn data scraping, and real-time audio/video processing to create a complete interview automation solution.

### 🌟 Key Features

- **🕵️ Lie Detection & Analysis (LDA)** - Advanced AI system that detects inconsistencies between candidate claims and verified facts
- **💻 Code Interview Agent** - Real-time code monitoring with intelligent nudging during technical interviews
- **📄 Resume Parsing** - Automated extraction of structured data from PDF resumes
- **🔗 LinkedIn Profile Scraping** - Comprehensive LinkedIn data extraction and analysis
- **🎤 Voice Interface** - Real-time speech-to-text and text-to-speech capabilities
- **🌐 Modern Web Frontend** - React/Next.js application with beautiful UI and real-time status updates
- **📊 Performance Analytics** - Detailed interview metrics and candidate assessment
- **🔄 Log Consolidation** - Unified logging system across all interview components

---

## 🏗️ Architecture Overview

The project follows a **microservices architecture** with distinct components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   Interview     │
│   (Next.js)     │────│   Backend        │────│   Agents        │
│   React App     │    │   API Server     │    │   (LDA + Code)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                       ┌────────▼────────┐              │
                       │   Data Layer    │              │
                       │   - LinkedIn    │              │
                       │   - Resume      │              │
                       │   - Job Desc    │              │
                       └─────────────────┘              │
                                │                        │
                       ┌────────▼────────────────────────▼─────────┐
                       │           Audio/Video Layer             │
                       │   - Speech-to-Text (Deepgram/Azure)    │
                       │   - Text-to-Speech (Multiple TTS)      │
                       │   - Real-time Audio Processing         │
                       └─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
eightfold_finals/
├── 🌐 Frontend & UI
│   ├── coeus-frontend/                 # Next.js React application
│   │   ├── src/app/                   # App router pages
│   │   ├── src/components/            # Reusable UI components
│   │   └── src/hooks/                 # Custom React hooks
│   └── ui/                           # Additional UI assets
│
├── 🔧 Backend API
│   ├── api/                          # FastAPI backend server
│   │   ├── controllers/              # HTTP request handlers
│   │   ├── models/                   # Pydantic data models
│   │   ├── services/                 # Business logic layer
│   │   └── main.py                   # FastAPI application entry
│   └── tests/                        # Backend test suite
│
├── 🧠 AI Interview Agents
│   ├── Brain/
│   │   ├── lda/                      # Lie Detection & Analysis system
│   │   │   ├── agents.py             # LDA agents and models
│   │   │   ├── main.py               # LDA system entry point
│   │   │   └── knowledge_db.py       # Knowledge base management
│   │   └── code interview agent/     # Code interview monitoring
│   │       ├── main.py               # Code interview system
│   │       ├── agents.py             # Interview AI agents
│   │       ├── audio.py              # Audio processing
│   │       └── shared_state.py       # Interview state management
│   └── rstt/ & rtts/                 # Speech processing modules
│
├── 📄 Data Processing
│   ├── resume_parser/                # TypeScript resume parser
│   │   ├── parse_resume.ts           # Main parsing logic
│   │   ├── open-resume/              # Open-resume library integration
│   │   └── view_sections.ts          # Parsed data viewer
│   ├── linkedin_scraper/             # LinkedIn profile scraper
│   │   └── linkedin_scraper/         # Core scraping modules
│   └── linkdin_scrapper.py           # LinkedIn scraper wrapper
│
├── 🔄 Code Engine & Testing
│   ├── code_engine/                  # Code execution environments
│   │   └── react-code-editor-app/    # In-browser code editor
│   └── playground/                   # Development and testing tools
│       ├── code_engine/              # Alternative code editors
│       └── integrator_api/           # Integration testing
│
├── 📊 Logs & Data
│   ├── logs/                         # Interview and processing logs
│   ├── consolidated_logs/            # Unified log output
│   ├── temp_uploads/                 # Temporary file storage
│   └── old logs/                     # Archived log files
│
└── 🔧 Configuration & Utils
    ├── pyproject.toml                # Python project configuration
    ├── requirements.txt              # Python dependencies
    ├── job_description.txt           # Job posting for context
    └── log_consolidator.py           # Log aggregation utility
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.13+** (with `uv` package manager)
- **Node.js 16.0.0+** with `pnpm`
- **Chrome Browser** (for LinkedIn scraping)
- **ChromeDriver** (compatible with Chrome version)

### 1. Clone Repository

```bash
git clone <repository-url>
cd eightfold_finals
```

### 2. Python Environment Setup

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync

# Or using pip (fallback)
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd coeus-frontend
pnpm install
cd ..
```

### 4. Resume Parser Setup

```bash
cd resume_parser
npm install
cd ..
```

### 5. Code Engine Setup (Optional)

```bash
cd playground/code_engine/react-code-editor-app
npm install
cd ../../..
```

### 6. Environment Configuration

Create a `.env` file in the project root:

```bash
# LinkedIn Scraping Credentials
LINKEDIN_EMAIL=your-linkedin-email@example.com
LINKEDIN_PASSW=your-linkedin-password

# AI/ML API Keys
CEREBRAS_API_KEY=your-cerebras-api-key
OPENAI_API_KEY=your-openai-api-key  # Optional

# Audio Processing Keys (Optional)
DEEPGRAM_API_KEY=your-deepgram-key
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-azure-region

# ChromeDriver Path (if not in PATH)
CHROMEDRIVER=/path/to/chromedriver
```

---

## 🎮 Usage Guide

### Quick Start - Complete Interview Workflow

1. **Start the Backend API**:

   ```bash
   cd api
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the Frontend**:

   ```bash
   cd coeus-frontend
   pnpm dev
   ```

3. **Access the Platform**:
   - Open browser to `http://localhost:3000`
   - Navigate through the interview setup form
   - Upload candidate resume and LinkedIn profile
   - Monitor real-time interview progress

### Individual Component Usage

#### 🕵️ Lie Detection & Analysis (LDA) System

```bash
cd Brain/lda
uv run python main.py
```

**Features:**

- Real-time lie detection during interviews
- Intelligent nudging when inconsistencies detected
- Comprehensive analysis against verified facts
- Multi-level confidence scoring

#### 💻 Code Interview Agent

```bash
cd "Brain/code interview agent"
uv run python main.py --candidate-name "John Doe" --interview-mode challenging
```

**Features:**

- Real-time code monitoring
- Intelligent hint system
- Performance tracking
- Audio interaction capabilities

#### 📄 Resume Parser

```bash
cd resume_parser
npm run dev parse_resume.ts /path/to/resume.pdf

# View parsed sections
npx ts-node view_sections.ts ../logs/resume_example.json
```

**Extracts:**

- Personal information
- Work experience and internships
- Education and achievements
- Technical skills (60+ categories)
- Projects and accomplishments

#### 🔗 LinkedIn Profile Scraper

```bash
# Set credentials in .env file first
python linkdin_scrapper.py

# Or use the integrated scraper
python collect_candidate_data.py --linkedin-url "https://linkedin.com/in/username"
```

**Extracts:**

- Professional summary
- Work experience (5+ positions)
- Education history
- Skills (20+ technical skills)
- Projects and certifications

#### 🔄 Log Consolidation

```bash
# Consolidate all interview logs
python log_consolidator.py
```

**Output:**

- Unified interview summary
- Lie detection results
- Performance metrics
- Hiring recommendations

---

## 🔧 Core Components

### 1. **Frontend Application (coeus-frontend)**

**Technology**: Next.js 15 + React 19 + TypeScript + Tailwind CSS

**Key Features:**

- Beautiful landing page with "COEUS" branding
- Interactive interview form with file uploads
- Real-time status polling and progress indicators
- Voice interface components with prismatic visualizations
- Responsive design with modern UI components

**Main Pages:**

- `/` - Landing page
- `/login` - Authentication
- `/dashboard` - Interview management
- `/akira` - Live interview interface
- `/voice-interface` - Voice interaction demos

### 2. **Backend API (api/)**

**Technology**: FastAPI + Pydantic + Model-Controller-Service Architecture

**Endpoints:**

- `POST /interview/start` - Begin interview workflow
- `GET /interview/status/{task_id}` - Check processing status
- `POST /interview/stop/{task_id}` - Terminate interview
- `GET /health` - System health check

**Features:**

- Async request handling
- File upload management (10MB max)
- Background task processing
- CORS middleware for frontend integration
- Comprehensive error handling and logging

### 3. **Lie Detection & Analysis (Brain/lda/)**

**Technology**: LangChain + Cerebras + Pydantic + Advanced NLP

**Core Components:**

- `LieDetectionAgent` - Analyzes transcripts for inconsistencies
- `InterviewerAgent` - Conducts grilling interviews with nudges
- `KnowledgeDatabase` - Manages verified candidate facts
- `FinalReviewAgent` - Generates hiring recommendations

**Capabilities:**

- Real-time transcript analysis
- Confidence-based lie scoring (0-1 scale)
- Escalating nudge system (polite → aggressive)
- Comprehensive fact verification
- Detailed logging with categorization

### 4. **Code Interview Agent (Brain/code interview agent/)**

**Technology**: Cerebras + WebSocket + Audio Processing + Browser Automation

**Core Components:**

- `CodeInterviewSystem` - Main orchestration system
- `CodeInterviewerAgent` - AI interviewer with challenging personality
- `AudioManager` - Real-time audio processing
- `PerformanceLogger` - Interview metrics tracking

**Features:**

- Real-time code monitoring via browser automation
- Intelligent nudging based on code analysis
- Multi-TTS engine support (Azure, OpenAI, gTTS, ElevenLabs)
- Speech-to-text with Deepgram integration
- WebSocket communication for real-time updates

### 5. **Resume Parser (resume_parser/)**

**Technology**: TypeScript + PDF.js + Open-Resume Library

**Capabilities:**

- PDF text extraction and processing
- Intelligent section detection
- Structured data extraction for:
  - Personal information
  - Work experience
  - Education history
  - Technical skills
  - Projects and achievements
- JSON output with comprehensive metadata

### 6. **LinkedIn Scraper (linkedin_scraper/)**

**Technology**: Selenium + Python + Chrome Automation

**Features:**

- Automated LinkedIn profile scraping
- Comprehensive data extraction:
  - Professional summary
  - Work experience
  - Education
  - Skills and endorsements
  - Projects and certifications
- Anti-detection measures
- Structured JSON output

---

## 🔄 Complete Workflow

### 1. **Candidate Onboarding**

1. Candidate accesses the platform at `http://localhost:3000`
2. Fills out interview form with personal details
3. Uploads resume PDF (max 10MB)
4. Provides LinkedIn profile URL
5. Submits form to initiate interview process

### 2. **Data Collection & Processing**

1. **Backend receives form submission** via `/interview/start`
2. **Resume parsing** extracts structured data from PDF
3. **LinkedIn scraping** gathers comprehensive profile information
4. **Data consolidation** merges resume and LinkedIn data
5. **Knowledge base creation** for fact verification

### 3. **Interview System Initialization**

1. **LDA system startup** with candidate knowledge base
2. **Code interview agent initialization**
3. **Audio systems activation** (TTS/STT)
4. **WebSocket connection establishment**
5. **Status updates** sent to frontend

### 4. **Live Interview Execution**

1. **Frontend navigation** to `/akira` interview interface
2. **Real-time audio interaction** between candidate and AI
3. **Code monitoring** (if applicable) with intelligent nudging
4. **Lie detection** analyzing responses against verified facts
5. **Performance tracking** throughout interview duration

### 5. **Post-Interview Processing**

1. **Interview completion** triggers cleanup processes
2. **Log consolidation** creates unified interview summary
3. **Performance analysis** generates candidate metrics
4. **Hiring recommendation** based on AI analysis
5. **Results available** for review and decision-making

---

## 🛠️ Development

### Running the Full Stack

**Terminal 1 - Backend API:**

```bash
cd api
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**

```bash
cd coeus-frontend
pnpm dev
```

**Terminal 3 - LDA System (when needed):**

```bash
cd Brain/lda
uv run python main.py
```

**Terminal 4 - Code Interview Agent (when needed):**

```bash
cd "Brain/code interview agent"
uv run python main.py
```

### Testing

**Backend Tests:**

```bash
cd api
python test_interview_api.py
python test_api.py
```

**LDA System Tests:**

```bash
cd tests
uv run python test_lie_detection_logging.py
```

**WebSocket Tests:**

```bash
python test_websocket_simple.py
```

### Code Style & Linting

```bash
# Python code formatting
uv run black .

# Frontend linting
cd coeus-frontend
pnpm lint
pnpm format
```

---

## 📊 Data Flow & Integration

### Input Data Sources

- **Candidate Resume** (PDF) → Structured extraction
- **LinkedIn Profile** → Comprehensive scraping
- **Job Description** → Context for evaluation
- **Real-time Audio** → Speech processing

### Processing Pipelines

1. **Resume Parser** → JSON with skills, experience, education
2. **LinkedIn Scraper** → JSON with professional history
3. **Knowledge Database** → Verified facts for lie detection
4. **Audio Pipeline** → STT → Analysis → TTS → Output

### Output Generation

- **Consolidated Interview Logs** → `consolidated_logs/`
- **Performance Metrics** → Detailed candidate assessment
- **Hiring Recommendations** → AI-powered hiring decisions
- **Lie Detection Reports** → Flagged inconsistencies with confidence scores

---

## 🎯 Key Technologies

### Backend Stack

- **FastAPI** - Modern async Python web framework
- **Pydantic** - Data validation and serialization
- **LangChain** - LLM orchestration and chain management
- **Cerebras** - High-performance LLM inference
- **WebSockets** - Real-time communication
- **Selenium** - Browser automation for scraping

### Frontend Stack

- **Next.js 15** - React framework with App Router
- **React 19** - Modern React with latest features
- **TypeScript** - Type-safe JavaScript development
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **Framer Motion** - Animation and interaction library

### AI & Audio

- **Cerebras Cloud SDK** - LLM API integration
- **Deepgram** - Advanced speech-to-text
- **Azure Cognitive Services** - Enterprise-grade STT/TTS
- **OpenAI** - Additional LLM capabilities
- **RealtimeTTS** - Multi-engine text-to-speech

### Data Processing

- **PDF.js** - Client-side PDF processing
- **Open-Resume** - Resume parsing algorithms
- **NLTK** - Natural language processing
- **NumPy/Pandas** - Data manipulation (where applicable)

---

## 📋 API Documentation

### Core Endpoints

#### Interview Management

- `POST /interview/start` - Start interview workflow
- `GET /interview/status/{task_id}` - Get interview status
- `POST /interview/stop/{task_id}` - Stop interview

#### Task Management (Legacy)

- `GET /tasks/health` - System health check
- `POST /tasks` - Create new task
- `GET /tasks/{task_id}` - Get task status

#### WebSocket Endpoints

- `WS /ws/agent` - Code interview agent communication

### Data Models

**Interview Request:**

```json
{
  "name": "string",
  "gender": "string",
  "linkedin_url": "string",
  "resume": "file",
  "duration": "integer (optional)"
}
```

**Status Response:**

```json
{
  "task_id": "string",
  "status": "ready|processing|failed",
  "processing_status": "string",
  "message": "string",
  "ready_for_interview": "boolean"
}
```

---

## 🧪 Testing & Quality Assurance

### Automated Testing

- **Backend API Tests** - FastAPI endpoint validation
- **LDA System Tests** - Lie detection accuracy
- **WebSocket Tests** - Real-time communication
- **Integration Tests** - End-to-end workflow

### Manual Testing Tools

- **WebSocket Test Client** - `test_websocket_simple.py`
- **Audio Testing** - `playground/test_local_mic.py`
- **Subprocess Testing** - `playground/test_subprocess.py`

### Code Quality

- **Black** - Python code formatting
- **Biome** - Frontend linting and formatting
- **TypeScript** - Static type checking
- **Pydantic** - Runtime data validation

---

## 📈 Performance & Scalability

### Optimization Features

- **Async/Await** throughout backend
- **Background task processing** for data collection
- **WebSocket connections** for real-time updates
- **Efficient PDF parsing** with streaming
- **Caching** for resume and LinkedIn data
- **Connection pooling** for database operations

### Monitoring & Logging

- **Structured logging** across all components
- **Performance metrics** collection
- **Error tracking** with detailed context
- **Audio processing metrics**
- **Interview completion analytics**

---

## 🔒 Security Considerations

### Data Protection

- **File upload validation** (PDF only, 10MB max)
- **Input sanitization** across all endpoints
- **Temporary file cleanup** after processing
- **Secure credential management** via environment variables

### Access Control

- **CORS configuration** for frontend access
- **Rate limiting** on API endpoints (future)
- **Authentication middleware** (planned)
- **Audit logging** for all operations

---

## 🔄 Deployment

### Development Deployment

```bash
# Start all services locally
./start_dev.sh  # If script exists, or manually start each component
```

### Production Considerations

- **Docker containerization** (future enhancement)
- **Kubernetes orchestration** for scaling
- **Load balancing** for multiple interview sessions
- **Database persistence** for candidate data
- **CDN integration** for static assets

---

## 📚 Additional Documentation

- [`INTERVIEW_WORKFLOW.md`](INTERVIEW_WORKFLOW.md) - Detailed workflow documentation
- [`LOG_CONSOLIDATOR_README.md`](LOG_CONSOLIDATOR_README.md) - Log aggregation system
- [`SCRAPER_INTEGRATION_GUIDE.md`](SCRAPER_INTEGRATION_GUIDE.md) - Data collection integration
- [`WEBSOCKET_REFACTOR.md`](WEBSOCKET_REFACTOR.md) - WebSocket architecture
- [`Brain/lda/LIE_DETECTION_README.md`](Brain/lda/LIE_DETECTION_README.md) - LDA system details
- [`Brain/code interview agent/README.md`](Brain/code%20interview%20agent/README.md) - Code interview agent
- [`resume_parser/README.md`](resume_parser/README.md) - Resume parsing details

---

## 🤝 Contributing

### Code Standards

- **Python**: Follow PEP 8, use type hints, comprehensive docstrings
- **TypeScript**: Strict typing, modern ES6+ features
- **React**: Functional components, hooks, TypeScript integration
- **Testing**: pytest for Python, Jest for TypeScript/React

### Development Workflow

1. Create feature branch from main
2. Implement changes with tests
3. Run full test suite
4. Submit pull request with detailed description
5. Code review and approval process

---

## 🆘 Support & Troubleshooting

### Common Issues

**LinkedIn Scraping Fails:**

- Verify credentials in `.env` file
- Check ChromeDriver compatibility
- Ensure Chrome browser is updated

**Resume Parsing Errors:**

- Verify PDF is not password-protected
- Check file size (max 10MB)
- Ensure file is valid PDF format

**Audio Issues:**

- Check microphone permissions
- Verify audio API keys (Deepgram, Azure)
- Test audio devices with `playground/test_local_mic.py`

**Frontend Connection Issues:**

- Verify backend is running on port 8000
- Check CORS configuration
- Ensure WebSocket connections are established

### Debug Commands

```bash
# Check API health
curl http://localhost:8000/health

# Test WebSocket connection
python test_websocket_simple.py

# Validate resume parser
cd resume_parser && npm run dev parse_resume.ts ../vatsal\ jain\ cv.pdf

# Test LinkedIn scraper
python linkdin_scrapper.py
```

---

## 🎯 Project Goals

This platform demonstrates advanced AI-powered interview automation with:

- **Comprehensive candidate assessment** through multi-modal data collection
- **Real-time lie detection** using state-of-the-art NLP techniques
- **Intelligent interview guidance** with contextual nudging
- **Scalable architecture** supporting multiple concurrent interviews
- **Modern user experience** with beautiful, responsive interfaces
- **Enterprise-grade reliability** with robust error handling and monitoring

The system showcases the future of technical interviewing where AI assists human recruiters in making more informed, objective, and efficient hiring decisions.

---

## 📄 License

This project is developed for Eightfold AI technical assessment. All rights reserved.

---

**Built with ❤️ for Eightfold AI Technical Assessment**
