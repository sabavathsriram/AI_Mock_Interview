"""
RAG Service Tests
Tests for RAG service operations and retrieval.
"""

import pytest
import tempfile
from pathlib import Path

from app.rag import (
    RAGService,
    Document,
    RAGContext,
)


class TestRAGServiceBasics:
    """Test basic RAG service functionality."""
    
    @pytest.fixture
    def rag_service_instance(self):
        """Create a temporary RAG service instance."""
        return RAGService(collection_name="test_collection")
    
    def test_service_initialization(self, rag_service_instance):
        """Test service initializes."""
        assert rag_service_instance is not None
    
    def test_ingest_document(self, rag_service_instance):
        """Test document ingestion."""
        doc = Document(
            content="Machine learning is a subset of AI" * 20,
            source="test.txt",
            document_type="text",
            category="machine_learning",
            title="ML Overview"
        )
        
        chunks, added = rag_service_instance.ingest_document(doc)
        assert chunks > 0
        assert added > 0


class TestRAGDuplicateDetection:
    """Test duplicate document detection."""
    
    @pytest.fixture
    def rag_service_instance(self):
        """Create RAG service."""
        return RAGService(collection_name="test_duplicates")
    
    def test_duplicate_detection(self, rag_service_instance):
        """Test that duplicates are detected."""
        content = "Test content " * 100
        doc1 = Document(
            content=content,
            source="file1.txt",
            document_type="text",
            category="test",
            title="Test 1"
        )
        doc2 = Document(
            content=content,
            source="file2.txt",
            document_type="text",
            category="test",
            title="Test 2"
        )
        
        chunks1, _ = rag_service_instance.ingest_document(doc1)
        chunks2, _ = rag_service_instance.ingest_document(doc2, skip_duplicates=True)
        
        assert chunks1 > 0
        assert chunks2 == 0  # Should be skipped as duplicate


class TestRAGSearch:
    """Test RAG search functionality."""
    
    @pytest.fixture
    def rag_service_with_docs(self):
        """Create service with test documents."""
        service = RAGService(collection_name="test_search")
        
        # Add test documents
        docs = [
            Document(
                content="Python is a programming language. " * 30,
                source="python.txt",
                document_type="text",
                category="programming",
                title="Python Overview"
            ),
            Document(
                content="Java is an object-oriented language. " * 30,
                source="java.txt",
                document_type="text",
                category="programming",
                title="Java Overview"
            ),
        ]
        
        for doc in docs:
            service.ingest_document(doc)
        
        return service
    
    def test_search_returns_context(self, rag_service_with_docs):
        """Test that search returns RAG context."""
        context = rag_service_with_docs.search("Python programming")
        
        assert context is not None
        assert isinstance(context, RAGContext)
        assert context.query == "Python programming"
    
    def test_search_retrieves_documents(self, rag_service_with_docs):
        """Test that search retrieves documents."""
        context = rag_service_with_docs.search("programming language")
        
        assert len(context.retrieved_documents) > 0
    
    def test_search_with_threshold(self, rag_service_with_docs):
        """Test search with similarity threshold."""
        context = rag_service_with_docs.search(
            "Python programming",
            similarity_threshold=0.7
        )
        
        # Should have high-confidence results
        for doc in context.retrieved_documents:
            assert doc.similarity_score >= 0.7
    
    def test_search_empty_query(self, rag_service_with_docs):
        """Test search with empty query."""
        with pytest.raises(Exception):
            rag_service_with_docs.search("")
    
    def test_search_top_k(self, rag_service_with_docs):
        """Test top_k parameter."""
        context = rag_service_with_docs.search(
            "programming",
            top_k=1
        )
        
        assert len(context.retrieved_documents) <= 1


class TestRAGContextCombining:
    """Test context combining functionality."""
    
    @pytest.fixture
    def rag_service_with_docs(self):
        """Create service with test documents."""
        service = RAGService(collection_name="test_context")
        
        doc = Document(
            content="Content " * 100,
            source="test.txt",
            document_type="text",
            category="test",
            title="Test Doc"
        )
        service.ingest_document(doc)
        
        return service
    
    def test_combined_context_string(self, rag_service_with_docs):
        """Test that context is properly combined."""
        context = rag_service_with_docs.search("Content")
        
        assert context.combined_context is not None
        assert len(context.combined_context) > 0
        assert "Content" in context.combined_context
    
    def test_retrieve_context_method(self, rag_service_with_docs):
        """Test retrieve_context convenience method."""
        context_str = rag_service_with_docs.retrieve_context("Content")
        
        assert isinstance(context_str, str)
        assert len(context_str) > 0


class TestRAGStatistics:
    """Test RAG statistics."""
    
    def test_get_statistics(self):
        """Test getting statistics."""
        from app.rag import rag_service
        
        stats = rag_service.get_statistics()
        
        assert stats is not None
        assert "embedding_model" in stats
        assert "chunk_size" in stats


__all__ = [
    'TestRAGServiceBasics',
    'TestRAGDuplicateDetection',
    'TestRAGSearch',
    'TestRAGContextCombining',
    'TestRAGStatistics',
]
