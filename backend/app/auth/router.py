"""
Authentication router with API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.auth.service import AuthService
from app.auth.dependencies.auth import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user
)
from app.auth.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    Token,
    RefreshTokenRequest,
    ChangePasswordRequest
)
from app.auth.models.user import UserWithPassword as User

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        UserResponse: The created user
        
    Raises:
        HTTPException: If user already exists
    """
    try:
        return await AuthService.register_user(user_data)
    except HTTPException:
        # Re-raise HTTPExceptions from the service
        raise
    except Exception as e:
        # Catch any other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Login user and get JWT tokens.
    
    Args:
        login_data: Login credentials
        
    Returns:
        Token: JWT access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        return await AuthService.login_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        
    Returns:
        Token: New JWT access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        return await AuthService.refresh_token(request.refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password.
    
    Args:
        password_data: Password change data
        current_user: Current authenticated user
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If current password is incorrect
    """
    try:
        success = await AuthService.change_password(
            str(current_user.id),
            password_data.current_password,
            password_data.new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/protected-test")
async def protected_test(current_user: User = Depends(get_current_active_user)):
    """
    Test endpoint for protected routes.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Test message with user info
    """
    return {
        "message": "This is a protected endpoint",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role
    }


@router.get("/admin-test")
async def admin_test(current_user: User = Depends(get_current_admin_user)):
    """
    Test endpoint for admin-only routes.
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        dict: Test message with user info
    """
    return {
        "message": "This is an admin-only endpoint",
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role
    }


@router.get("/health")
async def auth_health():
    """
    Authentication health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "healthy", "service": "authentication"}
