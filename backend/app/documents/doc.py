"""
DOC document processor for legacy Word format.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os


class DOCProcessor(DocumentProcessor):
    """Processor for DOC (legacy Word) documents."""
    
    supported_extensions = ('.doc',)
    mime_types = ('application/msword',)
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from DOC file.
        
        For legacy .doc files, we attempt conversion or use available tools.
        Note: Full .doc support requires additional libraries like python-docx
        with proper OLE2 compound file support or external tools.
        
        Args:
            file_path: Path to the DOC file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="doc",
                    success=False,
                    error="File not found"
                )
            
            # Try to use python-docx which has some .doc support
            try:
                from docx import Document
                doc = Document(file_path)
                
                text = ""
                paragraph_count = 0
                table_count = 0
                
                # Extract text from paragraphs
                for para in doc.paragraphs:
                    if para.text.strip():
                        text += para.text + "\n"
                        paragraph_count += 1
                
                # Extract text from tables
                for table in doc.tables:
                    table_count += 1
                    text += "\n[TABLE]\n"
                    for row in table.rows:
                        row_text = " | ".join(cell.text for cell in row.cells)
                        if row_text.strip():
                            text += row_text + "\n"
                
                # Normalize the text
                normalized_text = self.normalize_text(text)
                
                metadata: Dict[str, Any] = {
                    "paragraph_count": paragraph_count,
                    "table_count": table_count,
                    "processor": "python-docx",
                    "format": "doc"
                }
                
                return ExtractionResult(
                    text=normalized_text,
                    metadata=metadata,
                    file_type="doc",
                    success=True
                )
            
            except Exception as docx_error:
                # Try alternative method: read as binary and extract some text
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Very basic extraction: look for readable strings
                    text = ""
                    current_word = ""
                    for byte in content:
                        char = chr(byte)
                        if 32 <= byte <= 126:  # Printable ASCII
                            current_word += char
                        else:
                            if len(current_word) > 3:  # Only keep words of 4+ chars
                                text += current_word + " "
                            current_word = ""
                    
                    if len(current_word) > 3:
                        text += current_word
                    
                    # Normalize the text
                    normalized_text = self.normalize_text(text)
                    
                    metadata: Dict[str, Any] = {
                        "processor": "binary-extraction",
                        "format": "doc",
                        "note": "Partial extraction from binary content"
                    }
                    
                    return ExtractionResult(
                        text=normalized_text,
                        metadata=metadata,
                        file_type="doc",
                        success=True
                    )
                
                except Exception as binary_error:
                    return ExtractionResult(
                        text="",
                        metadata={},
                        file_type="doc",
                        success=False,
                        error=f"DOC extraction failed: {str(docx_error)} | {str(binary_error)}"
                    )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="doc",
                success=False,
                error=f"DOC extraction failed: {str(e)}"
            )
