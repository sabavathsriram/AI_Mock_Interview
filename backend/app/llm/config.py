"""
LLM Configuration Module
Handles configuration for LLM providers (primarily Google Gemini)
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM configuration settings loaded from environment variables."""
    
    # Gemini API Configuration
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key"
    )
    gemini_model: str = Field(
        default="gemini-1.5-flash",
        description="Gemini model name to use"
    )
    gemini_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for response generation (0-2)"
    )
    gemini_max_output_tokens: int = Field(
        default=2048,
        ge=1,
        le=8000,
        description="Maximum output tokens for responses"
    )
    gemini_request_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )
    
    # Feature Flags
    enabled: bool = Field(
        default=True,
        description="Whether LLM features are enabled"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "GEMINI_"
    
    @field_validator('gemini_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is provided."""
        if not v or v.strip() == "":
            raise ValueError("GEMINI_API_KEY environment variable is required")
        return v.strip()
    
    @field_validator('gemini_model')
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name."""
        if not v or v.strip() == "":
            raise ValueError("GEMINI_MODEL must not be empty")
        return v.strip()
    
    def is_configured(self) -> bool:
        """Check if LLM is properly configured."""
        return bool(self.gemini_api_key) and self.enabled
    
    def get_safe_config_dict(self) -> dict:
        """
        Get configuration dictionary without sensitive information.
        Safe for logging.
        """
        return {
            "model": self.gemini_model,
            "temperature": self.gemini_temperature,
            "max_output_tokens": self.gemini_max_output_tokens,
            "request_timeout": self.gemini_request_timeout,
            "enabled": self.enabled,
            "api_key_configured": bool(self.gemini_api_key),
        }


# Load settings
try:
    llm_settings = LLMSettings()
except Exception as e:
    # Create a default settings object that will fail gracefully
    # This allows the app to start but LLM operations will fail
    class DefaultLLMSettings:
        gemini_api_key = ""
        gemini_model = "gemini-1.5-flash"
        gemini_temperature = 0.7
        gemini_max_output_tokens = 2048
        gemini_request_timeout = 30
        enabled = False
        
        def is_configured(self):
            return False
        
        def get_safe_config_dict(self):
            return {"enabled": False, "error": str(e)}
    
    llm_settings = DefaultLLMSettings()


__all__ = ['LLMSettings', 'llm_settings']
