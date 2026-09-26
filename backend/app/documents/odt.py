"""
ODT document processor for OpenDocument Text files.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os
import zipfile
import xml.etree.ElementTree as ET


class ODTProcessor(DocumentProcessor):
    """Processor for ODT documents."""
    
    supported_extensions = ('.odt',)
    mime_types = ('application/vnd.oasis.opendocument.text',)
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from ODT file.
        
        Args:
            file_path: Path to the ODT file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="odt",
                    success=False,
                    error="File not found"
                )
            
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # ODT files are ZIP archives containing XML files
                    # The main content is in content.xml
                    
                    try:
                        content_xml = zip_file.read('content.xml')
                    except KeyError:
                        return ExtractionResult(
                            text="",
                            metadata={},
                            file_type="odt",
                            success=False,
                            error="Missing content.xml in ODT file"
                        )
                    
                    # Parse the XML
                    root = ET.fromstring(content_xml)
                    
                    # Extract text from all text elements
                    text = self._extract_text_from_xml(root)
                    
            except zipfile.BadZipFile:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="odt",
                    success=False,
                    error="Invalid ODT file format (not a valid ZIP archive)"
                )
            except Exception as e:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="odt",
                    success=False,
                    error=f"Failed to read ODT: {str(e)}"
                )
            
            # Normalize the text
            normalized_text = self.normalize_text(text)
            
            metadata: Dict[str, Any] = {
                "processor": "xml-based",
                "format": "odt"
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="odt",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="odt",
                success=False,
                error=f"ODT extraction failed: {str(e)}"
            )
    
    @staticmethod
    def _extract_text_from_xml(root: ET.Element) -> str:
        """
        Recursively extract text from XML elements.
        
        Args:
            root: Root XML element
            
        Returns:
            Extracted text
        """
        text = ""
        
        # Define namespaces used in ODT
        namespaces = {
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
        }
        
        # Find all text elements
        for elem in root.iter():
            # Handle paragraph and span elements
            if elem.tag.endswith('}p') or elem.tag.endswith('}text') or elem.tag.endswith('}span'):
                if elem.text:
                    text += elem.text
            
            # Add tail text (text after child elements)
            if elem.tail:
                text += elem.tail
        
        # Also try generic approach for compatibility
        if not text.strip():
            # Fallback: get all text content
            text = ''.join(elem.itertext() for elem in root.iter())
        
        return text
