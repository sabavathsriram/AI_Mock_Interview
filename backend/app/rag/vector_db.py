"""
Vector Database Management Module
Manages ChromaDB vector database operations with metadata support.
"""

import logging
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.rag.config import rag_settings
from app.rag.document_processor import Chunk

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Represents a document stored in the vector database."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict] = None


@dataclass
class SearchResult:
    """Represents a search result from the vector database."""
    id: str
    content: str
    similarity_score: float
    metadata: Optional[Dict] = None


class VectorDatabase:
    """Manages vector database operations with ChromaDB."""
    
    def __init__(self, collection_name: str = None):
        """
        Initialize vector database.
        
        Args:
            collection_name: Name of the collection to use
        """
        self.collection_name = collection_name or rag_settings.chromadb_collection_name
        self.logger = logger
        self.db_path = rag_settings.get_chromadb_path()
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info(
            f"Initialized vector database at {self.db_path} "
            f"with collection '{self.collection_name}'"
        )
    
    @staticmethod
    def _generate_document_hash(content: str) -> str:
        """
        Generate hash for document content for duplicate detection.
        
        Args:
            content: Document content
            
        Returns:
            SHA256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_chunk(self, chunk: Chunk) -> str:
        """
        Add a single chunk to the vector database.
        
        Args:
            chunk: Chunk to add
            
        Returns:
            Document ID
        """
        try:
            # Prepare metadata
            metadata = {
                "document_id": chunk.document_id,
                "source": chunk.source,
                "document_type": chunk.document_type,
                "category": chunk.category,
                "title": chunk.title,
                **(chunk.metadata or {})
            }
            
            # Add to collection
            self.collection.add(
                ids=[chunk.chunk_id],
                documents=[chunk.content],
                metadatas=[metadata]
            )
            
            return chunk.chunk_id
            
        except Exception as e:
            self.logger.error(f"Failed to add chunk {chunk.chunk_id}: {str(e)}")
            raise
    
    def add_chunks(self, chunks: List[Chunk]) -> List[str]:
        """
        Add multiple chunks to the vector database.
        
        Args:
            chunks: List of chunks to add
            
        Returns:
            List of document IDs
        """
        if not chunks:
            self.logger.warning("No chunks provided to add")
            return []
        
        try:
            ids = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                ids.append(chunk.chunk_id)
                documents.append(chunk.content)
                
                metadata = {
                    "document_id": chunk.document_id,
                    "source": chunk.source,
                    "document_type": chunk.document_type,
                    "category": chunk.category,
                    "title": chunk.title,
                    **(chunk.metadata or {})
                }
                metadatas.append(metadata)
            
            # Add all chunks
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            self.logger.info(f"Added {len(chunks)} chunks to vector database")
            return ids
            
        except Exception as e:
            self.logger.error(f"Failed to add chunks: {str(e)}")
            raise
    
    def search(
        self,
        query_text: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query_text: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        try:
            top_k = top_k or rag_settings.top_k
            similarity_threshold = similarity_threshold or rag_settings.similarity_threshold
            
            # Query the collection
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results or not results["documents"] or not results["documents"][0]:
                self.logger.debug(f"No results for query: {query_text}")
                return []
            
            # Convert ChromaDB distances to similarity scores
            # ChromaDB returns distances (smaller = more similar)
            # Convert to similarity (1 - distance)
            search_results = []
            
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ):
                # Convert distance to similarity (cosine distance to cosine similarity)
                similarity = 1 - distance
                
                # Filter by threshold
                if similarity < similarity_threshold:
                    self.logger.debug(
                        f"Skipping result with low similarity: {similarity} < {similarity_threshold}"
                    )
                    continue
                
                result = SearchResult(
                    id=results["ids"][0][i] if "ids" in results else f"result_{i}",
                    content=doc,
                    similarity_score=similarity,
                    metadata=metadata
                )
                search_results.append(result)
            
            self.logger.info(
                f"Search returned {len(search_results)} results "
                f"(threshold: {similarity_threshold})"
            )
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise
    
    def get_document_by_id(self, document_id: str) -> Optional[VectorDocument]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            VectorDocument or None if not found
        """
        try:
            result = self.collection.get(
                ids=[document_id],
                include=["documents", "metadatas"]
            )
            
            if not result or not result["documents"]:
                return None
            
            return VectorDocument(
                id=document_id,
                content=result["documents"][0],
                metadata=result["metadatas"][0] if result["metadatas"] else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {str(e)}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[document_id])
            self.logger.info(f"Deleted document {document_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return False
    
    def delete_documents_by_source(self, source: str) -> int:
        """
        Delete all documents from a specific source.
        
        Args:
            source: Source identifier
            
        Returns:
            Number of documents deleted
        """
        try:
            # Get all documents from source
            results = self.collection.get(
                where={"source": source}
            )
            
            if not results or not results["ids"]:
                self.logger.info(f"No documents found for source: {source}")
                return 0
            
            # Delete all found documents
            self.collection.delete(ids=results["ids"])
            
            self.logger.info(f"Deleted {len(results['ids'])} documents from {source}")
            return len(results["ids"])
            
        except Exception as e:
            self.logger.error(f"Failed to delete documents from {source}: {str(e)}")
            return 0
    
    def document_exists(self, document_id: str) -> bool:
        """
        Check if a document exists.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if exists
        """
        try:
            result = self.collection.get(ids=[document_id])
            return bool(result and result.get("ids"))
            
        except Exception as e:
            self.logger.error(f"Failed to check document existence: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.
        
        Args:
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "db_path": str(self.db_path)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Args:
            
        Returns:
            True if successful
        """
        try:
            # Get all documents and delete them
            results = self.collection.get()
            
            if results and results.get("ids"):
                self.collection.delete(ids=results["ids"])
                self.logger.warning(
                    f"Cleared {len(results['ids'])} documents from collection"
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear collection: {str(e)}")
            return False


__all__ = [
    'VectorDocument',
    'SearchResult',
    'VectorDatabase',
]
