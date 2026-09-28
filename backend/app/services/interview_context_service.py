"""
Interview Context Service - Manages interview session state and context.

This service provides:
1. Session state management (lock, unlock, update)
2. Question progression tracking
3. Context retrieval and formatting
4. Duplicate prevention
5. Memory management for interview flow
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from bson import ObjectId

from app.database.mongodb import mongodb
from app.database.models.interview_session import (
    InterviewSession,
    InterviewStatus,
    InterviewResponse,
    ResponseType
)
from app.database.models.interview_plan import InterviewPlan, GeneratedQuestion
from app.database.models.resume_intelligence import CandidateProfile
from app.database.models.job_description import JobDescription

logger = logging.getLogger(__name__)


class InterviewContextException(Exception):
    """Exception for interview context service errors."""
    pass


class InterviewContextService:
    """Manages interview session context and state."""
    
    # Configuration
    SESSION_LOCK_TIMEOUT_MINUTES = 5
    MAX_CONTEXT_HISTORY = 10
    
    def __init__(self):
        """Initialize the service."""
        self.logger = logger
    
    async def get_session_with_lock(
        self,
        session_id: str,
        user_id: str,
        process_id: str
    ) -> Optional[InterviewSession]:
        """
        Get interview session with exclusive lock.
        
        Args:
            session_id: Session ID
            user_id: User ID for authorization
            process_id: Process attempting to acquire lock
            
        Returns:
            InterviewSession with lock or None if not accessible
        """
        try:
            # Convert session ID to ObjectId
            try:
                session_oid = ObjectId(session_id)
            except Exception:
                raise InterviewContextException("Invalid session ID format")
            
            # Get session from database
            sessions_collection = mongodb.get_collection("interview_sessions")
            session_doc = await sessions_collection.find_one({
                "_id": session_oid,
                "user_id": user_id
            })
            
            if not session_doc:
                return None
            
            # Convert to model
            session_doc["_id"] = str(session_doc["_id"])
            session = InterviewSession(**session_doc)
            
            # Check if session is locked by another process
            if session.is_locked:
                if session.locked_by_process != process_id:
                    # Check if lock has expired
                    if session.locked_at and session.locked_at < datetime.utcnow() - timedelta(
                        minutes=self.SESSION_LOCK_TIMEOUT_MINUTES
                    ):
                        # Force unlock expired lock
                        session.unlock_session()
                        await self._save_session(session)
                        self.logger.warning(f"Force-unlocked expired session lock: {session_id}")
                    else:
                        # Session is locked by another process
                        self.logger.info(f"Session {session_id} is locked by {session.locked_by_process}")
                        return None
            
            # Acquire lock
            session.lock_session(process_id)
            
            # Save the lock to database
            await sessions_collection.update_one(
                {"_id": session_oid},
                {
                    "$set": {
                        "is_locked": session.is_locked,
                        "locked_at": session.locked_at,
                        "locked_by_process": session.locked_by_process
                    }
                }
            )
            
            return session
            
        except Exception as e:
            self.logger.error(f"Error getting session with lock: {str(e)}")
            raise InterviewContextException(f"Failed to get session with lock: {str(e)}")
    
    async def release_session_lock(self, session: InterviewSession) -> None:
        """
        Release session lock and save to database.
        
        Args:
            session: Session to unlock
        """
        try:
            if not session.id:
                return
            
            session.unlock_session()
            
            sessions_collection = mongodb.get_collection("interview_sessions")
            await sessions_collection.update_one(
                {"_id": ObjectId(session.id)},
                {
                    "$set": {
                        "is_locked": False,
                        "locked_at": None,
                        "locked_by_process": None
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error releasing session lock: {str(e)}")
    
    async def get_interview_plan(self, plan_id: str) -> Optional[InterviewPlan]:
        """
        Get interview plan by ID.
        
        Args:
            plan_id: Interview plan ID
            
        Returns:
            InterviewPlan or None if not found
        """
        try:
            plans_collection = mongodb.get_collection("interview_plans")
            plan_doc = await plans_collection.find_one({"_id": ObjectId(plan_id)})
            
            if not plan_doc:
                return None
            
            return InterviewPlan(**plan_doc)
            
        except Exception as e:
            self.logger.error(f"Error getting interview plan: {str(e)}")
            return None
    
    async def get_candidate_profile(self, resume_id: str) -> Optional[CandidateProfile]:
        """
        Get candidate profile by resume ID.
        
        Args:
            resume_id: Resume ID
            
        Returns:
            CandidateProfile or None if not found
        """
        try:
            # Get resume document first
            resumes_collection = mongodb.get_collection("resumes")
            resume_doc = await resumes_collection.find_one({"_id": ObjectId(resume_id)})
            
            if not resume_doc or not resume_doc.get("intelligence_profile_id"):
                return None
            
            # Get candidate profile
            profiles_collection = mongodb.get_collection("candidate_profiles")
            profile_doc = await profiles_collection.find_one({
                "_id": ObjectId(resume_doc["intelligence_profile_id"])
            })
            
            if not profile_doc:
                return None
            
            return CandidateProfile(**profile_doc)
            
        except Exception as e:
            self.logger.error(f"Error getting candidate profile: {str(e)}")
            return None
    
    async def get_job_description(self, job_description_id: str) -> Optional[JobDescription]:
        """
        Get job description by ID.
        
        Args:
            job_description_id: Job description ID
            
        Returns:
            JobDescription or None if not found
        """
        try:
            if not job_description_id:
                return None
            
            jobs_collection = mongodb.get_collection("job_descriptions")
            job_doc = await jobs_collection.find_one({"_id": ObjectId(job_description_id)})
            
            if not job_doc:
                return None
            
            return JobDescription(**job_doc)
            
        except Exception as e:
            self.logger.error(f"Error getting job description: {str(e)}")
            return None
    
    async def add_response_to_session(
        self,
        session: InterviewSession,
        question_id: str,
        answer: str,
        response_type: ResponseType = ResponseType.ANSWER,
        follow_up_question: Optional[str] = None,
        is_follow_up_to: Optional[str] = None
    ) -> str:
        """
        Add a candidate response to the session.
        
        Args:
            session: Interview session
            question_id: Question being answered
            answer: Candidate's answer
            response_type: Type of response
            follow_up_question: Follow-up question if applicable
            is_follow_up_to: Original question ID if this is a follow-up answer
            
        Returns:
            Response ID
        """
        try:
            response_id = session.add_response(question_id, answer, response_type)
            
            # Update the response with additional fields if needed
            if len(session.responses) > 0:
                latest_response = session.responses[-1]
                if follow_up_question:
                    latest_response.follow_up_question = follow_up_question
                if is_follow_up_to:
                    latest_response.is_follow_up_to = is_follow_up_to
            
            # Mark question as completed if this is not a follow-up answer
            if response_type == ResponseType.ANSWER and question_id not in session.completed_question_ids:
                session.completed_question_ids.append(question_id)
            
            # Update conversation context
            self._update_conversation_context(session)
            
            return response_id
            
        except Exception as e:
            self.logger.error(f"Error adding response to session: {str(e)}")
            raise InterviewContextException(f"Failed to add response: {str(e)}")
    
    async def mark_question_as_current(
        self,
        session: InterviewSession,
        question_id: str
    ) -> None:
        """
        Mark a question as the current active question.
        
        Args:
            session: Interview session
            question_id: Question ID to mark as current
        """
        try:
            session.current_question_id = question_id
            session.current_question_index = len(session.completed_question_ids)
            
        except Exception as e:
            self.logger.error(f"Error marking question as current: {str(e)}")
            raise InterviewContextException(f"Failed to mark question as current: {str(e)}")
    
    async def record_follow_up(
        self,
        session: InterviewSession,
        original_question_id: str,
        follow_up_question: str
    ) -> None:
        """
        Record that a follow-up question was asked.
        
        Args:
            session: Interview session
            original_question_id: Original question ID
            follow_up_question: Follow-up question text
        """
        try:
            session.add_follow_up(original_question_id, follow_up_question)
            
        except Exception as e:
            self.logger.error(f"Error recording follow-up: {str(e)}")
    
    def _update_conversation_context(self, session: InterviewSession) -> None:
        """
        Update the conversation context for the session.
        
        Args:
            session: Interview session
        """
        try:
            # Keep only the most recent exchanges
            if len(session.responses) > self.MAX_CONTEXT_HISTORY:
                # Keep the last MAX_CONTEXT_HISTORY responses
                session.responses = session.responses[-self.MAX_CONTEXT_HISTORY:]
            
            # Update conversation context
            session.conversation_context = session.get_recent_context(max_exchanges=5)
            
        except Exception as e:
            self.logger.error(f"Error updating conversation context: {str(e)}")
    
    async def save_session(self, session: InterviewSession) -> None:
        """
        Save session to database.
        
        Args:
            session: Session to save
        """
        try:
            await self._save_session(session)
        except Exception as e:
            self.logger.error(f"Error saving session: {str(e)}")
            raise InterviewContextException(f"Failed to save session: {str(e)}")
    
    async def _save_session(self, session: InterviewSession) -> None:
        """Internal method to save session to database."""
        if not session.id:
            return
        
        sessions_collection = mongodb.get_collection("interview_sessions")
        session_dict = session.model_dump(exclude={"id"})
        
        await sessions_collection.update_one(
            {"_id": ObjectId(session.id)},
            {"$set": session_dict}
        )
    
    async def check_duplicate_submission(
        self,
        session: InterviewSession,
        question_id: str,
        answer: str,
        time_window_seconds: int = 5
    ) -> bool:
        """
        Check if this answer was recently submitted to prevent duplicates.
        
        Args:
            session: Interview session
            question_id: Question ID
            answer: Answer text
            time_window_seconds: Time window to check for duplicates
            
        Returns:
            True if this appears to be a duplicate submission
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=time_window_seconds)
            
            # Check recent responses for similar answer to same question
            for response in reversed(session.responses):
                if (response.question_id == question_id and
                    response.submitted_at >= cutoff_time and
                    response.answer.strip() == answer.strip()):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking duplicate submission: {str(e)}")
            return False
    
    async def update_session_status(
        self,
        session: InterviewSession,
        status: InterviewStatus,
        end_time: Optional[datetime] = None
    ) -> None:
        """
        Update session status.
        
        Args:
            session: Interview session
            status: New status
            end_time: End time if completing/cancelling
        """
        try:
            session.status = status
            
            if end_time:
                session.end_time = end_time
            
            # Calculate time spent if ending
            if status in [InterviewStatus.COMPLETED, InterviewStatus.CANCELLED] and session.actual_start_time:
                if not session.end_time:
                    session.end_time = datetime.utcnow()
                
                time_spent = session.end_time - session.actual_start_time
                session.time_spent_seconds = int(time_spent.total_seconds()) - session.pause_duration_seconds
            
        except Exception as e:
            self.logger.error(f"Error updating session status: {str(e)}")
            raise InterviewContextException(f"Failed to update session status: {str(e)}")
    
    def get_session_progress(self, session: InterviewSession, total_questions: int) -> Dict[str, Any]:
        """
        Get session progress information.
        
        Args:
            session: Interview session
            total_questions: Total questions in interview plan
            
        Returns:
            Progress information dictionary
        """
        try:
            completed = len(session.completed_question_ids)
            
            return {
                "current_question_index": session.current_question_index,
                "completed_questions": completed,
                "total_questions": total_questions,
                "progress_percentage": (completed / total_questions * 100) if total_questions > 0 else 0,
                "responses_count": len(session.responses),
                "follow_ups_asked": sum(len(follow_ups) for follow_ups in session.asked_follow_ups.values()),
                "status": session.status.value
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session progress: {str(e)}")
            return {
                "current_question_index": 0,
                "completed_questions": 0,
                "total_questions": 0,
                "progress_percentage": 0,
                "responses_count": 0,
                "follow_ups_asked": 0,
                "status": "unknown"
            }


# Global instance
interview_context_service = InterviewContextService()

__all__ = [
    'InterviewContextService',
    'InterviewContextException',
    'interview_context_service',
]