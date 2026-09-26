"""
Pydantic schemas for resume intelligence and analysis.
Defines the structure of extracted resume data and analysis results.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ExtractedSkill(BaseModel):
    """Represents an extracted skill with evidence from resume."""
    
    skill: str = Field(..., min_length=1, max_length=100, description="Skill name")
    category: str = Field(
        ...,
        description="Skill category (e.g., 'Programming Language', 'Framework', 'Database')"
    )
    evidence: Optional[str] = Field(
        None,
        description="Evidence/context where skill was mentioned in resume"
    )


class EducationEntry(BaseModel):
    """Represents education information extracted from resume."""
    
    institution: Optional[str] = Field(None, description="College/University name")
    degree: Optional[str] = Field(None, description="Degree type (e.g., 'B.Tech', 'Master's')")
    field_of_study: Optional[str] = Field(None, description="Field of study (e.g., 'Computer Science')")
    graduation_year: Optional[int] = Field(None, description="Year of graduation")
    cgpa_percentage: Optional[str] = Field(None, description="CGPA or percentage (e.g., '3.8', '85%')")


class CertificationEntry(BaseModel):
    """Represents a certification extracted from resume."""
    
    name: str = Field(..., description="Certification name")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    year: Optional[int] = Field(None, description="Year obtained")


class InternshipEntry(BaseModel):
    """Represents internship experience from resume."""
    
    position: str = Field(..., description="Internship position/title")
    company: Optional[str] = Field(None, description="Company name")
    duration: Optional[str] = Field(None, description="Duration (e.g., '3 months', 'June - August 2022')")
    description: Optional[str] = Field(None, description="Brief description of work")
    skills_used: List[str] = Field(default_factory=list, description="Skills used during internship")


class WorkExperienceEntry(BaseModel):
    """Represents work experience from resume."""
    
    position: str = Field(..., description="Job position/title")
    company: str = Field(..., description="Company name")
    duration: Optional[str] = Field(None, description="Duration (e.g., '2 years', '2021-2023')")
    description: Optional[str] = Field(None, description="Brief description of responsibilities")
    skills_used: List[str] = Field(default_factory=list, description="Skills used in role")


class ProjectEntry(BaseModel):
    """Represents a project from resume."""
    
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="Project link/repository")


class HackathonEntry(BaseModel):
    """Represents hackathon participation from resume."""
    
    name: str = Field(..., description="Hackathon name")
    year: Optional[int] = Field(None, description="Year of participation")
    achievement: Optional[str] = Field(None, description="Achievement/award won")


class CompetitiveProgrammingInfo(BaseModel):
    """Represents competitive programming information."""
    
    platform: str = Field(..., description="Platform (e.g., 'LeetCode', 'CodeChef', 'Codeforces')")
    handle: Optional[str] = Field(None, description="Username/handle")
    stats: Optional[str] = Field(None, description="Stats (e.g., '500+ problems solved')")


class SkillCategory(BaseModel):
    """Represents a category of skills with evidence."""
    
    category: str = Field(..., description="Skill category name")
    skills: List[ExtractedSkill] = Field(..., description="List of skills in this category")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) for category extraction"
    )


class ResumeAnalysisResult(BaseModel):
    """Complete structured analysis result of a resume."""
    
    # Personal Information
    candidate_name: Optional[str] = Field(None, description="Candidate's full name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number if present")
    location: Optional[str] = Field(None, description="Location/City")
    
    # Education
    education: List[EducationEntry] = Field(
        default_factory=list,
        description="Education history"
    )
    
    # Skills organized by category
    technical_skills: List[SkillCategory] = Field(
        default_factory=list,
        description="Technical skills grouped by category"
    )
    
    # Experience
    work_experience: List[WorkExperienceEntry] = Field(
        default_factory=list,
        description="Work experience entries"
    )
    internships: List[InternshipEntry] = Field(
        default_factory=list,
        description="Internship entries"
    )
    
    # Additional sections
    projects: List[ProjectEntry] = Field(
        default_factory=list,
        description="Projects listed in resume"
    )
    certifications: List[CertificationEntry] = Field(
        default_factory=list,
        description="Certifications"
    )
    hackathons: List[HackathonEntry] = Field(
        default_factory=list,
        description="Hackathon participations"
    )
    competitive_programming: Optional[CompetitiveProgrammingInfo] = Field(
        None,
        description="Competitive programming information if present"
    )
    
    achievements: List[str] = Field(
        default_factory=list,
        description="Notable achievements mentioned"
    )
    
    other_info: Optional[str] = Field(
        None,
        description="Any other relevant professional information"
    )
    
    # Analysis metadata
    experience_level: Optional[str] = Field(
        None,
        description="Estimated experience level (e.g., 'Entry-level', 'Mid-level', 'Senior')"
    )
    primary_domains: List[str] = Field(
        default_factory=list,
        description="Primary technical domains (e.g., 'Backend Development', 'Data Science')"
    )
    secondary_domains: List[str] = Field(
        default_factory=list,
        description="Secondary technical domains"
    )
    estimated_skill_areas: List[str] = Field(
        default_factory=list,
        description="Estimated areas of expertise"
    )
    
    # Analysis insights
    resume_strengths: List[str] = Field(
        default_factory=list,
        description="Identified resume strengths"
    )
    potential_skill_gaps: List[str] = Field(
        default_factory=list,
        description="Potential skill gaps based on experience"
    )
    important_technologies: List[str] = Field(
        default_factory=list,
        description="Most important technologies mentioned"
    )
    important_projects: List[str] = Field(
        default_factory=list,
        description="Most significant projects mentioned"
    )
    
    # Confidence and quality metrics
    overall_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence score (0-1) for the entire analysis"
    )
    analysis_version: str = Field(
        default="1.0",
        description="Version of analysis schema"
    )


class ResumeAnalysisRequest(BaseModel):
    """Request to analyze a resume."""
    
    resume_id: str = Field(..., description="ID of the resume to analyze")
    force_reanalyze: bool = Field(
        default=False,
        description="Force re-analysis even if already analyzed"
    )


class ResumeAnalysisResponse(BaseModel):
    """Response containing resume analysis result."""
    
    resume_id: str = Field(..., description="Resume ID")
    user_id: str = Field(..., description="User ID")
    analysis: ResumeAnalysisResult = Field(..., description="Analysis result")
    status: str = Field(..., description="Analysis status (completed/failed)")
    analyzed_at: datetime = Field(..., description="When analysis was performed")
    message: Optional[str] = Field(None, description="Status message or error description")


__all__ = [
    'ExtractedSkill',
    'EducationEntry',
    'CertificationEntry',
    'InternshipEntry',
    'WorkExperienceEntry',
    'ProjectEntry',
    'HackathonEntry',
    'CompetitiveProgrammingInfo',
    'SkillCategory',
    'ResumeAnalysisResult',
    'ResumeAnalysisRequest',
    'ResumeAnalysisResponse',
]
