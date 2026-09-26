"""
User model/schema for MongoDB.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import Field, EmailStr

from .base import BaseDBModel


class UserRole(str, Enum):
    """User roles enum."""
    CANDIDATE = "candidate"
    ADMIN = "admin"
    INTERVIEWER = "interviewer"


class User(BaseDBModel):
    """User document model."""
    
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.CANDIDATE
    is_active: bool = True
    last_login: Optional[datetime] = None
    
    # Profile information
    phone_number: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    # Preferences
    preferred_interview_languages: List[str] = Field(default_factory=list)
    notification_settings: dict = Field(default_factory=lambda: {
        "email_notifications": True,
        "interview_reminders": True,
        "feedback_alerts": True
    })
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role": "candidate",
                "phone_number": "+1234567890",
                "location": "New York, USA",
                "bio": "Software engineer with 5 years of experience"
            }
        }