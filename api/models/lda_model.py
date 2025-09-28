"""
Task model definitions for the interview system.

This module contains Pydantic models for task-related operations,
including the request model for starting interview tasks.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class TaskStartRequest(BaseModel):
    """
    Request model for starting an interview task.
    
    Attributes:
        name: The name of the candidate or task identifier
        duration: Duration in seconds for the task execution
    """
    name: str = Field(..., description="Name of the candidate or task identifier", min_length=1)
    duration: int = Field(..., description="Duration in seconds", gt=0, le=7200)  # Max 2 hours
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """
        Validate the name field.
        
        Args:
            v: The name value to validate
            
        Returns:
            The validated name
            
        Raises:
            ValueError: If name is invalid
        """
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()
    
    @validator('duration')
    def validate_duration(cls, v: int) -> int:
        """
        Validate the duration field.
        
        Args:
            v: The duration value to validate
            
        Returns:
            The validated duration
            
        Raises:
            ValueError: If duration is invalid
        """
        if v <= 0:
            raise ValueError('Duration must be positive')
        if v > 7200:  # 2 hours max
            raise ValueError('Duration cannot exceed 2 hours (7200 seconds)')
        return v


class TaskStartResponse(BaseModel):
    """
    Response model for task start operations.
    
    Attributes:
        message: Success message
        task_id: Optional task identifier for tracking
        status: Status of the operation
    """
    message: str = Field(..., description="Response message")
    task_id: Optional[str] = Field(None, description="Task identifier for tracking")
    status: str = Field(default="success", description="Operation status")
