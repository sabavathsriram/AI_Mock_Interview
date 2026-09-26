"""
RAG Configuration Module
Manages all RAG-related settings and environment variables.
"""

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class RAGSettings(BaseSettings):
    """RAG configuration settings loaded from environment variables."""
    
    # Embedding Model Settings
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model to use"
    )
    embedding_dimension: int = Field(
        default=384,
        description="Dimension of embeddings (depends on model)"
    )
    
    # ChromaDB Settings
    chromadb_path: str = Field(
        default="./data/vector_db",
        description="Path to persistent ChromaDB storage"
    )
    chromadb_collection_name: str = Field(
        default="knowledge_base",
        description="Default ChromaDB collection name"
    )
    
    # Document Processing Settings
    chunk_size: int = Field(
        default=500,
        description="Number of characters per chunk"
    )
    chunk_overlap: int = Field(
        default=100,
        description="Number of overlapping characters between chunks"
    )
    
    # Retrieval Settings
    top_k: int = Field(
        default=5,
        description="Number of top documents to retrieve"
    )
    similarity_threshold: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1) for relevance"
    )
    
    # Knowledge Base Categories
    supported_categories: list = Field(
        default=[
            "interview_preparation",
            "technical_concepts",
            "behavioral_interview",
            "hr_interview",
            "programming",
            "data_structures",
            "algorithms",
            "dbms",
            "operating_systems",
            "computer_networks",
            "oop",
            "machine_learning",
            "ai",
            "cloud",
            "resume_preparation",
            "communication",
        ],
        description="Supported knowledge base categories"
    )
    
    # Knowledge Base Directory
    knowledge_base_dir: str = Field(
        default="./data/knowledge_base",
        description="Directory containing source documents"
    )
    
    # Ingestion Settings
    max_batch_size: int = Field(
        default=100,
        description="Maximum number of documents to ingest in one batch"
    )
    
    # Enable/Disable Features
    enable_metadata_filtering: bool = Field(
        default=True,
        description="Whether to apply metadata-based filtering"
    )
    enable_duplicate_detection: bool = Field(
        default=True,
        description="Whether to detect and skip duplicate documents"
    )
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
        env_prefix = "RAG_"
    
    def get_chromadb_path(self) -> Path:
        """Get ChromaDB path as Path object."""
        path = Path(self.chromadb_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_knowledge_base_path(self) -> Path:
        """Get knowledge base path as Path object."""
        path = Path(self.knowledge_base_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def validate_settings(self) -> bool:
        """Validate configuration settings."""
        # Validate chunk sizes
        if self.chunk_size < 100:
            raise ValueError("chunk_size must be >= 100")
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")
        
        # Validate retrieval settings
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")
        
        if not 0.0 <= self.similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0 and 1")
        
        return True
    
    def get_config_dict(self) -> dict:
        """Get safe configuration dictionary for logging."""
        return {
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "chromadb_path": str(self.chromadb_path),
            "chromadb_collection_name": self.chromadb_collection_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k,
            "similarity_threshold": self.similarity_threshold,
            "knowledge_base_dir": self.knowledge_base_dir,
            "categories_count": len(self.supported_categories),
        }


# Global RAG settings instance
try:
    rag_settings = RAGSettings()
    rag_settings.validate_settings()
except Exception as e:
    print(f"Warning: RAG settings validation failed: {str(e)}")
    # Use defaults if validation fails
    rag_settings = RAGSettings()


__all__ = ['RAGSettings', 'rag_settings']
