"""
Performance logging system for the Code Interview Agent.

This module provides comprehensive logging of interview performance data,
including scores, test results, timeline events, and detailed analytics.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from utils import safe_json_save, generate_timestamp_string

logger = logging.getLogger(__name__)


@dataclass
class ComponentScores:
    """Individual components of the interview score."""
    correctness: int = 0
    optimality: int = 0
    code_quality: int = 0
    understanding: int = 0
    communication: int = 0
    penalties: int = 0


@dataclass
class TestCase:
    """Individual test case result."""
    id: str
    input: str
    expected: str
    output: str
    result: str  # "pass" or "fail"
    runtime_ms: Optional[int] = None


@dataclass
class TestResults:
    """Test execution results."""
    public: List[TestCase]
    hidden: Dict[str, int]  # {"passed": int, "total": int}


@dataclass
class TimelineEvent:
    """Timeline event during the interview."""
    timestamp: str
    event: str
    text: Optional[str] = None
    level: Optional[int] = None


@dataclass
class Artifacts:
    """File artifacts from the interview."""
    final_code_path: str
    transcript_path: str


@dataclass
class Feedback:
    """Interview feedback summary."""
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str


@dataclass
class ExportLinks:
    """Export file links."""
    pdf: str


@dataclass
class InterviewPerformance:
    """Complete interview performance data."""
    session_id: str
    candidate: Dict[str, str]
    problem: Dict[str, str]
    time: Dict[str, Any]
    scores: Dict[str, Any]
    tests: Dict[str, Any]
    hints: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    artifacts: Dict[str, str]
    feedback: Dict[str, Any]
    export_links: Dict[str, str]


class PerformanceLogger:
    """
    Comprehensive performance logging system for coding interviews.
    
    This class tracks all aspects of interview performance and generates
    detailed reports for analysis and feedback.
    """

    def __init__(self, interviews_dir: str = None) -> None:
        """
        Initialize the performance logger.
        
        Args:
            interviews_dir: Directory to store interview logs
        """
        if interviews_dir is None:
            # Default to interviews directory in the project
            script_dir = os.path.dirname(os.path.abspath(__file__))
            interviews_dir = os.path.join(script_dir, "interviews")
        
        self.interviews_dir = interviews_dir
        self.artifacts_dir = os.path.join(interviews_dir, "artifacts")
        self.exports_dir = os.path.join(interviews_dir, "exports")
        
        # Ensure directories exist
        os.makedirs(self.interviews_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)
        
        logger.info(f"PerformanceLogger initialized with directory: {interviews_dir}")

    def calculate_scores(
        self,
        test_results: Dict[str, Any],
        code: str,
        question_info: Dict[str, Any],
        interview_data: Dict[str, Any]
    ) -> ComponentScores:
        """
        Calculate detailed component scores based on performance.
        
        Args:
            test_results: Test execution results
            code: Final code submission
            question_info: Question information
            interview_data: Complete interview data
            
        Returns:
            ComponentScores: Calculated component scores
        """
        try:
            scores = ComponentScores()
            
            # Correctness score (0-40 points)
            if test_results and 'score' in test_results:
                passed = test_results['score'].get('passed', 0)
                total = test_results['score'].get('total', 1)
                correctness_ratio = passed / total if total > 0 else 0
                scores.correctness = int(correctness_ratio * 40)
            
            # Code quality score (0-20 points)
            if code and code.strip():
                # Basic code quality metrics
                lines = [line.strip() for line in code.split('\n') if line.strip()]
                
                quality_score = 20
                
                # Penalize very short solutions (might be incomplete)
                if len(lines) < 3:
                    quality_score -= 5
                
                # Penalize very long solutions (might be inefficient)
                if len(lines) > 50:
                    quality_score -= 3
                
                # Check for comments (bonus)
                has_comments = any(line.startswith('#') for line in lines)
                if has_comments:
                    quality_score += 2
                
                scores.code_quality = max(0, min(20, quality_score))
            
            # Optimality score (0-20 points) - placeholder
            # This would require more sophisticated analysis
            scores.optimality = 15  # Default reasonable score
            
            # Understanding score (0-10 points)
            # Based on interaction quality and hints needed
            hints_given = interview_data.get('progress', {}).get('hints_given', 0)
            interactions = interview_data.get('progress', {}).get('interaction_count', 0)
            
            understanding_score = 10
            if hints_given > 3:
                understanding_score -= 3
            elif hints_given > 1:
                understanding_score -= 1
                
            if interactions < 3:  # Very quiet candidate
                understanding_score -= 2
                
            scores.understanding = max(0, understanding_score)
            
            # Communication score (0-15 points)
            communication_score = 10  # Base score
            if interactions > 5:  # Good communication
                communication_score += 3
            elif interactions > 10:  # Very good communication
                communication_score += 5
                
            scores.communication = min(15, communication_score)
            
            # Penalties (negative points)
            penalties = 0
            
            # Time-based penalties
            elapsed_time = interview_data.get('progress', {}).get('elapsed_time', 0)
            time_limit = question_info.get('estimated_time', 20) * 60  # Convert to seconds
            
            if elapsed_time > time_limit * 1.5:  # 50% over time
                penalties -= 5
            elif elapsed_time > time_limit * 1.2:  # 20% over time
                penalties -= 2
            
            scores.penalties = penalties
            
            logger.info(f"Calculated scores: {asdict(scores)}")
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating scores: {e}")
            return ComponentScores()

    def format_test_results(self, test_results: Dict[str, Any]) -> TestResults:
        """
        Format test results into structured format.
        
        Args:
            test_results: Raw test results from code monitor
            
        Returns:
            TestResults: Formatted test results
        """
        try:
            public_tests = []
            
            # Format individual test cases
            test_cases = test_results.get('test_cases', [])
            for i, test_case in enumerate(test_cases):
                public_tests.append(TestCase(
                    id=f"pub{i+1}",
                    input=f"Test case {test_case.get('test_case', i+1)}",
                    expected="Expected output",
                    output=test_case.get('output', ''),
                    result=test_case.get('status', 'unknown'),
                    runtime_ms=5  # Placeholder
                ))
            
            # Hidden test results (simulated)
            score = test_results.get('score', {})
            passed = score.get('passed', 0)
            total = score.get('total', 0)
            
            hidden_results = {
                "passed": max(0, passed - len(public_tests)),
                "total": max(0, total - len(public_tests))
            }
            
            return TestResults(
                public=public_tests,
                hidden=hidden_results
            )
            
        except Exception as e:
            logger.error(f"Error formatting test results: {e}")
            return TestResults(public=[], hidden={"passed": 0, "total": 0})

    def generate_timeline(self, interview_data: Dict[str, Any]) -> List[TimelineEvent]:
        """
        Generate timeline of events during the interview.
        
        Args:
            interview_data: Complete interview data
            
        Returns:
            List[TimelineEvent]: Timeline events
        """
        try:
            timeline = []
            
            # Add conversation events
            conversation = interview_data.get('conversation_history', [])
            for interaction in conversation:
                if interaction.get('role') == 'candidate':
                    timeline.append(TimelineEvent(
                        timestamp=interaction.get('timestamp', ''),
                        event="clarification",
                        text=interaction.get('content', '')[:100] + "..." if len(interaction.get('content', '')) > 100 else interaction.get('content', '')
                    ))
            
            # Add hint events
            hints_given = interview_data.get('progress', {}).get('hints_given', 0)
            if hints_given > 0:
                # Estimate hint timing (placeholder)
                for i in range(hints_given):
                    timeline.append(TimelineEvent(
                        timestamp=datetime.now().isoformat(),
                        event="hint",
                        level=1
                    ))
            
            # Sort by timestamp
            timeline.sort(key=lambda x: x.timestamp)
            return timeline
            
        except Exception as e:
            logger.error(f"Error generating timeline: {e}")
            return []

    def save_artifacts(
        self,
        session_id: str,
        final_code: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Artifacts:
        """
        Save interview artifacts to files.
        
        Args:
            session_id: Session identifier
            final_code: Final code submission
            conversation_history: Complete conversation history
            
        Returns:
            Artifacts: Paths to saved artifacts
        """
        try:
            # Save final code
            code_filename = f"{session_id}_final.py"
            code_path = os.path.join(self.artifacts_dir, code_filename)
            
            with open(code_path, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            # Save transcript
            transcript_filename = f"{session_id}_transcript.txt"
            transcript_path = os.path.join(self.artifacts_dir, transcript_filename)
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                for interaction in conversation_history:
                    timestamp = interaction.get('timestamp', '')
                    role = interaction.get('role', 'unknown')
                    content = interaction.get('content', '')
                    
                    f.write(f"[{timestamp}] {role.upper()}: {content}\n\n")
            
            return Artifacts(
                final_code_path=f"/files/{session_id}/{code_filename}",
                transcript_path=f"/files/{session_id}/{transcript_filename}"
            )
            
        except Exception as e:
            logger.error(f"Error saving artifacts: {e}")
            return Artifacts(
                final_code_path=f"/files/{session_id}/final.py",
                transcript_path=f"/files/{session_id}/transcript.txt"
            )

    def generate_feedback(
        self,
        scores: ComponentScores,
        test_results: TestResults,
        interview_data: Dict[str, Any]
    ) -> Feedback:
        """
        Generate structured feedback based on performance.
        
        Args:
            scores: Component scores
            test_results: Test results
            interview_data: Interview data
            
        Returns:
            Feedback: Structured feedback
        """
        try:
            strengths = []
            weaknesses = []
            
            # Analyze strengths
            if scores.correctness >= 30:
                strengths.append("Strong problem-solving accuracy")
            if scores.code_quality >= 15:
                strengths.append("Clean, well-structured code")
            if scores.communication >= 10:
                strengths.append("Good communication throughout")
            if scores.understanding >= 8:
                strengths.append("Demonstrated solid understanding")
            
            # Analyze weaknesses
            if scores.correctness < 20:
                weaknesses.append("Accuracy in implementation needs improvement")
            if scores.optimality < 10:
                weaknesses.append("Consider more efficient algorithmic approaches")
            if scores.code_quality < 10:
                weaknesses.append("Code organization and clarity could be enhanced")
            if scores.communication < 8:
                weaknesses.append("More verbal explanation would help demonstrate thinking")
            
            # Generate recommendation
            total_score = (scores.correctness + scores.optimality + 
                          scores.code_quality + scores.understanding + 
                          scores.communication + scores.penalties)
            
            if total_score >= 80:
                recommendation = "Excellent performance! Continue practicing advanced algorithms and system design."
            elif total_score >= 60:
                recommendation = "Good foundation. Focus on optimization techniques and edge case handling."
            else:
                recommendation = "Practice fundamental algorithms and improve problem-solving approach. Consider mock interviews."
            
            return Feedback(
                strengths=strengths,
                weaknesses=weaknesses,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return Feedback(
                strengths=["Completed the interview"],
                weaknesses=["Performance analysis incomplete"],
                recommendation="Continue practicing coding problems"
            )

    def log_performance(
        self,
        session_id: str,
        candidate_name: str,
        candidate_id: str,
        question_info: Dict[str, Any],
        final_code: str,
        interview_data: Dict[str, Any],
        test_results: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log complete interview performance data.
        
        Args:
            session_id: Session identifier
            candidate_name: Candidate name
            candidate_id: Candidate ID
            question_info: Question information
            final_code: Final code submission
            interview_data: Complete interview data
            test_results: Test execution results
            
        Returns:
            str: Path to the saved performance log
        """
        try:
            logger.info(f"Logging performance for session {session_id}")
            
            # Calculate scores
            scores = self.calculate_scores(test_results or {}, final_code, question_info, interview_data)
            
            # Format test results
            formatted_tests = self.format_test_results(test_results or {})
            
            # Generate timeline
            timeline = self.generate_timeline(interview_data)
            
            # Save artifacts
            artifacts = self.save_artifacts(session_id, final_code, interview_data.get('conversation_history', []))
            
            # Generate feedback
            feedback = self.generate_feedback(scores, formatted_tests, interview_data)
            
            # Get timing information
            progress = interview_data.get('progress', {})
            start_time = interview_data.get('session_info', {}).get('start_time', datetime.now().isoformat())
            elapsed_time = progress.get('elapsed_time', 0)
            
            # Create performance record
            performance = InterviewPerformance(
                session_id=session_id,
                candidate={
                    "name": candidate_name,
                    "user_id": candidate_id
                },
                problem={
                    "id": str(question_info.get('id', 'unknown')),
                    "title": question_info.get('title', 'Unknown Problem'),
                    "difficulty": question_info.get('difficulty', 'medium').lower(),
                    "language": "python"
                },
                time={
                    "start": start_time,
                    "end": datetime.now(timezone.utc).isoformat(),
                    "time_allowed_min": question_info.get('estimated_time', 20),
                    "time_used_min": int(elapsed_time / 60)
                },
                scores={
                    "final": sum([
                        scores.correctness, scores.optimality, scores.code_quality,
                        scores.understanding, scores.communication, scores.penalties
                    ]),
                    "components": asdict(scores)
                },
                tests={
                    "public": [asdict(test) for test in formatted_tests.public],
                    "hidden": formatted_tests.hidden
                },
                hints=[
                    {
                        "level": 1,
                        "text": "Consider updating counts as you move left pointer",
                        "timestamp": datetime.now().isoformat()
                    }
                ] * progress.get('hints_given', 0),
                timeline=[asdict(event) for event in timeline],
                artifacts=asdict(artifacts),
                feedback=asdict(feedback),
                export_links={
                    "pdf": f"/export/{session_id}/report.pdf"
                }
            )
            
            # Save performance log
            timestamp = generate_timestamp_string()
            filename = f"performance_{session_id}_{timestamp}.json"
            filepath = os.path.join(self.interviews_dir, filename)
            
            performance_dict = asdict(performance)
            
            if safe_json_save(performance_dict, filepath):
                logger.info(f"Performance log saved to {filepath}")
                return filepath
            else:
                logger.error(f"Failed to save performance log to {filepath}")
                return ""
                
        except Exception as e:
            logger.error(f"Error logging performance: {e}")
            return ""

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a specific session's performance.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[Dict[str, Any]]: Session summary or None if not found
        """
        try:
            # Find the performance log file
            for filename in os.listdir(self.interviews_dir):
                if filename.startswith(f"performance_{session_id}") and filename.endswith('.json'):
                    filepath = os.path.join(self.interviews_dir, filename)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    return {
                        "session_id": data.get('session_id'),
                        "candidate": data.get('candidate', {}).get('name'),
                        "problem": data.get('problem', {}).get('title'),
                        "final_score": data.get('scores', {}).get('final', 0),
                        "tests_passed": f"{len([t for t in data.get('tests', {}).get('public', []) if t.get('result') == 'pass'])}/{len(data.get('tests', {}).get('public', []))}",
                        "time_used": data.get('time', {}).get('time_used_min', 0),
                        "hints_given": len(data.get('hints', [])),
                        "recommendation": data.get('feedback', {}).get('recommendation', '')
                    }
                    
        except Exception as e:
            logger.error(f"Error getting session summary: {e}")
            
        return None
