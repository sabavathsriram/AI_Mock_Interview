"""
InterviewQuestion model/schema for MongoDB.
"""

from typing import Optional, List, Dict
from enum import Enum
from pydantic import Field

from .base import BaseDBModel


class QuestionType(str, Enum):
    """Question type enum."""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    CODE = "code"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"


class QuestionDifficulty(str, Enum):
    """Question difficulty enum."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewQuestion(BaseDBModel):
    """Interview question document model."""
    
    # Question content
    question_text: str = Field(..., min_length=1)
    question_type: QuestionType
    difficulty: QuestionDifficulty
    
    # Context and metadata
    category: str = Field(..., min_length=1, max_length=100)
    subcategory: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    language: str = "en"
    
    # For multiple choice questions
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    
    # For coding questions
    initial_code: Optional[str] = None
    test_cases: Optional[List[Dict]] = None
    programming_language: Optional[str] = None
    
    # For system design questions
    system_requirements: Optional[str] = None
    constraints: Optional[List[str]] = None
    
    # Expected answer guidelines
    expected_answer_length: Optional[int] = None  # In words or characters
    key_points: Optional[List[str]] = None
    scoring_criteria: Optional[Dict] = None
    
    # AI generation metadata
    is_ai_generated: bool = False
    ai_model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    
    # Usage statistics
    times_used: int = 0
    average_score: Optional[float] = None  # 0-100 scale
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "question_text": "Explain the difference between REST and GraphQL APIs.",
                "question_type": "long_answer",
                "difficulty": "medium",
                "category": "API Design",
                "tags": ["api", "rest", "graphql", "web"],
                "key_points": [
                    "REST is resource-oriented, GraphQL is query-oriented",
                    "REST uses multiple endpoints, GraphQL uses single endpoint",
                    "GraphQL allows clients to request specific data",
                    "REST has built-in caching advantages"
                ]
            }
        }