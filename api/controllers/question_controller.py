"""
Question controller for handling question selection API endpoints.

This module provides REST API endpoints for question selection
and management using the QuestionManager from the Brain system.
"""

import logging
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from models.question_model import (
    QuestionSelectionRequest,
    QuestionSelectionResponse,
    QuestionResponse,
    QuestionExample,
    QuestionTestCase
)
from services.question_service import question_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for question endpoints
router = APIRouter(prefix="/questions", tags=["questions"])


def convert_question_to_response(question_data: Dict[str, Any]) -> QuestionResponse:
    """
    Convert question data from QuestionManager to QuestionResponse model.
    
    Args:
        question_data: Raw question data from QuestionManager
        
    Returns:
        QuestionResponse: Formatted question response
    """
    # Convert examples
    examples = []
    for example in question_data.get("examples", []):
        examples.append(QuestionExample(
            input=example.get("input", ""),
            output=example.get("output", ""),
            explanation=example.get("explanation")
        ))
    
    # Convert test cases
    test_cases = []
    for test_case in question_data.get("testCases", []):
        test_cases.append(QuestionTestCase(
            input=test_case.get("input", ""),
            expectedOutput=test_case.get("expectedOutput", "")
        ))
    
    return QuestionResponse(
        id=question_data.get("id", 0),
        title=question_data.get("title", ""),
        difficulty=question_data.get("difficulty", "Easy"),
        problemType=question_data.get("problemType", ""),
        level=question_data.get("level", 1),
        description=question_data.get("description", ""),
        examples=examples,
        constraints=question_data.get("constraints", []),
        testCases=test_cases
    )


@router.post(
    "/select_question",
    response_model=QuestionSelectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Select Question by Difficulty",
    description="Select a coding question by difficulty level using the QuestionManager"
)
async def select_question(request: QuestionSelectionRequest) -> QuestionSelectionResponse:
    """
    Select a coding question by difficulty level.
    
    This endpoint uses the QuestionManager from the Brain code interview agent
    to select an appropriate question based on the specified difficulty.
    
    Args:
        request: Question selection request containing difficulty level
        
    Returns:
        QuestionSelectionResponse with selected question data
        
    Raises:
        HTTPException: If question selection fails
    """
    try:
        logger.info(f"Received question selection request: difficulty={request.difficulty}")
        
        # Use the question service to select a question
        success, message, question_data = question_service.select_question_by_difficulty(
            difficulty=request.difficulty
        )
        
        if not success:
            logger.error(f"Failed to select question: {message}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to select question: {message}"
            )
        
        if not question_data:
            logger.error("Question data is None despite success")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Question data is missing"
            )
        
        logger.info(f"Question selected successfully: {question_data.get('title', 'Unknown')}")
        
        # Convert question data to response model
        question_response = convert_question_to_response(question_data)
        
        # Return success response
        return QuestionSelectionResponse(
            message=message,
            question=question_response,
            status="success"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in select_question: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the question service is healthy and ready"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the question service.
    
    Returns:
        Dict containing health status and information
    """
    try:
        # Validate question manager availability
        is_available, message = question_service.validate_question_manager_availability()
        
        return {
            "status": "healthy" if is_available else "unhealthy",
            "message": message,
            "service": "question_service",
            "timestamp": "2025-01-27T10:30:00Z"  # This would be dynamic in real implementation
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "service": "question_service",
            "timestamp": "2025-01-27T10:30:00Z"
        }
