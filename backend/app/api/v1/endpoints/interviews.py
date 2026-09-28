"""
Live Interview endpoints - Enhanced for real conversational interviews.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from bson import ObjectId

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.database.mongodb import mongodb
from app.database.models.interview_session import (
    InterviewSession, 
    InterviewStatus, 
    InterviewType, 
    DifficultyLevel,
    ResponseType
)
from app.database.models.interview_plan import InterviewPlan
from app.services.interviewer_agent import interviewer_agent, InterviewerAction
from app.services.interview_context_service import interview_context_service

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class CreateSessionRequest(BaseModel):
    """Request to create a new interview session."""
    
    interview_plan_id: str = Field(..., description="ID of generated interview plan")
    title: Optional[str] = Field(None, description="Interview title (optional)")
    duration_minutes: Optional[int] = Field(None, ge=15, le=240, description="Override duration")
    
class StartInterviewRequest(BaseModel):
    """Request body for starting an interview session."""
    
    # Optional - can be provided during creation or start
    interview_plan_id: Optional[str] = Field(None, description="Interview plan to use")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)


class InterviewQuestionResponse(BaseModel):
    """Response containing an interview question."""
    
    question_id: str
    question: str
    question_type: str
    skill: str
    difficulty: str
    source: str
    is_follow_up: bool = False
    source_question_id: Optional[str] = None
    estimated_duration_seconds: int = 120
    progression_level: Optional[int] = None


class CreateSessionResponse(BaseModel):
    """Response from creating an interview session."""
    
    session_id: str
    status: str
    interview_plan_id: str
    title: str
    total_questions: int
    duration_minutes: int
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class StartInterviewResponse(BaseModel):
    """Response from starting an interview."""
    
    session_id: str
    status: str
    current_question_index: int
    total_questions: int
    current_question: InterviewQuestionResponse
    started_at: datetime
    candidate_name: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SubmitAnswerRequest(BaseModel):
    """Request body for submitting an answer."""
    
    question_id: str = Field(..., description="ID of question being answered")
    answer: str = Field(..., min_length=1, description="Candidate's answer")


class SubmitAnswerResponse(BaseModel):
    """Response from submitting an answer."""
    
    response_id: str
    question_id: str
    status: str
    current_question_index: int
    total_questions: int
    next_question: Optional[InterviewQuestionResponse] = None
    is_interview_complete: bool
    is_follow_up: bool = False

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class InterviewSessionStatusResponse(BaseModel):
    """Response containing interview session status."""
    
    session_id: str
    status: str
    current_question_index: int
    total_questions: int
    completed_questions: int
    responses_count: int
    follow_ups_asked: int
    progress_percentage: float
    time_spent_seconds: Optional[int] = None
    started_at: Optional[datetime] = None
    candidate_name: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class PauseResumeResponse(BaseModel):
    """Response from pausing or resuming interview."""
    
    session_id: str
    status: str
    message: str
    paused_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CompleteInterviewResponse(BaseModel):
    """Response from completing an interview."""
    
    session_id: str
    status: str
    total_questions_asked: int
    total_responses: int
    total_follow_ups: int
    time_spent_seconds: Optional[int] = None
    completed_at: datetime
    message: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/sessions", response_model=CreateSessionResponse)
async def create_interview_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new interview session from an interview plan.
    
    This creates a session in NOT_STARTED state. The interview can then be started
    using the start endpoint.
    """
    try:
        logger.info(f"Creating interview session for user {current_user.id}")
        
        # Get interview plan and verify ownership
        interview_plan = await interview_context_service.get_interview_plan(
            request.interview_plan_id
        )
        
        if not interview_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview plan not found"
            )
        
        if interview_plan.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Interview plan not owned by user"
            )
        
        # Create session
        session = InterviewSession(
            user_id=current_user.id,
            resume_id=interview_plan.resume_id,
            job_description_id=interview_plan.job_description_id,
            interview_plan_id=request.interview_plan_id,
            title=request.title or f"{interview_plan.interview_type.title()} Interview",
            interview_type=InterviewType(interview_plan.interview_type),
            difficulty_level=DifficultyLevel(interview_plan.difficulty.value),
            target_position="Software Engineer",  # Could be extracted from job description
            duration_minutes=request.duration_minutes or interview_plan.duration_minutes,
            question_count=len(interview_plan.questions),
            status=InterviewStatus.NOT_STARTED
        )
        
        # Save to database
        sessions_collection = mongodb.get_collection("interview_sessions")
        result = await sessions_collection.insert_one(session.model_dump(by_alias=True))
        session_id = str(result.inserted_id)
        
        logger.info(f"Created interview session: {session_id}")
        
        return CreateSessionResponse(
            session_id=session_id,
            status=session.status.value,
            interview_plan_id=request.interview_plan_id,
            title=session.title,
            total_questions=len(interview_plan.questions),
            duration_minutes=session.duration_minutes,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating interview session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview session: {str(e)}"
        )


