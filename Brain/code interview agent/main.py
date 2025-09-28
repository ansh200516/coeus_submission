"""
Main orchestration module for the Code Interview Agent system.

This module provides the main entry point and coordinates all system components
including audio management, code monitoring, AI agents, and interview flow.
"""

import argparse
import asyncio
import datetime
import json
import logging
import os
import signal
import sys
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras

from agents import CodeInterviewerAgent, CodeAnalysisAgent
from audio import AudioManager, InterviewSTT, InterviewTTS
from code_monitor import QuestionManager
from performance_logger import PerformanceLogger
from config import (
    CEREBRAS_MODEL,
    CEREBRAS_TEMPERATURE,
    CEREBRAS_MAX_TOKENS,
    MAX_INTERVIEW_DURATION,
    INACTIVITY_THRESHOLD,
    POLLING_INTERVAL,
    LISTENING_WINDOW,
    validate_config,
    get_config_summary
)
from shared_state import AudioState, InterviewState
from utils import find_project_root, safe_json_save, generate_timestamp_string

load_dotenv()

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for subprocess communication
PIPE_PATH: Optional[str] = None
SESSION_ID: Optional[str] = None


def notify_completion(reason: str = "completed", data: Optional[Dict[str, Any]] = None) -> None:
    """
    Notify the parent process (WebSocket server) that the agent has completed its task.
    
    This function is called when:
    - The interview is completed successfully
    - An exception occurs
    - The system is shutting down
    - The agent finishes its task for any reason
    
    Args:
        reason: Reason for completion ("completed", "error", "interrupted", "timeout")
        data: Optional additional data to send
    """
    global PIPE_PATH, SESSION_ID
    
    try:
        if not PIPE_PATH:
            logger.info(f"Agent completed: {reason} (no pipe path configured)")
            return
        
        completion_message = {
            "event_type": "agent_completed",
            "data": {
                "reason": reason,
                "session_id": SESSION_ID,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "message": f"Code interview agent finished: {reason}",
                **(data or {})
            }
        }
        
        # Write to pipe file
        with open(PIPE_PATH, 'a') as f:
            f.write(json.dumps(completion_message) + '\n')
        
        logger.info(f"Notified completion via pipe: {reason}")
        
    except Exception as e:
        logger.error(f"Failed to notify completion: {e}")


