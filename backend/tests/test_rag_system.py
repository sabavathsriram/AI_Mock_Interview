"""
Comprehensive tests for RAG system components.
Tests document ingestion, chunking, embedding, vector insertion, retrieval, and answer generation.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.rag.service import RAGService, RAGServiceException
from app.rag.answer_generator import AnswerGenerator, AnswerGenerationException
from app.rag.document_processor import (
    Document,
    DocumentProcessor,
    DocumentLoader,
    DocumentChunker,
)
from app.rag.vector_db import VectorDatabase, SearchResult
from app.rag.schemas import RAGContext, RetrievedDocument
from app.rag.config import rag_settings
from app.llm.service import TextGenerationResponse


class TestDocumentProcessing:
    """Test document loading and chunking."""
    
    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            content="This is test content for a document.",
            source="test.md",
            document_type="text",
            category="programming",
            title="Test Document"
        )
        
        assert doc.content == "This is test content for a document."
        assert doc.source == "test.md"
        assert doc.category == "programming"
    
    def test_document_chunking(self):
        """Test document chunking with default settings."""
        processor = DocumentProcessor()
        
        doc = Document(
            content="Python is a programming language. " * 50,  # Repeat to create content
            source="python.md",
            document_type="text",
            category="python",
            title="Python Basics"
        )
        
        chunks = processor.process_document(doc)
        
        assert len(chunks) > 0
        assert all(chunk.chunk_id.startswith("python.md:") for chunk in chunks)
        assert all(chunk.category == "python" for chunk in chunks)
        assert all(chunk.content for chunk in chunks)
    
    def test_document_chunking_with_overlap(self):
        """Test that chunks have overlap as configured."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        
        doc = Document(
            content="A" * 300,  # 300 characters of same letter
            source="test.txt",
            document_type="text",
            category="test",
            title="Test"
        )
        
        chunks = chunker.chunk(doc)
        
        # With overlap, we should have multiple chunks
        assert len(chunks) > 1
        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            # There should be some common content due to overlap
            assert chunks[i].content[-20:] in (chunks[i+1].content[:50] or "")
    
    def test_document_loader_with_temp_file(self):
        """Test loading document from file."""
        loader = DocumentLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is test content.")
            temp_path = f.name
        
        try:
            doc = loader.load_text_file(temp_path, category="test")
            
            assert doc is not None
            assert "Test Document" in doc.content
            assert doc.category == "test"
            assert doc.document_type == "text"
        finally:
            Path(temp_path).unlink()
    
    def test_document_loader_empty_file(self):
        """Test loading empty file returns None."""
        loader = DocumentLoader()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            doc = loader.load_text_file(temp_path)
            assert doc is None
        finally:
            Path(temp_path).unlink()
    
    def test_document_loader_nonexistent_file(self):
        """Test loading nonexistent file returns None."""
        loader = DocumentLoader()
        doc = loader.load_text_file("/nonexistent/path.md")
        assert doc is None


