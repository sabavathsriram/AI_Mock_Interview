"""
User endpoints for managing user profiles and authentication.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.database.mongodb import mongodb

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/skills")
async def get_user_skills(current_user: User = Depends(get_current_active_user)):
    """
    Get all skill assessments for the current user across all interviews.
    
    Returns a list of SkillAssessment documents ordered by creation date (newest first).
    """
    try:
        skill_assessments_collection = mongodb.get_collection("skill_assessments")
        assessments = await skill_assessments_collection.find({
            "user_id": str(current_user.id)
        }).sort("created_at", -1).to_list(None)
        
        # Convert ObjectIds to strings
        for assessment in assessments:
            assessment["_id"] = str(assessment["_id"])
            if "interview_session_id" in assessment:
                assessment["interview_session_id"] = str(assessment["interview_session_id"])
        
        return {
            "total": len(assessments),
            "skill_assessments": assessments
        }
    
    except Exception as e:
        logger.exception(f"Error fetching user skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch skill assessments: {str(e)}"
        )


@router.get("/recommendations")
async def get_user_recommendations(current_user: User = Depends(get_current_active_user)):
    """
    Get all learning recommendations for the current user across all interviews.
    
    Returns a list of LearningRecommendation documents ordered by creation date (newest first).
    """
    try:
        recommendations_collection = mongodb.get_collection("learning_recommendations")
        recommendations = await recommendations_collection.find({
            "user_id": str(current_user.id)
        }).sort("created_at", -1).to_list(None)
        
        # Convert ObjectIds to strings
        for rec in recommendations:
            rec["_id"] = str(rec["_id"])
            if "interview_session_id" in rec:
                rec["interview_session_id"] = str(rec["interview_session_id"])
        
        return {
            "total": len(recommendations),
            "learning_recommendations": recommendations
        }
    
    except Exception as e:
        logger.exception(f"Error fetching user recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch learning recommendations: {str(e)}"
        )
