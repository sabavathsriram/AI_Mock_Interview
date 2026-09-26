"""
API router for version 1 endpoints.
"""

from fastapi import APIRouter

# Import endpoint routers
from app.api.v1.endpoints import resumes, llm, resume_intelligence, rag

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(resumes.router)
api_router.include_router(llm.router)
api_router.include_router(resume_intelligence.router, prefix="/resumes")
api_router.include_router(rag.router)

# Placeholder endpoint for now
@api_router.get("/")
async def api_v1_root():
    """API v1 root endpoint."""
    return {
        "message": "AI-Powered Mock Interview API v1",
        "endpoints": [
            "/interviews (coming soon)",
            "/users (coming soon)",
            "/feedback (coming soon)",
        ]
    }