class TestVectorDatabase:
    """Test vector database operations."""
    
    def test_vector_db_initialization(self):
        """Test vector database initialization."""
        # Use a persistent test directory instead of temp
        test_dir = Path("./data/vector_db_test")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with patch('app.rag.vector_db.rag_settings') as mock_settings:
                mock_settings.get_chromadb_path.return_value = test_dir
                mock_settings.chromadb_collection_name = "test_collection"
                
                vdb = VectorDatabase(collection_name="test_collection")
                
                assert vdb.collection is not None
                assert vdb.collection_name == "test_collection"
        finally:
            # Clean up - ignore errors on Windows
            import shutil
            try:
                shutil.rmtree(test_dir, ignore_errors=True)
            except:
                pass
    
    def test_add_chunk_to_vector_db(self):
        """Test adding chunk to vector database."""
        from app.rag.document_processor import Chunk
        
        test_dir = Path("./data/vector_db_test_add")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with patch('app.rag.vector_db.rag_settings') as mock_settings:
                mock_settings.get_chromadb_path.return_value = test_dir
                mock_settings.chromadb_collection_name = "test"
                
                vdb = VectorDatabase()
                
                chunk = Chunk(
                    content="Test chunk content",
                    document_id="doc_1",
                    chunk_id="chunk_1",
                    source="test.md",
                    document_type="text",
                    category="test",
                    title="Test"
                )
                
                chunk_id = vdb.add_chunk(chunk)
                assert chunk_id == "chunk_1"
        finally:
            import shutil
            try:
                shutil.rmtree(test_dir, ignore_errors=True)
            except:
                pass
    
    def test_search_vector_db(self):
        """Test searching vector database."""
        test_dir = Path("./data/vector_db_test_search")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with patch('app.rag.vector_db.rag_settings') as mock_settings:
                mock_settings.get_chromadb_path.return_value = test_dir
                mock_settings.chromadb_collection_name = "test"
                mock_settings.top_k = 5
                mock_settings.similarity_threshold = 0.3
                
                vdb = VectorDatabase()
                
                # Add some chunks
                from app.rag.document_processor import Chunk
                chunks = [
                    Chunk(
                        content="Python is a programming language",
                        document_id="doc_1",
                        chunk_id=f"chunk_{i}",
                        source="python.md",
                        document_type="text",
                        category="python",
                        title="Python Basics"
                    )
                    for i in range(3)
                ]
                
                vdb.add_chunks(chunks)
                
                # Search
                results = vdb.search("Python programming", top_k=5)
                assert isinstance(results, list)
                assert len(results) > 0
        finally:
            import shutil
            try:
                shutil.rmtree(test_dir, ignore_errors=True)
            except:
                pass
    
    def test_get_collection_stats(self):
        """Test getting collection statistics."""
        test_dir = Path("./data/vector_db_test_stats")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with patch('app.rag.vector_db.rag_settings') as mock_settings:
                mock_settings.get_chromadb_path.return_value = test_dir
                mock_settings.chromadb_collection_name = "test"
                
                vdb = VectorDatabase()
                stats = vdb.get_collection_stats()
                
                assert "collection_name" in stats
                assert "document_count" in stats
        finally:
            import shutil
            try:
                shutil.rmtree(test_dir, ignore_errors=True)
            except:
                pass


class TestRAGService:
    """Test RAG service operations."""
    
    def test_rag_service_initialization(self):
        """Test RAG service initialization."""
        service = RAGService(collection_name="test_collection")
        assert service.collection_name == "test_collection"
        assert service.processor is not None
        assert service.vector_db is not None
    
    def test_document_ingestion(self):
        """Test ingesting a document."""
        service = RAGService(collection_name="test_ingestion")
        
        doc = Document(
            content="Machine learning is a subset of artificial intelligence. " * 10,
            source="ml_basics.md",
            document_type="text",
            category="ai_ml",
            title="ML Basics"
        )
        
        chunks_created, docs_added = service.ingest_document(doc)
        
        assert chunks_created > 0
        assert docs_added > 0
    
    def test_duplicate_document_detection(self):
        """Test that duplicate documents are detected."""
        service = RAGService(collection_name="test_duplicates")
        
        doc = Document(
            content="Duplicate content here",
            source="doc1.md",
            document_type="text",
            category="test",
            title="Doc 1"
        )
        
        # Ingest first time
        service.ingest_document(doc, skip_duplicates=True)
        
        # Try to ingest duplicate
        chunks, added = service.ingest_document(doc, skip_duplicates=True)
        
        assert chunks == 0
        assert added == 0
    
    def test_rag_service_search(self):
        """Test RAG service search."""
        service = RAGService(collection_name="test_search")
        
        # Ingest test documents
        docs = [
            Document(
                content="Arrays are fundamental data structures",
                source="arrays.md",
                document_type="text",
                category="data_structures",
                title="Arrays"
            ),
            Document(
                content="Linked lists use pointers to connect nodes",
                source="linked_lists.md",
                document_type="text",
                category="data_structures",
                title="Linked Lists"
            ),
        ]
        
        for doc in docs:
            service.ingest_document(doc)
        
        # Search
        context = service.search("data structures arrays")
        
        assert isinstance(context, RAGContext)
        assert context.query == "data structures arrays"
    
    def test_category_filtering(self):
        """Test category filtering in search."""
        service = RAGService(collection_name="test_category_filter")
        
        # Ingest documents with different categories
        docs = [
            Document(
                content="Python dictionaries are hash-based",
                source="python.md",
                document_type="text",
                category="python",
                title="Python"
            ),
            Document(
                content="JavaScript is a scripting language",
                source="javascript.md",
                document_type="text",
                category="javascript",
                title="JavaScript"
            ),
        ]
        
        for doc in docs:
            service.ingest_document(doc)
        
        # Search with category filter
        context = service.search(
            "programming language",
            category_filter="python"
        )
        
        # Results should only include Python category
        for doc in context.retrieved_documents:
            if doc.category:  # If category is set
                assert doc.category == "python" or doc.category is None
    
    def test_similarity_threshold(self):
        """Test similarity threshold filtering."""
        service = RAGService(collection_name="test_threshold")
        
        doc = Document(
            content="This is very specific test content about algorithms",
            source="algo.md",
            document_type="text",
            category="algorithms",
            title="Algorithms"
        )
        
        service.ingest_document(doc)
        
        # Search with high threshold
        context = service.search(
            "algorithms",
            similarity_threshold=0.9  # High threshold
        )
        
        # With exact match, should have results
        if context.retrieved_documents:
            assert all(score >= 0.9 - 0.1 for score in context.similarity_scores)
    
    def test_search_with_insufficient_results(self):
        """Test search when no results match threshold."""
        service = RAGService(collection_name="test_no_results")
        
        doc = Document(
            content="Python programming content",
            source="python.md",
            document_type="text",
            category="python",
            title="Python"
        )
        
        service.ingest_document(doc)
        
        # Search for completely unrelated term with high threshold
        context = service.search(
            "unrelatedxyzabc",
            similarity_threshold=0.99  # Very high threshold
        )
        
        assert len(context.retrieved_documents) == 0


