"""
Prompt Management Module
Centralized management of LLM prompts to avoid scattering them throughout the application
"""

from typing import Dict, Optional
from enum import Enum


class PromptType(str, Enum):
    """Types of prompts available in the system."""
    TEST = "test"
    RESUME_ANALYSIS = "resume_analysis"
    JOB_DESCRIPTION_ANALYSIS = "job_description_analysis"
    INTERVIEW_QUESTION_GENERATION = "interview_question_generation"
    ANSWER_EVALUATION = "answer_evaluation"
    SKILL_GAP_DETECTION = "skill_gap_detection"
    LEARNING_RECOMMENDATION = "learning_recommendation"
    FEEDBACK_GENERATION = "feedback_generation"


class PromptTemplate:
    """Base class for prompt templates."""
    
    def __init__(self, name: str, system_prompt: str, user_prompt_template: str):
        """
        Initialize prompt template.
        
        Args:
            name: Template name
            system_prompt: System-level instructions for the LLM
            user_prompt_template: Template for user prompt with placeholders
        """
        self.name = name
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
    
    def format_user_prompt(self, **kwargs) -> str:
        """Format user prompt with provided variables."""
        try:
            return self.user_prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required placeholder: {e}")
    
    def to_dict(self) -> dict:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "user_prompt_template": self.user_prompt_template,
        }


