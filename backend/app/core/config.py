"""
Application configuration settings.
"""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "AI-Powered Mock Interview System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Project directories
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent
    
    # Server
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    
    # CORS - Using string for simplicity, will parse in middleware
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # MongoDB Configuration
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_mock_interview_db"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # LLM Configuration (Google Gemini) - loaded by LLMSettings with env_prefix
    # These are declared here to allow the Settings class to accept them without validation errors
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = ""
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_OUTPUT_TOKENS: int = 2048
    GEMINI_REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields to support modular configuration
        extra = "ignore"


settings = Settings()