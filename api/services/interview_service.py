"""
Interview service for handling interview operations.

This module contains the business logic for processing interview form data,
coordinating with the LDA system, and managing the interview lifecycle.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from fastapi import UploadFile

from api.models.interview_model import DataProcessingStatus


logger = logging.getLogger(__name__)


class InterviewService:
    """
    Service class for managing interview operations.
    
    This service handles the processing of interview form data,
    coordinates with the unified scraper and LDA system, and
    manages the interview lifecycle.
    """
    
    def __init__(self) -> None:
        """Initialize the interview service."""
        self.base_path = Path(__file__).parent.parent.parent  # Go up to project root
        self.lda_path = self.base_path / "Brain" / "lda" / "main.py"
        self.unified_scraper_path = self.base_path / "Brain" / "lda" / "unified_scraper.py"
        self.active_tasks: Dict[str, Dict] = {}  # Track active interview tasks
        logger.info("InterviewService initialized")
        logger.info(f"LDA path: {self.lda_path}")
        logger.info(f"Unified scraper path: {self.unified_scraper_path}")
    
    async def save_resume_file(self, resume: UploadFile) -> Optional[str]:
        """
        Save uploaded resume file to temporary location.
        
        Args:
            resume: Uploaded resume file
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            # Create temp directory if it doesn't exist
            temp_dir = self.base_path / "temp_uploads"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resume_{timestamp}_{uuid.uuid4().hex[:8]}.pdf"
            file_path = temp_dir / filename
            
            # Save file
            content = await resume.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Resume saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save resume file: {e}")
            return None
    
    async def process_candidate_data(
        self, 
        name: str, 
        gender: str, 
        linkedin_url: str, 
        resume_path: str,
        task_id: str
    ) -> Tuple[bool, str, DataProcessingStatus]:
        """
        Process candidate data using the unified scraper.
        
        Args:
            name: Candidate name
            gender: Candidate gender
            linkedin_url: LinkedIn profile URL
            resume_path: Path to resume file
            task_id: Task identifier for tracking
            
        Returns:
            Tuple of (success: bool, message: str, status: DataProcessingStatus)
        """
        try:
            logger.info(f"Processing candidate data for task: {task_id}")
            
            # Initialize processing status
            status = DataProcessingStatus()
            
            # Update task status
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["processing_status"] = "data_collection"
            
            # Verify unified scraper exists
            if not self.unified_scraper_path.exists():
                error_msg = f"Unified scraper not found at: {self.unified_scraper_path}"
                logger.error(error_msg)
                status.error_message = error_msg
                return False, error_msg, status
            
            # Prepare command arguments
            cmd_args = [sys.executable, str(self.unified_scraper_path)]
            if linkedin_url:
                cmd_args.extend(["--linkedin-url", linkedin_url])
            if resume_path:
                cmd_args.extend(["--resume-pdf", resume_path])
            
            logger.info(f"Running unified scraper: {' '.join(cmd_args)}")
            
            # Run the unified scraper
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=self.unified_scraper_path.parent,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)  # 10 minute timeout
            
            if process.returncode == 0:
                logger.info("✅ Unified scraper completed successfully")
                status.linkedin_scraped = True
                status.resume_parsed = True
                status.data_combined = True
                
                # Find the latest combined data file
                lda_logs_dir = self.base_path / "Brain" / "lda" / "lda_logs"
                if lda_logs_dir.exists():
                    combined_files = [
                        f for f in lda_logs_dir.iterdir()
                        if f.name.startswith("combined_candidate_data_") and f.name.endswith(".json")
                    ]
                    if combined_files:
                        latest_file = max(combined_files, key=lambda f: f.stat().st_mtime)
                        logger.info(f"📄 Found combined data file: {latest_file.name}")
                        
                        # Update task with data file path
                        if task_id in self.active_tasks:
                            self.active_tasks[task_id]["data_file"] = str(latest_file)
                            self.active_tasks[task_id]["processing_status"] = "data_ready"
                        
                        return True, "Data processing completed successfully", status
                
                logger.warning("⚠️ Unified scraper completed but no combined data file found")
                status.error_message = "No combined data file found after processing"
                return False, "Data processing completed but no output file found", status
            else:
                error_msg = f"Unified scraper failed: {stderr.decode() if stderr else 'Unknown error'}"
                logger.error(error_msg)
                status.error_message = error_msg
                return False, error_msg, status
                
        except asyncio.TimeoutError:
            error_msg = "Data processing timed out"
            logger.error(error_msg)
            status.error_message = error_msg
            return False, error_msg, status
        except Exception as e:
            error_msg = f"Error processing candidate data: {e}"
            logger.error(error_msg, exc_info=True)
            status.error_message = error_msg
            return False, error_msg, status
    
    async def start_lda_interview(
        self, 
        name: str, 
        gender: str, 
        linkedin_url: str, 
        resume_path: str,
        duration: int,
        task_id: str
    ) -> Tuple[bool, str]:
        """
        Start the LDA interview system.
        
        Args:
            name: Candidate name
            gender: Candidate gender
            linkedin_url: LinkedIn profile URL
            resume_path: Path to resume file
            duration: Interview duration in seconds
            task_id: Task identifier for tracking
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info(f"Starting LDA interview for task: {task_id}")
            
            # Verify LDA script exists
            if not self.lda_path.exists():
                error_msg = f"LDA script not found at: {self.lda_path}"
                logger.error(error_msg)
                return False, error_msg
            
            # Prepare command arguments for LDA
            cmd_args = [
                sys.executable, 
                str(self.lda_path),
                "--candidate-name", name,
                "--gender", gender
            ]
            
            if linkedin_url:
                cmd_args.extend(["--linkedin-url", linkedin_url])
            if resume_path:
                cmd_args.extend(["--resume-pdf", resume_path])
            
            logger.info(f"Starting LDA with command: {' '.join(cmd_args)}")
            
            # Start the LDA process in the background
            process = subprocess.Popen(
                cmd_args,
                cwd=self.lda_path.parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"LDA process started with PID: {process.pid}")
            
            # Update task status
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["lda_process"] = process
                self.active_tasks[task_id]["processing_status"] = "interview_active"
                self.active_tasks[task_id]["lda_ready"] = True
            
            return True, f"LDA interview started successfully with PID: {process.pid}"
            
        except Exception as e:
            error_msg = f"Error starting LDA interview: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    async def execute_interview_workflow(
        self,
        name: str,
        gender: str,
        linkedin_url: str,
        resume: UploadFile,
        duration: int = 1800
    ) -> Tuple[bool, str, str]:
        """
        Execute the complete interview workflow.
        
        Args:
            name: Candidate name
            gender: Candidate gender
            linkedin_url: LinkedIn profile URL
            resume: Uploaded resume file
            duration: Interview duration in seconds
            
        Returns:
            Tuple of (success: bool, message: str, task_id: str)
        """
        try:
            # Generate unique task ID
            task_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Starting interview workflow: {task_id}")
            logger.info(f"Candidate: {name}, Gender: {gender}")
            logger.info(f"LinkedIn: {linkedin_url}")
            logger.info(f"Duration: {duration} seconds")
            
            # Initialize task tracking
            self.active_tasks[task_id] = {
                "name": name,
                "gender": gender,
                "linkedin_url": linkedin_url,
                "duration": duration,
                "start_time": datetime.now(),
                "processing_status": "initializing",
                "lda_ready": False
            }
            
            # Save resume file
            resume_path = await self.save_resume_file(resume)
            if not resume_path:
                error_msg = "Failed to save resume file"
                logger.error(error_msg)
                return False, error_msg, task_id
            
            self.active_tasks[task_id]["resume_path"] = resume_path
            
            # Start background processing
            asyncio.create_task(self._background_processing(
                name, gender, linkedin_url, resume_path, duration, task_id
            ))
            
            return True, f"Interview workflow started successfully", task_id
            
        except Exception as e:
            error_msg = f"Error starting interview workflow: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, ""
    
    async def _background_processing(
        self,
        name: str,
        gender: str,
        linkedin_url: str,
        resume_path: str,
        duration: int,
        task_id: str
    ) -> None:
        """
        Background processing for interview workflow.
        
        Args:
            name: Candidate name
            gender: Candidate gender
            linkedin_url: LinkedIn profile URL
            resume_path: Path to resume file
            duration: Interview duration in seconds
            task_id: Task identifier
        """
        try:
            logger.info(f"Starting background processing for task: {task_id}")
            
            # Step 1: Process candidate data
            success, message, status = await self.process_candidate_data(
                name, gender, linkedin_url, resume_path, task_id
            )
            
            if not success:
                logger.error(f"Data processing failed for task {task_id}: {message}")
                if task_id in self.active_tasks:
                    self.active_tasks[task_id]["processing_status"] = "failed"
                    self.active_tasks[task_id]["error"] = message
                return
            
            # Step 2: Start LDA interview
            success, message = await self.start_lda_interview(
                name, gender, linkedin_url, resume_path, duration, task_id
            )
            
            if not success:
                logger.error(f"LDA start failed for task {task_id}: {message}")
                if task_id in self.active_tasks:
                    self.active_tasks[task_id]["processing_status"] = "failed"
                    self.active_tasks[task_id]["error"] = message
                return
            
            logger.info(f"Background processing completed successfully for task: {task_id}")
            
        except Exception as e:
            logger.error(f"Error in background processing for task {task_id}: {e}", exc_info=True)
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["processing_status"] = "failed"
                self.active_tasks[task_id]["error"] = str(e)
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get the status of a specific task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task status dictionary or None if not found
        """
        return self.active_tasks.get(task_id)
    
    def is_interview_ready(self, task_id: str) -> bool:
        """
        Check if interview is ready to begin.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if interview is ready, False otherwise
        """
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        return (
            task.get("processing_status") == "interview_active" and
            task.get("lda_ready", False)
        )
    
    def cleanup_task(self, task_id: str) -> None:
        """
        Clean up resources for a completed task.
        
        Args:
            task_id: Task identifier
        """
        try:
            task = self.active_tasks.get(task_id)
            if task:
                # Clean up resume file
                resume_path = task.get("resume_path")
                if resume_path and os.path.exists(resume_path):
                    os.remove(resume_path)
                    logger.info(f"Cleaned up resume file: {resume_path}")
                
                # Remove from active tasks
                del self.active_tasks[task_id]
                logger.info(f"Task {task_id} cleaned up successfully")
                
        except Exception as e:
            logger.error(f"Error cleaning up task {task_id}: {e}")


# Create a singleton instance for dependency injection
interview_service = InterviewService()
