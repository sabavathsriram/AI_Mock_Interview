"""
Tests for resume text extraction functionality.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.resume_service import ResumeService
from app.documents.pdf import PDFProcessor
from app.documents.base import ExtractionResult


class TestResumeExtraction:
    """Test suite for resume text extraction."""
    
    @pytest.mark.asyncio
    async def test_pdf_extraction_success(self, tmp_path):
        """Test successful PDF text extraction."""
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")
        
        # Create mock PyPDF2 module
        mock_pdf_module = MagicMock()
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test Resume Content\nJohn Doe\nSoftware Engineer"
        mock_reader.pages = [mock_page]
        mock_pdf_module.PdfReader.return_value = mock_reader
        
        # Patch PyPDF2 import in the extract method
        import sys
        with patch.dict(sys.modules, {'PyPDF2': mock_pdf_module}):
            processor = PDFProcessor()
            result = await processor.extract(str(pdf_path))
            
            # Verify
            assert result.success is True
            assert "John Doe" in result.text
            assert result.file_type == "pdf"
            assert result.metadata["page_count"] == 1
    
    @pytest.mark.asyncio
    async def test_pdf_extraction_file_not_found(self):
        """Test PDF extraction with non-existent file."""
        processor = PDFProcessor()
        result = await processor.extract("/nonexistent/file.pdf")
        
        assert result.success is False
        assert result.error is not None
        assert "File not found" in result.error
    
    @pytest.mark.asyncio
    async def test_empty_pdf_handling(self, tmp_path):
        """Test handling of empty PDF."""
        pdf_path = tmp_path / "empty.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")
        
        mock_pdf_module = MagicMock()
        mock_reader = MagicMock()
        mock_reader.pages = []
        mock_pdf_module.PdfReader.return_value = mock_reader
        
        import sys
        with patch.dict(sys.modules, {'PyPDF2': mock_pdf_module}):
            processor = PDFProcessor()
            result = await processor.extract(str(pdf_path))
            
            assert result.success is True
            assert result.metadata["page_count"] == 0
            assert result.text.strip() == ""
    
    @pytest.mark.asyncio
    async def test_corrupt_pdf_handling(self, tmp_path):
        """Test handling of corrupt PDF file."""
        pdf_path = tmp_path / "corrupt.pdf"
        pdf_path.write_bytes(b"Not a real PDF")
        
        mock_pdf_module = MagicMock()
        mock_pdf_module.PdfReader.side_effect = Exception("PDF is corrupted")
        
        import sys
        with patch.dict(sys.modules, {'PyPDF2': mock_pdf_module}):
            processor = PDFProcessor()
            result = await processor.extract(str(pdf_path))
            
            assert result.success is False
            assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_file_size_validation(self):
        """Test file size validation."""
        # Test valid size
        is_valid, error = ResumeService.validate_file_size(5 * 1024 * 1024)  # 5 MB
        assert is_valid is True
        assert error is None
        
        # Test empty file
        is_valid, error = ResumeService.validate_file_size(0)
        assert is_valid is False
        assert "empty" in error.lower()
        
        # Test oversized file
        is_valid, error = ResumeService.validate_file_size(15 * 1024 * 1024)  # 15 MB
        assert is_valid is False
        assert "exceeds" in error.lower()
    
    @pytest.mark.asyncio
    async def test_file_extension_validation(self):
        """Test file extension validation."""
        # Valid extensions
        for ext in [".pdf", ".docx", ".txt", ".doc"]:
            is_valid, error = ResumeService.validate_file_extension(f"resume{ext}")
            assert is_valid is True
        
        # Invalid extensions
        is_valid, error = ResumeService.validate_file_extension("image.jpg")
        assert is_valid is False
        
        is_valid, error = ResumeService.validate_file_extension("archive.zip")
        assert is_valid is False


class TestResumeExtractionStatus:
    """Test suite for extraction status tracking."""
    
    @pytest.mark.asyncio
    async def test_extraction_status_completed(self):
        """Test that extraction status is set to 'completed' not 'success'."""
        # This test verifies the fix for the extraction status mismatch
        from app.database.models import ResumeDocument
        
        doc = ResumeDocument(
            user_id="test_user",
            filename="test.pdf",
            file_type="pdf",
            file_path="uploads/test.pdf",
            file_size=1000,
            mime_type="application/pdf",
            extracted_text="Test content",
            extraction_metadata={},
            uploaded_at=__import__('datetime').datetime.utcnow()
        )
        
        # Default extraction status should be 'completed'
        assert doc.extraction_status == "completed"
    
    @pytest.mark.asyncio
    async def test_extraction_status_values(self):
        """Test valid extraction status values."""
        from app.database.models import ResumeDocument
        import datetime
        
        # Test all valid statuses
        for status in ["pending", "completed", "failed"]:
            doc = ResumeDocument(
                user_id="test_user",
                filename="test.pdf",
                file_type="pdf",
                file_path="uploads/test.pdf",
                file_size=1000,
                mime_type="application/pdf",
                extracted_text="Test content",
                extraction_metadata={},
                extraction_status=status,
                uploaded_at=datetime.datetime.utcnow()
            )
            assert doc.extraction_status == status


class TestTextExtraction:
    """Test suite for actual text extraction from documents."""
    
    @pytest.mark.asyncio
    async def test_text_preservation_with_line_breaks(self, tmp_path):
        """Test that extracted text is normalized properly."""
        pdf_path = tmp_path / "multiline.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")
        
        mock_pdf_module = MagicMock()
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Line 1\nLine 2\nLine 3"
        mock_reader.pages = [mock_page]
        mock_pdf_module.PdfReader.return_value = mock_reader
        
        import sys
        with patch.dict(sys.modules, {'PyPDF2': mock_pdf_module}):
            processor = PDFProcessor()
            result = await processor.extract(str(pdf_path))
            
            # normalize_text joins lines with spaces after stripping and removing empty lines
            assert "Line 1" in result.text and "Line 2" in result.text and "Line 3" in result.text
            assert result.success is True
    
    @pytest.mark.asyncio
    async def test_multipage_pdf_extraction(self, tmp_path):
        """Test extraction from multi-page PDF."""
        pdf_path = tmp_path / "multipage.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")
        
        mock_pdf_module = MagicMock()
        
        # Create two mock pages
        page1 = MagicMock()
        page1.extract_text.return_value = "Page 1 content"
        
        page2 = MagicMock()
        page2.extract_text.return_value = "Page 2 content"
        
        mock_reader = MagicMock()
        mock_reader.pages = [page1, page2]
        mock_pdf_module.PdfReader.return_value = mock_reader
        
        import sys
        with patch.dict(sys.modules, {'PyPDF2': mock_pdf_module}):
            processor = PDFProcessor()
            result = await processor.extract(str(pdf_path))
            
            assert result.success is True
            assert result.metadata["page_count"] == 2
            assert "Page 1 content" in result.text
            assert "Page 2 content" in result.text
            assert "--- Page 1 ---" in result.text
            assert "--- Page 2 ---" in result.text
    
    @pytest.mark.asyncio
    async def test_extraction_error_handling(self, tmp_path):
        """Test graceful handling of extraction errors."""
        pdf_path = tmp_path / "error.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n")
        
        mock_pdf_module = MagicMock()
        
        # First page succeeds
        page1 = MagicMock()
        page1.extract_text.return_value = "Page 1 content"
        
        # Second page fails
        page2 = MagicMock()
        page2.extract_text.side_effect = Exception("Extraction error on page 2")
        
        mock_reader = MagicMock()
        mock_reader.pages = [page1, page2]
        mock_pdf_module.PdfReader.return_value = mock_reader
        
        import sys
        with patch.dict(sys.modules, {'PyPDF2': mock_pdf_module}):
            processor = PDFProcessor()
            result = await processor.extract(str(pdf_path))
            
            # Should still succeed with partial content
            assert result.success is True
            assert "Page 1 content" in result.text
            assert "Error extracting page 2" in result.text
