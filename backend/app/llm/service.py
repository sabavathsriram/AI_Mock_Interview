"""
LLM Service Module
Main service for interacting with LLM providers (Groq with OpenAI-compatible API)
Provides a provider-agnostic interface for the rest of the application
"""

import json
import logging
from typing import Any, Dict, Optional, Type
from datetime import datetime

from openai import OpenAI, RateLimitError, APITimeoutError, APIError
from pydantic import BaseModel, ValidationError

from app.llm.config import llm_settings
from app.llm.prompts import PromptType, prompt_library

# Configure logging
logger = logging.getLogger(__name__)


class LLMException(Exception):
    """Base exception for LLM service errors."""
    pass


class LLMConfigurationError(LLMException):
    """Raised when LLM is not properly configured."""
    pass


class LLMResponseError(LLMException):
    """Raised when LLM response is invalid or malformed."""
    pass


class LLMTimeoutError(LLMException):
    """Raised when LLM request times out."""
    pass


class LLMRateLimitError(LLMException):
    """Raised when rate limit is exceeded."""
    pass


class TextGenerationRequest(BaseModel):
    """Request model for text generation."""
    prompt: str
    temperature: Optional[float] = None
    max_output_tokens: Optional[int] = None


class TextGenerationResponse(BaseModel):
    """Response model for text generation."""
    text: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None


class StructuredResponse(BaseModel):
    """Base model for structured responses."""
    pass


