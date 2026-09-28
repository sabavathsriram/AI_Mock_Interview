"""
Resume upload and processing service.
"""

import os
import shutil
import logging
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

from app.database.mongodb import mongodb
from app.database.models import ResumeDocument
from app.documents import DocumentProcessorRegistry
from app.core.config import settings
from bson import ObjectId

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for handling resume uploads and processing."""
    
    # Storage settings
    UPLOAD_BASE_DIR = Path(settings.PROJECT_ROOT) / "uploads"
    TEMP_UPLOAD_DIR = UPLOAD_BASE_DIR / "temp"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @classmethod
    async def initialize_upload_directories(cls):
        """Initialize upload directories if they don't exist."""
        cls.UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_file_extension(cls, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        validation = DocumentProcessorRegistry.validate_file(filename)
        
        if not validation.get('valid'):
            error_msg = validation.get('reason', 'File format not supported')
            return False, error_msg
        
        return True, None
    
    @classmethod
    def validate_file_size(cls, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            file_size: Size of the file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if file_size == 0:
            return False, "File is empty"
        
        if file_size > cls.MAX_FILE_SIZE:
            max_mb = cls.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum allowed size of {max_mb:.1f} MB"
        
        return True, None
    
    @classmethod
    async def validate_file_content(cls, file_path: str, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate actual file content to detect file type.
        
        Args:
            file_path: Path to the file
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        import os
        
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # Read file header (magic bytes)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
        except Exception as e:
            return False, f"Cannot read file: {str(e)}"
        
        # Validate based on file extension
        if ext == '.pdf':
            if not header.startswith(b'%PDF'):
                return False, "File appears to be corrupted or not a valid PDF"
        
        elif ext == '.docx':
            if not header.startswith(b'PK\x03\x04'):  # ZIP file signature
                return False, "File appears to be corrupted or not a valid DOCX"
        
        elif ext == '.doc':
            # DOC files can have various signatures
            if not (header.startswith(b'\xd0\xcf\x11\xe0') or  # OLE2 signature
                    header.startswith(b'PK\x03\x04')):  # Can also be DOCX
                # Allow some leniency for DOC files
                pass
        
        elif ext == '.rtf':
            if not header.startswith(b'{\\rtf'):
                return False, "File appears to be corrupted or not a valid RTF"
        
        elif ext == '.odt':
            if not header.startswith(b'PK\x03\x04'):  # ZIP file signature
                return False, "File appears to be corrupted or not a valid ODT"
        
        elif ext in ['.html', '.htm']:
            # HTML files may start with various things
            try:
                content = header.decode('utf-8', errors='ignore')
                if not any(tag in content.lower() for tag in ['<', '<!', 'html']):
                    return False, "File does not appear to be valid HTML"
            except Exception:
                pass
        
        elif ext in ['.txt']:
            # Text files are generally permissive
            pass
        
        elif ext in ['.md', '.markdown']:
            # Markdown files should be readable as text
            try:
                header.decode('utf-8', errors='replace')
            except Exception:
                return False, "File does not appear to be valid text"
        
        # Check for explicitly unsupported formats based on magic bytes
        if header.startswith(b'\xff\xd8\xff'):  # JPEG
            return False, "Image files (JPG, JPEG) are not supported for resume upload"
        
        if header.startswith(b'\x89PNG'):  # PNG
            return False, "Image files (PNG) are not supported for resume upload"
        
        if header.startswith(b'BM'):  # BMP
            return False, "Image files (BMP) are not supported for resume upload"
        
        if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):  # GIF
            return False, "Image files (GIF) are not supported for resume upload"
        
        if header.startswith(b'PK\x03\x04'):  # ZIP
            # Check if it's actually a ZIP archive and not DOCX/ODT
            if ext not in ['.docx', '.odt']:
                return False, "ZIP archives are not supported for resume upload"
        
        if header.startswith(b'MZ'):  # EXE/DLL
            return False, "Executable files are not supported for resume upload"
        
        if header.startswith(b'\x1a\x45\xdf\xa3'):  # EBML (MKV container)
            return False, "Video files are not supported for resume upload"
        
        return True, None
    
    @classmethod
    async def save_uploaded_file(cls, file_path: str, user_id: str, filename: str) -> Tuple[str, str]:
        """
        Save uploaded file to permanent storage.
        
        Args:
            file_path: Temporary file path
            user_id: User ID (string representation)
            filename: Original filename
            
        Returns:
            Tuple of (permanent_file_path, relative_file_path)
        """
        # Create user-specific directory
        user_upload_dir = cls.UPLOAD_BASE_DIR / user_id
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        base, ext = os.path.splitext(filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{base}_{timestamp}{ext}"
        
        # Permanent path
        permanent_path = user_upload_dir / safe_filename
        
        # Move file from temp to permanent location
        try:
            shutil.move(file_path, str(permanent_path))
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")
        
        # Return both absolute and relative paths
        relative_path = os.path.join(user_id, safe_filename)
        return str(permanent_path), relative_path
    
    @classmethod
    async def extract_resume_text(cls, file_path: str, filename: str) -> dict:
        """
        Extract text from resume file.
        
        Args:
            file_path: Path to the file
            filename: Original filename
            
        Returns:
            Dictionary with extraction results
        """
        import os
        
        _, ext = os.path.splitext(filename)
        
        # Get appropriate processor
        processor = DocumentProcessorRegistry.get_processor_by_extension(ext)
        if not processor:
            return {
                'success': False,
                'error': f'No processor available for {ext} files',
                'text': '',
                'metadata': {}
            }
        
        # Extract text
        result = await processor.extract(file_path)
        
        return {
            'success': result.success,
            'text': result.text,
            'metadata': result.metadata,
            'file_type': result.file_type,
            'error': result.error
        }
    
    @classmethod
    async def save_resume_document(
        cls,
        user_id: str,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        extracted_text: str,
        extraction_metadata: dict,
        display_name: Optional[str] = None,
        is_primary: bool = False
    ) -> Optional[str]:
        """
        Save resume document metadata and extracted text to MongoDB.
        
        Args:
            user_id: User ID
            filename: Original filename
            file_path: Path to stored file
            file_size: File size in bytes
            mime_type: MIME type
            extracted_text: Extracted text content
            extraction_metadata: Metadata from extraction
            display_name: Optional display name
            is_primary: Whether this is the primary resume
            
        Returns:
            Document ID if successful, None otherwise
        """
        import os
        _, ext = os.path.splitext(filename)
        file_type = ext.lstrip('.')
        
        resume_doc = ResumeDocument(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            extracted_text=extracted_text,
            extraction_metadata=extraction_metadata,
            extraction_status="completed",
            is_primary=is_primary,
            display_name=display_name or filename,
            uploaded_at=datetime.utcnow()
        )
        
        # Save to MongoDB
        collection = mongodb.get_collection("resume_documents")
        
        # If setting as primary, unset other primary resumes for this user
        if is_primary:
            await collection.update_many(
                {"user_id": user_id},
                {"$set": {"is_primary": False}}
            )
        
        try:
            result = await collection.insert_one(resume_doc.dict(by_alias=True))
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Failed to save resume document: {str(e)}")
    
    @classmethod
    async def get_user_resumes(cls, user_id: str) -> list:
        """
        Get all resumes for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of resume documents
        """
        collection = mongodb.get_collection("resume_documents")
        
        resumes = await collection.find(
            {"user_id": user_id}
        ).sort("uploaded_at", -1).to_list(None)
        
        # Convert ObjectId to string
        for resume in resumes:
            if "_id" in resume:
                resume["_id"] = str(resume["_id"])
        
        return resumes
    
    @classmethod
    async def get_resume_by_id(cls, resume_id: str, user_id: str) -> Optional[dict]:
        """
        Get a specific resume by ID.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID (for validation)
            
        Returns:
            Resume document or None
        """
        collection = mongodb.get_collection("resume_documents")
        
        try:
            resume = await collection.find_one({
                "_id": ObjectId(resume_id),
                "user_id": user_id
            })
            
            if resume and "_id" in resume:
                resume["_id"] = str(resume["_id"])
            
            return resume
        except Exception:
            return None
    
    @classmethod
    async def link_intelligence_profile(
        cls,
        resume_id: str,
        user_id: str,
        profile_id: str
    ) -> bool:
        """
        Link a candidate intelligence profile to a resume document.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID
            profile_id: Candidate profile ID
            
        Returns:
            True if successful, False otherwise
        """
        collection = mongodb.get_collection("resume_documents")
        
        try:
            result = await collection.update_one(
                {
                    "_id": ObjectId(resume_id),
                    "user_id": user_id
                },
                {
                    "$set": {
                        "intelligence_profile_id": profile_id,
                        "intelligence_status": "completed",
                        "intelligence_analyzed_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"Failed to link intelligence profile: {str(e)}")
            return False
    
    @classmethod
    async def update_intelligence_status(
        cls,
        resume_id: str,
        user_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update intelligence analysis status on resume document.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID
            status: New status (pending, analyzing, completed, failed)
            error_message: Error message if failed
            
        Returns:
            True if successful, False otherwise
        """
        collection = mongodb.get_collection("resume_documents")
        
        try:
            update_data = {
                "intelligence_status": status
            }
            
            if error_message:
                update_data["intelligence_error"] = error_message
            
            if status == "completed":
                update_data["intelligence_analyzed_at"] = datetime.utcnow()
            
            result = await collection.update_one(
                {
                    "_id": ObjectId(resume_id),
                    "user_id": user_id
                },
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        
        except Exception as e:
            logger.error(f"Failed to update intelligence status: {str(e)}")
            return False
    
    @classmethod
    async def delete_resume(cls, resume_id: str, user_id: str) -> bool:
        """
        Delete a resume document.
        
        Args:
            resume_id: Resume document ID
            user_id: User ID (for validation)
            
        Returns:
            True if deleted, False otherwise
        """
        collection = mongodb.get_collection("resume_documents")
        
        try:
            # Get resume to find file path
            resume = await cls.get_resume_by_id(resume_id, user_id)
            
            if not resume:
                return False
            
            # Delete file from storage
            file_path = resume.get('file_path')
            if file_path:
                full_path = cls.UPLOAD_BASE_DIR / file_path
                if full_path.exists():
                    try:
                        os.remove(full_path)
                    except Exception:
                        pass  # Continue even if file deletion fails
            
            # Delete from MongoDB
            result = await collection.delete_one({
                "_id": ObjectId(resume_id),
                "user_id": user_id
            })
            
            return result.deleted_count > 0
        
        except Exception:
            return False
