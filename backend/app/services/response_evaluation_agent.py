"""
Response Evaluation Agent for Prompt 12.

Evaluates individual candidate answers against interview questions.
Returns structured evaluation with scores and feedback.
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.llm.service import llm_service, LLMResponseError, LLMRateLimitError, LLMConfigurationError

logger = logging.getLogger(__name__)


class ResponseEvaluationAgent:
    """
    Agent that evaluates a single candidate answer against a single interview question.
    
    Evaluation dimensions:
    - correctness: How accurate is the answer?
    - relevance: How relevant is the answer to the question?
    - technical_depth: How deep is the technical understanding? (0 if not applicable)
    - clarity: How clearly is the answer explained?
    - reasoning: How well-reasoned is the answer?
    - communication: How well is the answer communicated?
    - overall_score: Weighted average of all scores
    
    Returns strengths, weaknesses, demonstrated skills, and improvement suggestions.
    """
    
    def __init__(self):
        """Initialize the evaluation agent."""
        self.llm_service = llm_service
        self.model_used = llm_service.model_name if llm_service.configured else "groq-unavailable"
    
    async def evaluate_response(
        self,
        question_text: str,
        candidate_answer: str,
        interview_type: str,
        target_position: str,
        difficulty_level: str,
        resume_context: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate a candidate's response to an interview question.
        
        Args:
            question_text: The interview question
            candidate_answer: The candidate's answer
            interview_type: Type of interview (technical, behavioral, etc.)
            target_position: Target position being interviewed for
            difficulty_level: Difficulty level (easy, medium, hard, expert)
            resume_context: Optional resume context for grounding
            
        Returns:
            Dictionary with evaluation scores and feedback, or None if evaluation fails
            
        Structure:
        {
            "correctness": 0-10,
            "relevance": 0-10,
            "technical_depth": 0-10,
            "clarity": 0-10,
            "reasoning": 0-10,
            "communication": 0-10,
            "overall_score": 0-10,
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "skills_demonstrated": ["skill1", "skill2"],
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }
        """
        if not candidate_answer or not candidate_answer.strip():
            logger.warning("[AGENT] Attempted to evaluate empty answer")
            return None
        
        try:
            logger.info(f"[AGENT] Starting evaluation - interview_type={interview_type}, difficulty={difficulty_level}, model={self.model_used}")
            
            # Build evaluation prompt
            prompt = self._build_evaluation_prompt(
                question_text=question_text,
                candidate_answer=candidate_answer,
                interview_type=interview_type,
                target_position=target_position,
                difficulty_level=difficulty_level,
                resume_context=resume_context
            )
            
            logger.info(f"[AGENT] Evaluation prompt built: {len(prompt)} characters")
            
            # Call LLM
            logger.info(f"[AGENT] Calling LLM service: {self.model_used}")
            
            response = await self.llm_service.generate_text(
                prompt=prompt,
                system_prompt=self._get_system_prompt(interview_type),
                temperature=0.5,  # Lower temperature for consistent evaluation
                max_output_tokens=1500
            )
            
            logger.info(f"[AGENT] LLM response received, checking content")
            
            if not response or not response.text:
                logger.error("[AGENT] Empty response from LLM during evaluation")
                return None
            
            logger.info(f"[AGENT] LLM response text: {len(response.text)} characters, first 200 chars: {response.text[:200]}")
            
            # Parse evaluation from response
            evaluation = self._parse_evaluation_response(response.text)
            
            if not evaluation:
                logger.error("[AGENT] Failed to parse evaluation from LLM response")
                logger.error(f"[AGENT] Response text was: {response.text[:500]}")
                return None
            
            logger.info(f"[AGENT] Evaluation parsed: {evaluation}")
            
            # Validate evaluation structure
            if not self._validate_evaluation_structure(evaluation):
                logger.error("[AGENT] Evaluation structure validation failed")
                logger.error(f"[AGENT] Evaluation object: {evaluation}")
                return None
            
            logger.info(f"[AGENT] Successfully evaluated response. Overall score: {evaluation.get('overall_score')}/10")
            return evaluation
            
        except LLMRateLimitError as e:
            logger.error(f"[AGENT] Rate limit during evaluation: {str(e)}")
            return None
        except LLMConfigurationError as e:
            logger.error(f"[AGENT] LLM configuration error: {str(e)}")
            return None
        except LLMResponseError as e:
            logger.error(f"[AGENT] LLM response error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[AGENT] Unexpected error during evaluation: {str(e)}", exc_info=True)
            return None
    
    def _get_system_prompt(self, interview_type: str) -> str:
        """Get system prompt for the interview type."""
        base_prompt = """You are an expert technical interviewer and assessment specialist. 
Your job is to evaluate interview responses fairly and constructively.

Evaluation Guidelines:
- Be objective and data-driven
- Focus on what the candidate actually said, not assumptions
- For non-technical interviews, do not force technical criteria to dominate
- Distinguish between partially correct and fully correct answers
- Identify what the candidate knows well and what needs improvement
- Never invent facts or experience about the candidate
- Return ONLY valid JSON, no additional text or explanation"""
        
        return base_prompt
    
    def _build_evaluation_prompt(
        self,
        question_text: str,
        candidate_answer: str,
        interview_type: str,
        target_position: str,
        difficulty_level: str,
        resume_context: str = ""
    ) -> str:
        """Build the evaluation prompt."""
        resume_section = f"\n\nCandidate Resume Context:\n{resume_context}" if resume_context else ""
        
        prompt = f"""Evaluate this interview response on the following criteria.

Interview Configuration:
- Type: {interview_type}
- Position: {target_position}
- Difficulty: {difficulty_level}{resume_section}

Question:
{question_text}

Candidate Answer:
{candidate_answer}

Evaluation Criteria:
1. Correctness (0-10): How accurate is the answer?
2. Relevance (0-10): How relevant is the answer to the question?
3. Technical Depth (0-10): How deep is the technical understanding shown? (0 if not applicable)
4. Clarity (0-10): How clearly is the answer explained?
5. Reasoning (0-10): How well-reasoned is the answer?
6. Communication (0-10): How well is it communicated?

For each criterion:
- Consider the difficulty level: easier interviews should reward clear fundamentals; harder interviews should reward depth
- Award points only for what the candidate actually demonstrated
- Be specific about strengths and weaknesses

Return ONLY this JSON structure (no additional text):
{{
  "correctness": <0-10>,
  "relevance": <0-10>,
  "technical_depth": <0-10>,
  "clarity": <0-10>,
  "reasoning": <0-10>,
  "communication": <0-10>,
  "overall_score": <0-10>,
  "strengths": [<specific strengths demonstrated>],
  "weaknesses": [<specific gaps or areas for improvement>],
  "skills_demonstrated": [<concrete skills shown in answer>],
  "improvement_suggestions": [<actionable suggestions>]
}}"""
        
        return prompt
    
    def _parse_evaluation_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse evaluation JSON from LLM response.
        
        Handles responses that may be wrapped in markdown code blocks or contain extra text.
        """
        try:
            # Clean markdown code blocks
            text = response_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block or not line.startswith("```"):
                        json_lines.append(line)
                text = "\n".join(json_lines)
            
            # Extract JSON object (handle potential wrapping)
            start_idx = text.find('{')
            if start_idx == -1:
                logger.error("No JSON object found in response")
                return None
            
            # Find matching closing brace
            brace_count = 0
            end_idx = -1
            for i in range(start_idx, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i + 1
                        break
            
            if end_idx == -1:
                logger.error("Incomplete JSON in response")
                return None
            
            json_text = text[start_idx:end_idx]
            evaluation = json.loads(json_text)
            
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            logger.error(f"Response snippet: {response_text[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing evaluation response: {str(e)}")
            return None
    
    def _validate_evaluation_structure(self, evaluation: Dict[str, Any]) -> bool:
        """Validate that evaluation has required fields with correct types."""
        required_fields = {
            "correctness": int,
            "relevance": int,
            "technical_depth": int,
            "clarity": int,
            "reasoning": int,
            "communication": int,
            "overall_score": int,
            "strengths": list,
            "weaknesses": list,
            "skills_demonstrated": list,
            "improvement_suggestions": list
        }
        
        for field, expected_type in required_fields.items():
            if field not in evaluation:
                logger.warning(f"Missing required field: {field}")
                return False
            
            value = evaluation[field]
            if not isinstance(value, expected_type):
                logger.warning(
                    f"Field {field} has wrong type. Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                return False
            
            # Validate score ranges
            if expected_type == int:
                if not (0 <= value <= 10):
                    logger.warning(f"Score {field} out of range [0-10]: {value}")
                    return False
            
            # Validate arrays contain strings
            if expected_type == list:
                if not all(isinstance(item, str) for item in value):
                    logger.warning(f"Field {field} contains non-string items")
                    return False
        
        return True


# Global instance
response_evaluation_agent = ResponseEvaluationAgent()

__all__ = ["ResponseEvaluationAgent", "response_evaluation_agent"]
