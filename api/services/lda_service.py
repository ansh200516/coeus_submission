"""
Task service for handling interview task operations.

This module contains the business logic for interview task registration
and tracking. Browser auto-launching functionality has been disabled.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
import uuid
from datetime import datetime


logger = logging.getLogger(__name__)


class LDAService:
    """
    Service class for managing lda tasks.
    
    This service handles interview task registration and tracking.
    Browser auto-launching functionality has been disabled.
    """
    
    def __init__(self) -> None:
        """Initialize the task service."""
        self.base_path = Path(__file__).parent.parent.parent  # Go up to project root
        self.script_path = self.base_path / "Brain" / "code interview agent" / "test_subprocess.py"
        logger.info("TaskService initialized")
        logger.info(f"Script path: {self.script_path}")
        
    def execute_interview_task(self, name: str, duration: int) -> Tuple[bool, str, Optional[str]]:
        """
        Execute an interview task (browser auto-launching disabled).
        
        This method now only generates a task ID and logs the request without
        launching any subprocess or browser processes.
        
        Args:
            name: The candidate name or task identifier
            duration: Duration in seconds for the task
            
        Returns:
            Tuple of (success: bool, message: str, task_id: Optional[str])
        """
        try:
            # Generate unique task ID for tracking
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Interview task request received: {task_id}")
            logger.info(f"Candidate name: {name}")
            logger.info(f"Duration: {duration} seconds")
            logger.info("Browser auto-launching disabled - task registered without subprocess")
            
            # Task is now ready without launching external processes
            logger.info(f"Task {task_id} registered successfully (no subprocess launched)")
            
            return True, f"Interview task registered successfully with ID: {task_id} (browser auto-launch disabled)", task_id
            
        except Exception as e:
            error_msg = f"Unexpected error registering interview task: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None
    
    def validate_script_availability(self) -> Tuple[bool, str]:
        """
        Validate service availability (browser auto-launching disabled).
        
        This method now always returns True since we no longer depend on
        external scripts or subprocess launching.
        
        Returns:
            Tuple of (is_available: bool, message: str)
        """
        return True, "Task service is available (browser auto-launch disabled)"


# Create a singleton instance for dependency injection
task_service = TaskService()
