"""
Authentication service for user registration and login.
"""

from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status

from app.auth.password import PasswordManager
from app.auth.jwt import JWTManager
from app.auth.schemas.auth import UserCreate, UserResponse, LoginRequest, Token
from app.auth.models.user import UserWithPassword, UserRole
from app.database.mongodb import mongodb


class AuthService:
    """Authentication service for user management."""
    
    @staticmethod
    async def register_user(user_data: UserCreate) -> UserResponse:
        """
        Register a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            UserResponse: The created user
            
        Raises:
            HTTPException: If user already exists or validation fails
        """
        # Check if user already exists
        user_collection = mongodb.get_collection("users")
        existing_user = await user_collection.find_one({"email": user_data.email})
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        hashed_password = PasswordManager.hash_password(user_data.password)
        
        # Create user document
        user_doc = UserWithPassword(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=UserRole.CANDIDATE,
            is_active=True
        )
        
        # Insert user into database
        result = await user_collection.insert_one(user_doc.dict(by_alias=True))
        
        # Get the created user
        created_user = await user_collection.find_one({"_id": result.inserted_id})
        
        # Convert to response schema
        return UserResponse(
            id=str(created_user["_id"]),
            email=created_user["email"],
            full_name=created_user["full_name"],
            role=created_user["role"],
            is_active=created_user["is_active"],
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"]
        )
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[UserWithPassword]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Optional[UserWithPassword]: The authenticated user or None
        """
        user_collection = mongodb.get_collection("users")
        user_data = await user_collection.find_one({"email": email})
        
        if not user_data:
            return None
        
        # Convert ObjectId to string for Pydantic
        if "_id" in user_data:
            user_data["_id"] = str(user_data["_id"])
        
        user = UserWithPassword(**user_data)
        
        # Verify password
        if not PasswordManager.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    async def login_user(login_data: LoginRequest) -> Token:
        """
        Login a user and return JWT tokens.
        
        Args:
            login_data: Login credentials
            
        Returns:
            Token: JWT access and refresh tokens
            
        Raises:
            HTTPException: If authentication fails
        """
        # Authenticate user
        user = await AuthService.authenticate_user(
            login_data.email,
            login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Update last login
        user_collection = mongodb.get_collection("users")
        await user_collection.update_one(
            {"_id": user.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = JWTManager.create_access_token(token_data)
        refresh_token = JWTManager.create_refresh_token(token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60  # 30 minutes in seconds
        )
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            Token: New JWT access and refresh tokens
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Verify refresh token
        payload = JWTManager.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user exists and is active
        user_collection = mongodb.get_collection("users")
        user_data = await user_collection.find_one({"_id": user_id})
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user_data.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create new tokens
        token_data = {"sub": user_id, "email": email}
        new_access_token = JWTManager.create_access_token(token_data)
        new_refresh_token = JWTManager.create_refresh_token(token_data)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=30 * 60  # 30 minutes in seconds
        )
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[UserResponse]: User data or None
        """
        user_collection = mongodb.get_collection("users")
        user_data = await user_collection.find_one({"_id": user_id})
        
        if not user_data:
            return None
        
        return UserResponse(
            id=str(user_data["_id"]),
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"]
        )
    
    @staticmethod
    async def change_password(
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully
            
        Raises:
            HTTPException: If current password is incorrect or user not found
        """
        user_collection = mongodb.get_collection("users")
        user_data = await user_collection.find_one({"_id": user_id})
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not PasswordManager.verify_password(
            current_password,
            user_data["hashed_password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = PasswordManager.hash_password(new_password)
        
        # Update password
        await user_collection.update_one(
            {"_id": user_id},
            {"$set": {"hashed_password": new_hashed_password}}
        )
        
        return True