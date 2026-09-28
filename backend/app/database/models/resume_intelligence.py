"""
Resume Intelligence Profile model - structured candidate information extracted from resume.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, BaseModel

from .base import BaseDBModel


class ContactInfo(BaseModel):
    """Candidate contact information."""
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City/Location")


class EducationEntry(BaseModel):
    """Education entry in resume."""
    degree: Optional[str] = Field(None, description="Degree type (e.g., B.Tech, M.S., BA)")
    field_of_study: Optional[str] = Field(None, description="Major/Field of study")
    institution: Optional[str] = Field(None, description="University/College name")
    graduation_year: Optional[int] = Field(None, ge=1900, le=2100, description="Graduation year")
    cgpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="CGPA or percentage (0-4 scale)")
    percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Percentage score")


class SkillsCategory(BaseModel):
    """Categorized skills."""
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages (e.g., Python, Java)")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks (e.g., Django, React, Spring)")
    libraries: List[str] = Field(default_factory=list, description="Libraries and tools")
    databases: List[str] = Field(default_factory=list, description="Databases (e.g., PostgreSQL, MongoDB)")
    cloud_devops: List[str] = Field(default_factory=list, description="Cloud and DevOps (AWS, Docker, Kubernetes)")
    ai_ml: List[str] = Field(default_factory=list, description="AI/ML technologies (TensorFlow, PyTorch)")
    other: List[str] = Field(default_factory=list, description="Other technical skills")


class ProjectEntry(BaseModel):
    """Project entry in resume."""
    name: Optional[str] = Field(None, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="GitHub or project link if available")


class WorkExperienceEntry(BaseModel):
    """Work experience entry."""
    company: Optional[str] = Field(None, description="Company name")
    position: Optional[str] = Field(None, description="Job title/position")
    duration: Optional[str] = Field(None, description="Duration (e.g., '2 years', '2020-2022')")
    start_year: Optional[int] = Field(None, ge=1900, le=2100, description="Start year")
    end_year: Optional[int] = Field(None, ge=1900, le=2100, description="End year (None if current)")
    description: Optional[str] = Field(None, description="Job responsibilities and achievements")
    key_achievements: List[str] = Field(default_factory=list, description="Key achievements/accomplishments")


class InternshipEntry(BaseModel):
    """Internship entry."""
    company: Optional[str] = Field(None, description="Company name")
    position: Optional[str] = Field(None, description="Internship title")
    duration: Optional[str] = Field(None, description="Duration")
    start_month_year: Optional[str] = Field(None, description="Start month and year")
    end_month_year: Optional[str] = Field(None, description="End month and year")
    description: Optional[str] = Field(None, description="Internship responsibilities and learnings")
    technologies: List[str] = Field(default_factory=list, description="Technologies used during internship")


class CertificationEntry(BaseModel):
    """Certification or credential."""
    name: Optional[str] = Field(None, description="Certification name")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    issue_date: Optional[str] = Field(None, description="When certification was issued")
    expiry_date: Optional[str] = Field(None, description="Expiry date if applicable")
    link: Optional[str] = Field(None, description="Link to credential")


class AchievementEntry(BaseModel):
    """Achievement or award."""
    title: Optional[str] = Field(None, description="Achievement title")
    description: Optional[str] = Field(None, description="What was achieved")
    date: Optional[str] = Field(None, description="When it was achieved")


class CandidateProfile(BaseDBModel):
    """Complete candidate profile extracted from resume."""
    
    resume_id: str = Field(..., description="Reference to resume_documents ID")
    user_id: str = Field(..., description="Reference to User ID")
    
    # Basic Information
    candidate_name: Optional[str] = Field(None, description="Full name of candidate")
    contact: ContactInfo = Field(default_factory=ContactInfo, description="Contact information")
    
    # Education
    education: List[EducationEntry] = Field(default_factory=list, description="Education entries")
    
    # Skills
    skills: SkillsCategory = Field(default_factory=SkillsCategory, description="Categorized skills")
    
    # Projects
    projects: List[ProjectEntry] = Field(default_factory=list, description="Projects list")
    
    # Experience
    experience: List[WorkExperienceEntry] = Field(default_factory=list, description="Work experience")
    internships: List[InternshipEntry] = Field(default_factory=list, description="Internship experience")
    
    # Credentials
    certifications: List[CertificationEntry] = Field(default_factory=list, description="Certifications")
    achievements: List[AchievementEntry] = Field(default_factory=list, description="Achievements and awards")
    
    # Additional Information
    additional_information: List[str] = Field(default_factory=list, description="Other relevant information from resume")
    
    # Processing Information
    analysis_status: str = Field(
        default="pending",
        pattern="^(pending|analyzing|completed|failed)$",
        description="Status of resume intelligence analysis"
    )
    analysis_error: Optional[str] = Field(None, description="Error message if analysis failed")
    llm_model_used: Optional[str] = Field(None, description="LLM model used for analysis")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When profile was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When profile was last updated")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "resume_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "candidate_name": "John Doe",
                "contact": {
                    "email": "john@example.com",
                    "phone": "+1-234-567-8900",
                    "location": "San Francisco, CA"
                },
                "education": [
                    {
                        "degree": "B.Tech",
                        "field_of_study": "Computer Science",
                        "institution": "Stanford University",
                        "graduation_year": 2020,
                        "cgpa": 3.8
                    }
                ],
                "skills": {
                    "programming_languages": ["Python", "Java", "JavaScript"],
                    "frameworks": ["Django", "React", "Spring Boot"],
                    "databases": ["PostgreSQL", "MongoDB"],
                    "cloud_devops": ["AWS", "Docker", "Kubernetes"],
                    "ai_ml": ["TensorFlow", "PyTorch"]
                },
                "experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Software Engineer",
                        "duration": "2 years",
                        "start_year": 2021,
                        "description": "Led development of microservices..."
                    }
                ],
                "analysis_status": "completed"
            }
        }
