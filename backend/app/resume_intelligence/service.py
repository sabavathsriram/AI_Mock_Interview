"""
Resume Intelligence Service
Provides AI-powered resume analysis and skill extraction.
"""

import logging
from typing import Optional
from datetime import datetime
import json

from app.llm.service import LLMService
from app.llm.prompts import PromptType
from app.resume_intelligence.schemas import ResumeAnalysisResult

logger = logging.getLogger(__name__)


class ResumeAnalysisException(Exception):
    """Base exception for resume analysis."""
    pass


class ResumeAnalysisError(ResumeAnalysisException):
    """Raised when resume analysis fails."""
    pass


class ResumeAnalysisValidationError(ResumeAnalysisException):
    """Raised when analysis result validation fails."""
    pass


class ResumeIntelligenceService:
    """Service for AI-powered resume analysis using LLM."""
    
    def __init__(self):
        """Initialize Resume Intelligence Service."""
        self.llm_service = LLMService()
        self.logger = logger
    
    async def analyze_resume(
        self,
        resume_text: str,
        resume_id: Optional[str] = None,
    ) -> ResumeAnalysisResult:
        """
        Analyze resume text using LLM and return structured analysis.
        
        Args:
            resume_text: Extracted text from resume
            resume_id: Optional resume ID for logging
            
        Returns:
            ResumeAnalysisResult with structured analysis
            
        Raises:
            ResumeAnalysisError: If analysis fails
            ResumeAnalysisValidationError: If result validation fails
        """
        if not resume_text or not resume_text.strip():
            raise ResumeAnalysisError("Resume text is empty")
        
        self.logger.info(
            f"Starting resume analysis - Resume ID: {resume_id}, "
            f"Text length: {len(resume_text)} characters"
        )
        
        try:
            # Generate analysis from LLM
            analysis_result = await self.llm_service.generate_structured_response(
                prompt=self._prepare_analysis_prompt(resume_text),
                response_model=ResumeAnalysisResult,
                temperature=0.3,  # Lower temperature for consistency
                max_output_tokens=4096,
                system_prompt=self._get_system_prompt(),
            )
            
            # Validate result
            if not isinstance(analysis_result, ResumeAnalysisResult):
                raise ResumeAnalysisValidationError(
                    f"Invalid analysis result type: {type(analysis_result)}"
                )
            
            self.logger.info(
                f"Resume analysis completed successfully - Resume ID: {resume_id}, "
                f"Confidence: {analysis_result.overall_confidence}"
            )
            
            return analysis_result
            
        except Exception as e:
            error_msg = f"Resume analysis failed: {str(e)}"
            self.logger.error(error_msg)
            raise ResumeAnalysisError(error_msg) from e
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for resume analysis."""
        return (
            "You are an expert HR professional and career coach. Your task is to analyze resumes "
            "and extract structured information in JSON format. "
            "IMPORTANT RULES:\n"
            "1. NEVER invent information that is not explicitly stated in the resume\n"
            "2. For missing fields, use null or empty lists\n"
            "3. For every skill extracted, provide evidence (where it was mentioned)\n"
            "4. Be conservative with confidence scores (0-1 range)\n"
            "5. Identify experience level only if clearly indicated\n"
            "6. Return ONLY valid JSON that can be parsed"
        )
    
    def _prepare_analysis_prompt(self, resume_text: str) -> str:
        """
        Prepare the analysis prompt using prompt template.
        
        Args:
            resume_text: Extracted resume text
            
        Returns:
            Formatted prompt string
        """
        try:
            prompt_template = PromptType.RESUME_ANALYSIS
            from app.llm.prompts import prompt_library
            
            template = prompt_library.get_prompt(prompt_template)
            if not template:
                raise ResumeAnalysisError(f"Resume analysis prompt not found")
            
            return template.format_user_prompt(resume_text=resume_text)
            
        except Exception as e:
            raise ResumeAnalysisError(f"Failed to prepare analysis prompt: {str(e)}")
    
    def validate_analysis_result(self, analysis: ResumeAnalysisResult) -> bool:
        """
        Validate analysis result for quality.
        
        Args:
            analysis: ResumeAnalysisResult to validate
            
        Returns:
            True if valid, raises exception otherwise
        """
        # Ensure we have at least some extracted information
        if not analysis.candidate_name and not analysis.education and \
           not analysis.work_experience and not analysis.technical_skills:
            raise ResumeAnalysisValidationError(
                "Analysis returned no meaningful data"
            )
        
        # Ensure confidence score is reasonable
        if analysis.overall_confidence < 0.3:
            self.logger.warning(
                f"Low analysis confidence: {analysis.overall_confidence}"
            )
        
        return True
    
    def get_analysis_summary(self, analysis: ResumeAnalysisResult) -> dict:
        """
        Get a summary of the analysis result.
        
        Args:
            analysis: ResumeAnalysisResult
            
        Returns:
            Dictionary with summary information
        """
        return {
            "candidate_name": analysis.candidate_name,
            "experience_level": analysis.experience_level,
            "primary_domains": analysis.primary_domains,
            "secondary_domains": analysis.secondary_domains,
            "total_skills_extracted": sum(
                len(cat.skills) for cat in analysis.technical_skills
            ),
            "total_projects": len(analysis.projects),
            "total_experience_years": len(analysis.work_experience),
            "certifications_count": len(analysis.certifications),
            "overall_confidence": analysis.overall_confidence,
            "resume_strengths_count": len(analysis.resume_strengths),
            "skill_gaps_count": len(analysis.potential_skill_gaps),
        }


# Global service instance
resume_intelligence_service = ResumeIntelligenceService()

__all__ = [
    'ResumeIntelligenceService',
    'ResumeAnalysisException',
    'ResumeAnalysisError',
    'ResumeAnalysisValidationError',
    'resume_intelligence_service',
]
