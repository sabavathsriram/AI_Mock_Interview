"""
API schemas for version 1.
"""

from app.api.v1.schemas.resume import (
    ResumeUploadResponse,
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeDeleteResponse,
    FileSupportInfo,
    ErrorResponse,
)

__all__ = [
    "ResumeUploadResponse",
    "ResumeDetailResponse",
    "ResumeListResponse",
    "ResumeDeleteResponse",
    "FileSupportInfo",
    "ErrorResponse",
]
