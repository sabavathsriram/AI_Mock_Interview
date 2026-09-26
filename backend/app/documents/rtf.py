"""
RTF document processor for Rich Text Format files.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os
import re


class RTFProcessor(DocumentProcessor):
    """Processor for RTF documents."""
    
    supported_extensions = ('.rtf',)
    mime_types = ('application/rtf', 'text/rtf')
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from RTF file.
        
        Args:
            file_path: Path to the RTF file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="rtf",
                    success=False,
                    error="File not found"
                )
            
            try:
                with open(file_path, 'r', encoding='latin-1', errors='replace') as f:
                    rtf_content = f.read()
            except Exception as e:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="rtf",
                    success=False,
                    error=f"Failed to read RTF: {str(e)}"
                )
            
            # Extract text from RTF using regex
            text = self._extract_text_from_rtf(rtf_content)
            
            # Normalize the text
            normalized_text = self.normalize_text(text)
            
            metadata: Dict[str, Any] = {
                "processor": "regex-based",
                "format": "rtf"
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="rtf",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="rtf",
                success=False,
                error=f"RTF extraction failed: {str(e)}"
            )
    
    @staticmethod
    def _extract_text_from_rtf(rtf_content: str) -> str:
        """
        Extract plain text from RTF content using regex patterns.
        
        Args:
            rtf_content: Raw RTF file content
            
        Returns:
            Extracted plain text
        """
        # Remove RTF control words and groups
        # RTF format: control words start with \ followed by letters
        
        # Remove RTF header
        text = rtf_content
        text = re.sub(r'\\[a-z]+\d*\s?', ' ', text, flags=re.IGNORECASE)
        
        # Remove escaped characters
        text = re.sub(r"\\[{}]", '', text)
        
        # Remove braces (RTF structure)
        text = re.sub(r'[{}]', '', text)
        
        # Remove special RTF content
        text = re.sub(r'\\\*[^\\]*', '', text)
        
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up
        text = text.strip()
        
        return text
