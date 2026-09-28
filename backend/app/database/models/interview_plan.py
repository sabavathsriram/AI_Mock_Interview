"""
Interview Plan model - structured interview strategy and question metadata.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import Field, BaseModel

from .base import BaseDBModel


class QuestionSource(str, Enum):
    """Where the question comes from."""
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    KNOWLEDGE_BASE = "knowledge_base"
    GENERATED = "generated"


class QuestionDifficultyLevel(str, Enum):
    """Question difficulty."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestionType(str, Enum):
    """Type of question."""
    CONCEPTUAL = "conceptual"
    CODING = "coding"
    DEBUGGING = "debugging"
    PROJECT_BASED = "project_based"
    SCENARIO_BASED = "scenario_based"
    BEHAVIORAL = "behavioral"
    FOLLOW_UP = "follow_up"


class GeneratedQuestion(BaseModel):
    """A generated question with full context and traceability."""
    
    question_id: str = Field(..., description="Unique question ID")
    question: str = Field(..., description="The actual question text")
    question_type: QuestionType = Field(..., description="Type of question")
    skill: str = Field(..., description="Primary skill being tested")
    difficulty: QuestionDifficultyLevel = Field(..., description="Difficulty level")
    
    # Source traceability - WHY is this question being asked?
    source: QuestionSource = Field(..., description="Where question source comes from")
    source_reference: str = Field(..., description="Resume project/job skill/knowledge doc this references")
    reason: str = Field(..., description="Human-readable reason for asking this question")
    
    # Expected topics and evaluation
    expected_topics: List[str] = Field(
        default_factory=list,
        description="Topics candidate should cover in answer"
    )
    evaluation_criteria: List[str] = Field(
        default_factory=list,
        description="Criteria for evaluating the answer"
    )
    
    # Adaptive follow-up support
    follow_up_possible: bool = Field(
        default=True,
        description="Can this question have follow-ups?"
    )
    follow_up_triggers: List[str] = Field(
        default_factory=list,
        description="Keywords/signals that suggest asking a follow-up"
    )
    
    # Metadata for progression
    progression_level: int = Field(
        default=1,
        description="1=fundamentals, 2=application, 3=project understanding, 4=reasoning, 5=deeper understanding"
    )
    estimated_duration_seconds: int = Field(
        default=120,
        description="Expected time to answer"
    )
    
    # Additional context
    context: Optional[str] = Field(None, description="Additional context about question")
    keywords_to_avoid: List[str] = Field(
        default_factory=list,
        description="Keywords that would indicate memorized answers"
    )


class InterviewPlan(BaseDBModel):
    """Complete interview plan with strategy and questions."""
    
    # References
    user_id: str = Field(..., description="User ID")
    resume_id: str = Field(..., description="Resume ID used for planning")
    job_description_id: Optional[str] = Field(None, description="Job description ID if provided")
    
    # Interview configuration
    interview_type: str = Field(..., description="Type: technical, behavioral, HR, mixed")
    difficulty: QuestionDifficultyLevel = Field(
        default=QuestionDifficultyLevel.MEDIUM,
        description="Overall difficulty level"
    )
    duration_minutes: int = Field(
        default=60,
        description="Estimated interview duration"
    )
    
    # Strategy
    skill_areas: List[str] = Field(
        default_factory=list,
        description="Technical areas that will be tested"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="High-priority areas from resume analysis"
    )
    competency_areas: List[str] = Field(
        default_factory=list,
        description="Competencies to assess"
    )
    
    # Questions
    total_questions: int = Field(
        default=10,
        description="Total number of questions in interview"
    )
    questions: List[GeneratedQuestion] = Field(
        default_factory=list,
        description="All generated questions in order"
    )
    
    # Question distribution
    question_distribution: Dict[str, int] = Field(
        default_factory=lambda: {
            "conceptual": 2,
            "coding": 3,
            "debugging": 1,
            "project_based": 2,
            "scenario_based": 1,
            "behavioral": 1,
            "follow_up": 0
        },
        description="Expected count of each question type"
    )
    
    # Progression strategy
    progression_strategy: Dict = Field(
        default_factory=lambda: {
            "start_with_fundamentals": True,
            "progressively_harder": True,
            "interleave_behavioral": True,
            "project_deep_dives": True
        },
        description="Strategy for how questions should progress"
    )
    
    # Evaluation strategy
    evaluation_criteria: Dict = Field(
        default_factory=dict,
        description="Overall criteria for evaluating candidate"
    )
    
    # Resume analysis summary (for reference during interview)
    candidate_strengths: List[str] = Field(
        default_factory=list,
        description="Key strengths from resume"
    )
    candidate_gaps: List[str] = Field(
        default_factory=list,
        description="Potential gaps to explore"
    )
    
    # Job requirements summary (for reference during interview)
    job_required_skills: List[str] = Field(
        default_factory=list,
        description="Skills required by job description"
    )
    job_nice_to_have_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have skills for job"
    )
    
    # Metadata
    generated_at: Optional[Dict] = Field(
        None,
        description="Generation metadata (model, prompts, timing)"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "resume_id": "507f1f77bcf86cd799439012",
                "interview_type": "technical",
                "difficulty": "medium",
                "total_questions": 10,
                "skill_areas": ["Python", "FastAPI", "RAG Systems", "LLMs"],
                "focus_areas": ["LangChain integration", "Vector databases"]
            }
        }


__all__ = [
    'QuestionSource',
    'QuestionDifficultyLevel',
    'QuestionType',
    'GeneratedQuestion',
    'InterviewPlan',
]
