"""
Interview Planning API endpoints - Generate interview plans and questions.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.database.mongodb import mongodb
from app.services.interview_strategy_agent import (
    interview_strategy_agent,
    InterviewStrategyException,
)
from app.services.question_generator import (
    question_generator,
    QuestionGenerationException,
)
from app.services.resume_service import ResumeService
from app.database.models.interview_plan import InterviewPlan, GeneratedQuestion
from app.database.models.job_description import JobDescription
from app.database.models.resume_intelligence import CandidateProfile

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class GeneratePlanRequest(BaseModel):
    """Request to generate an interview plan."""
    
    resume_id: str = Field(..., description="Resume ID to base interview on")
    job_description_id: Optional[str] = Field(
        None,
        description="Job description ID (optional)"
    )
    interview_type: str = Field(
        default="technical",
        description="Type of interview: technical, behavioral, HR, mixed"
    )
    difficulty: str = Field(
        default="medium",
        description="Difficulty level: easy, medium, hard, expert"
    )
    question_count: Optional[int] = Field(
        None,
        description="Number of questions (default 10)"
    )


class InterviewQuestionResponse(BaseModel):
    """Response containing a generated question."""
    
    question_id: str
    question: str
    question_type: str
    skill: str
    difficulty: str
    source: str
    source_reference: str
    reason: str
    expected_topics: list
    evaluation_criteria: list
    follow_up_possible: bool
    progression_level: int
    estimated_duration_seconds: int


class InterviewPlanResponse(BaseModel):
    """Response containing complete interview plan."""
    
    plan_id: str = Field(alias="_id")
    interview_type: str
    difficulty: str
    total_questions: int
    duration_minutes: int
    skill_areas: list
    focus_areas: list
    candidate_strengths: list
    candidate_gaps: list
    questions: list[InterviewQuestionResponse]
    question_distribution: dict
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    job_company: Optional[str] = None
    generated_at: Optional[dict] = None
    
    class Config:
        allow_population_by_field_name = True


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/generate-plan", response_model=InterviewPlanResponse)
async def generate_interview_plan(
    request: GeneratePlanRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a personalized interview plan for a candidate.
    
    This endpoint:
    1. Retrieves the candidate's resume and extracted profile
    2. Optionally retrieves job description if provided
    3. Generates interview strategy using LLM
    4. Creates personalized questions from resume, job description, and knowledge base
    5. Returns complete interview plan with questions
    
    Security: Verifies user owns the resume and job description.
    
    Args:
        request: Interview plan generation request
        current_user: Authenticated user
        
    Returns:
        Complete interview plan with questions
    """
    try:
        logger.info(f"Generating interview plan for user {current_user.id}")
        
        # ====================================================================
        # 1. Retrieve and validate resume
        # ====================================================================
        
        # Get resume document
        resume_service = ResumeService()
        resume_doc = await mongodb.resumes.find_one({
            "_id": request.resume_id,
            "user_id": current_user.id
        })
        
        if not resume_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or not owned by user"
            )
        
        # Get resume intelligence profile
        if not resume_doc.get("intelligence_profile_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume has not been analyzed yet. Please run resume analysis first."
            )
        
        profile_doc = await mongodb.candidate_profiles.find_one({
            "_id": resume_doc["intelligence_profile_id"]
        })
        
        if not profile_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume analysis profile not found"
            )
        
        # Convert to CandidateProfile model
        candidate_profile = CandidateProfile(**profile_doc)
        
        logger.info(f"Retrieved candidate profile: {candidate_profile.candidate_name}")
        
        # ====================================================================
        # 2. Retrieve and validate job description (if provided)
        # ====================================================================
        
        job_description = None
        if request.job_description_id:
            job_doc = await mongodb.job_descriptions.find_one({
                "_id": request.job_description_id,
                "user_id": current_user.id
            })
            
            if not job_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job description not found or not owned by user"
                )
            
            job_description = JobDescription(**job_doc)
            logger.info(f"Retrieved job description: {job_description.title}")
        
        # ====================================================================
        # 3. Validate interview parameters
        # ====================================================================
        
        valid_interview_types = ["technical", "behavioral", "HR", "mixed"]
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        
        if request.interview_type not in valid_interview_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interview type. Must be one of: {valid_interview_types}"
            )
        
        if request.difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid difficulty. Must be one of: {valid_difficulties}"
            )
        
        question_count = request.question_count or 10
        if question_count < 5 or question_count > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question count must be between 5 and 50"
            )
        
        # ====================================================================
        # 4. Generate interview plan
        # ====================================================================
        
        logger.info("Creating interview plan using strategy agent")
        
        try:
            interview_plan = await interview_strategy_agent.create_interview_plan(
                user_id=current_user.id,
                resume_id=request.resume_id,
                candidate_profile=candidate_profile,
                job_description=job_description,
                interview_type=request.interview_type,
                difficulty=request.difficulty,
                question_count=question_count,
                job_description_id=request.job_description_id
            )
        except InterviewStrategyException as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate interview strategy: {str(e)}"
            )
        
        # ====================================================================
        # 5. Generate questions
        # ====================================================================
        
        logger.info(f"Generating {question_count} interview questions")
        
        try:
            questions = await question_generator.generate_all_questions(
                candidate_profile=candidate_profile,
                job_description=job_description,
                interview_type=request.interview_type,
                difficulty=request.difficulty,
                total_count=question_count,
                skill_areas=interview_plan.skill_areas
            )
        except QuestionGenerationException as e:
            logger.error(f"Question generation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to generate questions: {str(e)}"
            )
        
        # Validate we got questions
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate any questions"
            )
        
        logger.info(f"Generated {len(questions)} questions")
        
        # ====================================================================
        # 6. Update plan with questions
        # ====================================================================
        
        interview_plan.questions = questions
        
        # ====================================================================
        # 7. Save plan to database
        # ====================================================================
        
        plan_dict = interview_plan.model_dump(exclude_unset=True)
        result = await mongodb.interview_plans.insert_one(plan_dict)
        plan_id = str(result.inserted_id)
        
        logger.info(f"Interview plan saved with ID: {plan_id}")
        
        # ====================================================================
        # 8. Format and return response
        # ====================================================================
        
        question_responses = [
            InterviewQuestionResponse(
                question_id=q.question_id,
                question=q.question,
                question_type=q.question_type.value,
                skill=q.skill,
                difficulty=q.difficulty.value,
                source=q.source.value,
                source_reference=q.source_reference,
                reason=q.reason,
                expected_topics=q.expected_topics,
                evaluation_criteria=q.evaluation_criteria,
                follow_up_possible=q.follow_up_possible,
                progression_level=q.progression_level,
                estimated_duration_seconds=q.estimated_duration_seconds
            )
            for q in questions
        ]
        
        response = InterviewPlanResponse(
            _id=plan_id,
            interview_type=interview_plan.interview_type,
            difficulty=interview_plan.difficulty.value,
            total_questions=len(questions),
            duration_minutes=interview_plan.duration_minutes,
            skill_areas=interview_plan.skill_areas,
            focus_areas=interview_plan.focus_areas,
            candidate_strengths=interview_plan.candidate_strengths,
            candidate_gaps=interview_plan.candidate_gaps,
            questions=question_responses,
            question_distribution=interview_plan.question_distribution,
            candidate_name=candidate_profile.candidate_name,
            job_title=job_description.title if job_description else None,
            job_company=job_description.company if job_description else None,
            generated_at=interview_plan.generated_at
        )
        
        logger.info(f"Interview plan generation completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in interview plan generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during interview plan generation"
        )


@router.get("/plans/{plan_id}")
async def get_interview_plan(
    plan_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve a previously generated interview plan.
    
    Security: Verifies user owns the plan.
    
    Args:
        plan_id: Interview plan ID
        current_user: Authenticated user
        
    Returns:
        Interview plan details
    """
    try:
        from bson import ObjectId
        
        plan = await mongodb.interview_plans.find_one({
            "_id": ObjectId(plan_id),
            "user_id": current_user.id
        })
        
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview plan not found"
            )
        
        plan["_id"] = str(plan["_id"])
        return plan
        
    except Exception as e:
        logger.error(f"Error retrieving plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving interview plan"
        )


__all__ = ['router']
