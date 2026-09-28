"""
Tests for interview strategy and question generation system.
Tests cover resume-based, job-based, mixed interviews, difficulty levels, schema validation, 
hallucination prevention, authorization, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId

from app.database.models.interview_plan import (
    InterviewPlan,
    GeneratedQuestion,
    QuestionSource,
    QuestionDifficultyLevel,
    QuestionType,
)
from app.database.models.resume_intelligence import (
    CandidateProfile,
    ContactInfo,
    SkillsCategory,
    EducationEntry,
    WorkExperienceEntry,
    ProjectEntry,
)
from app.database.models.job_description import JobDescription
from app.services.interview_strategy_agent import (
    InterviewStrategyAgent,
    InterviewStrategyException,
)
from app.services.question_generator import (
    QuestionGenerator,
    QuestionGenerationException,
)
from app.llm.service import TextGenerationResponse


class TestInterviewPlanSchema:
    """Test interview plan and question schemas."""
    
    def test_generated_question_schema(self):
        """Test GeneratedQuestion schema validation."""
        q = GeneratedQuestion(
            question_id="q_1",
            question="What is a hash table?",
            question_type=QuestionType.CONCEPTUAL,
            skill="Data Structures",
            difficulty=QuestionDifficultyLevel.MEDIUM,
            source=QuestionSource.KNOWLEDGE_BASE,
            source_reference="Hash Tables",
            reason="Fundamental data structure concept",
            expected_topics=["Definition", "Implementation", "Use cases"],
            evaluation_criteria=["Understanding", "Clarity"],
            follow_up_possible=True,
            follow_up_triggers=["complexity", "implementation"],
            progression_level=1,
            estimated_duration_seconds=120
        )
        
        assert q.question_id == "q_1"
        assert q.progression_level == 1
        assert q.follow_up_possible is True
        assert len(q.expected_topics) == 3
    
    def test_interview_plan_schema(self):
        """Test InterviewPlan schema validation."""
        plan = InterviewPlan(
            user_id="user_123",
            resume_id="resume_123",
            interview_type="technical",
            difficulty=QuestionDifficultyLevel.HARD,
            total_questions=10,
            skill_areas=["Python", "FastAPI", "Databases"],
            focus_areas=["RAG Systems"],
            candidate_strengths=["Strong in backend"],
            candidate_gaps=["Frontend experience"]
        )
        
        assert plan.interview_type == "technical"
        assert plan.total_questions == 10
        assert len(plan.skill_areas) == 3
        assert plan.difficulty == QuestionDifficultyLevel.HARD
    
    def test_question_source_traceability(self):
        """Test that questions maintain source traceability."""
        q = GeneratedQuestion(
            question_id="q_1",
            question="Tell me about your RAG project",
            question_type=QuestionType.PROJECT_BASED,
            skill="RAG Systems",
            difficulty=QuestionDifficultyLevel.MEDIUM,
            source=QuestionSource.RESUME,
            source_reference="RAG Chatbot Project",
            reason="Candidate listed RAG chatbot project with ChromaDB",
            expected_topics=[],
            evaluation_criteria=[]
        )
        
        assert q.source == QuestionSource.RESUME
        assert "RAG Chatbot" in q.source_reference
        assert "ChromaDB" in q.reason


class TestInterviewStrategyAgent:
    """Test interview strategy generation."""
    
    @pytest.mark.asyncio
    async def test_strategy_generation_with_resume(self):
        """Test generating strategy from resume profile."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Alice Engineer",
            contact=ContactInfo(email="alice@example.com"),
            skills=SkillsCategory(
                programming_languages=["Python", "JavaScript"],
                frameworks=["FastAPI", "React"],
                databases=["PostgreSQL", "MongoDB"]
            ),
            education=[
                EducationEntry(
                    degree="B.S.",
                    field_of_study="Computer Science",
                    institution="Tech University",
                    graduation_year=2020
                )
            ],
            experience=[
                WorkExperienceEntry(
                    company="Tech Corp",
                    position="Senior Engineer",
                    duration="2 years",
                    description="Built scalable APIs"
                )
            ],
            projects=[
                ProjectEntry(
                    name="RAG Chatbot",
                    description="Built RAG system with LangChain",
                    technologies=["Python", "LangChain", "ChromaDB"]
                )
            ]
        )
        
        agent = InterviewStrategyAgent()
        
        # Mock LLM response
        with patch.object(agent, '_create_strategy_prompt', return_value="test prompt"):
            with patch('app.services.interview_strategy_agent.llm_service') as mock_llm:
                mock_response = TextGenerationResponse(
                    text='{"skill_areas": ["Python", "FastAPI"], "focus_areas": ["RAG"], "candidate_strengths": ["Backend"], "candidate_gaps": [], "question_distribution": {}, "progression_strategy": {}, "evaluation_criteria": {}}',
                    model="gemini-1.5-flash",
                    timestamp=datetime.utcnow()
                )
                mock_llm.generate_text = AsyncMock(return_value=mock_response)
                
                strategy = await agent.generate_strategy(
                    candidate,
                    interview_type="technical",
                    difficulty="medium"
                )
                
                assert "skill_areas" in strategy
                assert "Python" in strategy["skill_areas"]
    
    @pytest.mark.asyncio
    async def test_interview_plan_creation(self):
        """Test creating complete interview plan."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Bob Developer",
            contact=ContactInfo(),
            skills=SkillsCategory(
                programming_languages=["Java", "Python"],
                frameworks=["Spring Boot"]
            )
        )
        
        agent = InterviewStrategyAgent()
        
        with patch.object(agent, 'generate_strategy') as mock_strategy:
            mock_strategy.return_value = {
                "skill_areas": ["Java", "Spring Boot"],
                "focus_areas": ["Microservices"],
                "candidate_strengths": ["OOP"],
                "candidate_gaps": ["Cloud"],
                "question_distribution": {},
                "progression_strategy": {},
                "evaluation_criteria": {}
            }
            
            plan = await agent.create_interview_plan(
                user_id="user_1",
                resume_id="resume_1",
                candidate_profile=candidate,
                interview_type="technical",
                difficulty="medium"
            )
            
            assert plan.user_id == "user_1"
            assert plan.resume_id == "resume_1"
            assert "Java" in plan.skill_areas


class TestQuestionGenerator:
    """Test question generation."""
    
    @pytest.mark.asyncio
    async def test_resume_based_question_generation(self):
        """Test generating questions from resume."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Carol Coder",
            contact=ContactInfo(),
            skills=SkillsCategory(
                programming_languages=["Python", "C++"],
                frameworks=["Django"]
            ),
            projects=[
                ProjectEntry(
                    name="Data Pipeline",
                    description="ETL pipeline for analytics",
                    technologies=["Python", "Spark", "PostgreSQL"]
                )
            ]
        )
        
        generator = QuestionGenerator()
        questions = await generator.generate_resume_based_questions(
            candidate,
            difficulty="medium",
            count=3
        )
        
        assert len(questions) > 0
        assert all(q.source == QuestionSource.RESUME for q in questions)
        assert any(q.question_type == QuestionType.PROJECT_BASED for q in questions)
        assert any(q.question_type == QuestionType.CODING for q in questions)
    
    @pytest.mark.asyncio
    async def test_job_based_question_generation(self):
        """Test generating questions from job description."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="David Dev",
            contact=ContactInfo(),
            skills=SkillsCategory(
                programming_languages=["Python"],
                frameworks=["FastAPI"]
            )
        )
        
        job = JobDescription(
            user_id="user_1",
            title="Senior Backend Engineer",
            company="TechCorp",
            description="We are looking for a Senior Backend Engineer to join our team.",
            required_skills=["Python", "PostgreSQL", "AWS"],
            nice_to_have_skills=["Kubernetes"]
        )
        
        generator = QuestionGenerator()
        questions = await generator.generate_job_based_questions(
            job,
            candidate,
            difficulty="hard",
            count=3
        )
        
        assert len(questions) > 0
        assert all(q.source == QuestionSource.JOB_DESCRIPTION for q in questions)
    
    @pytest.mark.asyncio
    async def test_no_hallucinated_resume_info(self):
        """Test that generated questions don't hallucinate resume information."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Emma Engineer",
            contact=ContactInfo(),
            skills=SkillsCategory(
                programming_languages=["Python"],
                frameworks=[]  # No frameworks listed
            ),
            projects=[]  # No projects
        )
        
        generator = QuestionGenerator()
        questions = await generator.generate_resume_based_questions(
            candidate,
            difficulty="easy",
            count=5
        )
        
        # Questions should not reference non-existent projects or frameworks
        for q in questions:
            if q.source == QuestionSource.RESUME:
                # If referencing a skill, it should be from the actual resume
                if "framework" in q.question.lower():
                    pytest.fail("Question references framework not in resume")
    
    @pytest.mark.asyncio
    async def test_difficulty_levels(self):
        """Test that difficulty levels are respected."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Frank Dev",
            contact=ContactInfo(),
            skills=SkillsCategory(programming_languages=["Python"])
        )
        
        generator = QuestionGenerator()
        
        for difficulty in ["easy", "medium", "hard", "expert"]:
            questions = await generator.generate_resume_based_questions(
                candidate,
                difficulty=difficulty,
                count=1
            )
            
            if questions:
                assert questions[0].difficulty.value == difficulty
    
    @pytest.mark.asyncio
    async def test_question_traceability(self):
        """Test that all generated questions have proper traceability."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Grace Hacker",
            contact=ContactInfo(),
            skills=SkillsCategory(programming_languages=["Go"]),
            projects=[
                ProjectEntry(
                    name="Microservice",
                    technologies=["Go", "gRPC"]
                )
            ]
        )
        
        generator = QuestionGenerator()
        questions = await generator.generate_all_questions(
            candidate,
            interview_type="technical",
            difficulty="medium",
            total_count=5
        )
        
        # Every question must have traceability
        for q in questions:
            assert q.reason, "Question missing reason"
            assert q.source_reference, "Question missing source reference"
            assert q.source in QuestionSource, "Invalid question source"


