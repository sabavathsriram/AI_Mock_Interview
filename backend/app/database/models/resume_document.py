"""
Resume document model for MongoDB - stores uploaded resume files and extracted text.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field, HttpUrl

from .base import BaseDBModel


class ResumeDocument(BaseDBModel):
    """Resume document model for storing uploaded resumes."""
    
    user_id: str = Field(..., description="Reference to User ID")
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename")
    file_type: str = Field(..., min_length=2, max_length=10, description="File format (pdf, docx, txt, etc.)")
    file_path: str = Field(..., description="Path to stored file (relative to storage directory)")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    
    # Extracted content
    extracted_text: str = Field(..., description="Extracted plain text from the document")
    extraction_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from text extraction (page count, encoding, etc.)"
    )
    
    # Processing information
    extraction_status: str = Field(
        default="success",
        pattern="^(pending|success|failed)$",
        description="Status of text extraction"
    )
    extraction_error: Optional[str] = Field(None, description="Error message if extraction failed")
    
    # Resume information
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary resume for the user"
    )
    display_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User-friendly name for this resume"
    )
    
    # Timestamps
    uploaded_at: datetime = Field(..., description="When the file was uploaded")
    last_accessed_at: Optional[datetime] = Field(
        default=None,
        description="When the resume was last accessed"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "filename": "john_doe_resume.pdf",
                "file_type": "pdf",
                "file_path": "uploads/507f1f77bcf86cd799439011/john_doe_resume.pdf",
                "file_size": 102400,
                "mime_type": "application/pdf",
                "extracted_text": "John Doe\nSoftware Engineer\n...",
                "extraction_metadata": {"page_count": 2, "processor": "PyPDF2"},
                "extraction_status": "success",
                "is_primary": True,
                "display_name": "Main Resume",
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }
