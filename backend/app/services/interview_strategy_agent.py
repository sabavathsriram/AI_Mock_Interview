"""
Interview Strategy Agent - Generates personalized interview plans from resume intelligence and job descriptions.
"""

import logging
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database.models.interview_plan import (
    InterviewPlan,
    GeneratedQuestion,
    QuestionSource,
    QuestionDifficultyLevel,
    QuestionType,
)
from app.database.models.resume_intelligence import CandidateProfile
from app.database.models.job_description import JobDescription
from app.llm.service import llm_service, TextGenerationResponse
from app.rag.service import rag_service, RAGServiceException
from app.rag.answer_generator import answer_generator

logger = logging.getLogger(__name__)


class InterviewStrategyException(Exception):
    """Exception for interview strategy errors."""
    pass


class InterviewStrategyAgent:
    """Generates interview plans and questions personalized to candidates."""
    
    def __init__(self):
        """Initialize interview strategy agent."""
        self.logger = logger
    
    def _create_strategy_prompt(
        self,
        candidate_profile: CandidateProfile,
        job_description: Optional[JobDescription],
        interview_type: str,
        difficulty: str
    ) -> str:
        """
        Create prompt for LLM to generate interview strategy.
        
        Args:
            candidate_profile: Candidate's resume intelligence profile
            job_description: Job description if provided
            interview_type: Type of interview (technical, behavioral, etc.)
            difficulty: Difficulty level (easy, medium, hard, expert)
            
        Returns:
            Prompt string
        """
        # Format job description section
        job_section = ""
        if job_description:
            job_section = "JOB DESCRIPTION:\n" + self._format_job_description(job_description) + "\n\n"
        
        prompt = f"""You are an expert technical interviewer. Analyze the candidate profile and generate an interview strategy.

CANDIDATE PROFILE:
- Name: {candidate_profile.candidate_name or "Unknown"}
- Location: {candidate_profile.contact.location or "Not specified"}
- Years of Experience: (inferred from resume)
- Education: {candidate_profile.education[0].institution if candidate_profile.education else "Not specified"}

SKILLS:
- Programming Languages: {", ".join(candidate_profile.skills.programming_languages) if candidate_profile.skills.programming_languages else "None"}
- Frameworks: {", ".join(candidate_profile.skills.frameworks) if candidate_profile.skills.frameworks else "None"}
- Databases: {", ".join(candidate_profile.skills.databases) if candidate_profile.skills.databases else "None"}
- Cloud/DevOps: {", ".join(candidate_profile.skills.cloud_devops) if candidate_profile.skills.cloud_devops else "None"}
- AI/ML: {", ".join(candidate_profile.skills.ai_ml) if candidate_profile.skills.ai_ml else "None"}

WORK EXPERIENCE:
{self._format_experience(candidate_profile.experience)}

PROJECTS:
{self._format_projects(candidate_profile.projects)}

{job_section}INTERVIEW PARAMETERS:
- Type: {interview_type}
- Difficulty: {difficulty}

Generate a JSON response with the following structure:
{{
    "skill_areas": ["skill1", "skill2", ...],
    "focus_areas": ["focus1", "focus2", ...],
    "candidate_strengths": ["strength1", "strength2", ...],
    "candidate_gaps": ["gap1", "gap2", ...],
    "question_distribution": {{"conceptual": 2, "coding": 3, ...}},
    "progression_strategy": {{"start_with_fundamentals": true, ...}},
    "evaluation_criteria": {{"technical_depth": "...", "problem_solving": "...", ...}},
    "recommended_duration_minutes": 60,
    "recommended_question_count": 10
}}

Focus on:
1. What technical areas the candidate knows well
2. Gaps or areas to explore more deeply
3. Projects they can be deep-dived on
4. Appropriate difficulty progression
5. Interview structure for {interview_type} interview"""
        
        return prompt
    
    def _format_experience(self, experience: List[Any]) -> str:
        """Format work experience for prompt."""
        if not experience:
            return "No work experience listed."
        
        formatted = []
        for exp in experience:
            if hasattr(exp, 'company'):
                formatted.append(
                    f"- {exp.position} at {exp.company} ({exp.duration or 'Duration unknown'})"
                )
        
        return "\n".join(formatted) if formatted else "No work experience listed."
    
    def _format_projects(self, projects: List[Any]) -> str:
        """Format projects for prompt."""
        if not projects:
            return "No projects listed."
        
        formatted = []
        for proj in projects:
            if hasattr(proj, 'name'):
                techs = ", ".join(proj.technologies) if hasattr(proj, 'technologies') else "Unknown"
                formatted.append(f"- {proj.name} ({techs})")
        
        return "\n".join(formatted) if formatted else "No projects listed."
    
    def _format_job_description(self, job_description: JobDescription) -> str:
        """Format job description for prompt."""
        if not job_description:
            return ""
        
        return f"""Position: {job_description.title} at {job_description.company}
Required Skills: {", ".join(job_description.required_skills) if job_description.required_skills else "Not specified"}
Nice-to-Have: {", ".join(job_description.nice_to_have_skills) if job_description.nice_to_have_skills else "None"}
Experience Required: {job_description.required_experience_years} years
Technologies: {", ".join(job_description.required_technologies) if job_description.required_technologies else "Not specified"}"""
    
    async def generate_strategy(
        self,
        candidate_profile: CandidateProfile,
        job_description: Optional[JobDescription] = None,
        interview_type: str = "technical",
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate interview strategy for a candidate.
        
        Args:
            candidate_profile: Candidate profile from resume intelligence
            job_description: Optional job description
            interview_type: Type of interview
            difficulty: Difficulty level
            
        Returns:
            Strategy dictionary with skill areas, focus areas, etc.
        """
        try:
            if not candidate_profile:
                raise InterviewStrategyException("Candidate profile required")
            
            self.logger.info(
                f"Generating interview strategy for candidate: {candidate_profile.candidate_name}"
            )
            
            # Create strategy prompt
            prompt = self._create_strategy_prompt(
                candidate_profile,
                job_description,
                interview_type,
                difficulty
            )
            
            # Call LLM to generate strategy
            llm_response = await llm_service.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=2000
            )
            
            # Parse JSON response
            try:
                strategy = json.loads(llm_response.text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', llm_response.text, re.DOTALL)
                if json_match:
                    strategy = json.loads(json_match.group())
                else:
                    raise InterviewStrategyException("Failed to parse LLM response")
            
            self.logger.info("Interview strategy generated successfully")
            return strategy
            
        except Exception as e:
            self.logger.error(f"Strategy generation failed: {str(e)}")
            raise InterviewStrategyException(f"Failed to generate strategy: {str(e)}")
    
    async def create_interview_plan(
        self,
        user_id: str,
        resume_id: str,
        candidate_profile: CandidateProfile,
        job_description: Optional[JobDescription] = None,
        interview_type: str = "technical",
        difficulty: str = "medium",
        question_count: int = 10,
        job_description_id: Optional[str] = None
    ) -> InterviewPlan:
        """
        Create complete interview plan.
        
        Args:
            user_id: User ID
            resume_id: Resume ID
            candidate_profile: Candidate profile
            job_description: Optional job description
            interview_type: Interview type
            difficulty: Difficulty level
            question_count: Number of questions
            job_description_id: Job description ID
            
        Returns:
            Complete interview plan
        """
        try:
            self.logger.info(f"Creating interview plan for user {user_id}")
            
            # Generate strategy
            strategy = await self.generate_strategy(
                candidate_profile,
                job_description,
                interview_type,
                difficulty
            )
            
            # Extract strategy components
            skill_areas = strategy.get("skill_areas", [])
            focus_areas = strategy.get("focus_areas", [])
            candidate_strengths = strategy.get("candidate_strengths", [])
            candidate_gaps = strategy.get("candidate_gaps", [])
            question_distribution = strategy.get("question_distribution", {})
            progression_strategy = strategy.get("progression_strategy", {})
            evaluation_criteria = strategy.get("evaluation_criteria", {})
            
            # Create interview plan
            plan = InterviewPlan(
                user_id=user_id,
                resume_id=resume_id,
                job_description_id=job_description_id,
                interview_type=interview_type,
                difficulty=QuestionDifficultyLevel(difficulty),
                total_questions=question_count,
                skill_areas=skill_areas,
                focus_areas=focus_areas,
                candidate_strengths=candidate_strengths,
                candidate_gaps=candidate_gaps,
                question_distribution=question_distribution,
                progression_strategy=progression_strategy,
                evaluation_criteria=evaluation_criteria,
                job_required_skills=job_description.required_skills if job_description else [],
                job_nice_to_have_skills=job_description.nice_to_have_skills if job_description else [],
                generated_at={
                    "timestamp": datetime.utcnow().isoformat(),
                    "model": "gemini-1.5-flash",
                    "strategy_method": "llm_based"
                }
            )
            
            self.logger.info(f"Interview plan created with {len(plan.skill_areas)} skill areas")
            return plan
            
        except Exception as e:
            self.logger.error(f"Interview plan creation failed: {str(e)}")
            raise InterviewStrategyException(f"Failed to create interview plan: {str(e)}")


# Global instance
interview_strategy_agent = InterviewStrategyAgent()

__all__ = [
    'InterviewStrategyAgent',
    'InterviewStrategyException',
    'interview_strategy_agent',
]
