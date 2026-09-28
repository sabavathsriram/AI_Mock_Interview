"""
Live Interviewer Agent - Manages real-time interview sessions.

This agent handles the complete interview lifecycle:
- Loading generated questions
- Managing session state
- Tracking current question and responses
- Determining next question
- Supporting interview completion

This is a stateful wrapper around the InterviewerAgent that adds
session persistence and live flow management.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from app.database.models.interview_session import (
    InterviewSession,
    InterviewStatus,
    ResponseType,
    InterviewResponse,
)
from app.database.models.interview_question import InterviewQuestion
from app.database.mongodb import mongodb

logger = logging.getLogger(__name__)


class LiveInterviewerAgent:
    """
    Manages live interview sessions with real-time question delivery
    and response tracking.
    """

    def __init__(self):
        """Initialize the Live Interviewer Agent."""
        self.db = None
        self.sessions_collection = None
        self.questions_collection = None
        self.logger = logger

    def _ensure_collections(self):
        """Lazily initialize collections when first needed."""
        if self.db is None:
            self.db = mongodb
            self.sessions_collection = self.db.get_collection("interview_sessions")
            self.questions_collection = self.db.get_collection("interview_questions")

    async def start_interview_session(
        self,
        user_id: str,
        resume_id: Optional[str],
        interview_type: str,
        target_position: str,
        target_company: Optional[str],
        difficulty: str,
        duration_minutes: int,
        questions: List[Dict[str, Any]],
    ) -> InterviewSession:
        """
        Create and initialize a new interview session.

        Args:
            user_id: User starting the interview
            resume_id: Associated resume (optional)
            interview_type: Type of interview (technical, behavioral, etc.)
            target_position: Target position
            target_company: Target company (optional)
            difficulty: Difficulty level
            duration_minutes: Interview duration
            questions: List of generated interview questions

        Returns:
            Created InterviewSession with first question loaded
        """
        self._ensure_collections()
        try:
            # Create session document
            session = InterviewSession(
                user_id=user_id,
                resume_id=resume_id,
                title=f"{interview_type.title()} Interview - {target_position}",
                interview_type=interview_type,
                difficulty_level=difficulty,
                target_position=target_position,
                target_company=target_company,
                duration_minutes=duration_minutes,
                question_count=len(questions),
                status=InterviewStatus.IN_PROGRESS,
                actual_start_time=datetime.utcnow(),
                current_question_index=0,
                ai_model_used="openai/gpt-oss-120b",  # Groq model
                interviewer_agent_version="1.0",
            )

            # Persist questions in session memory for fast access
            session.session_metadata["original_questions"] = [
                {
                    "index": i,
                    "question_id": q.get("_id", f"q_{i}"),
                    "question_text": q.get("question_text", ""),
                    "question_type": q.get("question_type", ""),
                    "difficulty": q.get("difficulty", ""),
                    "category": q.get("category", ""),
                    "key_points": q.get("key_points", []),
                }
                for i, q in enumerate(questions)
            ]

            # Set the first question as current
            if questions:
                first_question = questions[0]
                session.current_question_id = str(first_question.get("_id", "q_0"))
                session.current_question_index = 0

            # Save session to MongoDB
            result = await self.sessions_collection.insert_one(
                session.model_dump(by_alias=True)
            )
            session_id = str(result.inserted_id)

            self.logger.info(
                f"Created interview session {session_id} for user {user_id} "
                f"with {len(questions)} questions"
            )

            return session_id, session, questions[0] if questions else None

        except Exception as e:
            self.logger.error(f"Error creating interview session: {str(e)}")
            raise

    async def get_session(
        self, session_id: str, user_id: str
    ) -> Optional[InterviewSession]:
        """
        Retrieve an interview session.

        Args:
            session_id: Session to retrieve
            user_id: User requesting (for authorization)

        Returns:
            InterviewSession or None if not found or unauthorized
        """
        self._ensure_collections()
        try:
            session_doc = await self.sessions_collection.find_one(
                {"_id": ObjectId(session_id), "user_id": user_id}
            )

            if not session_doc:
                return None

            return InterviewSession(**session_doc)

        except Exception as e:
            self.logger.error(f"Error retrieving session {session_id}: {str(e)}")
            raise

    async def store_response(
        self, session_id: str, user_id: str, question_id: str, answer: str
    ) -> str:
        """
        Store a candidate response to a question.

        Args:
            session_id: Interview session
            user_id: User responding (for authorization)
            question_id: Question being answered
            answer: Candidate's answer text

        Returns:
            response_id of the stored response
        """
        self._ensure_collections()
        try:
            # Get session
            session = await self.get_session(session_id, user_id)
            if not session:
                raise ValueError(f"Session {session_id} not found or unauthorized")

            # Validate session is in progress
            if session.status != InterviewStatus.IN_PROGRESS:
                raise ValueError(
                    f"Cannot submit answer to {session.status.value} interview"
                )

            # Create response object
            response_id = f"resp_{session.total_responses + 1}"
            response = InterviewResponse(
                response_id=response_id,
                question_id=question_id,
                answer=answer,
                submitted_at=datetime.utcnow(),
                sequence_number=session.total_responses + 1,
                response_type=ResponseType.ANSWER,
            )

            # Update session: add response and increment counter
            update_result = await self.sessions_collection.update_one(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {
                    "$push": {"responses": response.model_dump(by_alias=True)},
                    "$inc": {"total_responses": 1},
                },
            )

            if update_result.matched_count == 0:
                raise ValueError(f"Session {session_id} not found")

            self.logger.info(
                f"Stored response {response_id} for session {session_id}, "
                f"question {question_id}"
            )

            return response_id

        except Exception as e:
            self.logger.error(
                f"Error storing response for session {session_id}: {str(e)}"
            )
            raise

    async def get_next_question(
        self, session_id: str, user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the next question in the interview.

        Args:
            session_id: Interview session
            user_id: User requesting (for authorization)

        Returns:
            Next question dict or None if interview is complete
        """
        self._ensure_collections()
        try:
            # Get session
            session = await self.get_session(session_id, user_id)
            if not session:
                raise ValueError(f"Session {session_id} not found or unauthorized")

            # Check if interview is complete
            if session.status != InterviewStatus.IN_PROGRESS:
                return None

            # Get all original questions from session metadata
            original_questions = session.session_metadata.get("original_questions", [])

            # Calculate next index
            next_index = session.current_question_index + 1

            if next_index >= len(original_questions):
                # No more questions
                return None

            # Fetch the next question
            next_question_meta = original_questions[next_index]
            next_question_id = next_question_meta.get("question_id")

            # Try to fetch from MongoDB for full details
            try:
                next_question_doc = await self.questions_collection.find_one(
                    {"_id": ObjectId(next_question_id)}
                )
                if next_question_doc:
                    next_question = next_question_doc
                else:
                    # Fallback to metadata
                    next_question = next_question_meta
            except:
                # Fallback to metadata
                next_question = next_question_meta

            # Update session: move to next question
            updated_session = await self.sessions_collection.find_one_and_update(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {
                    "$set": {
                        "current_question_index": next_index,
                        "current_question_id": next_question_id,
                    },
                    "$push": {"completed_question_ids": session.current_question_id},
                },
                return_document=True,
            )

            if not updated_session:
                raise ValueError(f"Session {session_id} not found")

            self.logger.info(
                f"Advanced session {session_id} to question {next_index}: {next_question_id}"
            )

            return next_question

        except Exception as e:
            self.logger.error(f"Error getting next question for session {session_id}: {str(e)}")
            raise

    async def complete_interview(self, session_id: str, user_id: str) -> InterviewSession:
        """
        Mark an interview as completed.

        Args:
            session_id: Interview session to complete
            user_id: User completing (for authorization)

        Returns:
            Updated InterviewSession
        """
        self._ensure_collections()
        try:
            # Update session status to completed
            updated_session = await self.sessions_collection.find_one_and_update(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {
                    "$set": {
                        "status": InterviewStatus.COMPLETED.value,
                        "end_time": datetime.utcnow(),
                    }
                },
                return_document=True,
            )

            if not updated_session:
                raise ValueError(f"Session {session_id} not found or unauthorized")

            self.logger.info(f"Completed interview session {session_id}")

            return InterviewSession(**updated_session)

        except Exception as e:
            self.logger.error(f"Error completing interview session {session_id}: {str(e)}")
            raise

    async def abandon_interview(self, session_id: str, user_id: str) -> InterviewSession:
        """
        Mark an interview as abandoned.

        Args:
            session_id: Interview session to abandon
            user_id: User abandoning (for authorization)

        Returns:
            Updated InterviewSession
        """
        self._ensure_collections()
        try:
            # Update session status to abandoned
            updated_session = await self.sessions_collection.find_one_and_update(
                {"_id": ObjectId(session_id), "user_id": user_id},
                {
                    "$set": {
                        "status": InterviewStatus.CANCELLED.value,
                        "end_time": datetime.utcnow(),
                    }
                },
                return_document=True,
            )

            if not updated_session:
                raise ValueError(f"Session {session_id} not found or unauthorized")

            self.logger.info(f"Abandoned interview session {session_id}")

            return InterviewSession(**updated_session)

        except Exception as e:
            self.logger.error(f"Error abandoning interview session {session_id}: {str(e)}")
            raise


# Global instance
live_interviewer_agent = LiveInterviewerAgent()

__all__ = ["LiveInterviewerAgent", "live_interviewer_agent"]
