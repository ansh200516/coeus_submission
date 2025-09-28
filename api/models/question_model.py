"""
Pydantic models for question selection API endpoints.

This module defines the data models used for question selection
and management in the interview system.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuestionSelectionRequest(BaseModel):
    """
    Request model for question selection.
    
    Attributes:
        difficulty: Desired difficulty level ("Easy", "Medium", "Hard")
    """
    difficulty: str = Field(
        default="Easy",
        description="Difficulty level for question selection",
        pattern="^(Easy|Medium|Hard)$"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "difficulty": "Easy"
            }
        }


class QuestionExample(BaseModel):
    """
    Model for question examples.
    
    Attributes:
        input: Example input
        output: Expected output
        explanation: Explanation of the example
    """
    input: str = Field(description="Example input")
    output: str = Field(description="Expected output")
    explanation: Optional[str] = Field(default=None, description="Explanation of the example")


class QuestionTestCase(BaseModel):
    """
    Model for question test cases.
    
    Attributes:
        input: Test case input
        expectedOutput: Expected output for the test case
    """
    input: str = Field(description="Test case input")
    expectedOutput: str = Field(description="Expected output")


class QuestionResponse(BaseModel):
    """
    Response model for selected question.
    
    Attributes:
        id: Question ID
        title: Question title
        difficulty: Question difficulty level
        problemType: Type of problem (e.g., "sum", "array", etc.)
        level: Numeric level indicator
        description: Full problem description
        examples: List of examples
        constraints: List of constraints
        testCases: List of test cases
    """
    id: int = Field(description="Unique question identifier")
    title: str = Field(description="Question title")
    difficulty: str = Field(description="Difficulty level")
    problemType: str = Field(description="Type of problem")
    level: int = Field(description="Numeric level indicator")
    description: str = Field(description="Full problem description")
    examples: List[QuestionExample] = Field(description="List of examples")
    constraints: List[str] = Field(description="List of constraints")
    testCases: List[QuestionTestCase] = Field(description="List of test cases")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Two Sum",
                "difficulty": "Easy",
                "problemType": "sum",
                "level": 1,
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "examples": [
                    {
                        "input": "nums = [2,7,11,15], target = 9",
                        "output": "[0,1]",
                        "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                    }
                ],
                "constraints": [
                    "2 <= nums.length <= 10^4",
                    "-10^9 <= nums[i] <= 10^9"
                ],
                "testCases": [
                    {
                        "input": "[2,7,11,15]\n9",
                        "expectedOutput": "[0, 1]"
                    }
                ]
            }
        }


class QuestionSelectionResponse(BaseModel):
    """
    Response model for question selection endpoint.
    
    Attributes:
        message: Success message
        question: Selected question data
        status: Selection status
    """
    message: str = Field(description="Response message")
    question: QuestionResponse = Field(description="Selected question")
    status: str = Field(description="Selection status")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Question selected successfully",
                "question": {
                    "id": 1,
                    "title": "Two Sum",
                    "difficulty": "Easy",
                    "problemType": "sum",
                    "level": 1,
                    "description": "Given an array of integers nums and an integer target...",
                    "examples": [],
                    "constraints": [],
                    "testCases": []
                },
                "status": "success"
            }
        }
