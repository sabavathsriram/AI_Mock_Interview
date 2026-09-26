"""
RAG Response Schemas
Defines data structures for RAG pipeline responses.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RetrievedDocument(BaseModel):
    """Represents a retrieved document from RAG."""
    
    id: str = Field(..., description="Document chunk ID")
    content: str = Field(..., description="Document content")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    source: Optional[str] = Field(None, description="Document source")
    document_type: Optional[str] = Field(None, description="Type of document")
    category: Optional[str] = Field(None, description="Document category")
    title: Optional[str] = Field(None, description="Document title")
    chunk_index: Optional[int] = Field(None, description="Chunk index")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")


class RAGContext(BaseModel):
    """RAG response context with query and retrieved documents."""
    
    query: str = Field(..., description="Original query")
    retrieved_documents: List[RetrievedDocument] = Field(
        default_factory=list,
        description="Retrieved documents"
    )
    similarity_scores: List[float] = Field(
        default_factory=list,
        description="Similarity scores of retrieved documents"
    )
    combined_context: str = Field(
        default="",
        description="Combined context from all retrieved documents"
    )
    top_k_used: int = Field(default=0, description="Number of documents requested")
    similarity_threshold_used: float = Field(
        default=0.0,
        description="Similarity threshold used"
    )
    total_documents_retrieved: int = Field(
        default=0,
        description="Total documents retrieved"
    )
    retrieval_timestamp: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="When retrieval was performed"
    )


class IngestionRequest(BaseModel):
    """Request to ingest documents."""
    
    document_path: str = Field(..., description="Path to document or directory")
    category: str = Field(
        default="general",
        description="Document category"
    )
    document_type: str = Field(
        default="text",
        description="Type of document"
    )
    force_overwrite: bool = Field(
        default=False,
        description="Whether to overwrite existing documents"
    )


class IngestionResponse(BaseModel):
    """Response from document ingestion."""
    
    success: bool = Field(..., description="Whether ingestion succeeded")
    documents_ingested: int = Field(
        default=0,
        description="Number of documents ingested"
    )
    chunks_created: int = Field(
        default=0,
        description="Number of chunks created"
    )
    message: Optional[str] = Field(None, description="Status message")
    errors: List[str] = Field(
        default_factory=list,
        description="List of errors if any"
    )


class SearchRequest(BaseModel):
    """Request to search the knowledge base."""
    
    query: str = Field(..., min_length=1, description="Search query")
    top_k: Optional[int] = Field(None, description="Number of results to retrieve")
    similarity_threshold: Optional[float] = Field(None, description="Similarity threshold")
    category_filter: Optional[str] = Field(None, description="Filter by category")


class SearchResponse(BaseModel):
    """Response from knowledge base search."""
    
    success: bool = Field(..., description="Whether search succeeded")
    context: Optional[RAGContext] = Field(None, description="RAG context")
    message: Optional[str] = Field(None, description="Status message")


class DeletionRequest(BaseModel):
    """Request to delete documents."""
    
    source: str = Field(..., description="Source to delete")
    confirm: bool = Field(
        default=False,
        description="Confirmation to delete"
    )


class DeletionResponse(BaseModel):
    """Response from deletion request."""
    
    success: bool = Field(..., description="Whether deletion succeeded")
    documents_deleted: int = Field(default=0, description="Number of documents deleted")
    message: Optional[str] = Field(None, description="Status message")


__all__ = [
    'RetrievedDocument',
    'RAGContext',
    'IngestionRequest',
    'IngestionResponse',
    'SearchRequest',
    'SearchResponse',
    'DeletionRequest',
    'DeletionResponse',
]
