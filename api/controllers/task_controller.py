"""
Task controller for handling interview task API endpoints.

This module contains the FastAPI route handlers for task-related operations,
following the controller pattern for clean separation of concerns.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from api.models.task_model import TaskStartRequest, TaskStartResponse
from api.services.task_service import task_service


logger = logging.getLogger(__name__)

# Create router for task-related endpoints
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/start",
    response_model=TaskStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Start Interview Task",
    description="Start an interview task with specified name and duration"
)
async def start_interview_task(request: TaskStartRequest) -> TaskStartResponse:
    """
    Start an interview task by executing the subprocess script.
    
    This endpoint immediately returns a 200 response after initiating
    the task, as requested. The actual task runs in the background.
    
    Args:
        request: Task start request containing name and duration
        
    Returns:
        TaskStartResponse with success message and task ID
        
    Raises:
        HTTPException: If task cannot be started
    """
    try:
        logger.info(f"Received task start request: name={request.name}, duration={request.duration}, question_id={request.question_id}")
        
        # Execute the task through the service layer
        success, message, task_id = task_service.execute_interview_task(
            name=request.name,
            duration=request.duration,
            question_id=request.question_id
        )
        
        if not success:
            logger.error(f"Failed to start task: {message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start interview task: {message}"
            )
        
        logger.info(f"Task started successfully: {task_id}")
        
        # Return 200 immediately as requested
        return TaskStartResponse(
            message=message,
            task_id=task_id,
            status="started"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in start_interview_task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the task service is healthy and ready"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the task service.
    
    Returns:
        Dictionary with health status and service information
    """
    try:
        # Validate script availability
        is_available, message = task_service.validate_script_availability()
        
        return {
            "status": "healthy" if is_available else "degraded",
            "service": "task_service",
            "script_available": is_available,
            "script_message": message,
            "timestamp": "2025-09-27T00:00:00Z"  # Will be updated with actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "service": "task_service",
            "error": str(e),
            "timestamp": "2025-09-27T00:00:00Z"
        }
