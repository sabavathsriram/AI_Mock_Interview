"""
Document processor registry and factory.
"""

from typing import Dict, Optional, List
from app.documents.base import DocumentProcessor
from app.documents.pdf import PDFProcessor
from app.documents.docx import DOCXProcessor
from app.documents.doc import DOCProcessor
from app.documents.txt import TXTProcessor
from app.documents.rtf import RTFProcessor
from app.documents.odt import ODTProcessor
from app.documents.html import HTMLProcessor
from app.documents.markdown import MarkdownProcessor


class DocumentProcessorRegistry:
    """Registry for document processors."""
    
    _processors: Dict[str, DocumentProcessor] = {
        'pdf': PDFProcessor(),
        'docx': DOCXProcessor(),
        'doc': DOCProcessor(),
        'txt': TXTProcessor(),
        'rtf': RTFProcessor(),
        'odt': ODTProcessor(),
        'html': HTMLProcessor(),
        'markdown': MarkdownProcessor(),
    }
    
    # Supported extensions and MIME types
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.txt': 'txt',
        '.rtf': 'rtf',
        '.odt': 'odt',
        '.html': 'html',
        '.htm': 'html',
        '.md': 'markdown',
        '.markdown': 'markdown',
    }
    
    SUPPORTED_MIME_TYPES = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/msword': 'doc',
        'text/plain': 'txt',
        'application/rtf': 'rtf',
        'text/rtf': 'rtf',
        'application/vnd.oasis.opendocument.text': 'odt',
        'text/html': 'html',
        'text/markdown': 'markdown',
        'text/x-markdown': 'markdown',
    }
    
    # Unsupported formats that should be rejected
    UNSUPPORTED_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',  # Images
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',  # Archives
        '.exe', '.dll', '.so', '.dylib',  # Executables
        '.mp4', '.avi', '.mov', '.mkv', '.flv',  # Videos
        '.mp3', '.wav', '.flac', '.aac',  # Audio
        '.xlsx', '.xls', '.csv',  # Spreadsheets (separate from documents)
        '.ppt', '.pptx',  # Presentations (separate from documents)
    }
    
    @classmethod
    def get_processor(cls, file_type: str) -> Optional[DocumentProcessor]:
        """
        Get a processor for the specified file type.
        
        Args:
            file_type: File type key (e.g., 'pdf', 'docx')
            
        Returns:
            DocumentProcessor instance or None if not found
        """
        return cls._processors.get(file_type.lower())
    
    @classmethod
    def get_processor_by_extension(cls, extension: str) -> Optional[DocumentProcessor]:
        """
        Get a processor by file extension.
        
        Args:
            extension: File extension (e.g., '.pdf', '.docx')
            
        Returns:
            DocumentProcessor instance or None if not found
        """
        ext_lower = extension.lower()
        file_type = cls.SUPPORTED_EXTENSIONS.get(ext_lower)
        if file_type:
            return cls.get_processor(file_type)
        return None
    
    @classmethod
    def is_supported(cls, extension: str) -> bool:
        """
        Check if a file extension is supported.
        
        Args:
            extension: File extension (e.g., '.pdf', '.docx')
            
        Returns:
            True if supported, False otherwise
        """
        return extension.lower() in cls.SUPPORTED_EXTENSIONS
    
    @classmethod
    def is_unsupported(cls, extension: str) -> bool:
        """
        Check if a file extension is explicitly unsupported.
        
        Args:
            extension: File extension (e.g., '.jpg', '.exe')
            
        Returns:
            True if unsupported, False otherwise
        """
        return extension.lower() in cls.UNSUPPORTED_EXTENSIONS
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of all supported extensions."""
        return sorted(list(cls.SUPPORTED_EXTENSIONS.keys()))
    
    @classmethod
    def get_unsupported_extensions(cls) -> List[str]:
        """Get list of all unsupported extensions."""
        return sorted(list(cls.UNSUPPORTED_EXTENSIONS))
    
    @classmethod
    def validate_file(cls, filename: str) -> Dict:
        """
        Validate a filename to check support.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dictionary with validation results
        """
        import os
        _, ext = os.path.splitext(filename)
        
        if not ext:
            return {
                'valid': False,
                'reason': 'No file extension found',
                'extension': None
            }
        
        if cls.is_unsupported(ext):
            return {
                'valid': False,
                'reason': f'File type {ext} is not supported for resume upload',
                'extension': ext,
                'is_unsupported': True
            }
        
        if cls.is_supported(ext):
            return {
                'valid': True,
                'extension': ext,
                'file_type': cls.SUPPORTED_EXTENSIONS.get(ext.lower())
            }
        
        return {
            'valid': False,
            'reason': f'File type {ext} is not recognized',
            'extension': ext
        }
