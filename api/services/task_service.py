"""
Task service for handling interview task operations.

This module contains the business logic for executing interview tasks,
including subprocess management and task coordination.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
import uuid
from datetime import datetime


logger = logging.getLogger(__name__)


class TaskService:
    """
    Service class for managing interview tasks.
    
    This service handles the execution of interview tasks by coordinating
    with the subprocess-based interview agent system.
    """
    
    def __init__(self) -> None:
        """Initialize the task service."""
        self.base_path = Path(__file__).parent.parent.parent  # Go up to project root
        self.script_path = self.base_path / "Brain" / "code interview agent" / "test_subprocess.py"
        logger.info("TaskService initialized")
        logger.info(f"Script path: {self.script_path}")
        
    def execute_interview_task(self, name: str, duration: int, question_id: int) -> Tuple[bool, str, Optional[str]]:
        """
        Execute an interview task by running the test_subprocess.py script.
        
        This method runs the code interview agent subprocess script which handles
        the interview process (browser auto-launching is disabled in the agent).
        
        Args:
            name: The candidate name or task identifier
            duration: Duration in seconds for the task
            question_id: ID of the specific question to use
            
        Returns:
            Tuple of (success: bool, message: str, task_id: Optional[str])
        """
        try:
            # Generate unique task ID for tracking
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Starting interview task: {task_id}")
            logger.info(f"Candidate name: {name}")
            logger.info(f"Duration: {duration} seconds")
            logger.info(f"Question ID: {question_id}")
            logger.info(f"Script path: {self.script_path}")
            
            # Verify script exists
            if not self.script_path.exists():
                error_msg = f"Interview script not found at: {self.script_path}"
                logger.error(error_msg)
                return False, error_msg, None
            
            # Prepare command arguments
            cmd_args = [sys.executable, str(self.script_path), name, str(duration), str(question_id)]
            
            logger.info(f"Executing command: {' '.join(cmd_args)}")
            
            # Start the subprocess in the background (non-blocking)
            process = subprocess.Popen(
                cmd_args,
                cwd=self.script_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"Process started with PID: {process.pid}")
            logger.info(f"Task {task_id} initiated successfully")
            
            return True, f"Interview task started successfully with ID: {task_id}", task_id
            
        except FileNotFoundError as e:
            error_msg = f"Python interpreter or script not found: {e}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except PermissionError as e:
            error_msg = f"Permission denied when executing script: {e}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"Unexpected error starting interview task: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None
    
    def validate_script_availability(self) -> Tuple[bool, str]:
        """
        Validate that the interview script is available and executable.
        
        Returns:
            Tuple of (is_available: bool, message: str)
        """
        try:
            if not self.script_path.exists():
                return False, f"Script not found at: {self.script_path}"
            
            if not self.script_path.is_file():
                return False, f"Path exists but is not a file: {self.script_path}"
            
            # Check if we can read the file
            try:
                with open(self.script_path, 'r') as f:
                    f.read(100)  # Read first 100 chars to test readability
            except Exception as e:
                return False, f"Cannot read script file: {e}"
            
            return True, "Script is available and accessible"
            
        except Exception as e:
            return False, f"Error validating script: {e}"


# Create a singleton instance for dependency injection
task_service = TaskService()
