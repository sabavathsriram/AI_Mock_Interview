"""
Resume upload and management endpoints.
"""

import os
import mimetypes
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import FileResponse

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.services.resume_service import ResumeService
from app.services.resume_intelligence_agent import ResumeIntelligenceAgent
from app.api.v1.schemas.resume import (
    ResumeUploadResponse,
    ResumeDetailResponse,
    ResumeListResponse,
    ResumeDeleteResponse,
    FileSupportInfo,
    ErrorResponse,
    ResumeIntelligenceResponse
)
from app.documents import DocumentProcessorRegistry
from app.core.config import settings


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    display_name: Optional[str] = None,
    is_primary: bool = False,
    current_user: User = Depends(get_current_active_user)
) -> ResumeUploadResponse:
    """
    Upload and process a resume document.
    
    Supported formats: PDF, DOCX, DOC, TXT, RTF, ODT, HTML, Markdown
    Maximum file size: 10 MB
    
    Returns:
        ResumeUploadResponse with extracted text and metadata
    """
    
    # Ensure upload directories are initialized
    await ResumeService.initialize_upload_directories()
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    # Validate file extension
    is_valid_ext, ext_error = ResumeService.validate_file_extension(file.filename)
    if not is_valid_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ext_error
        )
    
    # Check file size before reading
    # Note: file.size might not be available, so we'll check as we read
    temp_file_path = ResumeService.TEMP_UPLOAD_DIR / f"temp_{file.filename}"
    
    try:
        # Read and save file temporarily
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        is_valid_size, size_error = ResumeService.validate_file_size(file_size)
        if not is_valid_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=size_error
            )
        
        # Write to temporary file
        with open(temp_file_path, 'wb') as f:
            f.write(content)
        
        # Validate file content
        is_valid_content, content_error = await ResumeService.validate_file_content(
            str(temp_file_path), file.filename
        )
        if not is_valid_content:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=content_error
            )
        
        # Extract text from document
        extraction_result = await ResumeService.extract_resume_text(
            str(temp_file_path),
            file.filename
        )
        
        if not extraction_result['success']:
            os.remove(temp_file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from document: {extraction_result.get('error', 'Unknown error')}"
            )
        
        # Save file to permanent storage
        permanent_path, relative_path = await ResumeService.save_uploaded_file(
            str(temp_file_path),
            str(current_user.id),
            file.filename
        )
        
        # Determine MIME type
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        
        # Save resume document to MongoDB
        resume_id = await ResumeService.save_resume_document(
            user_id=str(current_user.id),
            filename=file.filename,
            file_path=relative_path,
            file_size=file_size,
            mime_type=mime_type,
            extracted_text=extraction_result['text'],
            extraction_metadata=extraction_result['metadata'],
            display_name=display_name or file.filename,
            is_primary=is_primary
        )
        
        return ResumeUploadResponse(
            id=resume_id,
            filename=file.filename,
            file_type=extraction_result['file_type'],
            file_size=file_size,
            display_name=display_name or file.filename,
            is_primary=is_primary,
            extracted_text=extraction_result['text'][:1000],  # Return first 1000 chars
            extraction_metadata=extraction_result['metadata'],
            uploaded_at=__import__('datetime').datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/list", response_model=ResumeListResponse)
async def list_resumes(
    current_user: User = Depends(get_current_active_user)
) -> ResumeListResponse:
    """
    Get all resumes for the current user.
    
    Returns:
        List of resume documents with metadata
    """
    try:
        resumes = await ResumeService.get_user_resumes(str(current_user.id))
        
        resume_details = [
            ResumeDetailResponse(
                id=resume['_id'],
                filename=resume['filename'],
                file_type=resume['file_type'],
                file_size=resume['file_size'],
                mime_type=resume['mime_type'],
                display_name=resume.get('display_name', resume['filename']),
                is_primary=resume.get('is_primary', False),
                extraction_status=resume.get('extraction_status', 'unknown'),
                extraction_error=resume.get('extraction_error'),
                extraction_metadata=resume.get('extraction_metadata', {}),
                extracted_text=resume.get('extracted_text'),
                uploaded_at=resume['uploaded_at'],
                last_accessed_at=resume.get('last_accessed_at')
            )
            for resume in resumes
        ]
        
        return ResumeListResponse(
            resumes=resume_details,
            total_count=len(resume_details)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resumes: {str(e)}"
        )


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ResumeDetailResponse:
    """
    Get a specific resume with its extracted text.
    
    Args:
        resume_id: ID of the resume to retrieve
        
    Returns:
        Resume document details
    """
    try:
        resume = await ResumeService.get_resume_by_id(resume_id, str(current_user.id))
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        return ResumeDetailResponse(
            id=resume['_id'],
            filename=resume['filename'],
            file_type=resume['file_type'],
            file_size=resume['file_size'],
            mime_type=resume['mime_type'],
            display_name=resume.get('display_name', resume['filename']),
            is_primary=resume.get('is_primary', False),
            extraction_status=resume.get('extraction_status', 'unknown'),
            extraction_error=resume.get('extraction_error'),
            extraction_metadata=resume.get('extraction_metadata', {}),
            extracted_text=resume.get('extracted_text'),
            uploaded_at=resume['uploaded_at'],
            last_accessed_at=resume.get('last_accessed_at')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resume: {str(e)}"
        )


@router.delete("/{resume_id}", response_model=ResumeDeleteResponse)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ResumeDeleteResponse:
    """
    Delete a resume document.
    
    Args:
        resume_id: ID of the resume to delete
        
    Returns:
        Deletion status
    """
    try:
        success = await ResumeService.delete_resume(resume_id, str(current_user.id))
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or could not be deleted"
            )
        
        return ResumeDeleteResponse(
            success=True,
            message="Resume deleted successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting resume: {str(e)}"
        )


