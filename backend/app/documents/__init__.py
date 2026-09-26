"""
Document processing module for resume extraction.
"""

from app.documents.base import DocumentProcessor, ExtractionResult
from app.documents.registry import DocumentProcessorRegistry

__all__ = [
    'DocumentProcessor',
    'ExtractionResult',
    'DocumentProcessorRegistry',
]
