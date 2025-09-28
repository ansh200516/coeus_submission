"""
Interview model definitions for the interview system.

This module contains Pydantic models for interview-related operations,
including form data validation and response handling.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile


class InterviewStartRequest(BaseModel):
    """
    Request model for starting an interview with candidate data.
    
    Attributes:
        name: The candidate's full name
        gender: The candidate's gender
        linkedin_url: LinkedIn profile URL
        duration: Duration in seconds for the interview (default: 1800 = 30 minutes)
    """
    name: str = Field(..., description="Candidate's full name", min_length=1)
    gender: str = Field(..., description="Candidate's gender", min_length=1)
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    duration: int = Field(default=1800, description="Interview duration in seconds", gt=0, le=7200)  # Max 2 hours
    
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
    
    @validator('gender')
    def validate_gender(cls, v: str) -> str:
        """
        Validate the gender field.
        
        Args:
            v: The gender value to validate
            
        Returns:
            The validated gender
            
        Raises:
            ValueError: If gender is invalid
        """
        if not v.strip():
            raise ValueError('Gender cannot be empty or whitespace only')
        return v.strip()
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v: str) -> str:
        """
        Validate the LinkedIn URL field.
        
        Args:
            v: The LinkedIn URL to validate
            
        Returns:
            The validated LinkedIn URL
            
        Raises:
            ValueError: If LinkedIn URL is invalid
        """
        if not v.strip():
            raise ValueError('LinkedIn URL cannot be empty')
        
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        if 'linkedin.com' not in v.lower():
            raise ValueError('Must be a valid LinkedIn URL')
        
        return v
    
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


class InterviewStartResponse(BaseModel):
    """
    Response model for interview start operations.
    
    Attributes:
        message: Success message
        task_id: Task identifier for tracking
        status: Status of the operation
        processing_status: Current processing status
    """
    message: str = Field(..., description="Response message")
    task_id: str = Field(..., description="Task identifier for tracking")
    status: str = Field(default="started", description="Operation status")
    processing_status: str = Field(default="data_collection", description="Current processing phase")


class InterviewStatusResponse(BaseModel):
    """
    Response model for interview status checks.
    
    Attributes:
        task_id: Task identifier
        status: Current status of the interview
        processing_status: Detailed processing status
        message: Status message
        ready_for_interview: Whether the interview can begin
        redirect_url: URL to redirect to when ready
    """
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Current interview status")
    processing_status: str = Field(..., description="Detailed processing status")
    message: str = Field(..., description="Status message")
    ready_for_interview: bool = Field(default=False, description="Whether interview is ready to begin")
    redirect_url: Optional[str] = Field(None, description="URL to redirect to when ready")


class DataProcessingStatus(BaseModel):
    """
    Model for tracking data processing status.
    
    Attributes:
        linkedin_scraped: Whether LinkedIn data has been scraped
        resume_parsed: Whether resume has been parsed
        data_combined: Whether data has been combined
        lda_ready: Whether LDA system is ready
        error_message: Any error that occurred during processing
    """
    linkedin_scraped: bool = Field(default=False, description="LinkedIn scraping status")
    resume_parsed: bool = Field(default=False, description="Resume parsing status")
    data_combined: bool = Field(default=False, description="Data combination status")
    lda_ready: bool = Field(default=False, description="LDA system readiness")
    error_message: Optional[str] = Field(None, description="Error message if any")
