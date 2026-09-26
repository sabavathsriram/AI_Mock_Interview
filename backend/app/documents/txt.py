"""
TXT document processor for plain text files.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os
import chardet


class TXTProcessor(DocumentProcessor):
    """Processor for TXT documents."""
    
    supported_extensions = ('.txt',)
    mime_types = ('text/plain',)
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from TXT file.
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="txt",
                    success=False,
                    error="File not found"
                )
            
            # Detect encoding
            encoding = 'utf-8'
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    detected = chardet.detect(raw_data)
                    if detected and detected.get('encoding'):
                        encoding = detected['encoding']
            except Exception:
                encoding = 'utf-8'  # Default to UTF-8
            
            try:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    text = f.read()
            except Exception as e:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="txt",
                    success=False,
                    error=f"Failed to read TXT: {str(e)}"
                )
            
            # Normalize the text
            normalized_text = self.normalize_text(text)
            
            line_count = len([l for l in text.split('\n') if l.strip()])
            
            metadata: Dict[str, Any] = {
                "encoding": encoding,
                "line_count": line_count,
                "processor": "chardet"
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="txt",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="txt",
                success=False,
                error=f"TXT extraction failed: {str(e)}"
            )
