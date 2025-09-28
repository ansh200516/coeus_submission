"""
Shared state management for the Code Interview Agent system.

This module provides thread-safe state management for audio operations,
interview progress, and coordination between different system components.
"""

import asyncio
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


class AudioState:
    """
    Thread-safe audio state manager for coordinating STT and TTS operations.
    
    This class ensures that STT listening is properly coordinated with TTS playback
    to avoid audio conflicts and provide a smooth interview experience.
    """

    def __init__(self) -> None:
        """Initialize audio state with thread-safe events."""
        self._is_speaking = asyncio.Event()
        self._is_listening = asyncio.Event()
        self._lock = asyncio.Lock()

    def set_speaking(self, is_speaking: bool) -> None:
        """
        Set the speaking state.
        
        Args:
            is_speaking: True if TTS is currently active, False otherwise
        """
        if is_speaking:
            self._is_speaking.set()
        else:
            self._is_speaking.clear()

    def is_speaking(self) -> bool:
        """
        Check if TTS is currently active.
        
        Returns:
            bool: True if TTS is speaking, False otherwise
        """
        return self._is_speaking.is_set()

    def set_listening(self, is_listening: bool) -> None:
        """
        Set the listening state.
        
        Args:
            is_listening: True if STT is actively listening, False otherwise
        """
        if is_listening:
            self._is_listening.set()
        else:
            self._is_listening.clear()

    def is_listening(self) -> bool:
        """
        Check if STT is currently listening.
        
        Returns:
            bool: True if STT is listening, False otherwise
        """
        return self._is_listening.is_set()

    async def wait_for_silence(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until neither speaking nor listening is active.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if silence achieved, False if timeout
        """
        async with self._lock:
            try:
                if timeout:
                    await asyncio.wait_for(
                        self._wait_for_both_clear(), 
                        timeout=timeout
                    )
                else:
                    await self._wait_for_both_clear()
                return True
            except asyncio.TimeoutError:
                return False

    async def _wait_for_both_clear(self) -> None:
        """Wait until both speaking and listening are clear."""
        while self.is_speaking() or self.is_listening():
            await asyncio.sleep(0.1)


@dataclass
class InterviewProgress:
    """Data class for tracking interview progress and metrics."""
    
    start_time: datetime
    current_question_id: Optional[int] = None
    questions_completed: int = 0
    hints_given: int = 0
    code_changes_count: int = 0
    test_runs_count: int = 0
    successful_test_runs: int = 0
    interaction_count: int = 0
    total_speaking_time: float = 0.0
    total_coding_time: float = 0.0
    last_activity_time: Optional[datetime] = None


class InterviewState:
    """
    Centralized state management for the entire interview session.
    
    This class maintains the current state of the interview, including
    progress tracking, question management, and coordination flags.
    """

    def __init__(self, candidate_name: str = "Unknown", candidate_id: Optional[str] = None) -> None:
        """
        Initialize interview state.
        
        Args:
            candidate_name: Name of the candidate
            candidate_id: Unique identifier for the candidate
        """
        self.candidate_name = candidate_name
        self.candidate_id = candidate_id or self._generate_session_id()
        self.session_id = self._generate_session_id()
        
        # Interview state flags
        self.is_active = False
        self.is_paused = False
        self.interview_ended = False
        
        # Progress tracking
        self.progress = InterviewProgress(start_time=datetime.now())
        
        # Current state
        self.current_code = ""
        self.last_code_snapshot = ""
        self.current_question_data: Optional[Dict[str, Any]] = None
        self.conversation_history: list = []
        
        # Coordination flags
        self.waiting_for_response = False
        self.nudge_in_progress = False
        self.analysis_in_progress = False
        
        # Test results storage
        self.test_results_history: list = []
        
        # Thread safety
        self._lock = asyncio.Lock()

    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        import uuid
        return f"S{uuid.uuid4().hex[:8]}"

    async def update_code(self, new_code: str) -> bool:
        """
        Update the current code and track changes.
        
        Args:
            new_code: The new code content
            
        Returns:
            bool: True if code actually changed, False otherwise
        """
        async with self._lock:
            if new_code != self.current_code:
                self.last_code_snapshot = self.current_code
                self.current_code = new_code
                self.progress.code_changes_count += 1
                self.progress.last_activity_time = datetime.now()
                return True
            return False

    async def set_current_question(self, question_data: Dict[str, Any]) -> None:
        """
        Set the current question data.
        
        Args:
            question_data: Dictionary containing question information
        """
        async with self._lock:
            self.current_question_data = question_data
            self.progress.current_question_id = question_data.get("id")

    async def add_interaction(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an interaction to the conversation history.
        
        Args:
            role: Role of the speaker ("interviewer", "candidate", "system")
            content: Content of the interaction
            metadata: Optional metadata about the interaction
        """
        async with self._lock:
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
            self.conversation_history.append(interaction)
            self.progress.interaction_count += 1

    async def increment_hints(self) -> int:
        """
        Increment the hint counter.
        
        Returns:
            int: New hint count
        """
        async with self._lock:
            self.progress.hints_given += 1
            return self.progress.hints_given

    async def record_test_run(self, successful: bool = False) -> None:
        """
        Record a test execution.
        
        Args:
            successful: Whether the test run was successful
        """
        async with self._lock:
            self.progress.test_runs_count += 1
            if successful:
                self.progress.successful_test_runs += 1

    async def add_test_results(self, test_results: Dict[str, Any]) -> None:
        """
        Add test results to the history.
        
        Args:
            test_results: Dictionary containing test execution results
        """
        async with self._lock:
            # Add timestamp if not present
            if 'timestamp' not in test_results:
                test_results['timestamp'] = datetime.now().isoformat()
            
            self.test_results_history.append(test_results)
            
            # Update progress counters
            score = test_results.get('score', {})
            passed = score.get('passed', 0)
            total = score.get('total', 0)
            
            if total > 0:
                await self.record_test_run(successful=(passed == total))

    async def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current interview progress.
        
        Returns:
            Dict[str, Any]: Progress summary
        """
        async with self._lock:
            elapsed_time = (datetime.now() - self.progress.start_time).total_seconds()
            return {
                "session_id": self.session_id,
                "candidate_name": self.candidate_name,
                "elapsed_time": elapsed_time,
                "current_question_id": self.progress.current_question_id,
                "questions_completed": self.progress.questions_completed,
                "hints_given": self.progress.hints_given,
                "code_changes": self.progress.code_changes_count,
                "test_runs": self.progress.test_runs_count,
                "successful_tests": self.progress.successful_test_runs,
                "interactions": self.progress.interaction_count,
                "is_active": self.is_active,
                "is_paused": self.is_paused
            }

    async def to_dict(self) -> Dict[str, Any]:
        """
        Convert the entire state to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Complete state dictionary
        """
        async with self._lock:
            return {
                "session_info": {
                    "session_id": self.session_id,
                    "candidate_name": self.candidate_name,
                    "candidate_id": self.candidate_id,
                    "start_time": self.progress.start_time.isoformat(),
                },
                "progress": {
                    "current_question_id": self.progress.current_question_id,
                    "questions_completed": self.progress.questions_completed,
                    "hints_given": self.progress.hints_given,
                    "code_changes_count": self.progress.code_changes_count,
                    "test_runs_count": self.progress.test_runs_count,
                    "successful_test_runs": self.progress.successful_test_runs,
                    "interaction_count": self.progress.interaction_count,
                    "last_activity_time": self.progress.last_activity_time.isoformat() if self.progress.last_activity_time else None,
                },
                "current_state": {
                    "is_active": self.is_active,
                    "is_paused": self.is_paused,
                    "interview_ended": self.interview_ended,
                    "current_code": self.current_code,
                    "current_question_data": self.current_question_data,
                    "waiting_for_response": self.waiting_for_response,
                    "nudge_in_progress": self.nudge_in_progress,
                },
                "conversation_history": self.conversation_history,
                "test_results_history": self.test_results_history
            }