@router.post("/{session_id}/start", response_model=StartInterviewResponse)
async def start_interview(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Start an interview session.
    
    This transitions the session from NOT_STARTED to IN_PROGRESS and
    presents the first question.
    """
    try:
        logger.info(f"Starting interview session: {session_id}")
        
        process_id = f"start_{uuid.uuid4().hex[:8]}"
        
        # Get session with lock
        session = await interview_context_service.get_session_with_lock(
            session_id, current_user.id, process_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or locked"
            )
        
        try:
            # Verify session can be started
            if session.status != InterviewStatus.NOT_STARTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Interview cannot be started from status: {session.status.value}"
                )
            
            # Get interview plan
            interview_plan = await interview_context_service.get_interview_plan(
                session.interview_plan_id
            )
            
            if not interview_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interview plan not found"
                )
            
            # Get candidate profile for context
            candidate_profile = None
            if session.resume_id:
                candidate_profile = await interview_context_service.get_candidate_profile(
                    session.resume_id
                )
            
            # Update session status
            session.status = InterviewStatus.IN_PROGRESS
            session.actual_start_time = datetime.utcnow()
            session.ai_model_used = "gemini-1.5-flash"  # Could be configurable
            
            # Use interviewer agent to get first question
            decision = await interviewer_agent.decide_next_action(
                session=session,
                interview_plan=interview_plan,
                candidate_profile=candidate_profile
            )
            
            if decision.action != InterviewerAction.ASK_QUESTION:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to get first question from interview plan"
                )
            
            # Mark question as current
            await interview_context_service.mark_question_as_current(
                session, decision.question_id
            )
            
            # Save session
            await interview_context_service.save_session(session)
            
            # Prepare response
            question_response = InterviewQuestionResponse(
                question_id=decision.question_id,
                question=decision.question,
                question_type=decision.question_type,
                skill=decision.skill,
                difficulty=session.difficulty_level.value,
                source="interview_plan",
                is_follow_up=False,
                estimated_duration_seconds=decision.estimated_duration_seconds
            )
            
            return StartInterviewResponse(
                session_id=session_id,
                status=session.status.value,
                current_question_index=session.current_question_index,
                total_questions=len(interview_plan.questions),
                current_question=question_response,
                started_at=session.actual_start_time,
                candidate_name=candidate_profile.candidate_name if candidate_profile else None
            )
            
        finally:
            # Always release the lock
            await interview_context_service.release_session_lock(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}"
        )



@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: str,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit an answer to the current interview question.
    
    This processes the candidate's answer and determines the next question
    or follow-up using the interviewer agent.
    """
    try:
        logger.info(f"Submitting answer for session: {session_id}")
        
        process_id = f"answer_{uuid.uuid4().hex[:8]}"
        
        # Get session with lock
        session = await interview_context_service.get_session_with_lock(
            session_id, current_user.id, process_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or locked"
            )
        
        try:
            # Verify session is active
            if session.status != InterviewStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot submit answer for session in status: {session.status.value}"
                )
            
            # Check for duplicate submission
            is_duplicate = await interview_context_service.check_duplicate_submission(
                session, request.question_id, request.answer
            )
            
            if is_duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Duplicate answer submission detected"
                )
            
            # Verify question ID matches current question
            if session.current_question_id != request.question_id:
                # Check if it's a follow-up to the current question
                is_follow_up_answer = any(
                    request.question_id.startswith(f"{session.current_question_id}_follow_up")
                    for _ in [1]  # Simple way to make this a boolean check
                )
                
                if not is_follow_up_answer:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Question ID does not match current question"
                    )
            
            # Get interview plan and candidate profile
            interview_plan = await interview_context_service.get_interview_plan(
                session.interview_plan_id
            )
            
            candidate_profile = None
            if session.resume_id:
                candidate_profile = await interview_context_service.get_candidate_profile(
                    session.resume_id
                )
            
            if not interview_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Interview plan not found"
                )
            
            # Determine response type
            response_type = ResponseType.FOLLOW_UP_ANSWER if "_follow_up" in request.question_id else ResponseType.ANSWER
            
            # Add response to session
            response_id = await interview_context_service.add_response_to_session(
                session=session,
                question_id=request.question_id,
                answer=request.answer,
                response_type=response_type
            )
            
            # Use interviewer agent to decide next action
            decision = await interviewer_agent.decide_next_action(
                session=session,
                interview_plan=interview_plan,
                candidate_profile=candidate_profile,
                last_answer=request.answer,
                last_question_id=request.question_id
            )
            
            # Process the decision
            next_question = None
            is_follow_up = False
            is_complete = False
            
            if decision.action == InterviewerAction.ASK_QUESTION:
                # Regular next question
                await interview_context_service.mark_question_as_current(
                    session, decision.question_id
                )
                
                next_question = InterviewQuestionResponse(
                    question_id=decision.question_id,
                    question=decision.question,
                    question_type=decision.question_type,
                    skill=decision.skill,
                    difficulty=session.difficulty_level.value,
                    source="interview_plan",
                    is_follow_up=False,
                    estimated_duration_seconds=decision.estimated_duration_seconds
                )
                
            elif decision.action == InterviewerAction.ASK_FOLLOW_UP:
                # Follow-up question
                is_follow_up = True
                
                # Record the follow-up
                await interview_context_service.record_follow_up(
                    session, decision.source_question_id, decision.question
                )
                
                next_question = InterviewQuestionResponse(
                    question_id=decision.question_id,
                    question=decision.question,
                    question_type=decision.question_type,
                    skill=decision.skill,
                    difficulty=session.difficulty_level.value,
                    source="follow_up",
                    is_follow_up=True,
                    source_question_id=decision.source_question_id,
                    estimated_duration_seconds=decision.estimated_duration_seconds
                )
                
            elif decision.action == InterviewerAction.END_INTERVIEW:
                # Interview is complete
                is_complete = True
                await interview_context_service.update_session_status(
                    session, InterviewStatus.COMPLETED
                )
            
            # Save session
            await interview_context_service.save_session(session)
            
            return SubmitAnswerResponse(
                response_id=response_id,
                question_id=request.question_id,
                status="submitted",
                current_question_index=session.current_question_index,
                total_questions=len(interview_plan.questions),
                next_question=next_question,
                is_interview_complete=is_complete,
                is_follow_up=is_follow_up
            )
            
        finally:
            # Always release the lock
            await interview_context_service.release_session_lock(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit answer: {str(e)}"
        )


