"""
HTML document processor using BeautifulSoup.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os
import re


class HTMLProcessor(DocumentProcessor):
    """Processor for HTML documents."""
    
    supported_extensions = ('.html', '.htm')
    mime_types = ('text/html',)
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from HTML file.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="html",
                    success=False,
                    error="File not found"
                )
            
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                # Fallback if BeautifulSoup is not available
                return self._extract_html_fallback(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    html_content = f.read()
            except Exception as e:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="html",
                    success=False,
                    error=f"Failed to read HTML: {str(e)}"
                )
            
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(['script', 'style']):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
            except Exception as e:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="html",
                    success=False,
                    error=f"Failed to parse HTML: {str(e)}"
                )
            
            # Normalize the text
            normalized_text = self.normalize_text(text)
            
            metadata: Dict[str, Any] = {
                "processor": "beautifulsoup4",
                "format": "html"
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="html",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="html",
                success=False,
                error=f"HTML extraction failed: {str(e)}"
            )
    
    @staticmethod
    def _extract_html_fallback(file_path: str) -> ExtractionResult:
        """
        Fallback HTML extraction using regex when BeautifulSoup is not available.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            ExtractionResult
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                html_content = f.read()
            
            # Remove script and style tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            
            # Decode HTML entities
            import html
            text = html.unescape(text)
            
            # Normalize the text
            normalized_text = HTMLProcessor.normalize_text(text)
            
            metadata: Dict[str, Any] = {
                "processor": "regex-based",
                "format": "html"
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="html",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="html",
                success=False,
                error=f"HTML extraction failed: {str(e)}"
            )
