"""
Evaluation model/schema for MongoDB.
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field

from .base import BaseDBModel


class EvaluationCategory(BaseDBModel):
    """Evaluation category model."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    weight: float = Field(..., ge=0, le=1)  # Weight in overall score (0-1)
    score: float = Field(..., ge=0, le=100)  # 0-100 scale
    feedback: Optional[str] = None


class Evaluation(BaseDBModel):
    """Evaluation document model for an interview session."""
    
    interview_session_id: str  # Reference to InterviewSession
    user_id: str  # Reference to User
    
    # Overall evaluation
    overall_score: float = Field(..., ge=0, le=100)  # 0-100 scale
    overall_feedback: str
    
    # Breakdown by category
    categories: List[EvaluationCategory] = Field(default_factory=list)
    
    # Strengths and weaknesses
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    
    # Detailed analysis
    technical_knowledge_score: Optional[float] = None
    problem_solving_score: Optional[float] = None
    communication_score: Optional[float] = None
    code_quality_score: Optional[float] = None
    time_management_score: Optional[float] = None
    
    # Comparison metrics
    percentile_score: Optional[float] = None  # Compared to other candidates
    industry_average_score: Optional[float] = None
    
    # Recommendations
    recommended_positions: List[str] = Field(default_factory=list)
    skill_gaps: List[str] = Field(default_factory=list)
    training_recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    is_ai_generated: bool = True
    ai_model_used: Optional[str] = None
    manual_review_completed: bool = False
    reviewed_by: Optional[str] = None  # User ID of reviewer
    reviewed_at: Optional[datetime] = None
    
    # Additional notes
    notes: Optional[str] = None
    confidence_score: Optional[float] = None  # AI confidence in evaluation
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "interview_session_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439013",
                "overall_score": 78.5,
                "overall_feedback": "Good technical knowledge but needs improvement in communication.",
                "strengths": ["Strong problem-solving skills", "Good understanding of algorithms"],
                "weaknesses": ["Could communicate solutions more clearly", "Time management"],
                "improvement_areas": ["Public speaking", "System design patterns"]
            }
        }