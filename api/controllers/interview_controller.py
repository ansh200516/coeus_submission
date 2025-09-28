"""
Interview controller for handling interview API endpoints.

This module contains the FastAPI route handlers for interview-related operations,
following the controller pattern for clean separation of concerns.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Form, UploadFile, File
from fastapi.responses import JSONResponse

from api.models.interview_model import (
    InterviewStartRequest, 
    InterviewStartResponse, 
    InterviewStatusResponse
)
from api.services.interview_service import interview_service


logger = logging.getLogger(__name__)

# Create router for interview-related endpoints
router = APIRouter(
    prefix="/interview",
    tags=["interview"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/start",
    response_model=InterviewStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Interview Process",
    description="Start the complete interview process with candidate data collection and LDA initialization"
)
async def start_interview(
    name: str = Form(..., description="Candidate's full name"),
    gender: str = Form(..., description="Candidate's gender"),
    linkedin_url: str = Form(..., description="LinkedIn profile URL"),
    resume: UploadFile = File(..., description="Resume PDF file"),
    duration: int = Form(default=1800, description="Interview duration in seconds")
) -> InterviewStartResponse:
    """
    Start the complete interview process.
    
    This endpoint:
    1. Validates the form data
    2. Saves the resume file
    3. Starts background data processing (LinkedIn scraping + resume parsing)
    4. Initializes the LDA interview system
    5. Returns immediately with a task ID for status tracking
    
    Args:
        name: Candidate's full name
        gender: Candidate's gender
        linkedin_url: LinkedIn profile URL
        resume: Uploaded resume PDF file
        duration: Interview duration in seconds (default: 1800 = 30 minutes)
        
    Returns:
        InterviewStartResponse with task ID and status
        
    Raises:
        HTTPException: If validation fails or interview cannot be started
    """
    try:
        logger.info(f"Received interview start request: name={name}, gender={gender}")
        logger.info(f"LinkedIn URL: {linkedin_url}")
        logger.info(f"Resume file: {resume.filename}, size: {resume.size}")
        logger.info(f"Duration: {duration} seconds")
        
        # Validate file type
        if not resume.filename or not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume must be a PDF file"
            )
        
        # Validate file size (max 10MB)
        if resume.size and resume.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file size must be less than 10MB"
            )
        
        # Execute the interview workflow through the service layer
        success, message, task_id = await interview_service.execute_interview_workflow(
            name=name.strip(),
            gender=gender.strip(),
            linkedin_url=linkedin_url.strip(),
            resume=resume,
            duration=duration
        )
        
        if not success:
            logger.error(f"Failed to start interview workflow: {message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start interview: {message}"
            )
        
        logger.info(f"Interview workflow started successfully: {task_id}")
        
        # Return immediate response with task ID
        return InterviewStartResponse(
            message=message,
            task_id=task_id,
            status="started",
            processing_status="data_collection"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in start_interview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/status/{task_id}",
    response_model=InterviewStatusResponse,
    summary="Get Interview Status",
    description="Get the current status of an interview task"
)
async def get_interview_status(task_id: str) -> InterviewStatusResponse:
    """
    Get the current status of an interview task.
    
    This endpoint provides real-time status updates for the interview process,
    including data processing progress and readiness for the actual interview.
    
    Args:
        task_id: The task identifier returned from the start endpoint
        
    Returns:
        InterviewStatusResponse with current status and progress
        
    Raises:
        HTTPException: If task not found or error occurred
    """
    try:
        logger.debug(f"Checking status for task: {task_id}")
        
        # Get task status from service
        task_status = interview_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Check if interview is ready
        ready_for_interview = interview_service.is_interview_ready(task_id)
        
        # Determine status and message
        processing_status = task_status.get("processing_status", "unknown")
        error = task_status.get("error")
        
        if error:
            status_msg = "failed"
            message = f"Interview failed: {error}"
        elif ready_for_interview:
            status_msg = "ready"
            message = "Interview is ready to begin"
        elif processing_status == "data_collection":
            status_msg = "processing"
            message = "Collecting and processing candidate data..."
        elif processing_status == "data_ready":
            status_msg = "processing"
            message = "Data processing complete, starting interview system..."
        elif processing_status == "interview_active":
            status_msg = "ready"
            message = "Interview system is active and ready"
        else:
            status_msg = "processing"
            message = "Processing interview request..."
        
        # Set redirect URL when ready
        redirect_url = None
        if ready_for_interview:
            redirect_url = "/sesame"  # Frontend route for the interview interface
        
        return InterviewStatusResponse(
            task_id=task_id,
            status=status_msg,
            processing_status=processing_status,
            message=message,
            ready_for_interview=ready_for_interview,
            redirect_url=redirect_url
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in get_interview_status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/stop/{task_id}",
    summary="Stop Interview",
    description="Stop an active interview task"
)
async def stop_interview(task_id: str) -> Dict[str, Any]:
    """
    Stop an active interview task.
    
    This endpoint allows stopping an interview that is currently in progress
    and cleans up associated resources.
    
    Args:
        task_id: The task identifier to stop
        
    Returns:
        Dictionary with stop confirmation
        
    Raises:
        HTTPException: If task not found or cannot be stopped
    """
    try:
        logger.info(f"Stopping interview task: {task_id}")
        
        # Get task status
        task_status = interview_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Stop LDA process if running
        lda_process = task_status.get("lda_process")
        if lda_process:
            try:
                lda_process.terminate()
                logger.info(f"LDA process terminated for task: {task_id}")
            except Exception as e:
                logger.warning(f"Error terminating LDA process: {e}")
        
        # Clean up task resources
        interview_service.cleanup_task(task_id)
        
        return {
            "message": f"Interview task {task_id} stopped successfully",
            "task_id": task_id,
            "status": "stopped"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in stop_interview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    summary="Interview Service Health Check",
    description="Check if the interview service is healthy and ready"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the interview service.
    
    Returns:
        Dictionary with health status and service information
    """
    try:
        # Check if LDA script is available
        lda_available = interview_service.lda_path.exists()
        scraper_available = interview_service.unified_scraper_path.exists()
        
        # Count active tasks
        active_task_count = len(interview_service.active_tasks)
        
        # Determine overall health
        is_healthy = lda_available and scraper_available
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": "interview_service",
            "lda_available": lda_available,
            "scraper_available": scraper_available,
            "active_tasks": active_task_count,
            "lda_path": str(interview_service.lda_path),
            "scraper_path": str(interview_service.unified_scraper_path),
            "timestamp": "2025-09-28T00:00:00Z"  # Will be updated with actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "service": "interview_service",
            "error": str(e),
            "timestamp": "2025-09-28T00:00:00Z"
        }