class LLMService:
    """
    LLM Service for interacting with Groq (OpenAI-compatible API).
    
    This service provides a provider-agnostic interface that can be extended
    to support other LLM providers in the future.
    """
    
    def __init__(self):
        """Initialize LLM service."""
        self.configured = llm_settings.is_configured()
        self.model_name = llm_settings.groq_model
        self.client = None
        
        if self.configured:
            self._initialize_client()
        else:
            logger.warning(
                "LLM service not configured. Set GROQ_API_KEY environment variable."
            )
    
    def _initialize_client(self):
        """Initialize Groq OpenAI-compatible client."""
        try:
            self.client = OpenAI(
                api_key=llm_settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            logger.info(f"Groq client initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise LLMConfigurationError(
                f"Failed to initialize Groq client: {str(e)}"
            )
    
    def is_configured(self) -> bool:
        """Check if LLM service is properly configured."""
        return self.configured
    
    async def generate_text(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> TextGenerationResponse:
        """
        Generate text using the LLM (Groq).
        
        Args:
            prompt: The user prompt
            temperature: Response temperature (0-2), defaults to config value
            max_output_tokens: Maximum tokens in response, defaults to config value
            system_prompt: Optional system prompt for context
            
        Returns:
            TextGenerationResponse with generated text
            
        Raises:
            LLMConfigurationError: If LLM is not configured
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
            LLMResponseError: If response is invalid
        """
        if not self.configured:
            raise LLMConfigurationError(
                "LLM service is not configured. Set GROQ_API_KEY environment variable."
            )
        
        try:
            # Use provided values or defaults from config
            temperature = temperature or llm_settings.groq_temperature
            max_output_tokens = max_output_tokens or llm_settings.groq_max_output_tokens
            
            # Log request
            logger.info(
                f"LLM text generation request - Model: {self.model_name}, "
                f"Temperature: {temperature}, Max tokens: {max_output_tokens}"
            )
            
            # Build messages
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_output_tokens,
                timeout=llm_settings.groq_request_timeout
            )
            
            # Extract response text
            if not response or not response.choices or not response.choices[0].message.content:
                raise LLMResponseError("Empty response from LLM")
            
            response_text = response.choices[0].message.content
            
            logger.info(
                f"LLM text generation successful - "
                f"Response length: {len(response_text)} characters"
            )
            
            return TextGenerationResponse(
                text=response_text,
                model=self.model_name,
                timestamp=datetime.utcnow(),
                tokens_used=None,
            )
        
        except (LLMResponseError, LLMTimeoutError, LLMRateLimitError, LLMConfigurationError):
            # Re-raise our custom LLM exceptions as-is
            raise
        
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise LLMRateLimitError(
                "The Groq API rate limit has been exceeded. Please try again in a few moments."
            )
        
        except APITimeoutError as e:
            logger.error(f"LLM request timeout: {str(e)}")
            raise LLMTimeoutError(f"LLM request timed out: {str(e)}")
        
        except APIError as e:
            logger.error(f"Groq API error: {str(e)}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise LLMRateLimitError(str(e))
            raise LLMResponseError(f"Groq API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected LLM error: {str(e)}")
            raise LLMException(f"Unexpected LLM error: {str(e)}")
    
    async def generate_structured_response(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> BaseModel:
        """
        Generate a structured JSON response and validate it with a Pydantic model.
        
        Args:
            prompt: The user prompt
            response_model: Pydantic model to validate response against
            temperature: Response temperature (0-2), defaults to config value
            max_output_tokens: Maximum tokens in response, defaults to config value
            system_prompt: Optional system prompt for context
            
        Returns:
            Validated instance of response_model
            
        Raises:
            LLMConfigurationError: If LLM is not configured
            LLMTimeoutError: If request times out
            LLMRateLimitError: If rate limit is exceeded
            LLMResponseError: If response is invalid or malformed
        """
        if not self.configured:
            raise LLMConfigurationError(
                "LLM service is not configured. Set GROQ_API_KEY environment variable."
            )
        
        # Add JSON instruction to prompt
        json_prompt = f"""{prompt}

IMPORTANT: You must respond with ONLY valid JSON that matches this schema:
{response_model.model_json_schema()}

Do not include any text before or after the JSON."""
        
        try:
            # Log request
            logger.info(
                f"LLM structured response request - Model: {self.model_name}, "
                f"Response type: {response_model.__name__}"
            )
            
            # Generate response
            response = await self.generate_text(
                prompt=json_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                system_prompt=system_prompt,
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if it's wrapped in text
            if not response_text.startswith('{') and not response_text.startswith('['):
                # Look for JSON in the response
                import re
                json_match = re.search(r'[\{\[].*[\}\]]', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group()
                else:
                    raise LLMResponseError("No valid JSON found in response")
            
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response text: {response_text[:500]}")
                raise LLMResponseError(
                    f"Failed to parse JSON response: {str(e)}"
                )
            
            # Validate with Pydantic model
            try:
                validated_response = response_model(**data)
                logger.info(
                    f"LLM structured response validated successfully - "
                    f"Type: {response_model.__name__}"
                )
                return validated_response
            
            except ValidationError as e:
                logger.error(
                    f"Response validation failed: {str(e)}"
                )
                raise LLMResponseError(
                    f"Response validation failed: {str(e)}"
                )
        
        except (LLMTimeoutError, LLMRateLimitError, LLMException):
            raise
        
        except Exception as e:
            logger.error(f"Structured response generation failed: {str(e)}")
            raise LLMResponseError(f"Structured response generation failed: {str(e)}")
    
    async def generate_from_prompt_template(
        self,
        prompt_type: PromptType,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        **template_vars,
    ) -> TextGenerationResponse:
        """
        Generate text using a prompt template.
        
        Args:
            prompt_type: Type of prompt template to use
            temperature: Response temperature (0-2)
            max_output_tokens: Maximum tokens in response
            **template_vars: Variables to format the template with
            
        Returns:
            TextGenerationResponse with generated text
            
        Raises:
            LLMResponseError: If template not found or variables missing
        """
        template = prompt_library.get_prompt(prompt_type)
        if not template:
            raise LLMResponseError(f"Prompt template not found: {prompt_type}")
        
        try:
            user_prompt = template.format_user_prompt(**template_vars)
        except ValueError as e:
            raise LLMResponseError(f"Failed to format prompt template: {str(e)}")
        
        return await self.generate_text(
            prompt=user_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_prompt=template.system_prompt,
        )


# Global LLM service instance
llm_service = LLMService()


__all__ = [
    'LLMService',
    'llm_service',
    'LLMException',
    'LLMConfigurationError',
    'LLMResponseError',
    'LLMTimeoutError',
    'LLMRateLimitError',
    'TextGenerationRequest',
    'TextGenerationResponse',
    'StructuredResponse',
]
