"""
AI agents for the Code Interview system.

This module contains the main AI agents responsible for conducting code interviews,
analyzing code quality, and providing intelligent feedback to candidates.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from pydantic import BaseModel, Field

from audio import InterviewTTS
from code_monitor import CodeEditorMonitor, QuestionManager
from config import CEREBRAS_MODEL, CEREBRAS_TEMPERATURE, CEREBRAS_MAX_TOKENS
from prompts import (
    SYSTEM_PROMPT,
    CODE_ANALYSIS_SYSTEM_PROMPT,
    PROGRESS_ANALYSIS_PROMPT,
    get_nudge_prompt,
    get_transition_prompt
)
from shared_state import InterviewState
from utils import sanitize_llm_json_output, strip_markdown, clean_text_for_speech

load_dotenv()
logger = logging.getLogger(__name__)


# ========== DATA MODELS ==========
class CodeAnalysis(BaseModel):
    """Data model for code analysis results."""
    
    correctness_score: float = Field(description="Code correctness score 0-1", ge=0, le=1)
    complexity_assessment: str = Field(description="Time/space complexity analysis")
    code_quality_score: float = Field(description="Code quality score 0-1", ge=0, le=1)
    approach_feedback: str = Field(description="Feedback on the approach")
    suggestions: List[str] = Field(description="Specific improvement suggestions", default=[])
    strengths: List[str] = Field(description="Code strengths identified", default=[])
    issues: List[str] = Field(description="Issues or problems found", default=[])


class InterviewerResponse(BaseModel):
    """Data model for interviewer responses."""
    
    response_type: str = Field(description="Type of response: question, nudge, feedback, transition")
    content: str = Field(description="Main response content")
    follow_up: Optional[str] = Field(description="Optional follow-up question", default=None)
    urgency: str = Field(description="Response urgency: low, medium, high", default="medium")
    estimated_duration: int = Field(description="Estimated speaking time in seconds", default=20)


class ProgressAssessment(BaseModel):
    """Data model for progress assessment."""
    
    overall_progress: str = Field(description="Overall progress: behind, on_track, ahead")
    current_stage: str = Field(description="Current problem-solving stage")
    time_management: str = Field(description="Time management assessment")
    next_steps: List[str] = Field(description="Recommended next steps", default=[])
    intervention_needed: bool = Field(description="Whether interviewer intervention is needed")
    confidence_level: float = Field(description="Candidate confidence assessment 0-1", ge=0, le=1)


# ========== CODE ANALYSIS AGENT ==========
class CodeAnalysisAgent:
    """
    Agent responsible for analyzing code quality and providing technical feedback.
    
    This agent evaluates the candidate's code for correctness, efficiency,
    style, and approach, providing structured feedback for the interviewer.
    """

    def __init__(self, llm_client: Cerebras) -> None:
        """
        Initialize the code analysis agent.
        
        Args:
            llm_client: Cerebras client for LLM operations
        """
        self.llm = llm_client
        logger.info("CodeAnalysisAgent initialized")

    async def analyze_code(
        self,
        code: str,
        question_info: Dict[str, Any],
        test_results: Optional[Dict[str, Any]] = None
    ) -> CodeAnalysis:
        """
        Analyze code quality and correctness.
        
        Args:
            code: Source code to analyze
            question_info: Information about the current question
            test_results: Optional test execution results
            
        Returns:
            CodeAnalysis: Structured analysis results
        """
        try:
            analysis_prompt = self._build_analysis_prompt(code, question_info, test_results)
            
            response = self.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": CODE_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            # Parse the response and create CodeAnalysis object
            content = response.choices[0].message.content
            return self._parse_analysis_response(content)
            
        except Exception as e:
            logger.error(f"Error in code analysis: {e}")
            return self._create_fallback_analysis()

    def _build_analysis_prompt(
        self,
        code: str,
        question_info: Dict[str, Any],
        test_results: Optional[Dict[str, Any]]
    ) -> str:
        """Build the analysis prompt with all context."""
        prompt_parts = [
            f"QUESTION: {question_info.get('title', 'Unknown')}",
            f"DIFFICULTY: {question_info.get('difficulty', 'Unknown')}",
            f"DESCRIPTION: {question_info.get('description', 'No description')}",
            "",
            "CODE TO ANALYZE:",
            "```python",
            code if code.strip() else "# No code provided",
            "```"
        ]
        
        if test_results:
            prompt_parts.extend([
                "",
                "TEST RESULTS:",
                f"Success: {test_results.get('success', False)}",
                f"Passed: {test_results.get('passed', 0)}/{test_results.get('total', 0)}",
                f"Output: {test_results.get('output', 'No output')}"
            ])
        
        prompt_parts.extend([
            "",
            "Please provide a comprehensive analysis including:",
            "1. Correctness assessment (0-1 score)",
            "2. Time/space complexity analysis",
            "3. Code quality evaluation (0-1 score)",
            "4. Approach feedback",
            "5. Specific suggestions for improvement",
            "6. Identified strengths",
            "7. Issues or problems found"
        ])
        
        return "\n".join(prompt_parts)

    def _parse_analysis_response(self, content: str) -> CodeAnalysis:
        """Parse LLM response into CodeAnalysis object."""
        try:
            # For now, create a basic analysis from the text response
            # In a full implementation, you'd parse structured JSON
            return CodeAnalysis(
                correctness_score=0.7,  # Default values
                complexity_assessment="Analysis pending",
                code_quality_score=0.6,
                approach_feedback=content[:200] + "..." if len(content) > 200 else content,
                suggestions=["Review algorithm efficiency"],
                strengths=["Clear variable naming"],
                issues=["Potential edge case handling needed"]
            )
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._create_fallback_analysis()

    def _create_fallback_analysis(self) -> CodeAnalysis:
        """Create a fallback analysis when the main analysis fails."""
        return CodeAnalysis(
            correctness_score=0.5,
            complexity_assessment="Unable to analyze",
            code_quality_score=0.5,
            approach_feedback="Analysis unavailable due to technical error",
            suggestions=["Continue with current approach"],
            strengths=["Code structure"],
            issues=["Analysis incomplete"]
        )


# ========== CODE INTERVIEWER AGENT ==========
class CodeInterviewerAgent:
    """
    Main agent for conducting code interviews.
    
    This agent manages the interview flow, provides feedback, asks questions,
    and delivers nudges based on candidate progress and code analysis.
    """

    def __init__(
        self,
        llm_client: Cerebras,
        interview_state: InterviewState,
        mode: str = "challenging"
    ) -> None:
        """
        Initialize the code interviewer agent.
        
        Args:
            llm_client: Cerebras client for LLM operations
            interview_state: Shared interview state
            mode: Interview mode (only "challenging" supported - no more friendly mode)
        """
        self.llm = llm_client
        self.interview_state = interview_state
        self.mode = mode
        self.code_analysis_agent = CodeAnalysisAgent(llm_client)
        
        # Always use challenging system prompt - no more friendly mode
        self.system_prompt = SYSTEM_PROMPT
        
        logger.info(f"CodeInterviewerAgent initialized in {mode} mode (friendly mode removed)")

    async def generate_greeting(
        self,
        question_info: Dict[str, Any]
    ) -> str:
        """
        Generate an opening greeting for the interview.
        
        Args:
            question_info: Information about the selected question
            
        Returns:
            str: Greeting message
        """
        try:
            greeting_prompt = f"""
            Generate a welcoming greeting for a coding interview with these details:
            - Candidate: {self.interview_state.candidate_name}
            - Question: {question_info.get('title', 'Programming Challenge')}
            - Difficulty: {question_info.get('difficulty', 'Medium')}
            - Estimated time: {question_info.get('estimated_time', 20)} minutes
            
            The greeting should:
            1. Welcome the candidate warmly
            2. Introduce yourself as an AI interviewer
            3. Explain the format briefly
            4. Present the question
            5. IMPORTANT: Mention that the boilerplate/driver code is pre-written and they only need to implement the solution function
            6. Encourage questions and communication
            7. Set a positive, collaborative tone
            
            Keep it conversational and under 30 seconds of speech.
            """
            
            response = self.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": greeting_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return self._get_fallback_greeting(question_info)

    def _get_fallback_greeting(self, question_info: Dict[str, Any]) -> str:
        """Generate a fallback greeting when LLM fails."""
        return f"""Hello {self.interview_state.candidate_name}! I'm your AI interviewer for today's coding session. 
        I've selected the {question_info.get('title', 'coding challenge')} problem for you - it's a 
        {question_info.get('difficulty', 'medium')}-level question that should take about 
        {question_info.get('estimated_time', 20)} minutes. The boilerplate and driver code are already 
        provided - you just need to implement the solution function. I'll be here to help guide you through it. 
        Feel free to think out loud and ask questions. Let's get started!"""

    async def analyze_progress(
        self,
        current_code: str,
        question_info: Dict[str, Any],
        elapsed_time: float,
        test_results: Optional[Dict[str, Any]] = None
    ) -> ProgressAssessment:
        """
        Analyze candidate's current progress.
        
        Args:
            current_code: Current code content
            elapsed_time: Time elapsed in minutes
            question_info: Question information
            test_results: Optional test results
            
        Returns:
            ProgressAssessment: Progress analysis
        """
        try:
            progress = await self.interview_state.get_progress_summary()
            
            progress_prompt = PROGRESS_ANALYSIS_PROMPT.format(
                problem_title=question_info.get('title', 'Unknown'),
                difficulty=question_info.get('difficulty', 'Unknown'),
                elapsed_time=elapsed_time,
                current_code=current_code if current_code.strip() else "# No code written yet",
                code_history=f"{progress.get('code_changes', 0)} changes made",
                interaction_count=progress.get('interactions', 0),
                hints_given=progress.get('hints_given', 0)
            )
            
            response = self.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": progress_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            return self._parse_progress_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing progress: {e}")
            return self._create_fallback_progress()

    def _parse_progress_response(self, content: str) -> ProgressAssessment:
        """Parse progress analysis response."""
        # Simplified parsing - in production, use structured output
        return ProgressAssessment(
            overall_progress="on_track",
            current_stage="implementation",
            time_management="good",
            next_steps=["Continue current approach"],
            intervention_needed=False,
            confidence_level=0.7
        )

    def _create_fallback_progress(self) -> ProgressAssessment:
        """Create fallback progress assessment."""
        return ProgressAssessment(
            overall_progress="unknown",
            current_stage="analysis_pending",
            time_management="unknown",
            next_steps=["Monitor progress"],
            intervention_needed=True,
            confidence_level=0.5
        )

    async def generate_nudge(
        self,
        nudge_type: str,
        context: Dict[str, Any],
        tts: InterviewTTS
    ) -> None:
        """
        Generate and deliver a nudge to the candidate.
        
        Args:
            nudge_type: Type of nudge to generate
            context: Context information for the nudge
            tts: TTS system for audio delivery
        """
        try:
            # Get the appropriate nudge prompt
            nudge_prompt = get_nudge_prompt(nudge_type, **context)
            
            response = self.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": nudge_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            nudge_text = response.choices[0].message.content.strip()
            clean_text = clean_text_for_speech(nudge_text)
            
            # Record the interaction
            await self.interview_state.add_interaction("interviewer", nudge_text)
            await self.interview_state.increment_hints()
            
            # Deliver the nudge
            await tts.speak(clean_text, add_filler=True)
            logger.info(f"Delivered {nudge_type} nudge")
            
        except Exception as e:
            logger.error(f"Error generating nudge: {e}")
            # Fallback nudge
            fallback_text = "I notice you might need some guidance. Can you walk me through your current thinking?"
            await tts.speak(fallback_text, add_filler=True)

    async def generate_response(
        self,
        response_type: str,
        context: Dict[str, Any]
    ) -> InterviewerResponse:
        """
        Generate a general interviewer response.
        
        Args:
            response_type: Type of response needed
            context: Context for response generation
            
        Returns:
            InterviewerResponse: Structured response
        """
        try:
            # Build appropriate prompt based on response type
            prompt = self._build_response_prompt(response_type, context)
            
            response = self.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            
            return InterviewerResponse(
                response_type=response_type,
                content=content,
                follow_up=None,
                urgency="medium",
                estimated_duration=20
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return InterviewerResponse(
                response_type="fallback",
                content="I'm here to help. What would you like to discuss?",
                urgency="low",
                estimated_duration=10
            )

    def _build_response_prompt(self, response_type: str, context: Dict[str, Any]) -> str:
        """Build appropriate prompt for response generation."""
        base_prompt = f"Generate a {response_type} response for the coding interview."
        
        if "current_code" in context:
            base_prompt += f"\n\nCurrent code:\n```python\n{context['current_code']}\n```"
        
        if "question_info" in context:
            q = context["question_info"]
            base_prompt += f"\n\nQuestion: {q.get('title', 'Unknown')} ({q.get('difficulty', 'Unknown')})"
        
        return base_prompt

    async def generate_final_feedback(
        self,
        conversation_history: List[Dict[str, Any]],
        final_code: str,
        question_info: Dict[str, Any]
    ) -> str:
        """
        Generate final interview feedback.
        
        Args:
            conversation_history: Complete conversation history
            final_code: Final code submission
            question_info: Question information
            
        Returns:
            str: Final feedback message
        """
        try:
            progress_summary = await self.interview_state.get_progress_summary()
            
            feedback_prompt = f"""
            Generate final feedback for this coding interview:
            
            CANDIDATE: {self.interview_state.candidate_name}
            QUESTION: {question_info.get('title', 'Unknown')}
            DIFFICULTY: {question_info.get('difficulty', 'Unknown')}
            
            PERFORMANCE SUMMARY:
            - Time elapsed: {progress_summary.get('elapsed_time', 0) / 60:.1f} minutes
            - Hints given: {progress_summary.get('hints_given', 0)}
            - Code changes: {progress_summary.get('code_changes', 0)}
            - Test runs: {progress_summary.get('test_runs', 0)}
            - Interactions: {progress_summary.get('interactions', 0)}
            
            FINAL CODE:
            ```python
            {final_code if final_code.strip() else "# No final code submitted"}
            ```
            
            Provide constructive feedback that:
            1. Acknowledges their effort and progress
            2. Highlights what they did well
            3. Suggests areas for improvement
            4. Offers encouragement for future interviews
            5. Keeps a positive, professional tone
            
            Limit to 60 seconds of speech.
            """
            
            response = self.llm.chat.completions.create(
                model=CEREBRAS_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": feedback_prompt}
                ],
                temperature=CEREBRAS_TEMPERATURE,
                max_tokens=CEREBRAS_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating final feedback: {e}")
            return f"Thank you for your time today, {self.interview_state.candidate_name}. You showed good problem-solving skills and I appreciate your effort. Keep practicing and you'll continue to improve!"
