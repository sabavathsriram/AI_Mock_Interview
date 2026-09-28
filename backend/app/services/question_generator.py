"""
Question Generator - Creates personalized questions from resume, job description, and knowledge base.
"""

import logging
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database.models.interview_plan import (
    GeneratedQuestion,
    QuestionSource,
    QuestionDifficultyLevel,
    QuestionType,
)
from app.database.models.resume_intelligence import CandidateProfile
from app.database.models.job_description import JobDescription
from app.llm.service import llm_service
from app.rag.service import rag_service, RAGServiceException

logger = logging.getLogger(__name__)


class QuestionGenerationException(Exception):
    """Exception for question generation errors."""
    pass


class QuestionGenerator:
    """Generates personalized interview questions."""
    
    def __init__(self):
        """Initialize question generator."""
        self.logger = logger
    
    def _extract_project_skills(self, project_name: str, project: Any) -> List[str]:
        """Extract skills from a project."""
        skills = []
        if hasattr(project, 'technologies'):
            skills.extend(project.technologies)
        if hasattr(project, 'description'):
            # Extract common tech keywords from description
            desc = project.description.lower() if project.description else ""
            keywords = ['api', 'database', 'frontend', 'backend', 'ml', 'data', 'cloud']
            skills.extend([kw for kw in keywords if kw in desc])
        return skills
    
    async def generate_resume_based_questions(
        self,
        candidate_profile: CandidateProfile,
        difficulty: str = "medium",
        count: int = 5
    ) -> List[GeneratedQuestion]:
        """
        Generate questions based on resume/candidate profile.
        
        Args:
            candidate_profile: Candidate profile
            difficulty: Difficulty level
            count: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        try:
            self.logger.info(f"Generating {count} resume-based questions")
            questions = []
            
            # Extract key resume elements
            projects = candidate_profile.projects if hasattr(candidate_profile, 'projects') else []
            experience = candidate_profile.experience if hasattr(candidate_profile, 'experience') else []
            skills = candidate_profile.skills
            
            # Generate questions from projects
            for i, project in enumerate(projects[:min(3, count)]):
                if hasattr(project, 'name') and project.name:
                    project_name = project.name
                    project_techs = self._extract_project_skills(project_name, project)
                    
                    question_text = f"Tell me about your {project_name} project. What was the architecture, and what challenges did you face?"
                    
                    q = GeneratedQuestion(
                        question_id=f"resume_proj_{i}",
                        question=question_text,
                        question_type=QuestionType.PROJECT_BASED,
                        skill=", ".join(project_techs[:2]) if project_techs else "Project Management",
                        difficulty=QuestionDifficultyLevel(difficulty),
                        source=QuestionSource.RESUME,
                        source_reference=project_name,
                        reason=f"Candidate listed {project_name} project on resume",
                        expected_topics=[
                            "Project overview and goals",
                            "Technical architecture",
                            "Technologies used",
                            "Challenges and solutions",
                            "Your role and contributions"
                        ],
                        evaluation_criteria=[
                            "Clarity in explaining architecture",
                            "Understanding of tradeoffs",
                            "Problem-solving approach",
                            "Technical depth appropriate to role"
                        ],
                        follow_up_possible=True,
                        follow_up_triggers=["architecture", "database", "scaling", "api"],
                        progression_level=3,
                        estimated_duration_seconds=180
                    )
                    questions.append(q)
            
            # Generate questions from work experience
            for i, exp in enumerate(experience[:min(2, count - len(questions))]):
                if hasattr(exp, 'position') and hasattr(exp, 'company'):
                    position = exp.position
                    company = exp.company
                    
                    question_text = f"What was your biggest technical contribution as {position} at {company}?"
                    
                    q = GeneratedQuestion(
                        question_id=f"resume_exp_{i}",
                        question=question_text,
                        question_type=QuestionType.SCENARIO_BASED,
                        skill="Problem Solving",
                        difficulty=QuestionDifficultyLevel(difficulty),
                        source=QuestionSource.RESUME,
                        source_reference=f"{position} at {company}",
                        reason=f"Candidate has relevant experience as {position} at {company}",
                        expected_topics=[
                            "Technical problem identification",
                            "Solution design",
                            "Implementation details",
                            "Impact and results"
                        ],
                        evaluation_criteria=[
                            "Impact of contribution",
                            "Technical complexity",
                            "Collaboration demonstrated",
                            "Communication clarity"
                        ],
                        follow_up_possible=True,
                        follow_up_triggers=["problem", "solution", "challenge", "scale"],
                        progression_level=3,
                        estimated_duration_seconds=150
                    )
                    questions.append(q)
            
            # Generate skill-based questions
            if skills and skills.programming_languages:
                primary_lang = skills.programming_languages[0]
                question_text = f"You list {primary_lang} as a primary skill. Walk me through a complex {primary_lang} problem you've solved."
                
                q = GeneratedQuestion(
                    question_id=f"resume_skill_0",
                    question=question_text,
                    question_type=QuestionType.CODING,
                    skill=primary_lang,
                    difficulty=QuestionDifficultyLevel(difficulty),
                    source=QuestionSource.RESUME,
                    source_reference=f"{primary_lang} skill",
                    reason=f"Candidate lists {primary_lang} as primary programming language",
                    expected_topics=[
                        "Problem understanding",
                        "Algorithm selection",
                        "Implementation approach",
                        "Code quality and style"
                    ],
                    evaluation_criteria=[
                        "Language proficiency",
                        "Problem-solving approach",
                        "Code efficiency",
                        "Explanation clarity"
                    ],
                    follow_up_possible=True,
                    follow_up_triggers=["optimize", "edge case", "efficiency"],
                    progression_level=2,
                    estimated_duration_seconds=180
                )
                questions.append(q)
            
            self.logger.info(f"Generated {len(questions)} resume-based questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Resume question generation failed: {str(e)}")
            raise QuestionGenerationException(f"Failed to generate resume questions: {str(e)}")
    
    async def generate_job_based_questions(
        self,
        job_description: JobDescription,
        candidate_profile: CandidateProfile,
        difficulty: str = "medium",
        count: int = 3
    ) -> List[GeneratedQuestion]:
        """
        Generate questions based on job requirements.
        
        Args:
            job_description: Job description
            candidate_profile: Candidate profile
            difficulty: Difficulty level
            count: Number of questions
            
        Returns:
            List of generated questions
        """
        try:
            self.logger.info(f"Generating {count} job-based questions")
            questions = []
            
            if not job_description:
                return questions
            
            required_skills = job_description.required_skills if job_description.required_skills else []
            candidate_skills = self._get_candidate_skills(candidate_profile)
            
            # Find skills required but not in resume
            missing_skills = [s for s in required_skills if s.lower() not in [cs.lower() for cs in candidate_skills]]
            
            # Generate questions for required skills
            for i, skill in enumerate(required_skills[:min(count, 3)]):
                skill_match = skill in candidate_skills
                if not skill_match:
                    source = QuestionSource.JOB_DESCRIPTION
                    reason = f"Job description requires {skill}, but candidate hasn't listed it"
                else:
                    source = QuestionSource.JOB_DESCRIPTION
                    reason = f"Job description requires {skill}, and candidate has this skill"
                
                question_text = f"The position requires {skill}. Tell me about your experience with {skill}."
                
                q = GeneratedQuestion(
                    question_id=f"job_skill_{i}",
                    question=question_text,
                    question_type=QuestionType.CONCEPTUAL,
                    skill=skill,
                    difficulty=QuestionDifficultyLevel(difficulty),
                    source=source,
                    source_reference=skill,
                    reason=reason,
                    expected_topics=[
                        f"Experience with {skill}",
                        "Use cases and applications",
                        "Pros and cons",
                        "When to use it"
                    ],
                    evaluation_criteria=[
                        "Understanding of the technology",
                        "Practical experience",
                        "Knowledge of when to apply it",
                        "Awareness of limitations"
                    ],
                    follow_up_possible=True,
                    follow_up_triggers=["project", "implement", "problem"],
                    progression_level=2,
                    estimated_duration_seconds=120
                )
                questions.append(q)
            
            self.logger.info(f"Generated {len(questions)} job-based questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Job question generation failed: {str(e)}")
            raise QuestionGenerationException(f"Failed to generate job questions: {str(e)}")
    
    def _get_candidate_skills(self, candidate_profile: CandidateProfile) -> List[str]:
        """Extract all skills from candidate profile."""
        skills = []
        if hasattr(candidate_profile, 'skills'):
            skills_obj = candidate_profile.skills
            if hasattr(skills_obj, 'programming_languages'):
                skills.extend(skills_obj.programming_languages)
            if hasattr(skills_obj, 'frameworks'):
                skills.extend(skills_obj.frameworks)
            if hasattr(skills_obj, 'databases'):
                skills.extend(skills_obj.databases)
            if hasattr(skills_obj, 'cloud_devops'):
                skills.extend(skills_obj.cloud_devops)
        return skills
    
    async def generate_knowledge_based_questions(
        self,
        skill_areas: List[str],
        difficulty: str = "medium",
        count: int = 2
    ) -> List[GeneratedQuestion]:
        """
        Generate questions from RAG knowledge base.
        
        Args:
            skill_areas: Skills to generate questions for
            difficulty: Difficulty level
            count: Number of questions
            
        Returns:
            List of generated questions
        """
        try:
            self.logger.info(f"Generating {count} knowledge-based questions")
            questions = []
            
            for i, skill in enumerate(skill_areas[:min(count, 3)]):
                try:
                    # Search knowledge base for this skill
                    context = rag_service.search(
                        query=f"{skill} concepts and best practices",
                        top_k=3,
                        category_filter=skill.lower() if skill.lower() in [
                            "python", "java", "javascript", "react", "nodejs"
                        ] else None
                    )
                    
                    if not context.retrieved_documents:
                        continue
                    
                    # Create question based on knowledge
                    question_text = f"Explain the key concepts of {skill} and when you would use it in production systems."
                    
                    q = GeneratedQuestion(
                        question_id=f"know_skill_{i}",
                        question=question_text,
                        question_type=QuestionType.CONCEPTUAL,
                        skill=skill,
                        difficulty=QuestionDifficultyLevel(difficulty),
                        source=QuestionSource.KNOWLEDGE_BASE,
                        source_reference=skill,
                        reason=f"Fundamental knowledge in {skill} required for role",
                        expected_topics=[
                            "Core concepts",
                            "Use cases",
                            "Advantages and disadvantages",
                            "Real-world applications"
                        ],
                        evaluation_criteria=[
                            "Conceptual understanding",
                            "Knowledge depth",
                            "Practical awareness",
                            "Industry awareness"
                        ],
                        follow_up_possible=True,
                        follow_up_triggers=["example", "implement", "problem"],
                        progression_level=1,
                        estimated_duration_seconds=120
                    )
                    questions.append(q)
                    
                except RAGServiceException:
                    self.logger.debug(f"Knowledge base search failed for {skill}")
                    continue
            
            self.logger.info(f"Generated {len(questions)} knowledge-based questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Knowledge question generation failed: {str(e)}")
            # Don't raise - knowledge-based questions are optional
            return []
    
    async def generate_all_questions(
        self,
        candidate_profile: CandidateProfile,
        job_description: Optional[JobDescription] = None,
        interview_type: str = "technical",
        difficulty: str = "medium",
        total_count: int = 10,
        skill_areas: Optional[List[str]] = None
    ) -> List[GeneratedQuestion]:
        """
        Generate all interview questions.
        
        Args:
            candidate_profile: Candidate profile
            job_description: Optional job description
            interview_type: Interview type
            difficulty: Difficulty level
            total_count: Total questions to generate
            skill_areas: Skills to focus on
            
        Returns:
            List of all generated questions
        """
        try:
            self.logger.info(f"Generating {total_count} total interview questions")
            all_questions = []
            
            # Generate resume-based questions (40%)
            resume_count = max(1, int(total_count * 0.4))
            resume_questions = await self.generate_resume_based_questions(
                candidate_profile,
                difficulty,
                resume_count
            )
            all_questions.extend(resume_questions)
            
            # Generate job-based questions (30%)
            if job_description:
                job_count = max(1, int(total_count * 0.3))
                job_questions = await self.generate_job_based_questions(
                    job_description,
                    candidate_profile,
                    difficulty,
                    job_count
                )
                all_questions.extend(job_questions)
            
            # Generate knowledge-based questions (30%)
            if skill_areas:
                knowledge_count = total_count - len(all_questions)
                knowledge_questions = await self.generate_knowledge_based_questions(
                    skill_areas,
                    difficulty,
                    knowledge_count
                )
                all_questions.extend(knowledge_questions)
            
            # Limit to total count
            all_questions = all_questions[:total_count]
            
            self.logger.info(f"Generated {len(all_questions)} questions total")
            return all_questions
            
        except Exception as e:
            self.logger.error(f"Question generation failed: {str(e)}")
            raise QuestionGenerationException(f"Failed to generate questions: {str(e)}")


# Global instance
question_generator = QuestionGenerator()

__all__ = [
    'QuestionGenerator',
    'QuestionGenerationException',
    'question_generator',
]
