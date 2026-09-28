"""
Job Description model - stores job requirements and responsibilities.
"""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import Field

from .base import BaseDBModel


class JobDescription(BaseDBModel):
    """Job description document model."""
    
    # Basic information
    user_id: str = Field(..., description="User who created this job description")
    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    level: Optional[str] = Field(None, description="Job level (e.g., Junior, Senior, Lead)")
    
    # Content
    description: str = Field(..., min_length=1, description="Full job description text")
    responsibilities: List[str] = Field(
        default_factory=list,
        description="List of key responsibilities"
    )
    
    # Requirements
    required_skills: List[str] = Field(
        default_factory=list,
        description="Required technical skills"
    )
    nice_to_have_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have skills"
    )
    required_experience_years: Optional[int] = Field(
        None,
        description="Minimum years of experience required"
    )
    
    # Technologies and tools
    required_technologies: List[str] = Field(
        default_factory=list,
        description="Required technologies/tools"
    )
    required_languages: List[str] = Field(
        default_factory=list,
        description="Programming languages"
    )
    required_frameworks: List[str] = Field(
        default_factory=list,
        description="Frameworks and libraries"
    )
    required_databases: List[str] = Field(
        default_factory=list,
        description="Database systems"
    )
    
    # Education and qualifications
    education_requirements: List[str] = Field(
        default_factory=list,
        description="Education requirements (e.g., Bachelor's in CS)"
    )
    certifications_required: List[str] = Field(
        default_factory=list,
        description="Required certifications"
    )
    
    # Soft skills
    soft_skills_required: List[str] = Field(
        default_factory=list,
        description="Soft skills (communication, leadership, etc.)"
    )
    
    # Job specifics
    department: Optional[str] = Field(None, description="Department name")
    location: Optional[str] = Field(None, description="Job location")
    employment_type: Optional[str] = Field(None, description="Full-time, contract, etc.")
    
    # Description metadata (for AI processing)
    is_ai_extracted: bool = Field(
        default=False,
        description="Whether fields were extracted by AI"
    )
    ai_extraction_model: Optional[str] = Field(None, description="Model used for extraction")
    
    # Source information
    source_url: Optional[str] = Field(None, description="URL where job was posted")
    source_platform: Optional[str] = Field(None, description="Platform (LinkedIn, Indeed, etc.)")
    
    # Metadata
    is_active: bool = Field(default=True, description="Is this job description still relevant?")
    usage_count: int = Field(default=0, description="How many interviews used this JD")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "title": "Senior Software Engineer",
                "company": "Tech Company Inc.",
                "level": "Senior",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "nice_to_have_skills": ["LLMs", "RAG Systems"],
                "required_experience_years": 5
            }
        }


__all__ = ['JobDescription']
