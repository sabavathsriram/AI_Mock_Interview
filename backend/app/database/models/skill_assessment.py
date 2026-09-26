"""
SkillAssessment model/schema for MongoDB.
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field

from .base import BaseDBModel


class SkillMetric(BaseDBModel):
    """Skill metric model."""
    
    skill_name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    
    # Current assessment
    current_proficiency: int = Field(..., ge=1, le=5)  # 1-5 scale
    confidence_score: float = Field(..., ge=0, le=1)  # 0-1 scale
    
    # Assessment details
    evidence: List[str] = Field(default_factory=list)  # Evidence for assessment
    last_assessed_date: datetime
    assessment_method: str  # e.g., "interview", "test", "self-assessment"
    
    # Historical data
    previous_proficiency: Optional[int] = None
    proficiency_change: Optional[int] = None  # Current - Previous
    trend: Optional[str] = None  # "improving", "declining", "stable"
    
    # Industry comparison
    industry_average: Optional[float] = None  # 1-5 scale
    percentile: Optional[float] = None  # 0-100 scale


class SkillAssessment(BaseDBModel):
    """Skill assessment document model."""
    
    user_id: str  # Reference to User
    interview_session_id: Optional[str] = None  # Optional reference to InterviewSession
    
    # Assessment overview
    assessment_title: str = Field(..., min_length=1, max_length=200)
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    assessment_type: str  # e.g., "comprehensive", "targeted", "post-interview"
    
    # Skill metrics
    skills: List[SkillMetric] = Field(default_factory=list)
    
    # Summary statistics
    average_proficiency: float = Field(..., ge=1, le=5)
    strongest_skills: List[str] = Field(default_factory=list)
    weakest_skills: List[str] = Field(default_factory=list)
    
    # Category breakdown
    categories: Dict[str, float] = Field(default_factory=dict)  # Category -> Average proficiency
    
    # AI analysis
    is_ai_assessed: bool = True
    ai_model_used: Optional[str] = None
    ai_confidence: Optional[float] = None
    
    # Recommendations
    recommended_skill_focus: List[str] = Field(default_factory=list)
    skill_gap_analysis: Optional[str] = None
    
    # Metadata
    is_comprehensive: bool = False
    next_assessment_date: Optional[datetime] = None
    notes: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439013",
                "assessment_title": "Post-Technical Interview Skill Assessment",
                "assessment_type": "post-interview",
                "average_proficiency": 3.5,
                "strongest_skills": ["Python Programming", "Algorithms"],
                "weakest_skills": ["System Design", "Database Optimization"]
            }
        }