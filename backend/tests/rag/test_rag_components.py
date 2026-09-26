"""
RAG Component Tests
Tests for document processing, chunking, and vector operations.
"""

import pytest
import tempfile
from pathlib import Path

from app.rag.document_processor import (
    Document,
    Chunk,
    DocumentCleaner,
    DocumentChunker,
    DocumentLoader,
)
from app.rag.config import rag_settings


class TestDocumentCleaner:
    """Test document cleaning."""
    
    def test_clean_whitespace(self):
        """Test whitespace normalization."""
        cleaner = DocumentCleaner()
        text = "Hello   \n\n\n  World"
        result = cleaner.clean(text)
        assert "Hello" in result and "World" in result
    
    def test_clean_special_chars(self):
        """Test special character removal."""
        cleaner = DocumentCleaner()
        text = "Hello\x00World"
        result = cleaner.clean(text)
        assert "\x00" not in result


class TestDocumentChunker:
    """Test document chunking."""
    
    def test_chunk_creation(self):
        """Test basic chunking."""
        doc = Document(
            content="A" * 1000,
            source="test.txt",
            document_type="text",
            category="test",
            title="Test"
        )
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=10)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
    
    def test_chunk_metadata(self):
        """Test chunk metadata preservation."""
        doc = Document(
            content="Test content " * 100,
            source="test.txt",
            document_type="text",
            category="test",
            title="Test Doc"
        )
        chunker = DocumentChunker()
        chunks = chunker.chunk(doc)
        
        for chunk in chunks:
            assert chunk.source == "test.txt"
            assert chunk.category == "test"
            assert chunk.title == "Test Doc"
    
    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        content = " ".join([f"word{i}" for i in range(100)])
        doc = Document(
            content=content,
            source="test.txt",
            document_type="text",
            category="test",
            title="Test"
        )
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk(doc)
        assert len(chunks) > 1


class TestDocumentLoader:
    """Test document loading."""
    
    def test_load_text_file(self):
        """Test loading a text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            f.flush()
            
            loader = DocumentLoader()
            doc = loader.load_text_file(
                f.name,
                category="test",
                document_type="text"
            )
            
            assert doc is not None
            assert "Test content" in doc.content
            assert doc.category == "test"
            
            Path(f.name).unlink()
    
    def test_load_markdown_file(self):
        """Test loading a markdown file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Header\nContent")
            f.flush()
            
            loader = DocumentLoader()
            doc = loader.load_text_file(f.name)
            
            assert doc is not None
            assert len(doc.content) > 0
            
            Path(f.name).unlink()
    
    def test_load_directory(self):
        """Test loading directory of documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "file1.txt").write_text("Content 1")
            Path(tmpdir, "file2.txt").write_text("Content 2")
            
            loader = DocumentLoader()
            docs = loader.load_documents_from_directory(tmpdir)
            
            assert len(docs) == 2
    
    def test_load_nonexistent_file(self):
        """Test loading nonexistent file."""
        loader = DocumentLoader()
        doc = loader.load_text_file("/nonexistent/path.txt")
        assert doc is None


class TestChunkMetadata:
    """Test chunk metadata handling."""
    
    def test_metadata_preservation(self):
        """Test that metadata is preserved through chunking."""
        doc = Document(
            content="Content " * 100,
            source="source.txt",
            document_type="text",
            category="test",
            title="Title"
        )
        chunker = DocumentChunker()
        chunks = chunker.chunk(doc)
        
        for chunk in chunks:
            assert chunk.metadata is not None
            assert "chunk_index" in chunk.metadata
            assert "total_chunks" in chunk.metadata


class TestDocumentProcessing:
    """Test full document processing pipeline."""
    
    def test_process_document(self):
        """Test processing a single document."""
        from app.rag.document_processor import DocumentProcessor
        
        doc = Document(
            content="Test content " * 100,
            source="test.txt",
            document_type="text",
            category="test",
            title="Test"
        )
        
        processor = DocumentProcessor()
        chunks = processor.process_document(doc)
        
        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
    
    def test_process_empty_document(self):
        """Test processing empty document."""
        from app.rag.document_processor import DocumentProcessor
        
        doc = Document(
            content="",
            source="test.txt",
            document_type="text",
            category="test",
            title="Test"
        )
        
        processor = DocumentProcessor()
        chunks = processor.process_document(doc)
        
        assert len(chunks) == 0


class TestRAGConfig:
    """Test RAG configuration."""
    
    def test_config_defaults(self):
        """Test that RAG config has proper defaults."""
        assert rag_settings.chunk_size >= 100
        assert rag_settings.chunk_overlap < rag_settings.chunk_size
        assert 0 <= rag_settings.similarity_threshold <= 1.0
        assert rag_settings.top_k >= 1
    
    def test_config_validation(self):
        """Test config validation."""
        assert rag_settings.validate_settings()
    
    def test_get_config_dict(self):
        """Test config dict generation."""
        config_dict = rag_settings.get_config_dict()
        assert "embedding_model" in config_dict
        assert "chunk_size" in config_dict
        assert "similarity_threshold" in config_dict


__all__ = [
    'TestDocumentCleaner',
    'TestDocumentChunker',
    'TestDocumentLoader',
    'TestChunkMetadata',
    'TestDocumentProcessing',
    'TestRAGConfig',
]
