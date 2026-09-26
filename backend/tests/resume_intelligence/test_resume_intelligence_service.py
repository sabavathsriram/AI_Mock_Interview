"""
Unit tests for Resume Intelligence Service
Tests resume analysis with mocked LLM to ensure no real API calls are made.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.resume_intelligence.service import (
    ResumeIntelligenceService,
    ResumeAnalysisError,
    ResumeAnalysisValidationError,
)
from app.resume_intelligence.schemas import (
    ResumeAnalysisResult,
    SkillCategory,
    ExtractedSkill,
    EducationEntry,
    WorkExperienceEntry,
)


# Sample resume text for testing
SAMPLE_RESUME = """
John Doe
john.doe@example.com
+1-234-567-8900
New York, USA

EDUCATION
Bachelor of Science in Computer Science
Stanford University, Stanford, CA
Graduated: May 2020
GPA: 3.8/4.0

TECHNICAL SKILLS
Programming Languages: Python, Java, JavaScript, Go
Frameworks: Flask, FastAPI, React, Django
Databases: MongoDB, PostgreSQL, Redis
Cloud: AWS (EC2, S3, Lambda), Google Cloud
Tools: Git, Docker, Kubernetes, Jenkins

WORK EXPERIENCE
Senior Backend Engineer
Tech Company Inc., New York, NY
June 2022 - Present
- Led development of microservices architecture using FastAPI and Python
- Managed team of 3 engineers
- Improved API response time by 40%
- Technologies: Python, FastAPI, PostgreSQL, Docker, Kubernetes

Backend Engineer
StartUp Inc., San Francisco, CA
January 2021 - May 2022
- Developed RESTful APIs using Django and Flask
- Implemented database optimization strategies
- Technologies: Python, Django, MongoDB, Redis

PROJECTS
E-Commerce Platform
- Built scalable e-commerce backend handling 100k+ users
- Technologies: Python, FastAPI, PostgreSQL, AWS
- GitHub: github.com/johndoe/ecommerce

CERTIFICATIONS
AWS Certified Solutions Architect - Associate (2021)