class PromptLibrary:
    """Library of all system prompts."""
    
    def __init__(self):
        """Initialize prompt library with all templates."""
        self.templates: Dict[PromptType, PromptTemplate] = {}
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize all prompt templates."""
        
        # Test Prompt
        self.templates[PromptType.TEST] = PromptTemplate(
            name="Test Prompt",
            system_prompt=(
                "You are a helpful AI assistant for the AI-Powered Mock Interview System. "
                "Respond clearly and concisely."
            ),
            user_prompt_template=(
                "Hello! I'm testing the LLM integration for the AI-Powered Mock Interview System. "
                "Please respond with a brief greeting and confirm that you are working correctly.\n\n"
                "Test Parameters:\n"
                "- Model: {model}\n"
                "- Timestamp: {timestamp}"
            )
        )
        
        # Resume Analysis - MUST produce valid JSON
        self.templates[PromptType.RESUME_ANALYSIS] = PromptTemplate(
            name="Resume Analysis",
            system_prompt=(
                "You are an expert HR professional and career coach. Your task is to analyze resumes "
                "and extract structured information. IMPORTANT: You MUST return ONLY valid JSON that can be "
                "parsed. Do NOT include any text before or after the JSON. Do NOT invent information that is "
                "not in the resume. If information is missing, use null or empty lists. Each extracted skill "
                "must have evidence (where it was mentioned in the resume)."
            ),
            user_prompt_template=(
                "Analyze this resume and extract structured information. Return ONLY valid JSON "
                "(no additional text):\n\n"
                "Resume Content:\n{resume_text}\n\n"
                "Extract and return a JSON object with these fields:\n"
                "- candidate_name (null if not found)\n"
                "- email (null if not found)\n"
                "- phone (null if not found)\n"
                "- location (null if not found)\n"
                "- education: array of {{institution, degree, field_of_study, graduation_year, cgpa_percentage}}\n"
                "- technical_skills: array of {{category, skills: array of {{skill, category, evidence}}, confidence: 0-1}}\n"
                "- work_experience: array of {{position, company, duration, description, skills_used}}\n"
                "- internships: array of {{position, company, duration, description, skills_used}}\n"
                "- projects: array of {{name, description, technologies, link}}\n"
                "- certifications: array of {{name, issuer, year}}\n"
                "- hackathons: array of {{name, year, achievement}}\n"
                "- competitive_programming: {{platform, handle, stats}} or null\n"
                "- achievements: array of strings\n"
                "- other_info: string or null\n"
                "- experience_level: string (Entry-level/Mid-level/Senior) or null\n"
                "- primary_domains: array of strings\n"
                "- secondary_domains: array of strings\n"
                "- estimated_skill_areas: array of strings\n"
                "- resume_strengths: array of strings\n"
                "- potential_skill_gaps: array of strings\n"
                "- important_technologies: array of strings (top 10)\n"
                "- important_projects: array of strings\n"
                "- overall_confidence: float 0-1\n"
                "- analysis_version: '1.0'\n\n"
                "CRITICAL: Return ONLY the JSON object, nothing else. Ensure all strings are properly escaped."
            )
        )
        
        # Job Description Analysis Placeholder
        self.templates[PromptType.JOB_DESCRIPTION_ANALYSIS] = PromptTemplate(
            name="Job Description Analysis",
            system_prompt=(
                "You are an expert recruiter and job market analyst. Analyze job descriptions "
                "to extract key requirements, skills, and competencies."
            ),
            user_prompt_template=(
                "Please analyze the following job description and extract:\n\n"
                "Job Description:\n{job_description}\n\n"
                "Please structure your analysis to include:\n"
                "1. Required skills\n"
                "2. Preferred qualifications\n"
                "3. Key responsibilities\n"
                "4. Experience level required\n"
                "5. Compensation range (if mentioned)"
            )
        )
        
        # Interview Question Generation Placeholder
        self.templates[PromptType.INTERVIEW_QUESTION_GENERATION] = PromptTemplate(
            name="Interview Question Generation",
            system_prompt=(
                "You are an experienced interview conductor. Generate thoughtful, relevant "
                "interview questions that assess skills, experience, and cultural fit."
            ),
            user_prompt_template=(
                "Generate {num_questions} interview questions for the following role:\n\n"
                "Position: {position}\n"
                "Experience Level: {experience_level}\n"
                "Key Skills Required: {key_skills}\n\n"
                "Question Type: {question_type}\n"
                "Industry: {industry}\n\n"
                "Please provide questions that are:\n"
                "1. Relevant to the role\n"
                "2. Behavioral or technical as appropriate\n"
                "3. Open-ended to encourage detailed responses"
            )
        )
        
        # Answer Evaluation Placeholder
        self.templates[PromptType.ANSWER_EVALUATION] = PromptTemplate(
            name="Answer Evaluation",
            system_prompt=(
                "You are an expert interviewer and assessment specialist. Evaluate interview "
                "answers based on clarity, relevance, technical accuracy, and communication skills."
            ),
            user_prompt_template=(
                "Please evaluate the following interview answer:\n\n"
                "Question: {question}\n"
                "Candidate Answer: {answer}\n"
                "Expected Knowledge Areas: {expected_areas}\n"
                "Position Level: {position_level}\n\n"
                "Provide an evaluation with:\n"
                "1. Score (1-10)\n"
                "2. Strengths identified\n"
                "3. Areas for improvement\n"
                "4. Overall assessment"
            )
        )
        
        # Skill Gap Detection Placeholder
        self.templates[PromptType.SKILL_GAP_DETECTION] = PromptTemplate(
            name="Skill Gap Detection",
            system_prompt=(
                "You are a career development expert. Identify gaps between candidate skills "
                "and job requirements, prioritizing critical gaps."
            ),
            user_prompt_template=(
                "Identify skill gaps for this candidate:\n\n"
                "Candidate Skills: {candidate_skills}\n"
                "Target Position: {target_position}\n"
                "Required Skills: {required_skills}\n"
                "Experience Level: {experience_level}\n\n"
                "For each gap, provide:\n"
                "1. Gap name\n"
                "2. Importance (critical/important/nice-to-have)\n"
                "3. Learning difficulty (easy/medium/hard)"
            )
        )
        
        # Learning Recommendation Placeholder
        self.templates[PromptType.LEARNING_RECOMMENDATION] = PromptTemplate(
            name="Learning Recommendation",
            system_prompt=(
                "You are an expert learning and development specialist. Recommend personalized "
                "learning paths based on skill gaps and career goals."
            ),
            user_prompt_template=(
                "Recommend learning resources for these skill gaps:\n\n"
                "Skill Gaps: {skill_gaps}\n"
                "Current Proficiency: {current_proficiency}\n"
                "Target Proficiency: {target_proficiency}\n"
                "Available Time: {available_time}\n"
                "Learning Style: {learning_style}\n\n"
                "For each recommendation:\n"
                "1. Resource type (course/book/practice)\n"
                "2. Duration\n"
                "3. Expected outcome\n"
                "4. Difficulty level"
            )
        )
        
        # Feedback Generation Placeholder
        self.templates[PromptType.FEEDBACK_GENERATION] = PromptTemplate(
            name="Feedback Generation",
            system_prompt=(
                "You are a constructive feedback specialist. Generate encouraging yet honest "
                "feedback that helps candidates improve while maintaining their confidence."
            ),
            user_prompt_template=(
                "Generate constructive feedback for the interview:\n\n"
                "Interview Summary: {interview_summary}\n"
                "Key Strengths: {strengths}\n"
                "Areas for Improvement: {areas_for_improvement}\n"
                "Overall Performance Score: {performance_score}\n\n"
                "Feedback should:\n"
                "1. Be specific and actionable\n"
                "2. Balance positive and constructive comments\n"
                "3. Include next steps for improvement\n"
                "4. Encourage continued practice"
            )
        )
    
    def get_prompt(self, prompt_type: PromptType) -> Optional[PromptTemplate]:
        """
        Get a prompt template by type.
        
        Args:
            prompt_type: Type of prompt to retrieve
            
        Returns:
            PromptTemplate or None if not found
        """
        return self.templates.get(prompt_type)
    
    def get_prompt_by_name(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by name.
        
        Args:
            name: Name of the prompt
            
        Returns:
            PromptTemplate or None if not found
        """
        for template in self.templates.values():
            if template.name.lower() == name.lower():
                return template
        return None
    
    def list_prompts(self) -> dict:
        """List all available prompts."""
        return {
            str(prompt_type): template.name
            for prompt_type, template in self.templates.items()
        }
    
    def get_all_prompts_safe(self) -> dict:
        """Get all prompts in a format safe for logging/response."""
        return {
            str(prompt_type): template.to_dict()
            for prompt_type, template in self.templates.items()
        }


# Global prompt library instance
prompt_library = PromptLibrary()


__all__ = [
    'PromptType',
    'PromptTemplate',
    'PromptLibrary',
    'prompt_library',
]
