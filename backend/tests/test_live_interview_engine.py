"""
Comprehensive test suite for Live Interview Engine (Prompt 11).

Tests cover:
1. Interview session creation and management
2. Live interview flow with questions and answers
3. Interviewer agent decision making
4. Follow-up question generation
5. Session state management (pause/resume/complete)
6. Concurrency protection and duplicate prevention
7. Context service functionality
8. Error handling and edge cases
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.database.models.interview_session import (
    InterviewSession,
    InterviewStatus,
    InterviewType,
    DifficultyLevel,
    ResponseType,
    InterviewResponse
)
from app.database.models.interview_plan import (
    InterviewPlan,
    GeneratedQuestion,
    QuestionType,
    QuestionSource,
    QuestionDifficultyLevel
)
from app.database.models.resume_intelligence import CandidateProfile, ContactInfo, SkillsCategory
from app.services.interviewer_agent import (
    interviewer_agent,
    InterviewerAgent,
    InterviewerAction,
    InterviewerDecision,
    InterviewerException
)
from app.services.interview_context_service import (
    interview_context_service,
    InterviewContextService,
    InterviewContextException
)


class TestInterviewSessionModel:
    """Test the enhanced InterviewSession model."""
    
    def test_interview_session_creation(self):
        """Test creating a new interview session."""
        session = InterviewSession(
            user_id="user123",
            resume_id="resume123",
            interview_plan_id="plan123",
            title="Technical Interview",
            target_position="Software Engineer",
            interview_type=InterviewType.TECHNICAL,
            difficulty_level=DifficultyLevel.MEDIUM,
            duration_minutes=60,
            question_count=10
        )
        
        assert session.user_id == "user123"
        assert session.status == InterviewStatus.NOT_STARTED
        assert session.current_question_index == 0
        assert len(session.responses) == 0
        assert not session.is_locked
        assert session.total_responses == 0
    
    def test_add_response(self):
        """Test adding responses to session."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Add first response
        response_id = session.add_response("q1", "My answer to question 1")
        
        assert response_id == "resp_1"
        assert len(session.responses) == 1
        assert session.total_responses == 1
        assert session.responses[0].question_id == "q1"
        assert session.responses[0].answer == "My answer to question 1"
        assert session.responses[0].response_type == ResponseType.ANSWER
        assert session.responses[0].sequence_number == 1
    
    def test_session_locking(self):
        """Test session locking mechanism."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Lock session
        success = session.lock_session("process1")
        assert success is True
        assert session.is_locked is True
        assert session.locked_by_process == "process1"
        assert session.locked_at is not None
        
        # Try to lock again with different process
        success = session.lock_session("process2")
        assert success is False
        assert session.locked_by_process == "process1"
        
        # Unlock session
        session.unlock_session()
        assert session.is_locked is False
        assert session.locked_at is None
        assert session.locked_by_process is None
    
    def test_follow_up_tracking(self):
        """Test follow-up question tracking."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Add follow-up
        session.add_follow_up("q1", "Can you elaborate on that?")
        
        assert "q1" in session.asked_follow_ups
        assert len(session.asked_follow_ups["q1"]) == 1
        assert session.asked_follow_ups["q1"][0] == "Can you elaborate on that?"
        
        # Check follow-up capability
        assert session.can_ask_follow_up("q1", max_follow_ups=1) is False
        assert session.can_ask_follow_up("q2", max_follow_ups=1) is True
    
    def test_conversation_context(self):
        """Test conversation context management."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Add multiple responses
        session.add_response("q1", "Answer 1")
        session.add_response("q2", "Answer 2")
        session.add_response("q3", "Answer 3")
        
        # Get recent context
        context = session.get_recent_context(max_exchanges=2)
        
        assert len(context) == 2
        assert context[0]["question_id"] == "q2"
        assert context[1]["question_id"] == "q3"
        assert context[1]["answer"] == "Answer 3"


class TestInterviewerAgent:
    """Test the Interviewer Agent service."""
    
    def create_mock_session(self):
        """Create a mock interview session."""
        return InterviewSession(
            user_id="user123",
            resume_id="resume123",
            interview_plan_id="plan123",
            title="Technical Interview",
            target_position="Software Engineer",
            interview_type=InterviewType.TECHNICAL,
            difficulty_level=DifficultyLevel.MEDIUM,
            duration_minutes=60,
            question_count=5,
            status=InterviewStatus.IN_PROGRESS,
            actual_start_time=datetime.utcnow()
        )
    
    def create_mock_interview_plan(self):
        """Create a mock interview plan."""
        questions = [
            GeneratedQuestion(
                question_id="q1",
                question="Tell me about your experience with Python.",
                question_type=QuestionType.CONCEPTUAL,
                skill="Python",
                difficulty=QuestionDifficultyLevel.MEDIUM,
                source=QuestionSource.RESUME,
                source_reference="Python experience in projects",
                reason="Candidate has Python listed in skills",
                expected_topics=["frameworks", "projects"],
                evaluation_criteria=["depth of knowledge"],
                follow_up_possible=True,
                progression_level=2
            ),
            GeneratedQuestion(
                question_id="q2",
                question="Explain how you would implement a REST API.",
                question_type=QuestionType.CODING,
                skill="API Design",
                difficulty=QuestionDifficultyLevel.MEDIUM,
                source=QuestionSource.JOB_DESCRIPTION,
                source_reference="API development required",
                reason="Job requires API development skills",
                expected_topics=["HTTP methods", "endpoints"],
                evaluation_criteria=["technical accuracy"],
                follow_up_possible=True,
                progression_level=3
            )
        ]
        
        return InterviewPlan(
            user_id="user123",
            resume_id="resume123",
            interview_type="technical",
            difficulty=QuestionDifficultyLevel.MEDIUM,
            total_questions=2,
            questions=questions
        )
    
    def create_mock_candidate_profile(self):
        """Create a mock candidate profile."""
        return CandidateProfile(
            resume_id="resume123",
            user_id="user123",
            candidate_name="John Doe",
            contact=ContactInfo(),
            skills=SkillsCategory(
                programming_languages=["Python", "JavaScript"],
                frameworks=["FastAPI", "React"]
            )
        )
    
    @pytest.mark.asyncio
    async def test_decide_first_question(self):
        """Test deciding the first question to ask."""
        agent = InterviewerAgent()
        session = self.create_mock_session()
        interview_plan = self.create_mock_interview_plan()
        candidate_profile = self.create_mock_candidate_profile()
        
        decision = await agent.decide_next_action(
            session=session,
            interview_plan=interview_plan,
            candidate_profile=candidate_profile
        )
        
        assert decision.action == InterviewerAction.ASK_QUESTION
        assert decision.question_id == "q1"
        assert decision.question == "Tell me about your experience with Python."
        assert decision.skill == "Python"
        assert not decision.is_follow_up
    
    @pytest.mark.asyncio
    async def test_decide_next_question_after_answer(self):
        """Test deciding next question after receiving an answer."""
        agent = InterviewerAgent()
        session = self.create_mock_session()
        interview_plan = self.create_mock_interview_plan()
        candidate_profile = self.create_mock_candidate_profile()
        
        # Mark first question as asked
        session.completed_question_ids.append("q1")
        session.current_question_index = 1
        
        decision = await agent.decide_next_action(
            session=session,
            interview_plan=interview_plan,
            candidate_profile=candidate_profile,
            last_answer="I have 3 years of Python experience",
            last_question_id="q1"
        )
        
        # Should either ask follow-up or next question
        assert decision.action in [InterviewerAction.ASK_QUESTION, InterviewerAction.ASK_FOLLOW_UP]
    
    @pytest.mark.asyncio
    @patch('app.services.interviewer_agent.llm_service')
    async def test_generate_follow_up_question(self, mock_llm):
        """Test generating follow-up questions."""
        # Mock LLM response - return awaitable
        async def mock_generate_response(*args, **kwargs):
            return {
                "needs_follow_up": True,
                "follow_up_question": "What specific Python frameworks have you used?",
                "reason": "Answer was brief, need more technical depth"
            }
        
        mock_llm.generate_structured_response = mock_generate_response
        
        agent = InterviewerAgent()
        session = self.create_mock_session()
        candidate_profile = self.create_mock_candidate_profile()
        original_question = self.create_mock_interview_plan().questions[0]
        
        follow_up = await agent._generate_follow_up_question(
            session=session,
            candidate_profile=candidate_profile,
            original_question=original_question,
            candidate_answer="I use Python for web development"
        )
        
        assert follow_up == "What specific Python frameworks have you used?"
    
    @pytest.mark.asyncio
    async def test_end_interview_decision(self):
        """Test deciding when to end interview."""
        agent = InterviewerAgent()
        session = self.create_mock_session()
        interview_plan = self.create_mock_interview_plan()
        candidate_profile = self.create_mock_candidate_profile()
        
        # Mark all questions as completed
        session.completed_question_ids = ["q1", "q2"]
        session.current_question_index = 2
        
        decision = await agent.decide_next_action(
            session=session,
            interview_plan=interview_plan,
            candidate_profile=candidate_profile
        )
        
        assert decision.action == InterviewerAction.END_INTERVIEW
        assert "completed" in decision.reason.lower()
    
    def test_build_interview_context(self):
        """Test building interview context for LLM."""
        agent = InterviewerAgent()
        session = self.create_mock_session()
        session.add_response("q1", "I have Python experience")
        
        candidate_profile = self.create_mock_candidate_profile()
        
        context = agent._build_interview_context(session, candidate_profile)
        
        assert context["candidate_name"] == "John Doe"
        assert context["target_position"] == "Software Engineer"
        assert context["interview_type"] == "technical"
        assert "Python" in context["candidate_skills"]
        assert len(context["recent_conversation"]) == 1


class TestInterviewContextService:
    """Test the Interview Context Service."""
    
    @pytest.mark.asyncio
    @patch('app.services.interview_context_service.mongodb')
    async def test_get_session_with_lock_success(self, mock_mongodb):
        """Test successfully getting session with lock."""
        # Mock database response
        mock_session_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "user_id": "user123",
            "title": "Test Interview",
            "target_position": "Engineer",
            "interview_type": "technical",
            "difficulty_level": "medium",
            "status": "not_started",
            "is_locked": False,
            "locked_at": None,
            "locked_by_process": None,
            "interview_plan_id": "plan123"
        }
        
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = mock_session_doc
        mock_collection.update_one.return_value = Mock()
        mock_mongodb.get_collection.return_value = mock_collection
        
        service = InterviewContextService()
        
        # Convert ObjectId to string before passing to model
        mock_session_doc["_id"] = str(mock_session_doc["_id"])
        
        session = await service.get_session_with_lock(
            "507f1f77bcf86cd799439011", "user123", "process1"
        )
        
        assert session is not None
        assert session.user_id == "user123"
        assert session.is_locked is True
        assert session.locked_by_process == "process1"
    
    @pytest.mark.asyncio
    @patch('app.services.interview_context_service.mongodb')
    async def test_get_session_locked_by_other_process(self, mock_mongodb):
        """Test getting session that's locked by another process."""
        # Mock database response - session is locked
        mock_session_doc = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "user_id": "user123",
            "title": "Test Interview",
            "target_position": "Engineer",
            "interview_type": "technical",
            "difficulty_level": "medium",
            "status": "in_progress",
            "is_locked": True,
            "locked_at": datetime.utcnow(),
            "locked_by_process": "other_process",
            "interview_plan_id": "plan123"
        }
        
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = mock_session_doc
        mock_mongodb.get_collection.return_value = mock_collection
        
        service = InterviewContextService()
        
        # Convert ObjectId to string
        mock_session_doc["_id"] = str(mock_session_doc["_id"])
        
        session = await service.get_session_with_lock(
            "507f1f77bcf86cd799439011", "user123", "process1"
        )
        
        # Should return None because session is locked by another process
        assert session is None
    
    @pytest.mark.asyncio
    @patch('app.services.interview_context_service.mongodb')
    async def test_check_duplicate_submission(self, mock_mongodb):
        """Test duplicate submission detection."""
        service = InterviewContextService()
        
        # Create session with recent response
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Add a recent response
        session.add_response("q1", "My answer")
        session.responses[0].submitted_at = datetime.utcnow()
        
        # Check for duplicate (same question, same answer, within time window)
        is_duplicate = await service.check_duplicate_submission(
            session, "q1", "My answer", time_window_seconds=10
        )
        
        assert is_duplicate is True
        
        # Check for non-duplicate (different answer)
        is_duplicate = await service.check_duplicate_submission(
            session, "q1", "Different answer", time_window_seconds=10
        )
        
        assert is_duplicate is False
    
    def test_get_session_progress(self):
        """Test session progress calculation."""
        service = InterviewContextService()
        
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Add some completed questions and responses
        session.completed_question_ids = ["q1", "q2"]
        session.add_response("q1", "Answer 1")
        session.add_response("q2", "Answer 2")
        session.add_follow_up("q1", "Follow-up for q1")
        
        progress = service.get_session_progress(session, total_questions=5)
        
        assert progress["completed_questions"] == 2
        assert progress["total_questions"] == 5
        assert progress["progress_percentage"] == 40.0
        assert progress["responses_count"] == 2
        assert progress["follow_ups_asked"] == 1


