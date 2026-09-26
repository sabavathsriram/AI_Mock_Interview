"""
Resume Intelligence endpoints for AI-powered resume analysis.
Provides endpoints to analyze resumes and retrieve structured analysis results.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.database.repositories.resume_repository import resume_repository
from app.resume_intelligence import (
    ResumeIntelligenceService,
    ResumeAnalysisResponse,
    ResumeAnalysisRequest,
)
from app.resume_intelligence.service import (
    ResumeAnalysisError,
    ResumeAnalysisValidationError,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analysis",
    tags=["resume_intelligence"],
    dependencies=[Depends(get_current_active_user)]
)


class ResumAnalysisEndpointException(Exception):
    """Base exception for resume analysis endpoints."""
    pass


@router.post("/analyze")
async def analyze_resume(
    request: ResumeAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
) -> ResumeAnalysisResponse:
    """
    Trigger AI analysis of a resume.
    
    Extracts structured information from uploaded resume using LLM.
    Analysis includes skills, experience, education, projects, etc.
    
    Args:
        request: Analysis request with resume_id
        current_user: Authenticated user
        
    Returns:
        ResumeAnalysisResponse with analysis results
        
    Raises:
        HTTPException: If resume not found, unauthorized, or analysis fails
    """
    try:
        # Get resume from database
        resume = await resume_repository.get_resume_by_id(request.resume_id)
        
        if not resume:
            logger.warning(
                f"Resume {request.resume_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Check authorization - user can only analyze their own resumes
        if resume.user_id != current_user.id:
            logger.warning(
                f"Unauthorized attempt to analyze resume {request.resume_id} "
                f"by user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resume"
            )
        
        # Check if already analyzed and force_reanalyze is False
        if (
            resume.analysis_status == "completed"
            and not request.force_reanalyze
        ):
            logger.info(
                f"Returning cached analysis for resume {request.resume_id}"
            )
            analysis_result = resume.structured_analysis
        else:
            # Check if extracted text is available
            if not resume.extracted_text or not resume.extracted_text.strip():
                logger.warning(
                    f"Resume {request.resume_id} has no extracted text"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Resume has no extracted text. Please upload a valid resume."
                )
            
            # Update status to processing
            await resume_repository.update_analysis_status(
                request.resume_id,
                status="processing"
            )
            
            # Perform analysis
            service = ResumeIntelligenceService()
            try:
                analysis_result = await service.analyze_resume(
                    resume_text=resume.extracted_text,
                    resume_id=request.resume_id
                )
                
                # Convert analysis result to dict for storage
                analysis_dict = analysis_result.dict(exclude_none=False)
                
                # Store in database
                updated_resume = await resume_repository.update_analysis_status(
                    request.resume_id,
                    status="completed",
                    structured_analysis=analysis_dict
                )
                
                logger.info(
                    f"Resume {request.resume_id} analysis completed successfully"
                )
                
                if not updated_resume:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to store analysis results"
                    )
                
                resume = updated_resume
                analysis_result = analysis_dict
                
            except (ResumeAnalysisError, ResumeAnalysisValidationError) as e:
                error_msg = f"Resume analysis failed: {str(e)}"
                logger.error(error_msg)
                
                # Update status to failed
                await resume_repository.update_analysis_status(
                    request.resume_id,
                    status="failed",
                    error=str(e)
                )
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Resume analysis failed. Please try again."
                )
        
        return ResumeAnalysisResponse(
            resume_id=request.resume_id,
            user_id=current_user.id,
            analysis=analysis_result,
            status=resume.analysis_status,
            analyzed_at=resume.analyzed_at,
            message="Analysis completed successfully" if resume.analysis_status == "completed" else "Analysis in progress"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in resume analysis endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/results/{resume_id}")
async def get_analysis_results(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ResumeAnalysisResponse:
    """
    Retrieve analysis results for a resume.
    
    Args:
        resume_id: ID of the resume
        current_user: Authenticated user
        
    Returns:
        ResumeAnalysisResponse with stored analysis
        
    Raises:
        HTTPException: If resume not found or unauthorized
    """
    try:
        # Get resume from database
        resume = await resume_repository.get_resume_by_id(resume_id)
        
        if not resume:
            logger.warning(f"Resume {resume_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Check authorization
        if resume.user_id != current_user.id:
            logger.warning(
                f"Unauthorized attempt to access analysis for resume {resume_id} "
                f"by user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resume"
            )
        
        # Return analysis results
        return ResumeAnalysisResponse(
            resume_id=resume_id,
            user_id=current_user.id,
            analysis=resume.structured_analysis,
            status=resume.analysis_status,
            analyzed_at=resume.analyzed_at,
            message=resume.analysis_error if resume.analysis_status == "failed" else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving analysis results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis results"
        )


@router.get("/status/{resume_id}")
async def get_analysis_status(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Get analysis status for a resume.
    
    Args:
        resume_id: ID of the resume
        current_user: Authenticated user
        
    Returns:
        Dictionary with status and metadata
        
    Raises:
        HTTPException: If resume not found or unauthorized
    """
    try:
        # Get resume from database
        resume = await resume_repository.get_resume_by_id(resume_id)
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Check authorization
        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resume"
            )
        
        return {
            "resume_id": resume_id,
            "analysis_status": resume.analysis_status,
            "analyzed_at": resume.analyzed_at,
            "analysis_version": resume.analysis_version,
            "has_analysis": resume.structured_analysis is not None,
            "error": resume.analysis_error if resume.analysis_status == "failed" else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analysis status"
        )


@router.get("/summary/{resume_id}")
async def get_analysis_summary(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Get a quick summary of analysis results (without full details).
    
    Args:
        resume_id: ID of the resume
        current_user: Authenticated user
        
    Returns:
        Dictionary with summary information
        
    Raises:
        HTTPException: If resume not found, unauthorized, or not analyzed
    """
    try:
        # Get resume from database
        resume = await resume_repository.get_resume_by_id(resume_id)
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Check authorization
        if resume.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resume"
            )
        
        if not resume.structured_analysis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume has not been analyzed yet"
            )
        
        analysis = resume.structured_analysis
        
        return {
            "resume_id": resume_id,
            "candidate_name": analysis.get("candidate_name"),
            "experience_level": analysis.get("experience_level"),
            "primary_domains": analysis.get("primary_domains", []),
            "secondary_domains": analysis.get("secondary_domains", []),
            "total_skills": sum(
                len(cat.get("skills", []))
                for cat in analysis.get("technical_skills", [])
            ),
            "total_experience_entries": len(analysis.get("work_experience", [])),
            "total_projects": len(analysis.get("projects", [])),
            "overall_confidence": analysis.get("overall_confidence"),
            "resume_strengths": analysis.get("resume_strengths", []),
            "skill_gaps": analysis.get("potential_skill_gaps", []),
            "important_technologies": analysis.get("important_technologies", [])[:5],
            "analyzed_at": resume.analyzed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analysis summary"
        )


__all__ = ['router']
