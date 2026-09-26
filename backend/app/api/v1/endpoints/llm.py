"""
LLM Test Endpoints
Protected endpoints for testing LLM integration
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.llm import llm_service, LLMConfigurationError, LLMException, PromptType


router = APIRouter(prefix="/llm", tags=["llm"])


# Response Models
class LLMHealthResponse(BaseModel):
    """Health check response for LLM service."""
    status: str
    configured: bool
    model: str
    timestamp: datetime
    message: str


class LLMTestRequest(BaseModel):
    """Request model for LLM test."""
    prompt: str = "Say hello and confirm the LLM integration is working"
    temperature: float = 0.7


class LLMTestResponse(BaseModel):
    """Response model for LLM test."""
    success: bool
    response: str
    model: str
    timestamp: datetime
    message: str


# Health Check Endpoint
@router.get("/health", response_model=LLMHealthResponse)
async def llm_health_check():
    """
    Check LLM service health and configuration.
    
    Returns:
        LLMHealthResponse with service status
    """
    if not llm_service.is_configured():
        return LLMHealthResponse(
            status="unconfigured",
            configured=False,
            model="N/A",
            timestamp=datetime.utcnow(),
            message="LLM service is not configured. Set GEMINI_API_KEY environment variable."
        )
    
    return LLMHealthResponse(
        status="healthy",
        configured=True,
        model=llm_service.model_name,
        timestamp=datetime.utcnow(),
        message="LLM service is ready"
    )


# Protected Test Endpoint
@router.post("/test", response_model=LLMTestResponse)
async def test_llm_integration(
    request: LLMTestRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Test LLM integration with a simple prompt.
    
    This endpoint is protected and requires authentication.
    
    Args:
        request: LLMTestRequest with prompt and parameters
        current_user: Current authenticated user
        
    Returns:
        LLMTestResponse with the generated response
        
    Raises:
        HTTPException: If LLM is not configured or request fails
    """
    if not llm_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM service is not configured. Set GEMINI_API_KEY environment variable."
        )
    
    try:
        # Generate text using the service
        response = await llm_service.generate_text(
            prompt=request.prompt,
            temperature=request.temperature,
            system_prompt="You are a helpful AI assistant for the AI-Powered Mock Interview System."
        )
        
        return LLMTestResponse(
            success=True,
            response=response.text,
            model=response.model,
            timestamp=response.timestamp,
            message="LLM integration test successful"
        )
    
    except LLMConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM configuration error: {str(e)}"
        )
    
    except LLMException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM service error: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during LLM test: {str(e)}"
        )


# Info Endpoint
@router.get("/info")
async def get_llm_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about available LLM features and prompts.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary with LLM configuration and available prompts
    """
    from app.llm import prompt_library
    
    return {
        "configured": llm_service.is_configured(),
        "model": llm_service.model_name,
        "config": llm_service.configured if llm_service.is_configured() else None,
        "available_prompts": prompt_library.list_prompts(),
        "timestamp": datetime.utcnow()
    }


__all__ = ['router']
