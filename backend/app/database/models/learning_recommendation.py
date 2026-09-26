"""
LearningRecommendation model/schema for MongoDB.
"""

from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from pydantic import Field

from .base import BaseDBModel


class ResourceType(str, Enum):
    """Learning resource type enum."""
    COURSE = "course"
    ARTICLE = "article"
    VIDEO = "video"
    BOOK = "book"
    TUTORIAL = "tutorial"
    PRACTICE_EXERCISE = "practice_exercise"
    PROJECT = "project"


class DifficultyLevel(str, Enum):
    """Difficulty level enum."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LearningResource(BaseDBModel):
    """Learning resource model."""
    
    title: str = Field(..., min_length=1, max_length=200)
    resource_type: ResourceType
    url: str
    description: str
    
    # Metadata
    estimated_time_hours: Optional[float] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    free_resource: bool = True
    language: str = "en"
    
    # Content details
    skills_covered: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    
    # Quality indicators
    rating: Optional[float] = None  # 0-5 scale
    review_count: Optional[int] = None
    source: Optional[str] = None  # e.g., "Coursera", "YouTube", "FreeCodeCamp"
    
    # AI metadata
    is_ai_recommended: bool = True
    relevance_score: float = Field(..., ge=0, le=1)  # 0-1 scale


class LearningPath(BaseDBModel):
    """Learning path model."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str
    target_skill: str
    total_estimated_time_hours: float
    
    resources: List[LearningResource] = Field(default_factory=list)
    order: List[int] = Field(default_factory=list)  # Order of resources
    
    # Progress tracking
    is_completed: bool = False
    current_resource_index: int = 0
    progress_percentage: float = Field(default=0, ge=0, le=100)


class LearningRecommendation(BaseDBModel):
    """Learning recommendation document model."""
    
    user_id: str  # Reference to User
    interview_session_id: Optional[str] = None  # Optional reference to InterviewSession
    evaluation_id: Optional[str] = None  # Optional reference to Evaluation
    skill_assessment_id: Optional[str] = None  # Optional reference to SkillAssessment
    
    # Recommendation details
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    priority_level: int = Field(..., ge=1, le=5)  # 1-5 scale, 5 being highest priority
    
    # Target skills
    target_skills: List[str] = Field(default_factory=list)
    skill_gaps_addressed: List[str] = Field(default_factory=list)
    
    # Learning resources
    resources: List[LearningResource] = Field(default_factory=list)
    learning_paths: List[LearningPath] = Field(default_factory=list)
    
    # Timeline
    estimated_completion_time_hours: Optional[float] = None
    recommended_start_date: Optional[datetime] = None
    recommended_completion_date: Optional[datetime] = None
    
    # AI metadata
    is_ai_generated: bool = True
    ai_model_used: Optional[str] = None
    confidence_score: float = Field(..., ge=0, le=1)  # 0-1 scale
    
    # User engagement
    is_accepted: bool = False
    is_completed: bool = False
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    progress_percentage: float = Field(default=0, ge=0, le=100)
    
    # Feedback
    user_feedback: Optional[str] = None
    effectiveness_score: Optional[int] = None  # 1-5 scale
    notes: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439013",
                "title": "Improve System Design Skills",
                "description": "Resources to improve system design knowledge for senior engineering roles",
                "priority_level": 4,
                "target_skills": ["System Design", "Architecture Patterns", "Scalability"],
                "estimated_completion_time_hours": 40,
                "confidence_score": 0.85
            }
        }