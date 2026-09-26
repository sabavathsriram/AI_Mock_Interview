"""
Base document processor for all file formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Result of document text extraction."""
    text: str
    metadata: Dict[str, Any]
    file_type: str
    success: bool
    error: str = None


class DocumentProcessor(ABC):
    """Abstract base class for document processors."""
    
    supported_extensions: tuple = ()
    mime_types: tuple = ()
    
    @abstractmethod
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from the document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        pass
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize extracted text to a common format.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines
        
        # Join with single newlines
        normalized = '\n'.join(lines)
        
        # Remove multiple spaces
        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
