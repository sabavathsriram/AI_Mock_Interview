"""
Resume Intelligence Agent - analyzes extracted resume text and creates structured candidate profile.
"""

import json
import logging
from typing import Optional, Tuple
from datetime import datetime

from app.database.mongodb import mongodb
from app.database.models import CandidateProfile, SkillsCategory
from app.llm.service import llm_service
from app.llm.prompts import PromptType, prompt_library
from bson import ObjectId

logger = logging.getLogger(__name__)


class ResumeIntelligenceAgent:
    """Agent for analyzing resumes and extracting structured candidate information."""
    
    MAX_RETRIES = 1
    
    @classmethod
    async def analyze_resume(
        cls,
        resume_id: str,
        user_id: str,
        extracted_text: str
    ) -> Tuple[bool, Optional[CandidateProfile], Optional[str]]:
        """
        Analyze extracted resume text and create structured candidate profile.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID
            extracted_text: Plain text extracted from resume
            
        Returns:
            Tuple of (success, profile, error_message)
        """
        try:
            # Validate input
            if not extracted_text or not extracted_text.strip():
                error_msg = "No extracted text available for analysis"
                logger.error(f"Resume analysis failed for {resume_id}: {error_msg}")
                return False, None, error_msg
            
            logger.info(f"Starting resume analysis for resume {resume_id}, user {user_id}")
            
            # Generate prompt for LLM
            prompt = cls._create_analysis_prompt(extracted_text)
            
            # Get response from LLM with retry logic
            llm_response = None
            error_message = None
            
            for attempt in range(cls.MAX_RETRIES + 1):
                try:
                    logger.info(f"LLM analysis attempt {attempt + 1}/{cls.MAX_RETRIES + 1}")
                    
                    response = await llm_service.generate_text(
                        prompt=prompt,
                        temperature=0.3,  # Lower temperature for consistent structured output
                        max_output_tokens=4000
                    )
                    
                    if response and response.text:
                        llm_response = response.text
                        break
                    else:
                        error_message = "Empty response from LLM"
                
                except Exception as e:
                    error_message = str(e)
                    logger.warning(f"LLM attempt {attempt + 1} failed: {error_message}")
                    if attempt == cls.MAX_RETRIES:
                        logger.error(f"All LLM attempts failed for resume {resume_id}")
                        return False, None, f"LLM analysis failed after {cls.MAX_RETRIES + 1} attempts: {error_message}"
            
            if not llm_response:
                error_msg = error_message or "No response from LLM"
                logger.error(f"Resume analysis failed for {resume_id}: {error_msg}")
                return False, None, error_msg
            
            # Parse LLM response
            profile_data = cls._parse_llm_response(llm_response)
            if not profile_data:
                error_msg = "Failed to parse LLM response as JSON"
                logger.error(f"Resume analysis failed for {resume_id}: {error_msg}")
                return False, None, error_msg
            
            # Add metadata
            profile_data["resume_id"] = resume_id
            profile_data["user_id"] = user_id
            profile_data["analysis_status"] = "completed"
            profile_data["llm_model_used"] = llm_service.model_name
            
            # Create and validate profile
            try:
                profile = CandidateProfile(**profile_data)
                logger.info(f"Successfully analyzed resume {resume_id}")
                return True, profile, None
            
            except Exception as e:
                error_msg = f"Profile validation failed: {str(e)}"
                logger.error(f"Resume analysis failed for {resume_id}: {error_msg}")
                return False, None, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error during resume analysis: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    @classmethod
    def _create_analysis_prompt(cls, resume_text: str) -> str:
        """
        Create a detailed prompt for resume analysis.
        
        Args:
            resume_text: Extracted resume text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze the following resume and extract structured information about the candidate.

Resume Text:
---
{resume_text}
---

Extract and structure the following information from the resume. Be precise and only include information explicitly present in the resume. If information is not available, use null for single values or empty arrays for lists.

Return ONLY valid JSON with this exact structure:
{{
  "candidate_name": "full name or null",
  "contact": {{
    "email": "email or null",
    "phone": "phone number or null",
    "location": "city/location or null"
  }},
  "education": [
    {{
      "degree": "degree type (e.g., B.Tech, M.S., BA) or null",
      "field_of_study": "major/field of study or null",
      "institution": "university/college name or null",
      "graduation_year": year as integer or null,
      "cgpa": number (0-4.0) or null,
      "percentage": number (0-100) or null
    }}
  ],
  "skills": {{
    "programming_languages": ["list of programming languages"],
    "frameworks": ["list of frameworks and libraries"],
    "libraries": ["list of specific libraries"],
    "databases": ["list of databases and data stores"],
    "cloud_devops": ["cloud platforms, containerization, orchestration"],
    "ai_ml": ["AI/ML frameworks and tools"],
    "other": ["other technical skills"]
  }},
  "projects": [
    {{
      "name": "project name or null",
      "description": "project description or null",
      "technologies": ["list of technologies used"],
      "link": "github or project URL or null"
    }}
  ],
  "experience": [
    {{
      "company": "company name or null",
      "position": "job title or null",
      "duration": "duration string (e.g., '2 years', '2020-2022') or null",
      "start_year": year or null,
      "end_year": year or null (omit if currently working),
      "description": "job description or null",
      "key_achievements": ["list of achievements"]
    }}
  ],
  "internships": [
    {{
      "company": "company name or null",
      "position": "internship title or null",
      "duration": "duration or null",
      "start_month_year": "month year or null",
      "end_month_year": "month year or null",
      "description": "internship description or null",
      "technologies": ["technologies used"]
    }}
  ],
  "certifications": [
    {{
      "name": "certification name or null",
      "issuer": "issuing organization or null",
      "issue_date": "date or null",
      "expiry_date": "date or null",
      "link": "credential URL or null"
    }}
  ],
  "achievements": [
    {{
      "title": "achievement title or null",
      "description": "what was achieved or null",
      "date": "when achieved or null"
    }}
  ],
  "additional_information": ["any other relevant information from resume"]
}}

IMPORTANT RULES:
1. Extract ONLY information present in the resume - do not infer or guess
2. For skills, organize by category accurately (don't put Python in "frameworks")
3. Preserve dates in original format if year cannot be extracted
4. Return valid JSON only - no markdown, no code blocks
5. Use null for missing values, not empty strings
6. Use empty arrays [] for sections with no items
7. Remove any trailing commas from lists
8. Ensure all arrays are properly formatted

Resume analysis starts here:"""
        
        return prompt
    
    @classmethod
    def _parse_llm_response(cls, response: str) -> Optional[dict]:
        """
        Parse and validate LLM JSON response.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Parsed dictionary or None if invalid
        """
        try:
            # Clean up markdown code blocks if present
            response_text = response.strip()
            
            # Remove markdown code blocks
            if "```" in response_text:
                # Extract content between code blocks
                lines = response_text.split("\n")
                json_lines = []
                in_code_block = False
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)
                response_text = "\n".join(json_lines).strip()
            
            # Try to find JSON object in response
            if not response_text.strip().startswith('{'):
                # Look for JSON object in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                if start_idx >= 0 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx + 1]
                else:
                    logger.error("No JSON object found in LLM response")
                    return None
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Basic validation
            if not isinstance(data, dict):
                logger.error("LLM response is not a JSON object")
                return None
            
            # Ensure required structure exists
            if "contact" not in data:
                data["contact"] = {}
            if "skills" not in data:
                data["skills"] = {}
            if "education" not in data:
                data["education"] = []
            if "projects" not in data:
                data["projects"] = []
            if "experience" not in data:
                data["experience"] = []
            if "internships" not in data:
                data["internships"] = []
            if "certifications" not in data:
                data["certifications"] = []
            if "achievements" not in data:
                data["achievements"] = []
            if "additional_information" not in data:
                data["additional_information"] = []
            
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return None
    
    @classmethod
    async def save_profile(cls, profile: CandidateProfile) -> Optional[str]:
        """
        Save candidate profile to MongoDB.
        
        Args:
            profile: CandidateProfile instance
            
        Returns:
            Profile ID if successful, None otherwise
        """
        try:
            collection = mongodb.get_collection("candidate_profiles")
            
            # Check if profile already exists for this resume
            existing = await collection.find_one({
                "resume_id": profile.resume_id,
                "user_id": profile.user_id
            })
            
            if existing:
                # Update existing profile
                result = await collection.replace_one(
                    {"_id": existing["_id"]},
                    profile.dict(by_alias=True)
                )
                logger.info(f"Updated candidate profile {existing['_id']}")
                return str(existing["_id"])
            else:
                # Insert new profile
                result = await collection.insert_one(profile.dict(by_alias=True))
                logger.info(f"Created new candidate profile {result.inserted_id}")
                return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Failed to save candidate profile: {str(e)}")
            return None
    
    @classmethod
    async def get_profile(cls, resume_id: str, user_id: str) -> Optional[dict]:
        """
        Retrieve candidate profile from MongoDB.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID
            
        Returns:
            Profile dictionary or None
        """
        try:
            collection = mongodb.get_collection("candidate_profiles")
            
            profile = await collection.find_one({
                "resume_id": resume_id,
                "user_id": user_id
            })
            
            if profile:
                profile["_id"] = str(profile["_id"])
            
            return profile
        
        except Exception as e:
            logger.error(f"Failed to retrieve candidate profile: {str(e)}")
            return None
    
    @classmethod
    async def update_analysis_status(
        cls,
        resume_id: str,
        user_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update analysis status in candidate profile.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID
            status: New status (pending, analyzing, completed, failed)
            error_message: Error message if failed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            collection = mongodb.get_collection("candidate_profiles")
            
            update_data = {
                "analysis_status": status,
                "updated_at": datetime.utcnow()
            }
            
            if error_message:
                update_data["analysis_error"] = error_message
            
            result = await collection.update_one(
                {
                    "resume_id": resume_id,
                    "user_id": user_id
                },
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"Failed to update analysis status: {str(e)}")
            return False
