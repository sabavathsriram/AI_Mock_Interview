"""
InterviewSession model/schema for MongoDB.
"""

from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import Field

from .base import BaseDBModel


class InterviewStatus(str, Enum):
    """Interview status enum."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewType(str, Enum):
    """Interview type enum."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    MOCK = "mock"


class DifficultyLevel(str, Enum):
    """Difficulty level enum."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class InterviewSession(BaseDBModel):
    """Interview session document model."""
    
    user_id: str  # Reference to User
    resume_id: Optional[str] = None  # Reference to Resume (optional)
    
    # Interview details
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    interview_type: InterviewType = InterviewType.TECHNICAL
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    target_position: str = Field(..., min_length=1, max_length=100)
    target_company: Optional[str] = None
    
    # Timing
    scheduled_start_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(default=60, ge=15, le=240)  # 15 min to 4 hours
    
    # Status
    status: InterviewStatus = InterviewStatus.SCHEDULED
    is_ai_interviewer: bool = True
    ai_model_used: Optional[str] = None  # e.g., "gpt-4", "claude-3"
    
    # Settings
    question_count: int = Field(default=10, ge=5, le=50)
    enable_feedback: bool = True
    enable_recording: bool = False
    language: str = "en"
    
    # Progress tracking
    current_question_index: int = 0
    completed_questions: List[str] = Field(default_factory=list)  # List of question IDs
    
    # Results
    overall_score: Optional[float] = None  # 0-100 scale
    time_spent_seconds: Optional[int] = None
    notes: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "title": "Senior Software Engineer Technical Interview",
                "interview_type": "technical",
                "difficulty_level": "hard",
                "target_position": "Senior Software Engineer",
                "target_company": "Tech Company Inc.",
                "duration_minutes": 60,
                "question_count": 15
            }
        }