@router.get("/{session_id}/status", response_model=InterviewSessionStatusResponse)
async def get_interview_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current status of an interview session.
    """
    try:
        # Get session (no lock needed for read-only operation)
        sessions_collection = mongodb.get_collection("interview_sessions")
        session_doc = await sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": current_user.id
        })
        
        if not session_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        session = InterviewSession(**session_doc)
        
        # Get interview plan to calculate total questions
        interview_plan = await interview_context_service.get_interview_plan(
            session.interview_plan_id
        )
        
        total_questions = len(interview_plan.questions) if interview_plan else session.question_count
        
        # Get progress information
        progress = interview_context_service.get_session_progress(session, total_questions)
        
        # Get candidate name if available
        candidate_name = None
        if session.resume_id:
            candidate_profile = await interview_context_service.get_candidate_profile(
                session.resume_id
            )
            if candidate_profile:
                candidate_name = candidate_profile.candidate_name
        
        return InterviewSessionStatusResponse(
            session_id=session_id,
            status=session.status.value,
            current_question_index=progress["current_question_index"],
            total_questions=progress["total_questions"],
            completed_questions=progress["completed_questions"],
            responses_count=progress["responses_count"],
            follow_ups_asked=progress["follow_ups_asked"],
            progress_percentage=progress["progress_percentage"],
            time_spent_seconds=session.time_spent_seconds,
            started_at=session.actual_start_time,
            candidate_name=candidate_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get interview status: {str(e)}"
        )


@router.post("/{session_id}/pause", response_model=PauseResumeResponse)
async def pause_interview(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Pause an active interview session.
    """
    try:
        process_id = f"pause_{uuid.uuid4().hex[:8]}"
        
        # Get session with lock
        session = await interview_context_service.get_session_with_lock(
            session_id, current_user.id, process_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or locked"
            )
        
        try:
            if session.status != InterviewStatus.IN_PROGRESS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only pause interviews that are in progress"
                )
            
            # Update session status
            session.status = InterviewStatus.PAUSED
            session.paused_at = datetime.utcnow()
            
            # Save session
            await interview_context_service.save_session(session)
            
            return PauseResumeResponse(
                session_id=session_id,
                status=session.status.value,
                message="Interview paused successfully",
                paused_at=session.paused_at
            )
            
        finally:
            await interview_context_service.release_session_lock(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause interview: {str(e)}"
        )


