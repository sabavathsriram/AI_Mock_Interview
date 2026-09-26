"""
Authentication dependencies for protected routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.auth.jwt import JWTManager
from app.auth.schemas.auth import TokenData
from app.database.mongodb import mongodb
from app.auth.models.user import UserWithPassword as User

# HTTP Bearer security scheme
security = HTTPBearer()


class AuthException(Exception):
    """Base authentication exception."""
    pass


class InvalidTokenException(AuthException):
    """Invalid token exception."""
    pass


class UserNotFoundException(AuthException):
    """User not found exception."""
    pass


class InactiveUserException(AuthException):
    """Inactive user exception."""
    pass


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = JWTManager.verify_token(token)
        
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user_collection = mongodb.get_collection("users")
    from bson import ObjectId
    user_data = await user_collection.find_one({"_id": ObjectId(token_data.user_id)})
    
    if user_data is None:
        raise credentials_exception
    
    if not user_data.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Convert ObjectId to string for Pydantic
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])
    
    return User(**user_data)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get the current authenticated and active user.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The authenticated and active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to get the current authenticated admin user.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User: The authenticated admin user
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user