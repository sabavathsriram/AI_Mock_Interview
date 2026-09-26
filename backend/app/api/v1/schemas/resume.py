"""
Resume upload and management schemas.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    """Response schema for resume upload."""
    
    id: str = Field(..., description="Resume document ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File format")
    file_size: int = Field(..., description="File size in bytes")
    display_name: str = Field(..., description="Display name")
    is_primary: bool = Field(..., description="Whether this is the primary resume")
    extracted_text: str = Field(..., description="Extracted text content")
    extraction_metadata: Dict[str, Any] = Field(..., description="Extraction metadata")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "filename": "john_doe_resume.pdf",
                "file_type": "pdf",
                "file_size": 102400,
                "display_name": "Main Resume",
                "is_primary": True,
                "extracted_text": "John Doe\nSoftware Engineer\n...",
                "extraction_metadata": {"page_count": 2},
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }


class ResumeDetailResponse(BaseModel):
    """Detailed resume response."""
    
    id: str
    filename: str
    file_type: str
    file_size: int
    mime_type: str
    display_name: str
    is_primary: bool
    extraction_status: str
    extraction_error: Optional[str] = None
    extraction_metadata: Dict[str, Any]
    uploaded_at: datetime
    last_accessed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "filename": "john_doe_resume.pdf",
                "file_type": "pdf",
                "file_size": 102400,
                "mime_type": "application/pdf",
                "display_name": "Main Resume",
                "is_primary": True,
                "extraction_status": "success",
                "extraction_metadata": {"page_count": 2, "processor": "PyPDF2"},
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }


class ResumeListResponse(BaseModel):
    """List of user resumes."""
    
    resumes: list[ResumeDetailResponse] = Field(..., description="List of resumes")
    total_count: int = Field(..., description="Total number of resumes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resumes": [],
                "total_count": 0
            }
        }


class ResumeDeleteResponse(BaseModel):
    """Response for resume deletion."""
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")


class FileSupportInfo(BaseModel):
    """Information about supported file formats."""
    
    supported_formats: list[str] = Field(..., description="List of supported file extensions")
    unsupported_formats: list[str] = Field(..., description="List of explicitly unsupported formats")
    max_file_size_mb: float = Field(..., description="Maximum file size in MB")
    max_file_size_bytes: int = Field(..., description="Maximum file size in bytes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "supported_formats": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".html", ".md"],
                "unsupported_formats": [".jpg", ".png", ".zip", ".exe"],
                "max_file_size_mb": 10.0,
                "max_file_size_bytes": 10485760
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error code or type")
    detail: str = Field(..., description="Detailed error message")
    timestamp: datetime = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "unsupported_file_type",
                "detail": "Image files (JPG, JPEG) are not supported for resume upload",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
