"""
Database models for AI-Powered Mock Interview System.
"""

from .base import BaseDBModel, PyObjectId
from .user import User, UserRole
from .resume import Resume, Education, WorkExperience, Skill
from .resume_document import ResumeDocument
from .resume_intelligence import (
    CandidateProfile,
    ContactInfo,
    EducationEntry,
    SkillsCategory,
    ProjectEntry,
    WorkExperienceEntry,
    InternshipEntry,
    CertificationEntry,
    AchievementEntry,
)
from .interview_session import InterviewSession, InterviewStatus, InterviewType, DifficultyLevel
from .interview_question import InterviewQuestion, QuestionType, QuestionDifficulty
from .candidate_answer import CandidateAnswer, AnswerStatus
from .evaluation import Evaluation, EvaluationCategory
from .skill_assessment import SkillAssessment, SkillMetric
from .learning_recommendation import LearningRecommendation, LearningResource, LearningPath, ResourceType

__all__ = [
    "BaseDBModel",
    "PyObjectId",
    "User",
    "UserRole",
    "Resume",
    "Education",
    "WorkExperience", 
    "Skill",
    "ResumeDocument",
    "CandidateProfile",
    "ContactInfo",
    "EducationEntry",
    "SkillsCategory",
    "ProjectEntry",
    "WorkExperienceEntry",
    "InternshipEntry",
    "CertificationEntry",
    "AchievementEntry",
    "InterviewSession",
    "InterviewStatus",
    "InterviewType",
    "DifficultyLevel",
    "InterviewQuestion",
    "QuestionType",
    "QuestionDifficulty",
    "CandidateAnswer",
    "AnswerStatus",
    "Evaluation",
    "EvaluationCategory",
    "SkillAssessment",
    "SkillMetric",
    "LearningRecommendation",
    "LearningResource",
    "LearningPath",
    "ResourceType",
]