"""
FastAPI Main Application

This is the main entry point for the FastAPI backend application.
It follows the Model-Controller-Service architecture pattern and
provides REST endpoints for the interview system.
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.controllers.task_controller import router as task_router
from api.controllers.interview_controller import router as interview_router
from api.controllers.question_controller import router as question_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/api.log') if Path('logs').exists() else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None during application runtime
    """
    # Startup
    logger.info("Starting FastAPI application...")
    logger.info(f"Project root: {project_root}")
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Interview Task API",
    description="FastAPI backend for managing interview tasks following Model-Controller-Service architecture",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Next.js dev server alternative port
        "http://127.0.0.1:3001"
    ],  # Frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(task_router)
app.include_router(interview_router)
app.include_router(question_router)


@app.get("/", summary="Root Endpoint", description="API root endpoint with basic information")
async def root() -> dict[str, str]:
    """
    Root endpoint providing basic API information.
    
    Returns:
        Dictionary with API information
    """
    return {
        "message": "Interview Task API",
        "version": "1.0.0",
        "architecture": "Model-Controller-Service",
        "docs": "/docs",
        "health": "/tasks/health"
    }


@app.get("/health", summary="Application Health", description="Overall application health check")
async def health() -> dict[str, str]:
    """
    Application health check endpoint.
    
    Returns:
        Dictionary with health status
    """
    return {
        "status": "healthy",
        "application": "Interview Task API",
        "version": "1.0.0"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception that was raised
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting server with uvicorn...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
