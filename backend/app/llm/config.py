"""
LLM Configuration Module
Handles configuration for LLM providers (Groq with OpenAI-compatible API)
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Make sure environment variables are loaded
from dotenv import load_dotenv
from pathlib import Path

# Try to load .env from the backend directory
backend_dir = Path(__file__).parent.parent.parent
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)


class LLMSettings(BaseSettings):
    """LLM configuration settings loaded from environment variables."""
    
    # Groq API Configuration
    groq_api_key: str = Field(
        default_factory=lambda: os.getenv("GROQ_API_KEY", ""),
        description="Groq API key"
    )
    groq_model: str = Field(
        default="openai/gpt-oss-120b",
        description="Groq model name to use"
    )
    groq_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for response generation (0-2)"
    )
    groq_max_output_tokens: int = Field(
        default=2048,
        ge=1,
        le=8000,
        description="Maximum output tokens for responses"
    )
    groq_request_timeout: int = Field(
        default=120,
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
        env_file = str(backend_dir / ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_prefix = "GROQ_"
    
    @field_validator('groq_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is provided (or set to empty string if not configured)."""
        if v:
            return v.strip()
        return ""
    
    @field_validator('groq_model')
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name."""
        if not v or v.strip() == "":
            raise ValueError("GROQ_MODEL must not be empty")
        return v.strip()
    
    def is_configured(self) -> bool:
        """Check if LLM is properly configured."""
        return bool(self.groq_api_key) and self.enabled
    
    def get_safe_config_dict(self) -> dict:
        """
        Get configuration dictionary without sensitive information.
        Safe for logging.
        """
        return {
            "model": self.groq_model,
            "temperature": self.groq_temperature,
            "max_output_tokens": self.groq_max_output_tokens,
            "request_timeout": self.groq_request_timeout,
            "enabled": self.enabled,
            "api_key_configured": bool(self.groq_api_key),
        }


# Load settings
try:
    llm_settings = LLMSettings()
except Exception as e:
    # Create a default settings object that will fail gracefully
    # This allows the app to start but LLM operations will fail
    class DefaultLLMSettings:
        groq_api_key = ""
        groq_model = "openai/gpt-oss-120b"
        groq_temperature = 0.7
        groq_max_output_tokens = 2048
        groq_request_timeout = 120
        enabled = False
        
        def is_configured(self):
            return False
        
        def get_safe_config_dict(self):
            return {"enabled": False, "error": str(e)}
    
    llm_settings = DefaultLLMSettings()


__all__ = ['LLMSettings', 'llm_settings']