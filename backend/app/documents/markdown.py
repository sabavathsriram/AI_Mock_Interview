"""
Markdown document processor.
"""

from typing import Dict, Any
from app.documents.base import DocumentProcessor, ExtractionResult
import os
import re


class MarkdownProcessor(DocumentProcessor):
    """Processor for Markdown documents."""
    
    supported_extensions = ('.md', '.markdown')
    mime_types = ('text/markdown', 'text/x-markdown')
    
    async def extract(self, file_path: str) -> ExtractionResult:
        """
        Extract text from Markdown file.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            ExtractionResult containing extracted text and metadata
        """
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="markdown",
                    success=False,
                    error="File not found"
                )
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    markdown_content = f.read()
            except Exception as e:
                return ExtractionResult(
                    text="",
                    metadata={},
                    file_type="markdown",
                    success=False,
                    error=f"Failed to read Markdown: {str(e)}"
                )
            
            # Extract and process markdown
            text = self._extract_text_from_markdown(markdown_content)
            
            # Normalize the text
            normalized_text = self.normalize_text(text)
            
            # Count headers and code blocks for metadata
            header_count = len(re.findall(r'^#+\s', markdown_content, re.MULTILINE))
            code_block_count = len(re.findall(r'```', markdown_content))
            
            metadata: Dict[str, Any] = {
                "processor": "markdown-aware",
                "format": "markdown",
                "header_count": header_count,
                "code_block_count": code_block_count // 2  # Divide by 2 since each block has opening and closing
            }
            
            return ExtractionResult(
                text=normalized_text,
                metadata=metadata,
                file_type="markdown",
                success=True
            )
        
        except Exception as e:
            return ExtractionResult(
                text="",
                metadata={},
                file_type="markdown",
                success=False,
                error=f"Markdown extraction failed: {str(e)}"
            )
    
    @staticmethod
    def _extract_text_from_markdown(markdown_content: str) -> str:
        """
        Extract text from Markdown content while preserving structure.
        
        Args:
            markdown_content: Raw Markdown content
            
        Returns:
            Extracted text with minimal formatting
        """
        text = markdown_content
        
        # Remove code blocks (``` ... ```) but preserve their content
        # First, extract code block content
        code_blocks = re.findall(r'```[a-zA-Z0-9]*\n(.*?)\n```', text, re.DOTALL)
        code_content = '\n'.join(code_blocks) if code_blocks else ""
        
        # Remove code blocks from main text
        text = re.sub(r'```[a-zA-Z0-9]*\n.*?\n```', '', text, flags=re.DOTALL)
        
        # Remove inline code markers
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove markdown syntax but keep the text
        # Remove headings but keep the text
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Remove bold and italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Remove links but keep the text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove images
        text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
        
        # Remove horizontal rules
        text = re.sub(r'^(-{3,}|={3,}|\*{3,})$', '', text, flags=re.MULTILINE)
        
        # Remove list markers
        text = re.sub(r'^[\s]*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[\s]*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove blockquotes
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        
        # Add back code content
        if code_content.strip():
            text += '\n\n[Code Content]\n' + code_content
        
        return text
