"""
RAG (Retrieval-Augmented Generation) Module
Reusable RAG pipeline for knowledge base management and semantic search.
"""

from app.rag.config import RAGSettings, rag_settings
from app.rag.document_processor import (
    Document,
    Chunk,
    DocumentCleaner,
    DocumentChunker,
    DocumentLoader,
    DocumentProcessor,
)
from app.rag.vector_db import VectorDatabase, VectorDocument, SearchResult
from app.rag.schemas import (
    RetrievedDocument,
    RAGContext,
    IngestionRequest,
    IngestionResponse,
    SearchRequest,
    SearchResponse,
    DeletionRequest,
    DeletionResponse,
)
from app.rag.service import RAGService, RAGServiceException, rag_service

__all__ = [
    # Config
    'RAGSettings',
    'rag_settings',
    # Document Processing
    'Document',
    'Chunk',
    'DocumentCleaner',
    'DocumentChunker',
    'DocumentLoader',
    'DocumentProcessor',
    # Vector DB
    'VectorDatabase',
    'VectorDocument',
    'SearchResult',
    # Schemas
    'RetrievedDocument',
    'RAGContext',
    'IngestionRequest',
    'IngestionResponse',
    'SearchRequest',
    'SearchResponse',
    'DeletionRequest',
    'DeletionResponse',
    # Service
    'RAGService',
    'RAGServiceException',
    'rag_service',
]