def notify_event(event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
    """
    Send an event notification to the parent process via pipe.
    
    Args:
        event_type: Type of event
        data: Optional event data
    """
    global PIPE_PATH, SESSION_ID
    
    try:
        if not PIPE_PATH:
            return
        
        event_message = {
            "event_type": event_type,
            "data": {
                "session_id": SESSION_ID,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                **(data or {})
            }
        }
        
        # Write to pipe file
        with open(PIPE_PATH, 'a') as f:
            f.write(json.dumps(event_message) + '\n')
        
        logger.debug(f"Sent event via pipe: {event_type}")
        
    except Exception as e:
        logger.error(f"Failed to send event: {e}")


# ========== MAIN INTERVIEW SYSTEM ==========
class CodeInterviewSystem:
    """
    Main system orchestrating the code interview process.
    
    This class coordinates all components and manages the interview flow
    from initialization through completion and cleanup.
    """

    def __init__(
        self,
        candidate_name: str = "Unknown Candidate",
        candidate_id: Optional[str] = None,
        interview_mode: str = "challenging",
        question_id: Optional[int] = None
    ) -> None:
        """
        Initialize the code interview system.
        
        Args:
            candidate_name: Name of the candidate
            candidate_id: Optional candidate identifier
            interview_mode: Interview mode (only "challenging" supported - friendly mode removed)
            question_id: Optional specific question ID to use
        """
        self.candidate_name = candidate_name
        self.candidate_id = candidate_id
        self.interview_mode = interview_mode
        self.question_id = question_id
        
        # Core components (initialized in setup)
        self.audio_state: Optional[AudioState] = None
        self.audio_manager: Optional[AudioManager] = None
        self.tts: Optional[InterviewTTS] = None
        self.stt: Optional[InterviewSTT] = None
        self.question_manager: Optional[QuestionManager] = None
        self.interview_state: Optional[InterviewState] = None
        self.interviewer_agent: Optional[CodeInterviewerAgent] = None
        self.llm_client: Optional[Cerebras] = None
        self.performance_logger: Optional[PerformanceLogger] = None
        
        # Interview control
        self.is_running = False
        self.start_time: Optional[datetime.datetime] = None
        self.current_question: Optional[Dict] = None
        
        # Graceful shutdown handling
        self._shutdown_event = asyncio.Event()
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"CodeInterviewSystem initialized for {candidate_name} in {interview_mode} mode")
        
        # Notify initialization
        notify_event("interview_initializing", {
            "candidate_name": candidate_name,
            "interview_mode": interview_mode
        })

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_event.set()
        
        # Notify interruption
        notify_completion("interrupted", {
            "signal": signum,
            "duration": (datetime.datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        })

    async def initialize(self) -> bool:
        """
        Initialize all system components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Code Interview System...")
            
            # Validate configuration
            if not validate_config():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize core state
            self.audio_state = AudioState()
            self.interview_state = InterviewState(self.candidate_name, self.candidate_id)
            
            # Initialize LLM client
            self.llm_client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
            
            # Initialize audio system
            self.audio_manager = AudioManager(self.audio_state)
            self.tts = InterviewTTS(self.audio_manager)
            self.stt = InterviewSTT(self.audio_state)
            
            # Audio system initialized - skipping test to avoid interference
            logger.info("Audio system initialized successfully")
            
            # Code monitoring disabled - no browser interaction
            logger.info("Code monitoring disabled - running without browser interaction")
            
            # Initialize question management
            self.question_manager = QuestionManager()
            
            # Initialize AI agent
            self.interviewer_agent = CodeInterviewerAgent(
                self.llm_client,
                self.interview_state,
                mode=self.interview_mode
            )
            
            # Initialize performance logger
            self.performance_logger = PerformanceLogger()
            
            logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}", exc_info=True)
            return False

    def _load_frontend_questions(self) -> List[Dict[str, Any]]:
        """
        Load questions from the frontend's questions.json file.
        
        Returns:
            List[Dict[str, Any]]: List of questions from frontend
        """
        try:
            import json
            from pathlib import Path
            
            # Get path to frontend questions.json
            current_dir = Path(__file__).parent
            frontend_questions_path = current_dir.parent.parent / "coeus-frontend" / "src" / "data" / "questions.json"
            
            if frontend_questions_path.exists():
                with open(frontend_questions_path, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                logger.info(f"Loaded {len(questions)} questions from frontend")
                return questions
            else:
                logger.warning(f"Frontend questions.json not found at: {frontend_questions_path}")
                return []
                
        except Exception as e:
            logger.error(f"Error loading frontend questions: {e}")
            return []

    async def select_and_set_question(self) -> bool:
        """
        Select an appropriate question and set it in the code editor.
        
        Returns:
            bool: True if question selection successful
        """
        try:
            selected_question = None
            
            # If specific question_id is provided, use it
            if self.question_id is not None:
                logger.info(f"Using specific question ID: {self.question_id}")
                
                # First try to get from QuestionManager
                selected_question = self.question_manager.get_question_by_id(self.question_id)
                
                # If not found in QuestionManager, try frontend questions
                if not selected_question:
                    logger.info("Question not found in QuestionManager, trying frontend questions...")
                    frontend_questions = self._load_frontend_questions()
                    for q in frontend_questions:
                        if q.get("id") == self.question_id:
                            selected_question = q
                            logger.info(f"Found question in frontend data: {q.get('title', 'Unknown')}")
                            break
                
                if not selected_question:
                    logger.warning(f"Question ID {self.question_id} not found, falling back to default selection")
            
            # If no specific question_id or question not found, use default selection
            if not selected_question:
                logger.info("Using default question selection (Easy difficulty)")
                selected_question = self.question_manager.select_question_by_difficulty("easy")
            
            if not selected_question:
                logger.error("Failed to select a question")
                return False
            
            # Question setting in editor disabled (no browser interaction)
            logger.info("Question assignment handled without browser interaction")
            
            # Store question info in interview state
            await self.interview_state.set_current_question(selected_question)
            self.current_question = selected_question
            
            logger.info(f"Selected question: {selected_question.get('title', 'Unknown')} (ID: {selected_question.get('id', 'Unknown')}, Difficulty: {selected_question.get('difficulty', 'Unknown')})")
            return True
            
        except Exception as e:
            logger.error(f"Question selection failed: {e}")
            return False

    async def conduct_interview(self) -> None:
        """
        Main interview loop.
        
        This method orchestrates the entire interview process including
        greeting, monitoring, analysis, and feedback delivery.
        """
        if not await self.initialize():
            logger.error("System initialization failed, cannot start interview")
            return
        
        if not await self.select_and_set_question():
            logger.error("Question selection failed, cannot start interview")
            return
        
        self.is_running = True
        self.start_time = datetime.datetime.now()
        self.interview_state.is_active = True
        
        # Notify interview started
        notify_event("interview_started", {
            "candidate_name": self.candidate_name,
            "question_title": self.current_question.get("title", "Unknown"),
            "difficulty": self.current_question.get("difficulty", "Unknown")
        })
        
        try:
            # Generate and deliver greeting
            greeting = await self.interviewer_agent.generate_greeting(self.current_question)
            await self.tts.speak(greeting, add_filler=False)
            await self.audio_manager.wait_for_playback_to_finish()
            
            await self.interview_state.add_interaction("interviewer", greeting)
            
            logger.info("Interview started, entering main monitoring loop...")
            
            # Main interview loop
            last_code = ""
            last_activity_time = datetime.datetime.now()
            last_submit_check = datetime.datetime.now()
            
            while (
                self.is_running and
                not self._shutdown_event.is_set() and
                (datetime.datetime.now() - self.start_time).total_seconds() < MAX_INTERVIEW_DURATION
            ):
                # Code monitoring disabled - no browser interaction
                current_code = ""
                current_time = datetime.datetime.now()
                
                # Check for inactivity
                inactivity_duration = (current_time - last_activity_time).total_seconds()
                
                if inactivity_duration > INACTIVITY_THRESHOLD:
                    await self._handle_inactivity(current_code, inactivity_duration)
                    last_activity_time = current_time
                
                # Listen for candidate speech
                if not self.audio_state.is_speaking():
                    transcript = await self.stt.listen(timeout=POLLING_INTERVAL)
                    if transcript:
                        await self.interview_state.add_interaction("candidate", transcript)
                        await self._handle_candidate_response(transcript, current_code)
                        last_activity_time = current_time
                
                # Brief pause between monitoring cycles
                await asyncio.sleep(1)
            
            # Interview completion
            await self._complete_interview()
            
            # Notify successful completion
            notify_completion("completed", {
                "duration": (datetime.datetime.now() - self.start_time).total_seconds(),
                "question_title": self.current_question.get("title", "Unknown") if self.current_question else "Unknown"
            })
            
        except Exception as e:
            logger.error(f"Error during interview: {e}", exc_info=True)
            
            # Notify error completion
            notify_completion("error", {
                "error_message": str(e),
                "duration": (datetime.datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            })
            
        finally:
            await self._cleanup()

    async def _handle_inactivity(self, current_code: str, duration: float) -> None:
        """
        Handle periods of candidate inactivity.
        
        Args:
            current_code: Current code content
            duration: Inactivity duration in seconds
        """
        try:
            # Determine nudge type based on duration and context
            if duration < 60:
                nudge_type = "initial_inactivity"
            else:
                nudge_type = "prolonged_inactivity"
            
            # Build context for nudge generation
            context = {
                "duration": int(duration),
                "problem_title": self.current_question.get("title", "Unknown"),
                "difficulty": self.current_question.get("difficulty", "Unknown"),
                "current_code": current_code if current_code.strip() else "# No code written yet",
                "interaction_count": len(self.interview_state.conversation_history)
            }
            
            # Generate and deliver nudge
            await self.interviewer_agent.generate_nudge(nudge_type, context, self.tts)
            await self.audio_manager.wait_for_playback_to_finish()
            
            logger.info(f"Delivered {nudge_type} nudge after {duration:.1f}s inactivity")
            
        except Exception as e:
            logger.error(f"Error handling inactivity: {e}")

    async def _handle_candidate_response(self, transcript: str, current_code: str) -> None:
        """
        Handle candidate verbal responses.
        
        Args:
            transcript: Transcribed speech
            current_code: Current code content
        """
        try:
            logger.info(f"Candidate response: {transcript[:50]}...")
            
            # Analyze the response and generate appropriate follow-up
            # This could involve code analysis, progress assessment, etc.
            
            # For now, provide a simple acknowledgment
            responses = [
                "I see, that's a good approach.",
                "Interesting, tell me more about that.",
                "That makes sense, keep going.",
                "Good thinking, what's your next step?"
            ]
            
            import random
            response = random.choice(responses)
            
            await self.tts.speak(response, add_filler=True)
            await self.audio_manager.wait_for_playback_to_finish()
            
            await self.interview_state.add_interaction("interviewer", response)
            
        except Exception as e:
            logger.error(f"Error handling candidate response: {e}")

    async def _handle_submit_event(self, current_code: str) -> None:
        """
        Handle when the candidate submits their solution.
        
        Args:
            current_code: Current code content when submitted
        """
        try:
            logger.info("Submit button clicked - processing test results...")
            
            # Test execution monitoring disabled (no browser interaction)
            # Provide general feedback without test results
            fallback_feedback = "I see you've submitted your solution. Can you walk me through your approach and explain how you think it performs?"
            await self.tts.speak(fallback_feedback, add_filler=True)
            await self.audio_manager.wait_for_playback_to_finish()
            await self.interview_state.add_interaction("interviewer", fallback_feedback)
            
            logger.info("Provided general submit feedback (browser interaction disabled)")
                
        except Exception as e:
            logger.error(f"Error handling submit event: {e}")
            # Fallback response
            fallback = "I see you've submitted your solution. Tell me about your approach."
            await self.tts.speak(fallback, add_filler=True)
            await self.audio_manager.wait_for_playback_to_finish()

    async def _generate_submit_feedback(self, code: str, test_results: Dict[str, Any]) -> str:
        """
        Generate interviewer feedback based on submit results.
        
        Args:
            code: The submitted code
            test_results: Test execution results
            
        Returns:
            str: Feedback message
        """
        try:
            score = test_results.get('score', {})
            passed = score.get('passed', 0)
            total = score.get('total', 0)
            overall_status = test_results.get('overall_status', 'unknown')
            
            feedback_prompt = f"""
            Generate interviewer feedback for a coding interview submission with these results:
            
            SUBMISSION DETAILS:
            - Question: {self.current_question.get('title', 'Unknown')}
            - Test Results: {passed}/{total} tests passed
            - Overall Status: {overall_status}
            - Code Length: {len(code)} characters
            
            SUBMITTED CODE:
            ```python
            {code if code.strip() else "# No code submitted"}
            ```
            
            TEST RESULTS SUMMARY:
            {test_results.get('raw_output', 'No detailed output available')}
            
            Generate feedback that:
            1. Acknowledges the submission and test results
            2. If tests passed: Congratulate and ask about approach/optimizations
            3. If tests failed: Encourage and guide toward identifying issues
            4. Ask follow-up questions about their solution
            5. Keep it encouraging but thorough
            6. Limit to 30 seconds of speech
            
            Focus on their implementation, not the boilerplate code.
            """
            
            response = self.interviewer_agent.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.interviewer_agent.system_prompt},
                    {"role": "user", "content": feedback_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating submit feedback: {e}")
            # Fallback feedback based on results
            if test_results.get('score', {}).get('passed', 0) == test_results.get('score', {}).get('total', 1):
                return "Excellent! All tests passed. Can you walk me through your solution and discuss any optimizations you considered?"
            else:
                passed = test_results.get('score', {}).get('passed', 0)
                total = test_results.get('score', {}).get('total', 1)
                return f"I see {passed} out of {total} tests passed. Let's discuss what might be causing the issues. Can you trace through your logic with one of the failing test cases?"

    async def _complete_interview(self) -> None:
        """Complete the interview with final feedback and wrap-up."""
        try:
            logger.info("Completing interview...")
            
            # Get final code (browser interaction disabled)
            final_code = ""
            
            final_feedback = await self.interviewer_agent.generate_final_feedback(
                self.interview_state.conversation_history,
                final_code,
                self.current_question
            )
            
            # Deliver final feedback
            await self.tts.speak(final_feedback, add_filler=False)
            await self.audio_manager.wait_for_playback_to_finish()
            
            await self.interview_state.add_interaction("interviewer", final_feedback)
            
            # Save interview session
            await self._save_interview_session()
            
            logger.info("Interview completed successfully")
            
        except Exception as e:
            logger.error(f"Error completing interview: {e}")

    async def _save_interview_session(self) -> None:
        """Save the complete interview session to file."""
        try:
            # Generate session data
            session_data = await self.interview_state.to_dict()
            session_data["final_code"] = ""  # Browser interaction disabled
            session_data["question_info"] = self.current_question
            session_data["system_config"] = get_config_summary()
            
            # Generate filename for basic session data
            timestamp = generate_timestamp_string()
            project_root = find_project_root()
            
            if project_root:
                filename = os.path.join(
                    project_root,
                    "Brain", "code interview agent", "interviews", "sessions",
                    f"interview_{self.interview_state.session_id}_{timestamp}.json"
                )
                
                if safe_json_save(session_data, filename):
                    logger.info(f"Interview session saved to {filename}")
                else:
                    logger.error("Failed to save interview session")
            
            # Save comprehensive performance log
            if self.performance_logger:
                final_code = ""  # Browser interaction disabled
                
                # Get the latest test results if available
                latest_test_results = None
                if hasattr(self.interview_state, 'test_results_history') and self.interview_state.test_results_history:
                    latest_test_results = self.interview_state.test_results_history[-1]
                
                performance_log_path = self.performance_logger.log_performance(
                    session_id=self.interview_state.session_id,
                    candidate_name=self.interview_state.candidate_name,
                    candidate_id=self.interview_state.candidate_id,
                    question_info=self.current_question or {},
                    final_code=final_code,
                    interview_data=session_data,
                    test_results=latest_test_results
                )
                
                if performance_log_path:
                    logger.info(f"Performance log saved to {performance_log_path}")
                    
                    # Generate session summary
                    summary = self.performance_logger.get_session_summary(self.interview_state.session_id)
                    if summary:
                        logger.info(f"Session summary: {summary}")
            
        except Exception as e:
            logger.error(f"Error saving interview session: {e}")

    async def _cleanup(self) -> None:
        """Clean up all system resources."""
        logger.info("Starting system cleanup...")
        
        try:
            # Stop STT
            if self.stt:
                self.stt.stop()
            
            # Close audio manager
            if self.audio_manager:
                await self.audio_manager.close()
            
            # Code monitor cleanup skipped (browser interaction disabled)
            
            # Update interview state
            if self.interview_state:
                self.interview_state.is_active = False
                self.interview_state.interview_ended = True
            
            self.is_running = False
            
            logger.info("System cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# ========== MAIN ENTRY POINT ==========
async def main(
    candidate_name: str = "Test Candidate",
    candidate_id: Optional[str] = None,
    interview_mode: str = "challenging",
    question_id: Optional[int] = None
) -> None:
    """
    Main entry point for the code interview system.
    
    Args:
        candidate_name: Name of the candidate
        candidate_id: Optional candidate identifier
        interview_mode: Interview mode (only "challenging" supported - friendly mode removed)
        question_id: Optional specific question ID to use
    """
    print(f"""
    🎯 AI Code Interview System
    ================================
    
    Configuration:
    - Candidate: {candidate_name}
    - Mode: {interview_mode}
    - Inactivity Threshold: {INACTIVITY_THRESHOLD}s
    - Max Duration: {MAX_INTERVIEW_DURATION}s
    - Polling Interval: {POLLING_INTERVAL}s
    
    Starting system initialization...
    """)
    
    system = CodeInterviewSystem(candidate_name, candidate_id, interview_mode, question_id)
    await system.conduct_interview()


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Code Interview Agent")
    parser.add_argument("candidate_name", nargs="?", default="Unknown Candidate", 
                       help="Name of the candidate")
    parser.add_argument("--pipe-path", type=str, help="Path to communication pipe for subprocess mode")
    parser.add_argument("--session-id", type=str, help="Session ID for WebSocket communication")
    parser.add_argument("--mode", type=str, default="challenging", 
                       choices=["challenging", "friendly"], help="Interview mode")
    parser.add_argument("--question-id", type=int, help="Specific question ID to use")
    
    args = parser.parse_args()
    
    # Set global variables for subprocess communication
    PIPE_PATH = args.pipe_path
    SESSION_ID = args.session_id
    
    # Check for test mode or special commands
    if args.candidate_name == "test":
        print("🧪 Running system test...")
        # Add test functionality later
        sys.exit(0)
    elif args.candidate_name == "recover" and args.session_id:
        print(f"🔄 Recovering session: {args.session_id}")
        # Add recovery functionality later
        sys.exit(0)
    
    # Get candidate name
    candidate_name = args.candidate_name
    interview_mode = args.mode
    
    try:
        asyncio.run(main(candidate_name, args.session_id, interview_mode, args.question_id))
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
        notify_completion("interrupted", {"reason": "KeyboardInterrupt"})
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ System error: {e}")
        notify_completion("error", {"error_message": str(e)})
    finally:
        print("\n✅ System shutdown complete")