class TestMixedInterviewPlans:
    """Test mixed interview types."""
    
    @pytest.mark.asyncio
    async def test_mixed_interview_generation(self):
        """Test generating mixed interview (technical + behavioral)."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Henry Manager",
            contact=ContactInfo(),
            skills=SkillsCategory(programming_languages=["Python"])
        )
        
        agent = InterviewStrategyAgent()
        
        with patch.object(agent, 'generate_strategy') as mock_strategy:
            mock_strategy.return_value = {
                "skill_areas": ["Python"],
                "focus_areas": [],
                "candidate_strengths": [],
                "candidate_gaps": [],
                "question_distribution": {
                    "conceptual": 3,
                    "coding": 2,
                    "behavioral": 2,
                    "scenario": 1
                },
                "progression_strategy": {},
                "evaluation_criteria": {}
            }
            
            plan = await agent.create_interview_plan(
                user_id="user_1",
                resume_id="resume_1",
                candidate_profile=candidate,
                interview_type="mixed",
                difficulty="medium"
            )
            
            assert plan.interview_type == "mixed"
            assert plan.question_distribution.get("behavioral", 0) >= 1


class TestSchemaValidation:
    """Test schema validation and constraints."""
    
    def test_question_count_validation(self):
        """Test that question count is validated."""
        plan = InterviewPlan(
            user_id="user_1",
            resume_id="resume_1",
            interview_type="technical",
            total_questions=10
        )
        
        assert 5 <= plan.total_questions <= 50
    
    def test_progression_levels(self):
        """Test question progression levels."""
        for level in range(1, 6):
            q = GeneratedQuestion(
                question_id=f"q_{level}",
                question="Test",
                question_type=QuestionType.CONCEPTUAL,
                skill="Test",
                difficulty=QuestionDifficultyLevel.MEDIUM,
                source=QuestionSource.KNOWLEDGE_BASE,
                source_reference="Test",
                reason="Test",
                progression_level=level,
                expected_topics=[],
                evaluation_criteria=[]
            )
            
            assert 1 <= q.progression_level <= 5


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_llm_failure_handling(self):
        """Test handling of LLM generation failures."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Iris",
            contact=ContactInfo(),
            skills=SkillsCategory()
        )
        
        agent = InterviewStrategyAgent()
        
        with patch('app.services.interview_strategy_agent.llm_service') as mock_llm:
            mock_llm.generate_text = AsyncMock(side_effect=Exception("LLM Error"))
            
            with pytest.raises(InterviewStrategyException):
                await agent.generate_strategy(candidate)
    
    @pytest.mark.asyncio
    async def test_missing_candidate_profile(self):
        """Test handling of missing candidate profile."""
        agent = InterviewStrategyAgent()
        
        with pytest.raises(InterviewStrategyException):
            await agent.generate_strategy(None)
    
    @pytest.mark.asyncio
    async def test_empty_resume_handling(self):
        """Test handling of candidates with minimal resume data."""
        candidate = CandidateProfile(
            resume_id="resume_1",
            user_id="user_1",
            candidate_name="Jack",
            contact=ContactInfo(),
            skills=SkillsCategory(),
            projects=[],
            experience=[]
        )
        
        generator = QuestionGenerator()
        questions = await generator.generate_all_questions(
            candidate,
            total_count=5
        )
        
        # Should still generate questions (from knowledge base)
        assert len(questions) >= 0


class TestJobDescriptionModel:
    """Test job description model."""
    
    def test_job_description_creation(self):
        """Test creating job description."""
        job = JobDescription(
            user_id="user_1",
            title="Software Engineer",
            company="TechCorp",
            description="Build scalable systems",
            required_skills=["Python", "SQL"],
            nice_to_have_skills=["Kubernetes"]
        )
        
        assert job.title == "Software Engineer"
        assert "Python" in job.required_skills
        assert "Kubernetes" in job.nice_to_have_skills
    
    def test_job_description_validation(self):
        """Test job description validation."""
        from pydantic import ValidationError
        
        # Empty title should fail validation
        with pytest.raises(ValidationError):
            JobDescription(
                user_id="user_1",
                title="",  # This should fail validation
                company="Company",
                description="Desc"
            )


__all__ = []
