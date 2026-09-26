"""
CandidateAnswer model/schema for MongoDB.
"""

from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import Field

from .base import BaseDBModel


class AnswerStatus(str, Enum):
    """Answer status enum."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    TIMED_OUT = "timed_out"


class CandidateAnswer(BaseDBModel):
    """Candidate answer document model."""
    
    interview_session_id: str  # Reference to InterviewSession
    question_id: str  # Reference to InterviewQuestion
    user_id: str  # Reference to User
    
    # Answer content
    answer_text: Optional[str] = None
    code_answer: Optional[str] = None
    selected_option: Optional[str] = None
    file_attachments: List[str] = Field(default_factory=list)
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    time_spent_seconds: Optional[int] = None
    
    # Status
    status: AnswerStatus = AnswerStatus.NOT_STARTED
    is_submitted: bool = False
    
    # AI evaluation
    ai_feedback: Optional[str] = None
    ai_score: Optional[float] = None  # 0-100 scale
    confidence_score: Optional[float] = None  # AI's confidence in evaluation
    
    # Manual evaluation (if applicable)
    manual_score: Optional[float] = None
    manual_feedback: Optional[str] = None
    evaluated_by: Optional[str] = None  # User ID of evaluator
    evaluated_at: Optional[datetime] = None
    
    # Metadata
    revision_count: int = 0
    draft_answers: List[str] = Field(default_factory=list)
    
    # Analysis
    keywords_matched: List[str] = Field(default_factory=list)
    grammar_score: Optional[float] = None
    clarity_score: Optional[float] = None
    completeness_score: Optional[float] = None
    
    # For coding questions
    code_quality_score: Optional[float] = None
    test_cases_passed: Optional[int] = None
    total_test_cases: Optional[int] = None
    compilation_errors: Optional[List[str]] = None
    runtime_errors: Optional[List[str]] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "interview_session_id": "507f1f77bcf86cd799439011",
                "question_id": "507f1f77bcf86cd799439012",
                "user_id": "507f1f77bcf86cd799439013",
                "answer_text": "REST APIs are resource-based while GraphQL is query-based...",
                "status": "submitted",
                "ai_score": 85.5,
                "ai_feedback": "Good explanation of key differences. Could expand on caching advantages."
            }
        }