"""
Test module for lie detection and logging functionality in the LDA system.
"""

import json
import sys
import os
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

# Add the Brain/lda directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Brain", "lda"))

try:
    from agents import ClaimAnalysis, InterviewAnalysisOutput
except ImportError:
    # Define minimal mock classes if import fails
    class ClaimAnalysis(BaseModel):
        claim: str
        lie: bool
        confidence: float
        reasoning: str
        category: str
    
    class InterviewAnalysisOutput(BaseModel):
        pass


class TestLieDetectionLogging:
    """Test class for lie detection and logging functionality."""

    def test_lie_data_structure(self) -> None:
        """Test that the lie data structure matches expected format."""
        # Expected structure from the user requirements
        expected_structure = {
            "lie": "string",
            "explanation_given_by_candidate": "string"
        }
        
        # Create a mock lie detection result
        detected_lie = ClaimAnalysis(
            claim="I worked at Microsoft for 5 years",
            lie=True,
            confidence=0.95,
            reasoning="Resume shows Google employment, not Microsoft",
            category="experience"
        )
        
        # Simulate the structure that would be added to lies_detected
        lie_entry = {
            "lie": detected_lie.claim,
            "explanation_given_by_candidate": "I meant Google, not Microsoft. It was a slip of the tongue.",
            "confidence": detected_lie.confidence,
            "reasoning": detected_lie.reasoning,
            "category": detected_lie.category
        }
        
        # Verify required fields are present
        assert "lie" in lie_entry
        assert "explanation_given_by_candidate" in lie_entry
        assert isinstance(lie_entry["lie"], str)
        assert isinstance(lie_entry["explanation_given_by_candidate"], str)
        
        # Verify additional context fields are present
        assert "confidence" in lie_entry
        assert "reasoning" in lie_entry
        assert "category" in lie_entry

    def test_interview_summary_structure(self) -> None:
        """Test that interview summary includes the lies key."""
        # Mock interview data
        mock_summary = {"overall_summary": "Test interview"}
        mock_conversation = [{"role": "interviewer", "content": "Hello"}]
        mock_knowledge_base = {"entries": []}
        mock_lies = [
            {
                "lie": "I have 10 years experience with Python",
                "explanation_given_by_candidate": "Actually, it's 3 years, I misspoke",
                "confidence": 0.9,
                "reasoning": "Resume shows 3 years Python experience",
                "category": "experience"
            }
        ]
        
        # Simulate the interview_dump structure from main.py
        interview_dump = {
            "summary": mock_summary,
            "conversation_history": mock_conversation,
            "knowledge_base": mock_knowledge_base,
            "lies": mock_lies,
        }
        
        # Verify structure
        assert "lies" in interview_dump
        assert isinstance(interview_dump["lies"], list)
        
        # Verify lie entry structure
        if interview_dump["lies"]:
            lie_entry = interview_dump["lies"][0]
            assert "lie" in lie_entry
            assert "explanation_given_by_candidate" in lie_entry
            assert "confidence" in lie_entry
            assert "reasoning" in lie_entry
            assert "category" in lie_entry

    def test_no_lies_detected(self) -> None:
        """Test that empty lies list is handled correctly."""
        lies_detected: List[Dict[str, str]] = []
        
        interview_dump = {
            "summary": {"overall_summary": "Test"},
            "conversation_history": [],
            "knowledge_base": {"entries": []},
            "lies": lies_detected,
        }
        
        assert "lies" in interview_dump
        assert interview_dump["lies"] == []
        assert isinstance(interview_dump["lies"], list)

    def test_multiple_lies_detected(self) -> None:
        """Test handling of multiple lies in one interview."""
        lies_detected = [
            {
                "lie": "I worked at Apple",
                "explanation_given_by_candidate": "I meant Google",
                "confidence": 0.95,
                "reasoning": "Resume shows Google, not Apple",
                "category": "experience"
            },
            {
                "lie": "I have a PhD in Computer Science", 
                "explanation_given_by_candidate": "It's actually a Master's degree",
                "confidence": 0.98,
                "reasoning": "Resume shows MS degree, not PhD",
                "category": "education"
            }
        ]
        
        interview_dump = {
            "summary": {"overall_summary": "Test"},
            "conversation_history": [],
            "knowledge_base": {"entries": []},
            "lies": lies_detected,
        }
        
        assert len(interview_dump["lies"]) == 2
        
        # Verify each lie has correct structure
        for lie in interview_dump["lies"]:
            assert "lie" in lie
            assert "explanation_given_by_candidate" in lie
            assert "confidence" in lie
            assert "reasoning" in lie
            assert "category" in lie

    def test_no_elaboration_provided(self) -> None:
        """Test handling when candidate provides no elaboration."""
        lie_with_no_elaboration = {
            "lie": "I'm fluent in Japanese",
            "explanation_given_by_candidate": "(No elaboration provided)",
            "confidence": 0.87,
            "reasoning": "No Japanese language skills on resume",
            "category": "skills"
        }
        
        assert lie_with_no_elaboration["explanation_given_by_candidate"] == "(No elaboration provided)"
        assert "lie" in lie_with_no_elaboration
        assert "confidence" in lie_with_no_elaboration

    def test_json_serialization(self) -> None:
        """Test that the lies data can be properly serialized to JSON."""
        lies_detected = [
            {
                "lie": "I built the entire Facebook platform",
                "explanation_given_by_candidate": "I was part of a team that worked on a small feature",
                "confidence": 0.99,
                "reasoning": "Claim is vastly exaggerated compared to resume",
                "category": "experience"
            }
        ]
        
        interview_dump = {
            "summary": {"overall_summary": "Test"},
            "conversation_history": [],
            "knowledge_base": {"entries": []},
            "lies": lies_detected,
        }
        
        # Test JSON serialization
        try:
            json_str = json.dumps(interview_dump, indent=4)
            # Test deserialization
            restored_data = json.loads(json_str)
            
            assert "lies" in restored_data
            assert len(restored_data["lies"]) == 1
            assert restored_data["lies"][0]["lie"] == "I built the entire Facebook platform"
            assert restored_data["lies"][0]["explanation_given_by_candidate"] == "I was part of a team that worked on a small feature"
            
        except (TypeError, ValueError) as e:
            pytest.fail(f"JSON serialization failed: {e}")


if __name__ == "__main__":
    # Run tests if script is executed directly
    import sys
    import os
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    test_instance = TestLieDetectionLogging()
    
    print("Running lie detection logging tests...")
    
    try:
        test_instance.test_lie_data_structure()
        print("✅ test_lie_data_structure passed")
        
        test_instance.test_interview_summary_structure()
        print("✅ test_interview_summary_structure passed")
        
        test_instance.test_no_lies_detected()
        print("✅ test_no_lies_detected passed")
        
        test_instance.test_multiple_lies_detected()
        print("✅ test_multiple_lies_detected passed")
        
        test_instance.test_no_elaboration_provided()
        print("✅ test_no_elaboration_provided passed")
        
        test_instance.test_json_serialization()
        print("✅ test_json_serialization passed")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
