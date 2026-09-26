"""
Resume model/schema for MongoDB.
"""

from typing import Optional, List, Dict
from datetime import date, datetime
from pydantic import Field

from .base import BaseDBModel


class Education(BaseDBModel):
    """Education entry model."""
    
    institution: str = Field(..., min_length=1, max_length=200)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    description: Optional[str] = None


class WorkExperience(BaseDBModel):
    """Work experience entry model."""
    
    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    current: bool = False
    description: str
    skills_used: List[str] = Field(default_factory=list)


class Skill(BaseDBModel):
    """Skill entry model."""
    
    name: str = Field(..., min_length=1, max_length=50)
    category: str = Field(..., min_length=1, max_length=50)
    proficiency: int = Field(..., ge=1, le=5)  # 1-5 scale
    years_of_experience: float


class Resume(BaseDBModel):
    """Resume document model."""
    
    user_id: str  # Reference to User
    title: str = Field(..., min_length=1, max_length=100)
    summary: Optional[str] = None
    
    # Contact information
    contact_email: str
    contact_phone: Optional[str] = None
    location: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    
    # Sections
    education: List[Education] = Field(default_factory=list)
    work_experience: List[WorkExperience] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    
    # Metadata
    is_primary: bool = False
    file_url: Optional[str] = None  # If resume was uploaded as a file
    parsed_data: Optional[Dict] = None  # Parsed resume data from AI
    
    # Resume Analysis Fields
    extracted_text: Optional[str] = Field(
        None,
        description="Raw extracted text from resume document"
    )
    analysis_status: str = Field(
        default="pending",
        description="Analysis status: pending, processing, completed, failed"
    )
    structured_analysis: Optional[Dict] = Field(
        None,
        description="Structured analysis result from LLM (ResumeAnalysisResult as dict)"
    )
    analyzed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when analysis was completed"
    )
    analysis_version: str = Field(
        default="1.0",
        description="Version of analysis schema used"
    )
    analysis_error: Optional[str] = Field(
        None,
        description="Error message if analysis failed"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "title": "Software Engineer Resume",
                "summary": "Experienced software engineer specializing in backend development",
                "contact_email": "john.doe@example.com",
                "location": "New York, USA",
                "extracted_text": "John Doe...",
                "analysis_status": "completed",
                "analyzed_at": "2024-01-15T10:30:00Z",
                "analysis_version": "1.0"
            }
        }