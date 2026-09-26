"""
Authentication module for AI-Powered Mock Interview System.
"""

from .password import PasswordManager
from .jwt import JWTManager
from .service import AuthService
from .router import router as auth_router
from .dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    security
)
from .schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
    RefreshTokenRequest,
    ChangePasswordRequest,
    TokenData
)
from .models.user import UserWithPassword, UserRole

__all__ = [
    # Password utilities
    "PasswordManager",
    
    # JWT utilities
    "JWTManager",
    
    # Service
    "AuthService",
    
    # Router
    "auth_router",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user", 
    "get_current_admin_user",
    "security",
    
    # Schemas
    "UserCreate",
    "UserResponse",
    "LoginRequest",
    "Token",
    "RefreshTokenRequest",
    "ChangePasswordRequest",
    "TokenData",
    
    # Models
    "UserWithPassword",
    "UserRole",
]