"""
Question service for handling question selection operations.

This module contains the business logic for question selection
using the QuestionManager from the Brain code interview agent.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Add the Brain code interview agent path to sys.path
brain_path = Path(__file__).parent.parent.parent / "Brain" / "code interview agent"
sys.path.insert(0, str(brain_path))

try:
    from code_monitor import QuestionManager
except ImportError as e:
    logging.error(f"Failed to import QuestionManager: {e}")
    QuestionManager = None

logger = logging.getLogger(__name__)


class QuestionService:
    """
    Service class for managing question selection.
    
    This service handles question selection using the QuestionManager
    from the Brain code interview agent system.
    """
    
    def __init__(self) -> None:
        """Initialize the question service."""
        self.question_manager: Optional[QuestionManager] = None
        
        if QuestionManager is not None:
            try:
                self.question_manager = QuestionManager()
                logger.info("QuestionService initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize QuestionManager: {e}")
                self.question_manager = None
        else:
            logger.error("QuestionManager not available - import failed")
        
    def select_question_by_difficulty(self, difficulty: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Select a question by difficulty level.
        
        Args:
            difficulty: Desired difficulty level ("Easy", "Medium", "Hard")
            
        Returns:
            Tuple of (success: bool, message: str, question: Optional[Dict[str, Any]])
        """
        try:
            if not self.question_manager:
                error_msg = "QuestionManager not available"
                logger.error(error_msg)
                return False, error_msg, None
            
            logger.info(f"Selecting question with difficulty: {difficulty}")
            
            # Use the QuestionManager to select a question
            selected_question = self.question_manager.select_question_by_difficulty(difficulty)
            
            if not selected_question:
                error_msg = f"No questions found for difficulty: {difficulty}"
                logger.warning(error_msg)
                return False, error_msg, None
            
            logger.info(f"Successfully selected question: {selected_question.get('title', 'Unknown')} (ID: {selected_question.get('id', 'Unknown')})")
            
            return True, f"Question selected successfully", selected_question
            
        except Exception as e:
            error_msg = f"Unexpected error selecting question: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None
    
    def get_question_by_id(self, question_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Get a specific question by ID.
        
        Args:
            question_id: Question ID to retrieve
            
        Returns:
            Tuple of (success: bool, message: str, question: Optional[Dict[str, Any]])
        """
        try:
            if not self.question_manager:
                error_msg = "QuestionManager not available"
                logger.error(error_msg)
                return False, error_msg, None
            
            logger.info(f"Getting question by ID: {question_id}")
            
            # Use the QuestionManager to get a specific question
            question = self.question_manager.get_question_by_id(question_id)
            
            if not question:
                error_msg = f"Question not found: {question_id}"
                logger.warning(error_msg)
                return False, error_msg, None
            
            logger.info(f"Successfully retrieved question: {question.get('title', 'Unknown')}")
            
            return True, f"Question retrieved successfully", question
            
        except Exception as e:
            error_msg = f"Unexpected error retrieving question: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None
    
    def validate_question_manager_availability(self) -> Tuple[bool, str]:
        """
        Validate that the QuestionManager is available and functional.
        
        Returns:
            Tuple of (is_available: bool, message: str)
        """
        try:
            if not self.question_manager:
                return False, "QuestionManager not initialized"
            
            # Check if questions are loaded
            if not hasattr(self.question_manager, 'questions') or not self.question_manager.questions:
                return False, "No questions loaded in QuestionManager"
            
            question_count = len(self.question_manager.questions)
            return True, f"QuestionManager is available with {question_count} questions"
            
        except Exception as e:
            return False, f"Error validating QuestionManager: {e}"


# Create a singleton instance for dependency injection
question_service = QuestionService()