class TestAnswerGenerator:
    """Test answer generation from context."""
    
    @pytest.mark.asyncio
    async def test_answer_generation_with_context(self):
        """Test generating answer from context."""
        mock_llm = AsyncMock()
        mock_llm.generate_text = AsyncMock(
            return_value=TextGenerationResponse(
                text="Based on the provided context, [Source 1] explains that arrays provide O(1) access time.",
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
        )
        
        generator = AnswerGenerator(llm_service_instance=mock_llm)
        
        # Create mock context
        docs = [
            RetrievedDocument(
                id="chunk_1",
                content="Arrays provide O(1) random access",
                similarity_score=0.95,
                source="arrays.md",
                category="data_structures",
                title="Arrays"
            )
        ]
        
        context = RAGContext(
            query="What is array access time?",
            retrieved_documents=docs,
            similarity_scores=[0.95],
            combined_context="Arrays provide O(1) random access",
            total_documents_retrieved=1
        )
        
        result = await generator.generate_answer(
            query="What is array access time?",
            context=context
        )
        
        assert result["success"] is True
        assert "answer" in result
        assert result["documents_used"] == 1
    
    @pytest.mark.asyncio
    async def test_citation_extraction(self):
        """Test extracting citations from answer."""
        mock_llm = AsyncMock()
        mock_llm.generate_text = AsyncMock(
            return_value=TextGenerationResponse(
                text="[Source 1] explains concept A. [Source 2] explains concept B.",
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
        )
        
        generator = AnswerGenerator(llm_service_instance=mock_llm)
        
        docs = [
            RetrievedDocument(
                id="chunk_1",
                content="Concept A",
                similarity_score=0.9,
                source="doc1.md",
                category="test",
                title="Doc 1"
            ),
            RetrievedDocument(
                id="chunk_2",
                content="Concept B",
                similarity_score=0.85,
                source="doc2.md",
                category="test",
                title="Doc 2"
            ),
        ]
        
        context = RAGContext(
            query="What are concepts?",
            retrieved_documents=docs,
            similarity_scores=[0.9, 0.85],
            combined_context="Combined"
        )
        
        result = await generator.generate_answer("What are concepts?", context)
        
        citations = result.get("citations", [])
        assert len(citations) >= 1  # At least one citation found
    
    @pytest.mark.asyncio
    async def test_insufficient_context_handling(self):
        """Test handling of insufficient context."""
        generator = AnswerGenerator()
        
        # Empty context
        context = RAGContext(
            query="What is something?",
            retrieved_documents=[],
            similarity_scores=[],
            combined_context=""
        )
        
        result = await generator.generate_answer_with_insufficient_context_handling(
            "What is something?",
            context
        )
        
        assert result["success"] is True
        assert result["has_context"] is False
        assert result["insufficient_context"] is True
    
    @pytest.mark.asyncio
    async def test_low_confidence_warning(self):
        """Test low confidence warning."""
        mock_llm = AsyncMock()
        mock_llm.generate_text = AsyncMock(
            return_value=TextGenerationResponse(
                text="Some answer",
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
        )
        
        generator = AnswerGenerator(llm_service_instance=mock_llm)
        
        docs = [
            RetrievedDocument(
                id="chunk_1",
                content="Vaguely related content",
                similarity_score=0.3,  # Low confidence
                source="doc.md",
                category="test",
                title="Doc"
            )
        ]
        
        context = RAGContext(
            query="What is X?",
            retrieved_documents=docs,
            similarity_scores=[0.3]
        )
        
        result = await generator.generate_answer_with_insufficient_context_handling(
            "What is X?",
            context,
            min_confidence_threshold=0.5
        )
        
        assert result.get("insufficient_context") is True
        assert "low_confidence_warning" in result


class TestRAGIntegration:
    """Integration tests for RAG system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_rag_flow(self):
        """Test complete RAG flow: ingest -> search -> answer."""
        # Create service and ingest documents
        service = RAGService(collection_name="test_e2e")
        
        doc = Document(
            content="Python lists are mutable sequences that can store any type of object. " +
                    "Lists support indexing, slicing, and various methods like append, extend, and sort. " +
                    "Time complexity for access is O(1), search is O(n), and insertion/deletion depends on position.",
            source="python_lists.md",
            document_type="text",
            category="python",
            title="Python Lists"
        )
        
        service.ingest_document(doc)
        
        # Search
        context = service.search("Python list operations")
        
        assert len(context.retrieved_documents) > 0
        
        # Mock LLM for answer generation
        mock_llm = AsyncMock()
        mock_llm.generate_text = AsyncMock(
            return_value=TextGenerationResponse(
                text="Based on [Source 1], Python lists have O(1) access time complexity.",
                model="gemini-1.5-flash",
                timestamp=datetime.utcnow()
            )
        )
        
        generator = AnswerGenerator(llm_service_instance=mock_llm)
        result = await generator.generate_answer("What is list access time?", context)
        
        assert result["success"] is True
        assert result["documents_used"] > 0


class TestRAGConfiguration:
    """Test RAG configuration and settings."""
    
    def test_rag_settings_validation(self):
        """Test RAG settings validation."""
        assert rag_settings.validate_settings() is True
        assert rag_settings.chunk_size >= 100
        assert rag_settings.chunk_overlap < rag_settings.chunk_size
        assert 0.0 <= rag_settings.similarity_threshold <= 1.0
        assert rag_settings.top_k >= 1


class TestRAGEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_query_search(self):
        """Test search with empty query."""
        service = RAGService(collection_name="test_empty_query")
        
        with pytest.raises(RAGServiceException):
            service.search("")
    
    def test_document_with_empty_content(self):
        """Test ingesting document with empty content."""
        service = RAGService(collection_name="test_empty_doc")
        
        doc = Document(
            content="",
            source="empty.md",
            document_type="text",
            category="test",
            title="Empty"
        )
        
        chunks, added = service.ingest_document(doc)
        assert chunks == 0
        assert added == 0
    
    @pytest.mark.asyncio
    async def test_answer_generation_with_empty_context(self):
        """Test answer generation with empty context."""
        generator = AnswerGenerator()
        
        context = RAGContext(
            query="Test query",
            retrieved_documents=[],
            similarity_scores=[],
            combined_context=""
        )
        
        result = await generator.generate_answer_with_insufficient_context_handling(
            "Test query",
            context
        )
        
        assert result["insufficient_context"] is True
