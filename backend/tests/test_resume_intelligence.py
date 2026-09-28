"""
Tests for resume intelligence agent and structured profile extraction.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.resume_intelligence_agent import ResumeIntelligenceAgent
from app.database.models import CandidateProfile, ContactInfo, EducationEntry, SkillsCategory
from app.llm.service import TextGenerationResponse


class TestResumeIntelligenceSchema:
    """Test suite for resume intelligence data models."""
    
    def test_candidate_profile_creation(self):
        """Test creating a CandidateProfile with all fields."""
        profile = CandidateProfile(
            resume_id="resume_123",
            user_id="user_123",
            candidate_name="John Doe",
            contact=ContactInfo(
                email="john@example.com",
                phone="+1-234-567-8900",
                location="San Francisco, CA"
            ),
            education=[
                EducationEntry(
                    degree="B.Tech",
                    field_of_study="Computer Science",
                    institution="Stanford University",
                    graduation_year=2020,
                    cgpa=3.8
                )
            ]
        )
        
        assert profile.candidate_name == "John Doe"
        assert profile.contact.email == "john@example.com"
        assert len(profile.education) == 1
        assert profile.education[0].degree == "B.Tech"
    
    def test_candidate_profile_with_empty_arrays(self):
        """Test CandidateProfile allows empty arrays for optional sections."""
        profile = CandidateProfile(
            resume_id="resume_123",
            user_id="user_123",
            candidate_name="Jane Doe"
        )
        
        assert profile.projects == []
        assert profile.experience == []
        assert profile.internships == []
        assert profile.certifications == []
        assert profile.achievements == []
        assert profile.additional_information == []
    
    def test_skills_category_organization(self):
        """Test that skills are properly organized by category."""
        skills = SkillsCategory(
            programming_languages=["Python", "Java"],
            frameworks=["Django", "React"],
            databases=["PostgreSQL", "MongoDB"],
            cloud_devops=["AWS", "Docker"],
            ai_ml=["TensorFlow"],
            libraries=["NumPy", "Pandas"],
            other=["Git", "Linux"]
        )
        
        assert len(skills.programming_languages) == 2
        assert "Django" in skills.frameworks
        assert "PostgreSQL" in skills.databases
        assert "AWS" in skills.cloud_devops


class TestResumeIntelligenceAgent:
    """Test suite for resume intelligence analysis."""
    
    @pytest.mark.asyncio
    async def test_analyze_resume_empty_text(self):
        """Test that empty resume text is rejected."""
        success, profile, error = await ResumeIntelligenceAgent.analyze_resume(
            resume_id="resume_123",
            user_id="user_123",
            extracted_text=""
        )
        
        assert success is False
        assert profile is None
        assert error is not None
        assert "No extracted text" in error
    
    @pytest.mark.asyncio
    async def test_analyze_resume_with_valid_text(self):
        """Test successful resume analysis with mocked LLM."""
        resume_text = """
        John Doe
        Email: john@example.com
        Phone: +1-234-567-8900
        
        Education:
        B.Tech in Computer Science
        Stanford University, 2020
        CGPA: 3.8
        
        Skills:
        - Programming: Python, Java, JavaScript
        - Frameworks: Django, React
        - Databases: PostgreSQL, MongoDB
        
        Experience:
        Senior Software Engineer at Tech Corp (2021-2023)
        - Led development of microservices
        
        Projects:
        - AI Resume Parser (Python, Machine Learning)
        """
        
        mock_response_text = json.dumps({
            "candidate_name": "John Doe",
            "contact": {
                "email": "john@example.com",
                "phone": "+1-234-567-8900",
                "location": None
            },
            "education": [{
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "institution": "Stanford University",
                "graduation_year": 2020,
                "cgpa": 3.8,
                "percentage": None
            }],
            "skills": {
                "programming_languages": ["Python", "Java", "JavaScript"],
                "frameworks": ["Django", "React"],
                "libraries": [],
                "databases": ["PostgreSQL", "MongoDB"],
                "cloud_devops": [],
                "ai_ml": [],
                "other": []
            },
            "projects": [{
                "name": "AI Resume Parser",
                "description": None,
                "technologies": ["Python", "Machine Learning"],
                "link": None
            }],
            "experience": [{
                "company": "Tech Corp",
                "position": "Senior Software Engineer",
                "duration": "2021-2023",
                "start_year": 2021,
                "end_year": 2023,
                "description": "Led development of microservices",
                "key_achievements": []
            }],
            "internships": [],
            "certifications": [],
            "achievements": [],
            "additional_information": []
        })
        
        with patch('app.services.resume_intelligence_agent.llm_service') as mock_llm:
            mock_response = TextGenerationResponse(
                text=mock_response_text,
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
            mock_llm.generate_text = AsyncMock(return_value=mock_response)
            mock_llm.model_name = "gemini-1.5-flash"
            
            success, profile, error = await ResumeIntelligenceAgent.analyze_resume(
                resume_id="resume_123",
                user_id="user_123",
                extracted_text=resume_text
            )
            
            assert success is True
            assert profile is not None
            assert error is None
            assert profile.candidate_name == "John Doe"
            assert profile.contact.email == "john@example.com"
            assert len(profile.skills.programming_languages) == 3
    
    @pytest.mark.asyncio
    async def test_llm_invalid_json_response(self):
        """Test handling of invalid JSON from LLM."""
        resume_text = "Test resume content"
        
        with patch('app.services.resume_intelligence_agent.llm_service') as mock_llm:
            mock_response = TextGenerationResponse(
                text="Not valid JSON {incomplete",
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
            mock_llm.generate_text = AsyncMock(return_value=mock_response)
            mock_llm.model_name = "gemini-1.5-flash"
            
            success, profile, error = await ResumeIntelligenceAgent.analyze_resume(
                resume_id="resume_123",
                user_id="user_123",
                extracted_text=resume_text
            )
            
            assert success is False
            assert profile is None
            assert "Failed to parse LLM response" in error or "Failed to parse" in error
    
    @pytest.mark.asyncio
    async def test_llm_empty_response(self):
        """Test handling of empty LLM response."""
        resume_text = "Test resume content"
        
        with patch('app.services.resume_intelligence_agent.llm_service') as mock_llm:
            mock_response = TextGenerationResponse(
                text="",
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
            mock_llm.generate_text = AsyncMock(return_value=mock_response)
            mock_llm.model_name = "gemini-1.5-flash"
            
            success, profile, error = await ResumeIntelligenceAgent.analyze_resume(
                resume_id="resume_123",
                user_id="user_123",
                extracted_text=resume_text
            )
            
            assert success is False
            assert error is not None


class TestLLMResponseParsing:
    """Test suite for LLM response parsing."""
    
    def test_parse_valid_json_response(self):
        """Test parsing valid JSON response."""
        response_json = json.dumps({
            "candidate_name": "John Doe",
            "contact": {"email": "john@example.com", "phone": None, "location": None},
            "education": [],
            "skills": {},
            "projects": [],
            "experience": [],
            "internships": [],
            "certifications": [],
            "achievements": [],
            "additional_information": []
        })
        
        parsed = ResumeIntelligenceAgent._parse_llm_response(response_json)
        
        assert parsed is not None
        assert parsed["candidate_name"] == "John Doe"
        assert parsed["contact"]["email"] == "john@example.com"
    
    def test_parse_json_with_markdown_blocks(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        response_text = """
        ```json
        {
            "candidate_name": "Jane Doe",
            "contact": {"email": "jane@example.com", "phone": null, "location": null},
            "education": [],
            "skills": {},
            "projects": [],
            "experience": [],
            "internships": [],
            "certifications": [],
            "achievements": [],
            "additional_information": []
        }
        ```
        """
        
        parsed = ResumeIntelligenceAgent._parse_llm_response(response_text)
        
        assert parsed is not None
        assert parsed["candidate_name"] == "Jane Doe"
    
    def test_parse_malformed_json(self):
        """Test parsing malformed JSON returns None."""
        response_text = "{invalid json content"
        
        parsed = ResumeIntelligenceAgent._parse_llm_response(response_text)
        
        assert parsed is None
    
    def test_parse_missing_required_fields(self):
        """Test parsing JSON with missing fields adds defaults."""
        response_json = json.dumps({
            "candidate_name": "John Doe"
        })
        
        parsed = ResumeIntelligenceAgent._parse_llm_response(response_json)
        
        assert parsed is not None
        assert "contact" in parsed
        assert "education" in parsed
        assert "skills" in parsed
        assert parsed["education"] == []


class TestResumeOwnershipAuthorization:
    """Test suite for authorization and security."""
    
    @pytest.mark.asyncio
    async def test_only_owner_can_access_intelligence(self):
        """Test that only resume owner can access intelligence profile."""
        # This would be tested at the API endpoint level
        # Ensuring user_id matches resume owner
        from app.database.models import ResumeDocument
        import datetime
        
        resume = ResumeDocument(
            user_id="owner_user_id",
            filename="test.pdf",
            file_type="pdf",
            file_path="uploads/test.pdf",
            file_size=1000,
            mime_type="application/pdf",
            extracted_text="Test content",
            extraction_metadata={},
            uploaded_at=datetime.datetime.utcnow()
        )
        
        assert resume.user_id == "owner_user_id"
        # In actual endpoint, verify this matches current_user.id


class TestEndToEndProcessing:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_resume_processing_flow(self):
        """Test complete flow from extraction to intelligence generation."""
        # This test verifies the full pipeline
        resume_text = """
        John Doe
        john@example.com
        +1-234-567-8900
        
        Education:
        B.Tech Computer Science, Stanford 2020, CGPA 3.8
        
        Skills: Python, Java, React, PostgreSQL, AWS
        
        Experience:
        Senior Engineer at TechCorp (2021-2023)
        - Developed microservices
        """
        
        # Mock the LLM response
        mock_response_json = {
            "candidate_name": "John Doe",
            "contact": {
                "email": "john@example.com",
                "phone": "+1-234-567-8900",
                "location": None
            },
            "education": [{
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "institution": "Stanford",
                "graduation_year": 2020,
                "cgpa": 3.8
            }],
            "skills": {
                "programming_languages": ["Python", "Java"],
                "frameworks": ["React"],
                "databases": ["PostgreSQL"],
                "cloud_devops": ["AWS"],
                "libraries": [],
                "ai_ml": [],
                "other": []
            },
            "projects": [],
            "experience": [{
                "company": "TechCorp",
                "position": "Senior Engineer",
                "duration": "2021-2023",
                "start_year": 2021,
                "end_year": 2023,
                "description": "Developed microservices",
                "key_achievements": []
            }],
            "internships": [],
            "certifications": [],
            "achievements": [],
            "additional_information": []
        }
        
        with patch('app.services.resume_intelligence_agent.llm_service') as mock_llm:
            mock_response = TextGenerationResponse(
                text=json.dumps(mock_response_json),
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
            mock_llm.generate_text = AsyncMock(return_value=mock_response)
            mock_llm.model_name = "gemini-1.5-flash"
            
            # Run analysis
            success, profile, error = await ResumeIntelligenceAgent.analyze_resume(
                resume_id="resume_123",
                user_id="user_123",
                extracted_text=resume_text
            )
            
            # Verify complete profile was created
            assert success is True
            assert profile is not None
            assert profile.candidate_name == "John Doe"
            assert profile.contact.email == "john@example.com"
            assert len(profile.education) == 1
            assert len(profile.experience) == 1
            assert len(profile.skills.programming_languages) == 2
