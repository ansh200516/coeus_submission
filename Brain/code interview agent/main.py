"""
Main orchestration module for the Code Interview Agent system.

This module provides the main entry point and coordinates all system components
including audio management, code monitoring, AI agents, and interview flow.
"""

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
from code_monitor import CodeEditorMonitor, QuestionManager
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
from utils import find_project_root, safe_json_save, generate_timestamp_string, remove_asterisks_from_response

load_dotenv()

# ========== LOGGING SETUP ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        interview_mode: str = "friendly"
    ) -> None:
        """
        Initialize the code interview system.
        
        Args:
            candidate_name: Name of the candidate
            candidate_id: Optional candidate identifier
            interview_mode: Interview mode ("friendly" or "challenging")
        """
        self.candidate_name = candidate_name
        self.candidate_id = candidate_id
        self.interview_mode = interview_mode
        
        # Core components (initialized in setup)
        self.audio_state: Optional[AudioState] = None
        self.audio_manager: Optional[AudioManager] = None
        self.tts: Optional[InterviewTTS] = None
        self.stt: Optional[InterviewSTT] = None
        self.code_monitor: Optional[CodeEditorMonitor] = None
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

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_event.set()

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
            
            # Initialize code monitoring
            self.code_monitor = CodeEditorMonitor()
            if not self.code_monitor.setup_browser():
                logger.warning("Failed to setup browser for code monitoring")
                logger.warning("Next.js app may not be running at http://localhost:3000")
                logger.warning("Please start the Next.js app with: cd ../../coeus-frontend && npm run dev")
                
                # Ask user if they want to continue without browser monitoring
                try:
                    choice = input("\nContinue without browser monitoring? (y/N): ").strip().lower()
                    if choice != 'y':
                        logger.error("Browser setup required for interview system")
                        return False
                    else:
                        logger.info("Continuing in demo mode without browser monitoring")
                        self.code_monitor = None  # Disable code monitoring
                except KeyboardInterrupt:
                    logger.error("Setup interrupted by user")
                    return False
            
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

    async def select_and_set_question(self) -> bool:
        """
        Select an appropriate question and set it in the code editor.
        
        Returns:
            bool: True if question selection successful
        """
        try:
            # For now, select a medium difficulty question
            # In a full implementation, this would be more sophisticated
            selected_question = self.question_manager.select_question_by_difficulty("Medium")
            
            if not selected_question:
                logger.error("Failed to select a question")
                return False
            
            # Set the question in the code editor (if available)
            if self.code_monitor and not self.code_monitor.set_question(selected_question["id"]):
                logger.warning("Failed to set question in editor, continuing with manual assignment")
            
            # Store question info in interview state
            await self.interview_state.set_current_question(selected_question)
            self.current_question = selected_question
            
            logger.info(f"Selected question: {selected_question['title']} ({selected_question['difficulty']})")
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
                # Monitor code changes (if browser monitoring is available)
                current_code = ""
                if self.code_monitor:
                    current_code = self.code_monitor.get_current_code()
                current_time = datetime.datetime.now()
                
                # Check for code changes
                if current_code != last_code:
                    await self.interview_state.update_code(current_code)
                    last_activity_time = current_time
                    last_code = current_code
                    logger.debug("Code change detected")
                
                # Check for submit button clicks (every 3 seconds to avoid excessive checking)
                if self.code_monitor and (current_time - last_submit_check).total_seconds() > 3:
                    if self.code_monitor.detect_submit_click():
                        await self._handle_submit_event(current_code)
                        last_activity_time = current_time
                    last_submit_check = current_time
                
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
            
        except Exception as e:
            logger.error(f"Error during interview: {e}", exc_info=True)
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
            
            # Generate contextual response using the interviewer agent
            response = await self._generate_contextual_response(transcript, current_code)
            
            await self.tts.speak(response, add_filler=True)
            await self.audio_manager.wait_for_playback_to_finish()
            
            await self.interview_state.add_interaction("interviewer", response)
            
        except Exception as e:
            logger.error(f"Error handling candidate response: {e}")
            # Fallback to a generic but helpful response
            fallback_response = "I understand. Can you tell me more about your approach?"
            await self.tts.speak(fallback_response, add_filler=True)
            await self.audio_manager.wait_for_playback_to_finish()

    async def _generate_contextual_response(self, transcript: str, current_code: str) -> str:
        """
        Generate a contextual response based on the candidate's speech.
        
        Args:
            transcript: What the candidate said
            current_code: Current code content
            
        Returns:
            str: Appropriate interviewer response
        """
        try:
            # Build context for the response
            context_prompt = f"""
            You are conducting a coding interview. The candidate just said: "{transcript}"
            
            Current question: {self.current_question.get('title', 'Unknown')}
            Difficulty: {self.current_question.get('difficulty', 'Unknown')}
            
            Current code:
            ```python
            {current_code if current_code.strip() else "# No code written yet"}
            ```
            
            Generate an appropriate interviewer response that:
            1. Directly addresses what the candidate said
            2. Shows you're actively listening and engaged
            3. Provides helpful guidance if they're asking questions
            4. Encourages them to continue if they're explaining their approach
            5. Answers any direct questions they asked
            6. Keeps the conversation flowing naturally
            7. Is encouraging and supportive
            
            Respond as if you're having a natural conversation. Keep it under 20 seconds of speech.
            """
            
            response = self.interviewer_agent.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.interviewer_agent.system_prompt},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            return remove_asterisks_from_response(response.choices[0].message.content.strip())
            
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            # Intelligent fallback based on keywords in transcript
            transcript_lower = transcript.lower()
            
            if "submit" in transcript_lower:
                return "Yes, feel free to submit when you're ready! The submit button should run your tests."
            elif "question" in transcript_lower or "?" in transcript:
                return "Great question! What specifically would you like to know more about?"
            elif "think" in transcript_lower or "approach" in transcript_lower:
                return "That sounds like a solid approach. Walk me through your thinking."
            elif "reverse" in transcript_lower:
                return "Reversing is an interesting approach. How are you planning to implement that?"
            else:
                return "I see what you mean. Can you elaborate on that a bit more?"

    async def _handle_submit_event(self, current_code: str) -> None:
        """
        Handle when the candidate submits their solution.
        
        Args:
            current_code: Current code content when submitted
        """
        try:
            logger.info("Submit button clicked - processing test results...")
            
            # Wait for test execution to complete
            if self.code_monitor.wait_for_test_completion(timeout=30):
                # Get test results
                test_results = self.code_monitor.get_latest_test_results()
                
                if test_results:
                    # Store test results in interview state
                    await self.interview_state.add_test_results(test_results)
                    
                    # Generate interviewer feedback based on results
                    feedback = await self._generate_submit_feedback(current_code, test_results)
                    
                    # Deliver feedback
                    await self.tts.speak(feedback, add_filler=True)
                    await self.audio_manager.wait_for_playback_to_finish()
                    
                    await self.interview_state.add_interaction("interviewer", feedback)
                    
                    logger.info(f"Provided submit feedback for {test_results['score']['passed']}/{test_results['score']['total']} passed tests")
                else:
                    # Fallback if we couldn't extract results
                    fallback_feedback = "I see you've submitted your solution. Can you walk me through your approach and let me know how you think it performed?"
                    await self.tts.speak(fallback_feedback, add_filler=True)
                    await self.audio_manager.wait_for_playback_to_finish()
                    await self.interview_state.add_interaction("interviewer", fallback_feedback)
            else:
                # Test execution timed out
                timeout_feedback = "I notice the tests are taking some time to run. Can you explain your solution while we wait for the results?"
                await self.tts.speak(timeout_feedback, add_filler=True)
                await self.audio_manager.wait_for_playback_to_finish()
                await self.interview_state.add_interaction("interviewer", timeout_feedback)
                
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
            
            return remove_asterisks_from_response(response.choices[0].message.content.strip())
            
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
            
            # Get final code and generate feedback
            final_code = self.code_monitor.get_current_code() if self.code_monitor else ""
            
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
            session_data["final_code"] = self.code_monitor.get_current_code() if self.code_monitor else ""
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
                final_code = self.code_monitor.get_current_code() if self.code_monitor else ""
                
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
            
            # Close code monitor
            if self.code_monitor:
                self.code_monitor.close()
            
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
    interview_mode: str = "friendly"
) -> None:
    """
    Main entry point for the code interview system.
    
    Args:
        candidate_name: Name of the candidate
        candidate_id: Optional candidate identifier
        interview_mode: Interview mode ("friendly" or "challenging")
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
    
    system = CodeInterviewSystem(candidate_name, candidate_id, interview_mode)
    await system.conduct_interview()


if __name__ == "__main__":
    # Check for test mode or special commands
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("🧪 Running system test...")
            # Add test functionality later
            sys.exit(0)
        elif sys.argv[1] == "recover" and len(sys.argv) > 2:
            print(f"🔄 Recovering session: {sys.argv[2]}")
            # Add recovery functionality later
            sys.exit(0)
    
    # Get candidate name from command line or prompt (matching nudge.py)
    candidate_name = "Unknown Candidate"
    if len(sys.argv) > 1:
        candidate_name = " ".join(sys.argv[1:])
    else:
        try:
            candidate_name = input(
                "Enter candidate name (or press Enter for 'Unknown Candidate'): "
            ).strip()
            if not candidate_name:
                candidate_name = "Unknown Candidate"
        except KeyboardInterrupt:
            print("\nStarting with default candidate name...")
            candidate_name = "Unknown Candidate"
    
    # Default to friendly mode
    interview_mode = "friendly"
    
    try:
        asyncio.run(main(candidate_name, None, interview_mode))
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ System error: {e}")
    finally:
        print("\n✅ System shutdown complete")