COMPETITIVE PROGRAMMING
LeetCode: 500+ problems solved, Top 5% rating
"""


@pytest.fixture
def resume_service():
    """Create a resume intelligence service instance."""
    return ResumeIntelligenceService()


@pytest.fixture
def mock_analysis_result():
    """Create a mock analysis result."""
    return ResumeAnalysisResult(
        candidate_name="John Doe",
        email="john.doe@example.com",
        phone="+1-234-567-8900",
        location="New York, USA",
        education=[
            EducationEntry(
                institution="Stanford University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_year=2020,
                cgpa_percentage="3.8/4.0"
            )
        ],
        technical_skills=[
            SkillCategory(
                category="Programming Languages",
                skills=[
                    ExtractedSkill(skill="Python", category="Programming Language", 
                                 evidence="Led development of microservices using Python and FastAPI"),
                    ExtractedSkill(skill="Java", category="Programming Language",
                                 evidence="Mentioned in skills section"),
                ],
                confidence=0.95
            ),
            SkillCategory(
                category="Frameworks",
                skills=[
                    ExtractedSkill(skill="FastAPI", category="Framework",
                                 evidence="Led development of microservices architecture using FastAPI"),
                    ExtractedSkill(skill="Django", category="Framework",
                                 evidence="Developed RESTful APIs using Django and Flask"),
                ],
                confidence=0.92
            ),
        ],
        work_experience=[
            WorkExperienceEntry(
                position="Senior Backend Engineer",
                company="Tech Company Inc.",
                duration="June 2022 - Present",
                description="Led development of microservices architecture",
                skills_used=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"]
            ),
        ],
        projects=[],
        certifications=[],
        hackathons=[],
        competitive_programming=None,
        achievements=["AWS Certified Solutions Architect"],
        experience_level="Mid-level",
        primary_domains=["Backend Development", "Cloud Architecture"],
        secondary_domains=["DevOps"],
        estimated_skill_areas=["Python", "FastAPI", "PostgreSQL"],
        resume_strengths=[
            "Strong technical background with relevant certifications",
            "Demonstrated leadership experience",
        ],
        potential_skill_gaps=[
            "Frontend technologies (React mentioned but no projects)",
            "Machine learning expertise",
        ],
        important_technologies=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        important_projects=["E-Commerce Platform"],
        overall_confidence=0.89,
        analysis_version="1.0"
    )


class TestResumeIntelligenceServiceInitialization:
    """Test service initialization."""
    
    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = ResumeIntelligenceService()
        assert service is not None
        assert service.llm_service is not None


class TestResumeAnalysis:
    """Test resume analysis functionality."""
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_successful_resume_analysis(self, mock_llm_class, resume_service, mock_analysis_result):
        """Test successful resume analysis with valid input."""
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value=mock_analysis_result)
        resume_service.llm_service = mock_llm
        
        # Analyze resume
        result = await resume_service.analyze_resume(SAMPLE_RESUME, resume_id="test-resume-1")
        
        # Verify result
        assert result is not None
        assert result.candidate_name == "John Doe"
        assert result.email == "john.doe@example.com"
        assert len(result.technical_skills) > 0
        assert result.overall_confidence > 0.8
        
        # Verify LLM was called
        mock_llm.generate_structured_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_resume_analysis_empty_text(self, resume_service):
        """Test analysis with empty resume text."""
        with pytest.raises(ResumeAnalysisError) as exc_info:
            await resume_service.analyze_resume("")
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_resume_analysis_whitespace_only(self, resume_service):
        """Test analysis with whitespace-only resume text."""
        with pytest.raises(ResumeAnalysisError) as exc_info:
            await resume_service.analyze_resume("   \n\t  ")
        
        assert "empty" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_resume_analysis_with_missing_optional_fields(
        self, 
        mock_llm_class, 
        resume_service
    ):
        """Test analysis handles missing optional fields gracefully."""
        # Create result with minimal fields
        minimal_result = ResumeAnalysisResult(
            candidate_name="Jane Doe",
            email=None,
            phone=None,
            location=None,
            education=[],
            technical_skills=[],
            work_experience=[],
            internships=[],
            projects=[],
            certifications=[],
            hackathons=[],
            competitive_programming=None,
            achievements=[],
            other_info=None,
            experience_level=None,
            primary_domains=[],
            secondary_domains=[],
            estimated_skill_areas=[],
            resume_strengths=[],
            potential_skill_gaps=[],
            important_technologies=[],
            important_projects=[],
            overall_confidence=0.5,
            analysis_version="1.0"
        )
        
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value=minimal_result)
        resume_service.llm_service = mock_llm
        
        # Analyze resume
        result = await resume_service.analyze_resume(SAMPLE_RESUME)
        
        # Verify it still works with minimal data
        assert result.candidate_name == "Jane Doe"
        assert result.email is None
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_resume_analysis_llm_failure(self, mock_llm_class, resume_service):
        """Test handling of LLM failures."""
        # Mock LLM to raise exception
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(
            side_effect=Exception("LLM service error")
        )
        resume_service.llm_service = mock_llm
        
        # Attempt analysis
        with pytest.raises(ResumeAnalysisError) as exc_info:
            await resume_service.analyze_resume(SAMPLE_RESUME)
        
        assert "analysis failed" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_resume_analysis_validation_error(self, mock_llm_class, resume_service):
        """Test handling of invalid LLM response."""
        # Mock LLM to return invalid type
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value="invalid")
        resume_service.llm_service = mock_llm
        
        # Attempt analysis
        with pytest.raises(ResumeAnalysisError):
            await resume_service.analyze_resume(SAMPLE_RESUME)


class TestResumeAnalysisValidation:
    """Test analysis result validation."""
    
    def test_validate_analysis_result_valid(self, resume_service, mock_analysis_result):
        """Test validation of valid analysis result."""
        result = resume_service.validate_analysis_result(mock_analysis_result)
        assert result is True
    
    def test_validate_analysis_result_empty(self, resume_service):
        """Test validation rejects completely empty analysis."""
        empty_result = ResumeAnalysisResult(
            overall_confidence=0.5,
            analysis_version="1.0"
        )
        
        with pytest.raises(ResumeAnalysisValidationError) as exc_info:
            resume_service.validate_analysis_result(empty_result)
        
        assert "no meaningful data" in str(exc_info.value).lower()
    
    def test_validate_analysis_result_low_confidence(self, resume_service, mock_analysis_result):
        """Test validation logs warning for low confidence."""
        # Set very low confidence
        mock_analysis_result.overall_confidence = 0.2
        
        # Should still be valid but log warning
        result = resume_service.validate_analysis_result(mock_analysis_result)
        assert result is True


class TestAnalysisSummary:
    """Test analysis summary generation."""
    
    def test_get_analysis_summary(self, resume_service, mock_analysis_result):
        """Test generation of analysis summary."""
        summary = resume_service.get_analysis_summary(mock_analysis_result)
        
        # Verify summary contains expected fields
        assert "candidate_name" in summary
        assert "experience_level" in summary
        assert "primary_domains" in summary
        assert "total_skills_extracted" in summary
        assert "overall_confidence" in summary
        
        # Verify values
        assert summary["candidate_name"] == "John Doe"
        assert summary["experience_level"] == "Mid-level"
        assert summary["total_skills_extracted"] > 0


class TestPromptPreparation:
    """Test prompt preparation for LLM."""
    
    def test_prepare_analysis_prompt(self, resume_service):
        """Test prompt is correctly formatted."""
        prompt = resume_service._prepare_analysis_prompt(SAMPLE_RESUME)
        
        # Verify prompt contains resume text
        assert "John Doe" in prompt
        assert SAMPLE_RESUME in prompt
        
        # Verify it's a string
        assert isinstance(prompt, str)
    
    def test_prepare_analysis_prompt_with_special_characters(self, resume_service):
        """Test prompt handles special characters."""
        special_resume = "Resume with special chars: @#$%^&*() \"quotes\" 'apostrophes'"
        
        prompt = resume_service._prepare_analysis_prompt(special_resume)
        assert special_resume in prompt


class TestSystemPrompt:
    """Test system prompt."""
    
    def test_get_system_prompt(self, resume_service):
        """Test system prompt is retrieved correctly."""
        system_prompt = resume_service._get_system_prompt()
        
        # Verify it contains key instructions
        assert "expert" in system_prompt.lower()
        assert "json" in system_prompt.lower()
        assert "never invent" in system_prompt.lower()
        assert isinstance(system_prompt, str)


class TestEdgeCases:
    """Test edge cases."""
    
    @pytest.mark.asyncio
    async def test_resume_analysis_with_resume_id(self, resume_service, mock_analysis_result):
        """Test that resume_id is logged correctly."""
        with patch.object(resume_service, 'llm_service') as mock_llm:
            mock_llm.generate_structured_response = AsyncMock(return_value=mock_analysis_result)
            
            await resume_service.analyze_resume(SAMPLE_RESUME, resume_id="custom-id-123")
            
            # Verify it was called (logging happens internally)
            mock_llm.generate_structured_response.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_resume_analysis_very_long_resume(self, mock_llm_class, resume_service, mock_analysis_result):
        """Test analysis of very long resume text."""
        # Create a very long resume
        long_resume = SAMPLE_RESUME * 10
        
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value=mock_analysis_result)
        resume_service.llm_service = mock_llm
        
        # Should still work
        result = await resume_service.analyze_resume(long_resume)
        assert result is not None
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_resume_analysis_with_unicode_characters(self, mock_llm_class, resume_service, mock_analysis_result):
        """Test analysis with unicode characters."""
        unicode_resume = SAMPLE_RESUME + "\nCertification: 中文 (Chinese), Français (French), Español (Spanish)"
        
        # Mock LLM service
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value=mock_analysis_result)
        resume_service.llm_service = mock_llm
        
        # Should handle unicode
        result = await resume_service.analyze_resume(unicode_resume)
        assert result is not None


class TestLLMIntegration:
    """Test LLM integration points."""
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_llm_called_with_correct_temperature(self, mock_llm_class, resume_service):
        """Test that LLM is called with appropriate temperature for consistency."""
        mock_result = ResumeAnalysisResult(
            overall_confidence=0.8,
            analysis_version="1.0"
        )
        
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value=mock_result)
        resume_service.llm_service = mock_llm
        
        await resume_service.analyze_resume(SAMPLE_RESUME)
        
        # Verify temperature was set to low value for consistency
        call_kwargs = mock_llm.generate_structured_response.call_args[1]
        assert call_kwargs.get("temperature") == 0.3
    
    @pytest.mark.asyncio
    @patch('app.resume_intelligence.service.LLMService')
    async def test_llm_called_with_correct_tokens(self, mock_llm_class, resume_service):
        """Test that LLM is called with appropriate token limit."""
        mock_result = ResumeAnalysisResult(
            overall_confidence=0.8,
            analysis_version="1.0"
        )
        
        mock_llm = AsyncMock()
        mock_llm.generate_structured_response = AsyncMock(return_value=mock_result)
        resume_service.llm_service = mock_llm
        
        await resume_service.analyze_resume(SAMPLE_RESUME)
        
        # Verify max tokens for detailed analysis
        call_kwargs = mock_llm.generate_structured_response.call_args[1]
        assert call_kwargs.get("max_output_tokens") == 4096


__all__ = [
    'test_successful_resume_analysis',
    'test_resume_analysis_empty_text',
    'test_resume_analysis_llm_failure',
    'test_validate_analysis_result_valid',
    'test_get_analysis_summary',
]
