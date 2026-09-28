"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB connection and operations."""
    with patch('app.database.mongodb.mongodb') as mock_db:
        mock_collection = AsyncMock()
        mock_db.get_collection.return_value = mock_collection
        mock_db.client = MagicMock()
        yield mock_db


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    with patch('app.services.resume_intelligence_agent.llm_service') as mock_llm:
        mock_llm.configured = True
        mock_llm.model_name = "gemini-1.5-flash"
        mock_llm.generate_text = AsyncMock()
        yield mock_llm


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Email: john.doe@example.com
    Phone: +1-234-567-8900
    Location: San Francisco, CA
    
    EDUCATION
    Bachelor of Technology (B.Tech) in Computer Science
    Stanford University, Palo Alto, CA
    Graduation: May 2020
    CGPA: 3.8/4.0
    
    TECHNICAL SKILLS
    Programming Languages: Python, Java, JavaScript, C++
    Web Frameworks: Django, React, Spring Boot
    Databases: PostgreSQL, MongoDB, MySQL
    Cloud & DevOps: AWS, Docker, Kubernetes
    AI/ML: TensorFlow, PyTorch, Scikit-learn
    
    PROFESSIONAL EXPERIENCE
    
    Senior Software Engineer
    Tech Corporation, San Francisco, CA
    January 2021 - December 2023
    - Designed and implemented microservices architecture for e-commerce platform
    - Led team of 5 engineers in developing REST APIs
    - Reduced API response time by 40% through optimization
    
    Software Engineer
    StartUp Inc, Mountain View, CA
    June 2020 - December 2020
    - Built Python backend for data analytics dashboard
    - Implemented authentication and authorization systems
    - Deployed applications on AWS using Docker and Kubernetes
    
    INTERNSHIP EXPERIENCE
    
    Software Engineering Intern
    Google, Mountain View, CA
    Summer 2019
    - Developed features for Google Cloud Platform console
    - Wrote unit tests and documentation
    - Mentored by senior engineers in software design best practices
    
    PROJECTS
    
    AI Resume Parser
    - Developed machine learning model to parse and extract information from resumes
    - Technologies: Python, TensorFlow, PyTorch, Natural Language Processing
    - GitHub: github.com/johndoe/ai-resume-parser
    
    E-commerce Platform
    - Built full-stack e-commerce application with Django and React
    - Technologies: Django, React, PostgreSQL, AWS
    
    CERTIFICATIONS
    - AWS Certified Solutions Architect - Associate (2021)
    - Google Cloud Certified Associate Cloud Engineer (2020)
    
    ACHIEVEMENTS
    - Employee of the Year at Tech Corporation (2022)
    - Won hackathon competition (2019)
    """


@pytest.fixture
def sample_candidate_profile_json():
    """Sample parsed candidate profile JSON."""
    return {
        "candidate_name": "John Doe",
        "contact": {
            "email": "john.doe@example.com",
            "phone": "+1-234-567-8900",
            "location": "San Francisco, CA"
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
            "programming_languages": ["Python", "Java", "JavaScript", "C++"],
            "frameworks": ["Django", "React", "Spring Boot"],
            "libraries": [],
            "databases": ["PostgreSQL", "MongoDB", "MySQL"],
            "cloud_devops": ["AWS", "Docker", "Kubernetes"],
            "ai_ml": ["TensorFlow", "PyTorch", "Scikit-learn"],
            "other": []
        },
        "projects": [
            {
                "name": "AI Resume Parser",
                "description": "Machine learning model to parse and extract information from resumes",
                "technologies": ["Python", "TensorFlow", "PyTorch", "NLP"],
                "link": "https://github.com/johndoe/ai-resume-parser"
            },
            {
                "name": "E-commerce Platform",
                "description": "Full-stack e-commerce application",
                "technologies": ["Django", "React", "PostgreSQL", "AWS"],
                "link": None
            }
        ],
        "experience": [
            {
                "company": "Tech Corporation",
                "position": "Senior Software Engineer",
                "duration": "2 years",
                "start_year": 2021,
                "end_year": 2023,
                "description": "Designed and implemented microservices architecture",
                "key_achievements": [
                    "Reduced API response time by 40%",
                    "Led team of 5 engineers"
                ]
            },
            {
                "company": "StartUp Inc",
                "position": "Software Engineer",
                "duration": "7 months",
                "start_year": 2020,
                "end_year": 2020,
                "description": "Built Python backend for data analytics dashboard",
                "key_achievements": []
            }
        ],
        "internships": [
            {
                "company": "Google",
                "position": "Software Engineering Intern",
                "duration": "3 months",
                "start_month_year": "Summer 2019",
                "end_month_year": "Summer 2019",
                "description": "Developed features for Google Cloud Platform console",
                "technologies": ["Python", "GCP"]
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect - Associate",
                "issuer": "Amazon Web Services",
                "issue_date": "2021",
                "expiry_date": None,
                "link": None
            },
            {
                "name": "Google Cloud Certified Associate Cloud Engineer",
                "issuer": "Google Cloud",
                "issue_date": "2020",
                "expiry_date": None,
                "link": None
            }
        ],
        "achievements": [
            {
                "title": "Employee of the Year",
                "description": "Awarded at Tech Corporation",
                "date": "2022"
            },
            {
                "title": "Hackathon Winner",
                "description": "Won hackathon competition",
                "date": "2019"
            }
        ],
        "additional_information": []
    }
