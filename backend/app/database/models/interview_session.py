"""
InterviewSession model/schema for MongoDB - Enhanced for live interview engine.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import Field

from .base import BaseDBModel


class InterviewStatus(str, Enum):
    """Interview status enum - Enhanced for live interview flow."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class InterviewType(str, Enum):
    """Interview type enum."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    HR = "hr"
    MIXED = "mixed"
    MOCK = "mock"


class DifficultyLevel(str, Enum):
    """Difficulty level enum."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ResponseType(str, Enum):
    """Type of candidate response."""
    ANSWER = "answer"
    FOLLOW_UP_ANSWER = "follow_up_answer"


class InterviewResponse(BaseDBModel):
    """Candidate response to an interview question."""
    
    response_id: str = Field(..., description="Unique response ID")
    question_id: str = Field(..., description="Question being answered")
    answer: str = Field(..., description="Candidate's answer")
    submitted_at: datetime = Field(..., description="When answer was submitted")
    sequence_number: int = Field(..., description="Order in conversation")
    response_type: ResponseType = Field(default=ResponseType.ANSWER, description="Type of response")
    
    # Follow-up tracking
    is_follow_up_to: Optional[str] = Field(None, description="Original question ID if this is a follow-up answer")
    follow_up_question: Optional[str] = Field(None, description="Follow-up question text if applicable")
    
    # Processing metadata
    processing_duration_ms: Optional[int] = Field(None, description="Time to process response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response_id": "resp_1",
                "question_id": "q_1",
                "answer": "I implemented a RAG system using LangChain and ChromaDB...",
                "submitted_at": "2024-01-15T10:30:00Z",
                "sequence_number": 1,
                "response_type": "answer"
            }
        }


class InterviewSession(BaseDBModel):
    """Enhanced interview session for live interview engine."""
    
    # Core references
    user_id: str = Field(..., description="Reference to User")
    resume_id: Optional[str] = Field(None, description="Reference to Resume")
    job_description_id: Optional[str] = Field(None, description="Reference to JobDescription") 
    interview_plan_id: Optional[str] = Field(None, description="Reference to generated InterviewPlan")
    
    # Interview details
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    interview_type: InterviewType = InterviewType.TECHNICAL
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM
    target_position: str = Field(..., min_length=1, max_length=100)
    target_company: Optional[str] = None
    
    # Timing
    scheduled_start_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = Field(default=60, ge=15, le=240)
    paused_at: Optional[datetime] = Field(None, description="When session was paused")
    pause_duration_seconds: int = Field(default=0, description="Total time paused")
    
    # Status and AI
    status: InterviewStatus = InterviewStatus.NOT_STARTED
    is_ai_interviewer: bool = True
    ai_model_used: Optional[str] = Field(None, description="LLM model used for interviewing")
    
    # Settings
    question_count: int = Field(default=10, ge=5, le=50)
    enable_feedback: bool = True
    enable_recording: bool = False
    language: str = "en"
    
    # Live interview progress tracking
    current_question_index: int = Field(default=0, description="Current position in question sequence")
    current_question_id: Optional[str] = Field(None, description="Current active question ID")
    completed_question_ids: List[str] = Field(default_factory=list, description="Questions already asked")
    asked_follow_ups: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Follow-up questions asked for each original question"
    )
    
    # Response tracking
    responses: List[InterviewResponse] = Field(
        default_factory=list, 
        description="All candidate responses in order"
    )
    total_responses: int = Field(default=0, description="Total number of responses submitted")
    
    # Interview memory and context
    conversation_context: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent conversation context for interviewer agent"
    )
    
    # Concurrency protection
    is_locked: bool = Field(default=False, description="Prevents concurrent modifications")
    locked_at: Optional[datetime] = Field(None, description="When session was locked")
    locked_by_process: Optional[str] = Field(None, description="Process that locked the session")
    
    # Results
    overall_score: Optional[float] = Field(None, description="0-100 scale")
    time_spent_seconds: Optional[int] = None
    notes: Optional[str] = None
    
    # Metadata
    interviewer_agent_version: Optional[str] = Field(None, description="Version of interviewer agent used")
    session_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional session metadata"
    )
    
    def add_response(self, question_id: str, answer: str, response_type: ResponseType = ResponseType.ANSWER) -> str:
        """Add a new response to the session."""
        response_id = f"resp_{self.total_responses + 1}"
        
        response = InterviewResponse(
            response_id=response_id,
            question_id=question_id,
            answer=answer,
            submitted_at=datetime.utcnow(),
            sequence_number=len(self.responses) + 1,
            response_type=response_type
        )
        
        self.responses.append(response)
        self.total_responses += 1
        
        return response_id
    
    def get_recent_context(self, max_exchanges: int = 3) -> List[Dict[str, Any]]:
        """Get recent conversation context for interviewer agent."""
        if len(self.responses) == 0:
            return []
        
        # Get last few exchanges
        recent_responses = self.responses[-max_exchanges:] if max_exchanges else self.responses
        
        context = []
        for response in recent_responses:
            context.append({
                "question_id": response.question_id,
                "answer": response.answer,
                "response_type": response.response_type.value,
                "sequence": response.sequence_number
            })
        
        return context
    
    def is_question_asked(self, question_id: str) -> bool:
        """Check if a question has already been asked."""
        return question_id in self.completed_question_ids
    
    def get_follow_ups_for_question(self, question_id: str) -> List[str]:
        """Get follow-up questions already asked for a specific question."""
        return self.asked_follow_ups.get(question_id, [])
    
    def add_follow_up(self, original_question_id: str, follow_up_question: str) -> None:
        """Record that a follow-up was asked for a question."""
        if original_question_id not in self.asked_follow_ups:
            self.asked_follow_ups[original_question_id] = []
        
        self.asked_follow_ups[original_question_id].append(follow_up_question)
    
    def can_ask_follow_up(self, question_id: str, max_follow_ups: int = 1) -> bool:
        """Check if more follow-ups can be asked for a question."""
        current_follow_ups = len(self.get_follow_ups_for_question(question_id))
        return current_follow_ups < max_follow_ups
    
    def lock_session(self, process_id: str) -> bool:
        """Lock session to prevent concurrent modifications."""
        if self.is_locked:
            return False
        
        self.is_locked = True
        self.locked_at = datetime.utcnow()
        self.locked_by_process = process_id
        return True
    
    def unlock_session(self) -> None:
        """Unlock session."""
        self.is_locked = False
        self.locked_at = None
        self.locked_by_process = None
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "resume_id": "507f1f77bcf86cd799439012",
                "interview_plan_id": "507f1f77bcf86cd799439013",
                "title": "Senior Software Engineer Technical Interview",
                "interview_type": "technical",
                "difficulty_level": "hard",
                "target_position": "Senior Software Engineer",
                "target_company": "Tech Company Inc.",
                "duration_minutes": 60,
                "question_count": 15,
                "status": "not_started",
                "current_question_index": 0,
                "responses": [],
                "conversation_context": []
            }
        }


__all__ = [
    'InterviewStatus',
    'InterviewType', 
    'DifficultyLevel',
    'ResponseType',
    'InterviewResponse',
    'InterviewSession',
]