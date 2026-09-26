"""
PDF document processor using PyPDF2.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os


class PDFProcessor(DocumentProcessor):
    """Processor for PDF documents."""
    
    supported_extensions = ('.pdf',)
    mime_types = ('application/pdf',)
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            import PyPDF2
            
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="pdf",
                    success=False,
                    error="File not found"
                )
            
            text = ""
            page_count = 0
            
            with open(file_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            text += f"\n--- Page {page_num + 1} ---\n"
                            text += page.extract_text()
                        except Exception as e:
                            text += f"\n[Error extracting page {page_num + 1}: {str(e)}]\n"
                except Exception as e:
                    return ExtractionResult(
                        text="",
                        metadata={},
                        file_type="pdf",
                        success=False,
                        error=f"Failed to read PDF: {str(e)}"
                    )
            
            # Normalize the text
            normalized_text = self.normalize_text(text)
            
            metadata: Dict[str, Any] = {
                "page_count": page_count,
                "processor": "PyPDF2"
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="pdf",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="pdf",
                success=False,
                error=f"PDF extraction failed: {str(e)}"
            )