@router.get("/text/{resume_id}")
async def get_resume_text(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the full extracted text from a resume.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        Full extracted text
    """
    try:
        resume = await ResumeService.get_resume_by_id(resume_id, str(current_user.id))
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        return {
            "resume_id": resume['_id'],
            "filename": resume['filename'],
            "file_type": resume['file_type'],
            "extracted_text": resume.get('extracted_text', ''),
            "extraction_metadata": resume.get('extraction_metadata', {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resume text: {str(e)}"
        )


@router.get("/info/supported-formats", response_model=FileSupportInfo)
async def get_supported_formats() -> FileSupportInfo:
    """
    Get information about supported file formats.
    
    Returns:
        Information about supported and unsupported formats
    """
    max_size = ResumeService.MAX_FILE_SIZE
    max_size_mb = max_size / (1024 * 1024)
    
    return FileSupportInfo(
        supported_formats=DocumentProcessorRegistry.get_supported_extensions(),
        unsupported_formats=DocumentProcessorRegistry.get_unsupported_extensions(),
        max_file_size_mb=max_size_mb,
        max_file_size_bytes=max_size
    )


@router.post("/{resume_id}/analyze", response_model=ResumeIntelligenceResponse)
async def analyze_resume(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ResumeIntelligenceResponse:
    """
    Trigger resume intelligence analysis to extract structured candidate profile.
    
    This endpoint will analyze the resume using an LLM and extract:
    - Candidate name, contact info
    - Education and certifications
    - Skills (organized by category)
    - Work experience and internships
    - Projects and achievements
    - Other relevant information
    
    Args:
        resume_id: ID of the resume to analyze
        
    Returns:
        Structured candidate profile
    """
    try:
        user_id = str(current_user.id)
        
        # Get resume document
        resume = await ResumeService.get_resume_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Check extraction status
        if resume.get("extraction_status") != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resume extraction not completed. Status: {resume.get('extraction_status')}"
            )
        
        extracted_text = resume.get("extracted_text", "")
        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No extracted text available for analysis"
            )
        
        # Update status to analyzing
        await ResumeService.update_intelligence_status(resume_id, user_id, "analyzing")
        
        # Analyze resume using intelligence agent
        success, profile, error_msg = await ResumeIntelligenceAgent.analyze_resume(
            resume_id=resume_id,
            user_id=user_id,
            extracted_text=extracted_text
        )
        
        if not success:
            # Update status to failed
            await ResumeService.update_intelligence_status(
                resume_id, user_id, "failed", error_msg
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resume analysis failed: {error_msg}"
            )
        
        # Save profile to MongoDB
        profile_id = await ResumeIntelligenceAgent.save_profile(profile)
        if not profile_id:
            await ResumeService.update_intelligence_status(
                resume_id, user_id, "failed", "Failed to save profile"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save candidate profile"
            )
        
        # Link profile to resume
        await ResumeService.link_intelligence_profile(resume_id, user_id, profile_id)
        
        return ResumeIntelligenceResponse(
            resume_id=resume_id,
            status="completed",
            profile=profile.dict(),
            llm_model_used=profile.llm_model_used,
            analyzed_at=profile.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        )


@router.get("/{resume_id}/intelligence", response_model=ResumeIntelligenceResponse)
async def get_resume_intelligence(
    resume_id: str,
    current_user: User = Depends(get_current_active_user)
) -> ResumeIntelligenceResponse:
    """
    Retrieve the resume intelligence profile for a resume.
    
    If analysis is not yet complete, returns current status.
    If analysis failed, returns error message.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        Resume intelligence profile or status
    """
    try:
        user_id = str(current_user.id)
        
        # Get resume document
        resume = await ResumeService.get_resume_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        intelligence_status = resume.get("intelligence_status", "pending")
        
        # If not yet analyzed, return status
        if intelligence_status in ["pending", "analyzing"]:
            return ResumeIntelligenceResponse(
                resume_id=resume_id,
                status=intelligence_status,
                profile=None,
                error=None
            )
        
        # If failed, return error
        if intelligence_status == "failed":
            return ResumeIntelligenceResponse(
                resume_id=resume_id,
                status="failed",
                profile=None,
                error=resume.get("intelligence_error", "Analysis failed")
            )
        
        # If completed, get profile
        profile_id = resume.get("intelligence_profile_id")
        if not profile_id:
            return ResumeIntelligenceResponse(
                resume_id=resume_id,
                status="pending",
                profile=None,
                error=None
            )
        
        # Retrieve profile from MongoDB
        profile = await ResumeIntelligenceAgent.get_profile(resume_id, user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found"
            )
        
        return ResumeIntelligenceResponse(
            resume_id=resume_id,
            status="completed",
            profile=profile,
            llm_model_used=profile.get("llm_model_used"),
            analyzed_at=profile.get("created_at")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving resume intelligence: {str(e)}"
        )