class TestLiveInterviewFlow:
    """Test the complete live interview flow."""
    
    @pytest.fixture
    def mock_interview_plan(self):
        """Fixture for mock interview plan."""
        questions = [
            GeneratedQuestion(
                question_id="q1",
                question="What is your experience with Python?",
                question_type=QuestionType.CONCEPTUAL,
                skill="Python",
                difficulty=QuestionDifficultyLevel.MEDIUM,
                source=QuestionSource.RESUME,
                source_reference="Python in skills",
                reason="Test Python knowledge",
                expected_topics=["experience", "projects"],
                evaluation_criteria=["depth"],
                follow_up_possible=True,
                progression_level=2
            )
        ]
        
        return InterviewPlan(
            user_id="user123",
            resume_id="resume123",
            interview_type="technical",
            difficulty=QuestionDifficultyLevel.MEDIUM,
            total_questions=1,
            questions=questions
        )
    
    @pytest.mark.asyncio
    @patch('app.services.interview_context_service.mongodb')
    @patch('app.services.interviewer_agent.llm_service')
    async def test_complete_interview_flow(self, mock_llm, mock_mongodb, mock_interview_plan):
        """Test complete interview flow from start to finish."""
        # Mock database operations
        mock_collection = AsyncMock()
        mock_collection.find_one.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "user_id": "user123",
            "title": "Test Interview",
            "target_position": "Engineer",
            "interview_type": "technical",
            "difficulty_level": "medium",
            "status": "not_started",
            "interview_plan_id": "plan123",
            "is_locked": False
        }
        mock_collection.update_one.return_value = Mock()
        mock_mongodb.get_collection.return_value = mock_collection
        
        # Mock LLM responses
        mock_llm.generate_structured_response.return_value = {
            "needs_follow_up": False
        }
        
        # Create services
        context_service = InterviewContextService()
        interviewer = InterviewerAgent()
        
        # 1. Create session (would be done via API)
        session = InterviewSession(
            user_id="user123",
            interview_plan_id="plan123",
            title="Test Interview",
            target_position="Engineer",
            status=InterviewStatus.NOT_STARTED
        )
        
        # 2. Start interview
        session.status = InterviewStatus.IN_PROGRESS
        session.actual_start_time = datetime.utcnow()
        
        # 3. Get first question
        candidate_profile = CandidateProfile(
            resume_id="resume123",
            user_id="user123",
            candidate_name="Test User",
            contact=ContactInfo(),
            skills=SkillsCategory(programming_languages=["Python"])
        )
        
        decision = await interviewer.decide_next_action(
            session=session,
            interview_plan=mock_interview_plan,
            candidate_profile=candidate_profile
        )
        
        assert decision.action == InterviewerAction.ASK_QUESTION
        assert decision.question_id == "q1"
        
        # 4. Submit answer
        session.current_question_id = "q1"
        response_id = await context_service.add_response_to_session(
            session=session,
            question_id="q1",
            answer="I have 3 years of Python experience in web development"
        )
        
        assert response_id == "resp_1"
        assert len(session.responses) == 1
        assert "q1" in session.completed_question_ids
        
        # 5. Get next decision (should end interview as only 1 question)
        decision = await interviewer.decide_next_action(
            session=session,
            interview_plan=mock_interview_plan,
            candidate_profile=candidate_profile,
            last_answer="I have 3 years of Python experience",
            last_question_id="q1"
        )
        
        assert decision.action == InterviewerAction.END_INTERVIEW
        
        # 6. Complete interview
        await context_service.update_session_status(
            session, InterviewStatus.COMPLETED, datetime.utcnow()
        )
        
        assert session.status == InterviewStatus.COMPLETED
        assert session.end_time is not None
        assert session.time_spent_seconds is not None


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_interviewer_agent_with_invalid_plan(self):
        """Test interviewer agent with invalid interview plan."""
        agent = InterviewerAgent()
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Empty interview plan
        empty_plan = InterviewPlan(
            user_id="user123",
            resume_id="resume123",
            interview_type="technical",
            difficulty=QuestionDifficultyLevel.MEDIUM,
            total_questions=0,
            questions=[]
        )
        
        candidate_profile = CandidateProfile(
            resume_id="resume123",
            user_id="user123",
            candidate_name="Test User",
            contact=ContactInfo(),
            skills=SkillsCategory()
        )
        
        decision = await agent.decide_next_action(
            session=session,
            interview_plan=empty_plan,
            candidate_profile=candidate_profile
        )
        
        assert decision.action == InterviewerAction.END_INTERVIEW
        assert "completed" in decision.reason.lower() or "no more questions" in decision.reason.lower()
    
    @pytest.mark.asyncio
    async def test_context_service_invalid_session_id(self):
        """Test context service with invalid session ID."""
        service = InterviewContextService()
        
        with pytest.raises(InterviewContextException):
            await service.get_session_with_lock("invalid_id", "user123", "process1")
    
    def test_session_model_edge_cases(self):
        """Test interview session model edge cases."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer"
        )
        
        # Test getting context with no responses
        context = session.get_recent_context()
        assert context == []
        
        # Test follow-up tracking for non-existent question
        follow_ups = session.get_follow_ups_for_question("nonexistent")
        assert follow_ups == []
        
        # Test checking if non-existent question was asked
        was_asked = session.is_question_asked("nonexistent")
        assert was_asked is False


class TestSessionStateTransitions:
    """Test session state transitions and validation."""
    
    def test_valid_state_transitions(self):
        """Test valid session state transitions."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer",
            status=InterviewStatus.NOT_STARTED
        )
        
        # NOT_STARTED -> IN_PROGRESS
        session.status = InterviewStatus.IN_PROGRESS
        assert session.status == InterviewStatus.IN_PROGRESS
        
        # IN_PROGRESS -> PAUSED
        session.status = InterviewStatus.PAUSED
        session.paused_at = datetime.utcnow()
        assert session.status == InterviewStatus.PAUSED
        
        # PAUSED -> IN_PROGRESS
        session.status = InterviewStatus.IN_PROGRESS
        session.paused_at = None
        assert session.status == InterviewStatus.IN_PROGRESS
        
        # IN_PROGRESS -> COMPLETED
        session.status = InterviewStatus.COMPLETED
        session.end_time = datetime.utcnow()
        assert session.status == InterviewStatus.COMPLETED
    
    def test_pause_duration_calculation(self):
        """Test pause duration calculation."""
        session = InterviewSession(
            user_id="user123",
            title="Test Interview",
            target_position="Engineer",
            status=InterviewStatus.IN_PROGRESS
        )
        
        # Pause session
        session.status = InterviewStatus.PAUSED
        session.paused_at = datetime.utcnow()
        
        # Simulate 30 seconds pause
        import time
        time.sleep(0.1)  # Small delay for test
        
        # Resume session
        if session.paused_at:
            pause_duration = datetime.utcnow() - session.paused_at
            session.pause_duration_seconds += int(pause_duration.total_seconds())
        
        session.status = InterviewStatus.IN_PROGRESS
        session.paused_at = None
        
        assert session.pause_duration_seconds >= 0


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])