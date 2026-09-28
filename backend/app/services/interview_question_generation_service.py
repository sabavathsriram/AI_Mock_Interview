"""
Interview Question Generation Service

Generates personalized interview questions based on candidate resume,
interview type, difficulty level, and optional job description.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database.mongodb import mongodb
from app.database.models.interview_question import InterviewQuestion, QuestionType, QuestionDifficulty
from app.llm.service import llm_service
from app.llm.prompts import PromptType

logger = logging.getLogger(__name__)


class InterviewQuestionGenerationService:
    """Service for generating personalized interview questions."""

    async def generate_questions(
        self,
        user_id: str,
        resume_id: str,
        interview_type: str,
        difficulty_level: str,
        target_position: str,
        target_company: Optional[str] = None,
        num_questions: int = 10,
        job_description_id: Optional[str] = None,
    ) -> List[InterviewQuestion]:
        """
        Generate personalized interview questions for a candidate.

        Args:
            user_id: Current user ID
            resume_id: Resume ID to base questions on
            interview_type: Type of interview (technical, behavioral, coding, system_design)
            difficulty_level: Difficulty level (easy, medium, hard)
            target_position: Target position/job title
            target_company: Target company (optional)
            num_questions: Number of questions to generate
            job_description_id: Optional job description ID for additional context

        Returns:
            List of generated InterviewQuestion documents

        Raises:
            ValueError: If resume is invalid or not analyzed
            HTTPException: If generation fails
        """
        try:
            logger.info(f"Starting question generation for user {user_id}, resume {resume_id}")
            from bson import ObjectId
            
            # Validate resume exists and belongs to user
            # Use resume_documents collection (matches the upload and list endpoints)
            resumes_collection = mongodb.get_collection("resume_documents")
            
            try:
                resume_oid = ObjectId(resume_id)
            except:
                raise ValueError("Invalid resume ID format")
            
            resume = await resumes_collection.find_one({
                "_id": resume_oid,
                "user_id": user_id
            })
            
            if not resume:
                raise ValueError("Resume not found or does not belong to user")
            
            logger.info(f"Resume found: {resume.get('filename', 'unknown')}, extraction_status: {resume.get('extraction_status')}")
            
            # Check if resume has been extracted
            if resume.get("extraction_status") != "completed":
                raise ValueError(
                    f"Resume extraction required. Current status: {resume.get('extraction_status', 'unknown')}"
                )
            
            # Get extracted text for analysis
            extracted_text = resume.get("extracted_text", "")
            if not extracted_text:
                raise ValueError("No extracted text available from resume")
            
            # Get job description if provided
            job_description_text = ""
            if job_description_id:
                job_descriptions = mongodb.get_collection("job_descriptions")
                try:
                    job_desc_oid = ObjectId(job_description_id)
                except:
                    logger.warning("Invalid job description ID format, skipping")
                    job_description_id = None
                
                if job_description_id:
                    job_desc = await job_descriptions.find_one({
                        "_id": job_desc_oid,
                        "user_id": user_id
                    })
                    if job_desc:
                        job_description_text = job_desc.get("description", "")
            
            # Extract structured data from resume to ground questions
            resume_summary = self._extract_resume_summary(extracted_text, target_position)
            candidate_skills = self._extract_candidate_skills(extracted_text)
            experience_text = self._extract_work_experience(extracted_text)
            projects_text = self._extract_projects(extracted_text)
            
            # Prepare prompt parameters
            prompt_params = {
                "num_questions": num_questions,
                "resume_summary": resume_summary,
                "candidate_skills": candidate_skills,
                "candidate_experience": experience_text,
                "candidate_projects": projects_text,
                "interview_type": interview_type,
                "difficulty_level": difficulty_level,
                "target_position": target_position,
                "target_company": target_company or "Not specified",
                "job_description": job_description_text or "No job description provided",
            }
            
            logger.info(f"Generating {num_questions} interview questions for user {user_id}")
            
            # Get prompt template
            from app.llm.prompts import prompt_library
            prompt_template = prompt_library.get_prompt(PromptType.INTERVIEW_QUESTION_GENERATION)
            if not prompt_template:
                raise ValueError("Interview question generation prompt not found")
            
            # Format the prompt
            user_prompt = prompt_template.format_user_prompt(**prompt_params)
            
            # Generate questions using LLM
            llm_response = await llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=prompt_template.system_prompt,
                temperature=0.7,
                max_output_tokens=4000
            )
            
            if not llm_response:
                raise ValueError("LLM returned empty response")
            
            # Parse JSON response (extract text from TextGenerationResponse)
            response_text = llm_response.text if hasattr(llm_response, 'text') else str(llm_response)
            questions_data = self._parse_llm_response(response_text, num_questions)
            
            if not questions_data or len(questions_data) == 0:
                raise ValueError("No questions generated from LLM response")
            
            # Validate difficulty levels and adjust if needed
            questions_data = self._validate_and_adjust_difficulty(questions_data, difficulty_level)
            
            # Validate and create question documents
            generated_questions = []
            questions_collection = mongodb.get_collection("interview_questions")
            
            for idx, question_data in enumerate(questions_data[:num_questions]):
                try:
                    # Validate required fields
                    question_text = question_data.get("question_text")
                    if not question_text:
                        logger.warning(f"Skipping question {idx}: missing question_text")
                        continue
                    
                    # Create InterviewQuestion document
                    question = InterviewQuestion(
                        question_text=question_text,
                        question_type=QuestionType(
                            question_data.get("question_type", "long_answer")
                        ),
                        difficulty=QuestionDifficulty(
                            question_data.get("difficulty", difficulty_level)
                        ),
                        category=question_data.get("category", "General"),
                        key_points=question_data.get("expected_concepts", []),
                        tags=[
                            interview_type,
                            difficulty_level,
                            question_data.get("source", "resume")
                        ],
                        is_ai_generated=True,
                        ai_model_used="gemini",
                        generation_prompt="personalized_for_resume",
                    )
                    
                    # Store in MongoDB
                    result = await questions_collection.insert_one(question.dict(by_alias=True))
                    question_id = str(result.inserted_id)
                    
                    # Add ID to question object for return
                    question_dict = question.dict(by_alias=True)
                    question_dict["_id"] = question_id
                    
                    generated_questions.append(question_dict)
                    
                except Exception as e:
                    logger.error(f"Error creating question {idx}: {str(e)}")
                    continue
            
            if not generated_questions:
                raise ValueError("Failed to create any interview questions")
            
            logger.info(f"Successfully generated {len(generated_questions)} interview questions")
            return generated_questions
        
        except Exception as e:
            logger.error(f"Error generating interview questions: {str(e)}")
            raise


    def _extract_resume_summary(self, extracted_text: str, target_position: str) -> str:
        """
        Extract a structured summary of the resume focusing on relevant content.
        
        Truncates to first 1000 chars of extracted text to avoid token overflow.
        """
        # Use first portion of extracted text as context
        summary = extracted_text[:1000] if len(extracted_text) > 1000 else extracted_text
        return f"Candidate with background in {target_position}:\n{summary}"
    
    def _extract_candidate_skills(self, extracted_text: str) -> str:
        """Extract skills section from resume text."""
        lines = extracted_text.split('\n')
        skills_section = []
        in_skills = False
        
        for line in lines:
            lower_line = line.lower()
            # Look for skills section markers
            if any(marker in lower_line for marker in ['skills', 'technical skills', 'competencies']):
                in_skills = True
                continue
            
            # Stop at next section
            if in_skills and any(marker in lower_line for marker in ['experience', 'education', 'projects', 'certification']):
                break
            
            # Collect skill lines
            if in_skills and line.strip() and len(line.strip()) > 2:
                skills_section.append(line.strip())
                if len(skills_section) >= 20:  # Limit to 20 lines
                    break
        
        # If found skills section, use it; otherwise extract from full text
        if skills_section:
            return "Skills:\n" + "\n".join(skills_section[:15])
        else:
            # Look for common tech keywords in the text (first 1500 chars)
            return "Technical background visible in resume:\n" + extracted_text[:1500]
    
    def _extract_work_experience(self, extracted_text: str) -> str:
        """Extract work experience section from resume text."""
        lines = extracted_text.split('\n')
        exp_section = []
        in_exp = False
        
        for line in lines:
            lower_line = line.lower()
            # Look for experience section markers
            if any(marker in lower_line for marker in ['work experience', 'professional experience', 'employment']):
                in_exp = True
                continue
            
            # Stop at next section
            if in_exp and any(marker in lower_line for marker in ['education', 'skills', 'projects', 'certification']):
                break
            
            # Collect experience lines
            if in_exp and line.strip() and len(line.strip()) > 2:
                exp_section.append(line.strip())
                if len(exp_section) >= 25:  # Limit to 25 lines
                    break
        
        # If found experience section, use it; otherwise extract from full text
        if exp_section:
            return "Work Experience:\n" + "\n".join(exp_section[:20])
        else:
            # Default to middle section of resume
            start = len(extracted_text) // 4
            end = start + 2000
            return "Professional background:\n" + extracted_text[start:end]
    
    def _extract_projects(self, extracted_text: str) -> str:
        """Extract projects section from resume text."""
        lines = extracted_text.split('\n')
        proj_section = []
        in_proj = False
        
        for line in lines:
            lower_line = line.lower()
            # Look for projects section markers
            if any(marker in lower_line for marker in ['projects', 'portfolio', 'key projects']):
                in_proj = True
                continue
            
            # Stop at next section
            if in_proj and any(marker in lower_line for marker in ['experience', 'education', 'skills', 'certification']):
                break
            
            # Collect project lines
            if in_proj and line.strip() and len(line.strip()) > 2:
                proj_section.append(line.strip())
                if len(proj_section) >= 20:  # Limit to 20 lines
                    break
        
        # If found projects section, use it; otherwise note absence
        if proj_section:
            return "Projects:\n" + "\n".join(proj_section[:15])
        else:
            return "No dedicated projects section found - refer to work experience and skills"

    def _validate_and_adjust_difficulty(self, questions_data: List[Dict[str, Any]], requested_difficulty: str) -> List[Dict[str, Any]]:
        """
        Validate that questions match the requested difficulty level.
        
        Checks question text for keywords that indicate difficulty level.
        If a question appears to be above the requested level, it's flagged and difficulty is reset.
        
        Args:
            questions_data: List of question dictionaries from LLM
            requested_difficulty: The difficulty level that was requested
            
        Returns:
            Validated questions with adjusted difficulty fields
        """
        # Keywords indicating difficulty levels
        expert_keywords = [
            'advanced', 'senior', 'complex distributed', 'enterprise', 'highly scalable',
            'microservices architecture', 'distributed consensus', 'edge cases', 'fault tolerance',
            'at scale', 'millions of', 'billions of', 'petabyte'
        ]
        
        hard_keywords = [
            'optimize', 'tradeoff', 'architecture', 'design', 'performance', 'bottleneck',
            'debugging', 'algorithm', 'data structure', 'complex', 'multi-step'
        ]
        
        medium_keywords = [
            'difference between', 'compare', 'implement', 'example', 'use case', 'when would'
        ]
        
        for question in questions_data:
            question_text = question.get("question_text", "").lower()
            stated_difficulty = question.get("difficulty", requested_difficulty)
            
            # Detect actual difficulty from question text
            detected_difficulty = self._detect_question_difficulty(
                question_text, expert_keywords, hard_keywords, medium_keywords
            )
            
            # If detected difficulty is higher than requested, force it to requested
            difficulty_order = {"easy": 0, "medium": 1, "hard": 2, "expert": 3}
            requested_level = difficulty_order.get(requested_difficulty.lower(), 1)
            detected_level = difficulty_order.get(detected_difficulty.lower(), 1)
            
            if detected_level > requested_level:
                logger.warning(
                    f"Question detected as {detected_difficulty} but requested {requested_difficulty}. "
                    f"Resetting to {requested_difficulty}. Question: {question_text[:80]}"
                )
                question["difficulty"] = requested_difficulty
            else:
                # Ensure difficulty field matches requested if not overridden
                question["difficulty"] = requested_difficulty
        
        return questions_data
    
    def _detect_question_difficulty(self, question_text: str, expert_kw: List[str], hard_kw: List[str], medium_kw: List[str]) -> str:
        """
        Detect difficulty level from question text by looking for keywords.
        
        Returns: 'easy', 'medium', 'hard', or 'expert'
        """
        # Check for expert-level keywords
        if any(kw in question_text for kw in expert_kw):
            return "expert"
        
        # Check for hard-level keywords
        if any(kw in question_text for kw in hard_kw):
            return "hard"
        
        # Check for medium-level keywords
        if any(kw in question_text for kw in medium_kw):
            return "medium"
        
        # Default to easy if no keywords detected
        return "easy"

    def _parse_llm_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """
        Parse and validate LLM JSON response.
        
        Args:
            response: Raw LLM response text
            expected_count: Expected number of questions
            
        Returns:
            List of validated question dictionaries
        """
        try:
            # Log raw response for debugging
            logger.info(f"Raw LLM Response (first 500 chars): {response[:500]}")
            
            # Clean up markdown code blocks if present
            if response.startswith("```"):
                # Extract content between code blocks
                lines = response.split("\n")
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block and line.strip():
                        json_lines.append(line)
                response = "\n".join(json_lines)
            
            # Parse JSON
            questions_data = json.loads(response)
            
            # Ensure it's a list
            if isinstance(questions_data, dict):
                questions_data = [questions_data]
            
            # Validate and clean up questions
            validated_questions = []
            for q in questions_data:
                if isinstance(q, dict) and "question_text" in q:
                    validated_questions.append(q)
            
            return validated_questions[:expected_count]
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {str(e)}")
            logger.error(f"Response was: {response[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            logger.error(f"Response was: {response[:500]}")
            return []

    async def get_or_generate_questions(
        self,
        user_id: str,
        resume_id: str,
        interview_type: str,
        difficulty_level: str,
        target_position: str,
        target_company: Optional[str] = None,
        num_questions: int = 10,
        job_description_id: Optional[str] = None,
    ) -> List[InterviewQuestion]:
        """
        Get existing questions or generate new ones if they don't exist.
        
        Checks for existing questions before regenerating to avoid unnecessary API calls.
        """
        # Check if questions already exist for this configuration
        questions_collection = mongodb.get_collection("interview_questions")
        
        existing = await questions_collection.find_one({
            "tags": {"$all": [interview_type, difficulty_level]}
        })
        
        if existing:
            logger.info(f"Using existing questions for {interview_type}/{difficulty_level}")
            return []  # Return empty - questions already exist
        
        # Generate new questions
        return await self.generate_questions(
            user_id=user_id,
            resume_id=resume_id,
            interview_type=interview_type,
            difficulty_level=difficulty_level,
            target_position=target_position,
            target_company=target_company,
            num_questions=num_questions,
            job_description_id=job_description_id,
        )
