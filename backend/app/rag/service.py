"""
RAG Service Module
Orchestrates the complete RAG pipeline for document ingestion and retrieval.
"""

import logging
import hashlib
from typing import List, Optional, Dict
from datetime import datetime

from app.rag.config import rag_settings
from app.rag.document_processor import (
    Document,
    Chunk,
    DocumentProcessor,
    DocumentLoader,
)
from app.rag.vector_db import VectorDatabase, SearchResult
from app.rag.schemas import RAGContext, RetrievedDocument

logger = logging.getLogger(__name__)


class RAGServiceException(Exception):
    """Base exception for RAG service."""
    pass


class RAGService:
    """Main RAG service orchestrating the pipeline."""
    
    def __init__(self, collection_name: str = None):
        """
        Initialize RAG service.
        
        Args:
            collection_name: Name of the vector database collection
        """
        self.collection_name = collection_name or rag_settings.chromadb_collection_name
        self.processor = DocumentProcessor(
            chunk_size=rag_settings.chunk_size,
            chunk_overlap=rag_settings.chunk_overlap
        )
        self.vector_db = VectorDatabase(collection_name=self.collection_name)
        self.logger = logger
        
        # Track ingested documents for duplicate detection
        self._ingested_hashes: Dict[str, str] = {}
        
        self.logger.info(f"Initialized RAG service with collection '{self.collection_name}'")
    
    def _compute_content_hash(self, content: str) -> str:
        """
        Compute hash of content.
        
        Args:
            content: Content to hash
            
        Returns:
            SHA256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _is_duplicate(self, content: str, source: str) -> bool:
        """
        Check if document is a duplicate.
        
        Args:
            content: Document content
            source: Document source
            
        Returns:
            True if duplicate
        """
        if not rag_settings.enable_duplicate_detection:
            return False
        
        content_hash = self._compute_content_hash(content)
        
        # Check if hash already exists in memory cache
        if content_hash in self._ingested_hashes:
            self.logger.warning(
                f"Duplicate document detected: {source} "
                f"(matches {self._ingested_hashes[content_hash]})"
            )
            return True
        
        return False
    
    def ingest_document(
        self,
        document: Document,
        skip_duplicates: bool = True
    ) -> tuple[int, int]:
        """
        Ingest a single document.
        
        Args:
            document: Document to ingest
            skip_duplicates: Whether to skip duplicate documents
            
        Returns:
            Tuple of (chunks_created, documents_added)
        """
        try:
            if not document or not document.content:
                self.logger.warning(f"Cannot ingest empty document: {document.source}")
                return 0, 0
            
            # Check for duplicates
            if skip_duplicates and self._is_duplicate(document.content, document.source):
                self.logger.info(f"Skipping duplicate: {document.source}")
                return 0, 0
            
            # Process document into chunks
            chunks = self.processor.process_document(document)
            
            if not chunks:
                self.logger.warning(f"No chunks created from {document.source}")
                return 0, 0
            
            # Add to vector database
            chunk_ids = self.vector_db.add_chunks(chunks)
            
            # Store hash for duplicate detection
            content_hash = self._compute_content_hash(document.content)
            self._ingested_hashes[content_hash] = document.source
            
            self.logger.info(
                f"Ingested document '{document.title}' ({document.source}): "
                f"{len(chunks)} chunks added to vector database"
            )
            
            return len(chunks), len(chunk_ids)
            
        except Exception as e:
            self.logger.error(f"Failed to ingest document {document.source}: {str(e)}")
            raise RAGServiceException(f"Document ingestion failed: {str(e)}")
    
    def ingest_documents(
        self,
        documents: List[Document],
        skip_duplicates: bool = True
    ) -> tuple[int, int]:
        """
        Ingest multiple documents.
        
        Args:
            documents: List of documents to ingest
            skip_duplicates: Whether to skip duplicates
            
        Returns:
            Tuple of (total_chunks, total_added)
        """
        total_chunks = 0
        total_added = 0
        
        for i, doc in enumerate(documents):
            try:
                chunks, added = self.ingest_document(doc, skip_duplicates)
                total_chunks += chunks
                total_added += added
                
            except Exception as e:
                self.logger.error(f"Failed to ingest document {i}: {str(e)}")
                continue
        
        self.logger.info(
            f"Batch ingestion complete: {total_chunks} chunks, {total_added} added"
        )
        
        return total_chunks, total_added
    
    def ingest_from_directory(
        self,
        directory: str,
        category: str = "general",
        document_type: str = "text",
        skip_duplicates: bool = True
    ) -> tuple[int, int]:
        """
        Ingest all documents from a directory.
        
        Args:
            directory: Directory path
            category: Document category
            document_type: Document type
            skip_duplicates: Whether to skip duplicates
            
        Returns:
            Tuple of (total_chunks, total_added)
        """
        try:
            # Load documents from directory
            loader = DocumentLoader()
            documents = loader.load_documents_from_directory(
                directory,
                category=category,
                document_type=document_type
            )
            
            if not documents:
                self.logger.warning(f"No documents found in {directory}")
                return 0, 0
            
            # Ingest all documents
            return self.ingest_documents(documents, skip_duplicates)
            
        except Exception as e:
            self.logger.error(f"Failed to ingest from directory {directory}: {str(e)}")
            raise RAGServiceException(f"Directory ingestion failed: {str(e)}")
    
    def search(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> RAGContext:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            RAGContext with retrieved documents
        """
        try:
            if not query or not query.strip():
                raise RAGServiceException("Query cannot be empty")
            
            top_k = top_k or rag_settings.top_k
            similarity_threshold = similarity_threshold or rag_settings.similarity_threshold
            
            self.logger.debug(
                f"Searching with query: '{query}' "
                f"(top_k={top_k}, threshold={similarity_threshold})"
            )
            
            # Search vector database
            search_results = self.vector_db.search(
                query_text=query,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # Convert to retrieved documents
            retrieved_docs = []
            similarity_scores = []
            
            for result in search_results:
                doc = RetrievedDocument(
                    id=result.id,
                    content=result.content,
                    similarity_score=result.similarity_score,
                    source=result.metadata.get("source") if result.metadata else None,
                    document_type=result.metadata.get("document_type") if result.metadata else None,
                    category=result.metadata.get("category") if result.metadata else None,
                    title=result.metadata.get("title") if result.metadata else None,
                    chunk_index=result.metadata.get("chunk_index") if result.metadata else None,
                    metadata=result.metadata
                )
                retrieved_docs.append(doc)
                similarity_scores.append(result.similarity_score)
            
            # Combine context
            combined_context = self._combine_context(retrieved_docs)
            
            # Create RAG context
            context = RAGContext(
                query=query,
                retrieved_documents=retrieved_docs,
                similarity_scores=similarity_scores,
                combined_context=combined_context,
                top_k_used=top_k,
                similarity_threshold_used=similarity_threshold,
                total_documents_retrieved=len(retrieved_docs),
                retrieval_timestamp=datetime.utcnow()
            )
            
            self.logger.info(
                f"Search completed: {len(retrieved_docs)} documents retrieved"
            )
            
            return context
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise RAGServiceException(f"Search failed: {str(e)}")
    
    def _combine_context(self, documents: List[RetrievedDocument]) -> str:
        """
        Combine retrieved documents into context string.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Combined context string
        """
        if not documents:
            return ""
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            # Format: [Source - Category] Title (Score: 0.95)
            header = f"[{i}. {doc.source or 'Unknown'}]"
            if doc.category:
                header += f" - {doc.category}"
            if doc.similarity_score:
                header += f" (Confidence: {doc.similarity_score:.2%})"
            
            context_parts.append(header)
            context_parts.append(doc.content)
            context_parts.append("")  # Empty line for separation
        
        combined = "\n".join(context_parts)
        
        self.logger.debug(
            f"Combined context from {len(documents)} documents: {len(combined)} chars"
        )
        
        return combined
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> str:
        """
        Retrieve context string for a query (convenience method).
        
        Args:
            query: Search query
            top_k: Number of results
            similarity_threshold: Minimum similarity
            
        Returns:
            Combined context string
        """
        context = self.search(query, top_k, similarity_threshold)
        return context.combined_context
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            result = self.vector_db.delete_document(document_id)
            self.logger.info(f"Document deleted: {document_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise RAGServiceException(f"Deletion failed: {str(e)}")
    
    def delete_documents_by_source(self, source: str) -> int:
        """
        Delete all documents from a source.
        
        Args:
            source: Source identifier
            
        Returns:
            Number of documents deleted
        """
        try:
            count = self.vector_db.delete_documents_by_source(source)
            self.logger.info(f"Deleted {count} documents from source: {source}")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to delete documents from {source}: {str(e)}")
            raise RAGServiceException(f"Deletion failed: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the knowledge base.
        
        Args:
            
        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.vector_db.get_collection_stats()
            
            stats.update({
                "embedding_model": rag_settings.embedding_model,
                "chunk_size": rag_settings.chunk_size,
                "chunk_overlap": rag_settings.chunk_overlap,
                "similarity_threshold": rag_settings.similarity_threshold,
                "top_k": rag_settings.top_k,
            })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {str(e)}")
            return {}


# Global RAG service instance
rag_service = RAGService()

__all__ = [
    'RAGService',
    'RAGServiceException',
    'rag_service',
]
