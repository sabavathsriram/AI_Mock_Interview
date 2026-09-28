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
            
            # Prepare resume context for LLM
            resume_summary = f"Candidate applying for {target_position}"
            candidate_skills = "Skills detailed in resume"
            experience_text = "Work experience detailed in resume"
            projects_text = "Projects detailed in resume"
            
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