@router.post("/{session_id}/resume", response_model=PauseResumeResponse)
async def resume_interview(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Resume a paused interview session.
    """
    try:
        process_id = f"resume_{uuid.uuid4().hex[:8]}"
        
        # Get session with lock
        session = await interview_context_service.get_session_with_lock(
            session_id, current_user.id, process_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or locked"
            )
        
        try:
            if session.status != InterviewStatus.PAUSED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only resume interviews that are paused"
                )
            
            # Calculate pause duration
            if session.paused_at:
                pause_duration = datetime.utcnow() - session.paused_at
                session.pause_duration_seconds += int(pause_duration.total_seconds())
            
            # Update session status
            session.status = InterviewStatus.IN_PROGRESS
            session.paused_at = None
            
            # Save session
            await interview_context_service.save_session(session)
            
            return PauseResumeResponse(
                session_id=session_id,
                status=session.status.value,
                message="Interview resumed successfully"
            )
            
        finally:
            await interview_context_service.release_session_lock(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume interview: {str(e)}"
        )


@router.post("/{session_id}/complete", response_model=CompleteInterviewResponse)
async def complete_interview(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete an interview session.
    
    This marks the session as completed and calculates final statistics.
    Evaluation will be handled separately in Prompt 12.
    """
    try:
        process_id = f"complete_{uuid.uuid4().hex[:8]}"
        
        # Get session with lock
        session = await interview_context_service.get_session_with_lock(
            session_id, current_user.id, process_id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found or locked"
            )
        
        try:
            if session.status not in [InterviewStatus.IN_PROGRESS, InterviewStatus.PAUSED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot complete interview from status: {session.status.value}"
                )
            
            # Update session status
            await interview_context_service.update_session_status(
                session, InterviewStatus.COMPLETED, datetime.utcnow()
            )
            
            # Calculate statistics
            total_follow_ups = sum(len(follow_ups) for follow_ups in session.asked_follow_ups.values())
            
            # Save session
            await interview_context_service.save_session(session)
            
            return CompleteInterviewResponse(
                session_id=session_id,
                status=session.status.value,
                total_questions_asked=len(session.completed_question_ids),
                total_responses=len(session.responses),
                total_follow_ups=total_follow_ups,
                time_spent_seconds=session.time_spent_seconds,
                completed_at=session.end_time,
                message="Interview completed successfully"
            )
            
        finally:
            await interview_context_service.release_session_lock(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete interview: {str(e)}"
        )



# ============================================================================
# LEGACY ENDPOINTS - These will be deprecated in favor of the new flow
# ============================================================================

class GenerateQuestionsRequest(BaseModel):
    """Request body for generating interview questions."""
    
    resume_id: str = Field(..., description="ID of the resume to base questions on")
    interview_type: str = Field(
        default="technical",
        description="Type of interview: technical, behavioral, coding, system_design"
    )
    difficulty_level: str = Field(
        default="medium",
        description="Difficulty level: easy, medium, hard, expert"
    )
    target_position: str = Field(..., min_length=1, max_length=100)
    target_company: Optional[str] = None
    num_questions: int = Field(default=10, ge=5, le=50)
    job_description_id: Optional[str] = None


class QuestionItemResponse(BaseModel):
    """Single question in response."""
    
    id: str = Field(alias="_id")
    question_text: str
    question_type: str
    difficulty: str
    category: str
    key_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_ai_generated: bool = True
    ai_model_used: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class GenerateQuestionsResponse(BaseModel):
    """Response from question generation endpoint."""
    
    success: bool
    questions: List[QuestionItemResponse]
    message: str


@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(
    request: GenerateQuestionsRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate personalized interview questions based on a candidate's resume.
    
    NOTE: This endpoint is maintained for backward compatibility. 
    New implementations should use the interview planning flow:
    1. POST /interviews/generate-plan (from interview_planning.py)
    2. POST /interviews/sessions (create session)
    3. POST /interviews/{session_id}/start (start interview)
    
    Args:
        request: Question generation request with resume_id and parameters
        current_user: Authenticated user
        
    Returns:
        Generated interview questions
        
    Raises:
        404: Resume not found
        403: Resume not owned by user
        400: Resume not ready (extraction incomplete or analysis missing)
        502/500: LLM or server error
    """
    try:
        logger.info(f"Generating questions for user {current_user.id}, resume {request.resume_id}")
        
        # Import required services
        from app.services.resume_service import ResumeService
        from app.services.interview_question_generation_service import InterviewQuestionGenerationService
        
        # ====================================================================
        # 1. Validate resume exists and belongs to user
        # ====================================================================
        resume = await ResumeService.get_resume_by_id(request.resume_id, str(current_user.id))
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or does not belong to user"
            )
        
        logger.info(f"Resume found: {resume.get('filename', 'unknown')}")
        
        # ====================================================================
        # 2. Validate interview parameters
        # ====================================================================
        valid_interview_types = ["technical", "behavioral", "system_design", "coding"]
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        
        if request.interview_type not in valid_interview_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interview type. Must be one of: {', '.join(valid_interview_types)}"
            )
        
        if request.difficulty_level not in valid_difficulties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid difficulty level. Must be one of: {', '.join(valid_difficulties)}"
            )
        
        num_questions = request.num_questions or 10
        if num_questions < 5 or num_questions > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of questions must be between 5 and 50"
            )
        
        # ====================================================================
        # 3. Generate questions using InterviewQuestionGenerationService
        # ====================================================================
        logger.info(f"Generating {num_questions} {request.interview_type} questions at {request.difficulty_level} difficulty")
        
        service = InterviewQuestionGenerationService()
        
        try:
            # Generate questions - service handles validation and LLM call
            questions = await service.generate_questions(
                user_id=str(current_user.id),
                resume_id=request.resume_id,
                interview_type=request.interview_type,
                difficulty_level=request.difficulty_level,
                target_position=request.target_position,
                target_company=request.target_company,
                num_questions=num_questions,
                job_description_id=request.job_description_id
            )
            
            if not questions or len(questions) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate any interview questions"
                )
            
            logger.info(f"Successfully generated {len(questions)} questions via LLM")
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Question generation failed: {error_str}")
            
            # Check if it's a rate limit error
            if "rate limit" in error_str.lower() or "quota" in error_str.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="API rate limit exceeded. Please try again in a few moments."
                )
            
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate questions: {error_str}"
            )
        
        # ====================================================================
        # 4. Convert to response format
        # ====================================================================
        question_responses = []
        for q in questions:
            # Handle both dict and object formats
            if hasattr(q, 'model_dump'):
                q_dict = q.model_dump()
            elif hasattr(q, 'dict'):
                q_dict = q.dict()
            else:
                q_dict = q
            
            question_responses.append(QuestionItemResponse(
                _id=q_dict.get("_id", ""),
                question_text=q_dict.get("question_text", ""),
                question_type=q_dict.get("question_type", request.interview_type),
                difficulty=q_dict.get("difficulty", request.difficulty_level),
                category=q_dict.get("category", "General"),
                key_points=q_dict.get("key_points", []),
                tags=q_dict.get("tags", [request.interview_type, request.difficulty_level]),
                is_ai_generated=True,
                ai_model_used=q_dict.get("ai_model_used", "gemini-1.5-flash")
            ))
        
        return GenerateQuestionsResponse(
            success=True,
            questions=question_responses,
            message=f"Generated {len(question_responses)} personalized questions from resume"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in generate-questions endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating questions"
        )


# ============================================================================
# PROMPT 11: LIVE INTERVIEW SESSION ENDPOINTS
# ============================================================================
# These endpoints implement the live interview flow:
# POST /start → create session and get first question
# POST /{session_id} → get session
# POST /{session_id}/responses → store answer
# POST /{session_id}/next-question → get next question
# POST /{session_id}/complete → complete interview
# POST /{session_id}/abandon → abandon interview

from app.services.live_interviewer_agent import live_interviewer_agent


class StartLiveInterviewRequest(BaseModel):
    """Request to start a live interview with generated questions."""
    
    resume_id: str = Field(..., description="Resume to base interview on")
    interview_type: str = Field(default="technical", description="Interview type")
    target_position: str = Field(..., description="Target position")
    target_company: Optional[str] = Field(None, description="Target company")
    difficulty: str = Field(default="medium", description="Difficulty level")
    duration_minutes: int = Field(default=60, ge=15, le=240, description="Interview duration")
    num_questions: int = Field(default=10, ge=5, le=50, description="Number of questions")


class QuestionItemForLiveInterview(BaseModel):
    """Question item for live interview response."""
    
    question_id: str
    question_text: str
    question_type: str
    difficulty: str
    category: str
    key_points: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class StartLiveInterviewResponse(BaseModel):
    """Response from starting a live interview."""
    
    session_id: str
    status: str
    current_question_index: int
    total_questions: int
    current_question: QuestionItemForLiveInterview
    started_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class StoreResponseRequest(BaseModel):
    """Request to store an interview response."""
    
    question_id: str = Field(..., description="Question ID")
    answer: str = Field(..., min_length=1, description="Candidate's answer")


class StoreResponseResponse(BaseModel):
    """Response from storing an answer."""
    
    response_id: str
    status: str = "stored"
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class NextQuestionResponse(BaseModel):
    """Response containing the next question."""
    
    current_question_index: int
    total_questions: int
    is_complete: bool
    current_question: Optional[QuestionItemForLiveInterview] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class GetSessionResponse(BaseModel):
    """Response containing session details."""
    
    session_id: str
    status: str
    current_question_index: int
    total_questions: int
    responses_count: int
    started_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class InterviewHistoryItem(BaseModel):
    """Single interview session in history list."""
    
    session_id: str
    interview_type: str
    target_position: str
    target_company: Optional[str] = None
    difficulty: str
    total_questions: int
    questions_answered: int
    interview_status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class InterviewHistoryResponse(BaseModel):
    """Response containing user's interview history."""
    
    interviews: List[InterviewHistoryItem]
    total_count: int
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CompleteInterviewResponse(BaseModel):
    """Response from completing interview."""
    
    session_id: str
    status: str
    message: str
    completed_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


@router.post("/start", response_model=StartLiveInterviewResponse)
async def start_live_interview(
    request: StartLiveInterviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Start a live interview session.
    
    1. Generate interview questions from resume
    2. Create interview session in MongoDB
    3. Return first question
    
    This is the main entry point for starting an interview.
    """
    try:
        logger.info(f"Starting live interview for user {current_user.id}, resume {request.resume_id}")
        
        # ====================================================================
        # 1. Validate resume exists and belongs to user
        # ====================================================================
        from app.services.resume_service import ResumeService
        from app.services.interview_question_generation_service import InterviewQuestionGenerationService
        
        resume = await ResumeService.get_resume_by_id(request.resume_id, str(current_user.id))
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # ====================================================================
        # 2. Generate questions
        # ====================================================================
        logger.info(f"Generating {request.num_questions} {request.interview_type} questions")
        
        service = InterviewQuestionGenerationService()
        try:
            questions = await service.generate_questions(
                user_id=str(current_user.id),
                resume_id=request.resume_id,
                interview_type=request.interview_type,
                difficulty_level=request.difficulty,
                target_position=request.target_position,
                target_company=request.target_company,
                num_questions=request.num_questions,
                job_description_id=None
            )
            
            if not questions or len(questions) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate questions"
                )
            
            logger.info(f"Generated {len(questions)} questions")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate questions: {str(e)}"
            )
        
        # ====================================================================
        # 3. Create interview session
        # ====================================================================
        try:
            session_id, session, first_question = await live_interviewer_agent.start_interview_session(
                user_id=str(current_user.id),
                resume_id=request.resume_id,
                interview_type=request.interview_type,
                target_position=request.target_position,
                target_company=request.target_company,
                difficulty=request.difficulty,
                duration_minutes=request.duration_minutes,
                questions=questions
            )
            
            logger.info(f"Created session {session_id}")
            
            # Format first question response
            first_q = QuestionItemForLiveInterview(
                question_id=first_question.get("_id", "q_0"),
                question_text=first_question.get("question_text", ""),
                question_type=first_question.get("question_type", ""),
                difficulty=first_question.get("difficulty", ""),
                category=first_question.get("category", ""),
                key_points=first_question.get("key_points", []),
                tags=first_question.get("tags", [])
            )
            
            return StartLiveInterviewResponse(
                session_id=session_id,
                status=session.status.value,
                current_question_index=0,
                total_questions=len(questions),
                current_question=first_q,
                started_at=session.actual_start_time
            )
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create interview session: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in start_live_interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/{session_id}", response_model=GetSessionResponse)
async def get_interview_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get current interview session details."""
    try:
        session = await live_interviewer_agent.get_session(session_id, str(current_user.id))
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        return GetSessionResponse(
            session_id=session_id,
            status=session.status.value,
            current_question_index=session.current_question_index,
            total_questions=session.question_count,
            responses_count=session.total_responses,
            started_at=session.actual_start_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session"
        )


@router.post("/{session_id}/responses", response_model=StoreResponseResponse)
async def store_interview_response(
    session_id: str,
    request: StoreResponseRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Store a candidate response to a question."""
    try:
        # Validate session exists and belongs to user
        session = await live_interviewer_agent.get_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        if session.status != InterviewStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot submit answer to {session.status.value} interview"
            )
        
        # Store response
        response_id = await live_interviewer_agent.store_response(
            session_id=session_id,
            user_id=str(current_user.id),
            question_id=request.question_id,
            answer=request.answer
        )
        
        logger.info(f"Stored response {response_id} for session {session_id}")
        
        return StoreResponseResponse(response_id=response_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error storing response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store response"
        )


@router.post("/{session_id}/next-question", response_model=NextQuestionResponse)
async def get_next_interview_question(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the next question in the interview."""
    try:
        # Validate session
        session = await live_interviewer_agent.get_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        if session.status != InterviewStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot get next question from {session.status.value} interview"
            )
        
        # Get next question
        next_question = await live_interviewer_agent.get_next_question(
            session_id=session_id,
            user_id=str(current_user.id)
        )
        
        # Refresh session to get updated index
        updated_session = await live_interviewer_agent.get_session(session_id, str(current_user.id))
        
        if next_question is None:
            # No more questions - interview complete
            return NextQuestionResponse(
                current_question_index=updated_session.current_question_index,
                total_questions=updated_session.question_count,
                is_complete=True,
                current_question=None
            )
        
        # Format next question
        question_id = next_question.get("_id", "")
        # Convert ObjectId to string if necessary
        if not isinstance(question_id, str):
            question_id = str(question_id)
        
        next_q = QuestionItemForLiveInterview(
            question_id=question_id,
            question_text=next_question.get("question_text", ""),
            question_type=next_question.get("question_type", ""),
            difficulty=next_question.get("difficulty", ""),
            category=next_question.get("category", ""),
            key_points=next_question.get("key_points", []),
            tags=next_question.get("tags", [])
        )
        
        return NextQuestionResponse(
            current_question_index=updated_session.current_question_index,
            total_questions=updated_session.question_count,
            is_complete=False,
            current_question=next_q
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get next question"
        )


@router.post("/{session_id}/complete", response_model=CompleteInterviewResponse)
async def complete_interview(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Complete an interview session."""
    try:
        # Validate and complete
        completed_session = await live_interviewer_agent.complete_interview(
            session_id=session_id,
            user_id=str(current_user.id)
        )
        
        logger.info(f"Completed interview session {session_id}")
        
        return CompleteInterviewResponse(
            session_id=session_id,
            status=completed_session.status.value,
            message="Interview completed successfully",
            completed_at=completed_session.end_time
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error completing interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete interview"
        )


@router.post("/{session_id}/abandon", response_model=CompleteInterviewResponse)
async def abandon_interview(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Abandon an interview session."""
    try:
        # Validate and abandon
        abandoned_session = await live_interviewer_agent.abandon_interview(
            session_id=session_id,
            user_id=str(current_user.id)
        )
        
        logger.info(f"Abandoned interview session {session_id}")
        
        return CompleteInterviewResponse(
            session_id=session_id,
            status=abandoned_session.status.value,
            message="Interview abandoned",
            completed_at=abandoned_session.end_time
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error abandoning interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to abandon interview"
        )


@router.get("", response_model=InterviewHistoryResponse)
async def get_interview_history(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the authenticated user's interview history.
    
    Returns all interview sessions belonging to the current user,
    sorted by most recent first.
    """
    try:
        sessions_collection = mongodb.get_collection("interview_sessions")
        
        # Fetch all sessions for the user, sorted by created_at descending
        sessions_cursor = sessions_collection.find(
            {"user_id": str(current_user.id)}
        ).sort("created_at", -1)
        
        interviews = []
        
        async for session_doc in sessions_cursor:
            # Convert to InterviewSession model for consistent data access
            session = InterviewSession(**session_doc)
            
            # Count how many questions have been answered
            questions_answered = len(session.responses)
            
            interview_item = InterviewHistoryItem(
                session_id=str(session_doc["_id"]),
                interview_type=session.interview_type.value,
                target_position=session.target_position,
                target_company=session.target_company,
                difficulty=session.difficulty_level.value,
                total_questions=session.question_count,
                questions_answered=questions_answered,
                interview_status=session.status.value,
                started_at=session.actual_start_time,
                completed_at=session.end_time
            )
            
            interviews.append(interview_item)
        
        return InterviewHistoryResponse(
            interviews=interviews,
            total_count=len(interviews)
        )
        
    except Exception as e:
        logger.error(f"Error fetching interview history for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch interview history"
        )


# Note: The old question generation endpoints are preserved for backward compatibility
# but the new flow uses the InterviewPlan from interview_planning.py

__all__ = ['router']
