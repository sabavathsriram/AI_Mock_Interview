"""
Database module for AI-Powered Mock Interview System.
"""

from .mongodb import mongodb, MongoDB

# Import models
from .models.base import BaseDBModel, PyObjectId
from .models.user import User, UserRole
from .models.resume import Resume, Education, WorkExperience, Skill
from .models.interview_session import InterviewSession, InterviewStatus, InterviewType, DifficultyLevel
from .models.interview_question import InterviewQuestion, QuestionType, QuestionDifficulty
from .models.candidate_answer import CandidateAnswer, AnswerStatus
from .models.evaluation import Evaluation, EvaluationCategory
from .models.skill_assessment import SkillAssessment, SkillMetric
from .models.learning_recommendation import LearningRecommendation, LearningResource, LearningPath, ResourceType

__all__ = [
    # Database
    "mongodb",
    "MongoDB",
    
    # Base model
    "BaseDBModel",
    "PyObjectId",
    
    # Models
    "User",
    "UserRole",
    "Resume",
    "Education", 
    "WorkExperience",
    "Skill",
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