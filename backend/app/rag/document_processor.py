"""
Document Processor Module
Handles document loading, cleaning, and chunking for RAG pipeline.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.rag.config import rag_settings

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document in the RAG system."""
    content: str
    source: str
    document_type: str
    category: str
    title: str
    metadata: Optional[Dict] = None


@dataclass
class Chunk:
    """Represents a chunk of text from a document."""
    content: str
    document_id: str
    chunk_id: str
    source: str
    document_type: str
    category: str
    title: str
    metadata: Optional[Dict] = None


class DocumentCleaner:
    """Cleans and normalizes document text."""
    
    def __init__(self):
        """Initialize document cleaner."""
        self.logger = logger
    
    def clean(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep common punctuation
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def normalize_section_headers(self, text: str) -> str:
        """
        Normalize section headers for consistency.
        
        Args:
            text: Text with headers
            
        Returns:
            Normalized text
        """
        # Normalize markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Normalize underlined headers
        text = re.sub(r'(.+)\n-+$', r'\1', text, flags=re.MULTILINE)
        
        return text


class DocumentChunker:
    """Chunks documents into manageable pieces."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize document chunker.
        
        Args:
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size or rag_settings.chunk_size
        self.chunk_overlap = chunk_overlap or rag_settings.chunk_overlap
        self.logger = logger
        
        # Create text splitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
    
    def chunk(self, document: Document) -> List[Chunk]:
        """
        Split document into chunks.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of Chunk objects
        """
        # Split text into chunks
        text_chunks = self.splitter.split_text(document.content)
        
        if not text_chunks:
            self.logger.warning(f"No chunks created from {document.source}")
            return []
        
        # Create Chunk objects
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk = Chunk(
                content=chunk_text,
                document_id=document.source,
                chunk_id=f"{document.source}:chunk_{i}",
                source=document.source,
                document_type=document.document_type,
                category=document.category,
                title=document.title,
                metadata={
                    **(document.metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(text_chunks)
                }
            )
            chunks.append(chunk)
        
        self.logger.info(
            f"Created {len(chunks)} chunks from {document.source} "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
        )
        
        return chunks


class DocumentLoader:
    """Loads documents from various sources."""
    
    def __init__(self):
        """Initialize document loader."""
        self.logger = logger
        self.cleaner = DocumentCleaner()
        self.supported_extensions = {'.txt', '.md', '.pdf'}
    
    def load_text_file(
        self,
        file_path: str,
        category: str = "general",
        document_type: str = "text"
    ) -> Optional[Document]:
        """
        Load a text or markdown file.
        
        Args:
            file_path: Path to file
            category: Document category
            document_type: Type of document
            
        Returns:
            Document object or None if failed
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.logger.error(f"File not found: {file_path}")
                return None
            
            if path.suffix.lower() not in {'.txt', '.md'}:
                self.logger.error(f"Unsupported file type: {path.suffix}")
                return None
            
            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                self.logger.warning(f"Empty file: {file_path}")
                return None
            
            # Clean content
            content = self.cleaner.clean(content)
            content = self.cleaner.normalize_section_headers(content)
            
            # Create document
            document = Document(
                content=content,
                source=str(path),
                document_type=document_type,
                category=category,
                title=path.stem
            )
            
            self.logger.info(
                f"Loaded document: {path.name} ({len(content)} chars)"
            )
            
            return document
            
        except Exception as e:
            self.logger.error(f"Failed to load document {file_path}: {str(e)}")
            return None
    
    def load_documents_from_directory(
        self,
        directory: str,
        category: str = "general",
        document_type: str = "text"
    ) -> List[Document]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory: Directory path
            category: Document category
            document_type: Type of document
            
        Returns:
            List of Document objects
        """
        documents = []
        
        try:
            path = Path(directory)
            
            if not path.exists():
                self.logger.error(f"Directory not found: {directory}")
                return documents
            
            # Find all supported files
            for ext in self.supported_extensions:
                for file_path in path.glob(f"**/*{ext}"):
                    doc = self.load_text_file(
                        str(file_path),
                        category=category,
                        document_type=document_type
                    )
                    if doc:
                        documents.append(doc)
            
            self.logger.info(f"Loaded {len(documents)} documents from {directory}")
            return documents
            
        except Exception as e:
            self.logger.error(f"Failed to load documents from {directory}: {str(e)}")
            return []


class DocumentProcessor:
    """Orchestrates document processing pipeline."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
        """
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)
        self.logger = logger
    
    def process_document(self, document: Document) -> List[Chunk]:
        """
        Process a single document into chunks.
        
        Args:
            document: Document to process
            
        Returns:
            List of chunks
        """
        if not document or not document.content.strip():
            self.logger.warning("Cannot process empty document")
            return []
        
        chunks = self.chunker.chunk(document)
        return chunks
    
    def process_documents(self, documents: List[Document]) -> List[Chunk]:
        """
        Process multiple documents into chunks.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of all chunks
        """
        all_chunks = []
        
        for document in documents:
            chunks = self.process_document(document)
            all_chunks.extend(chunks)
        
        self.logger.info(
            f"Processed {len(documents)} documents into {len(all_chunks)} chunks"
        )
        
        return all_chunks
    
    def process_directory(
        self,
        directory: str,
        category: str = "general",
        document_type: str = "text"
    ) -> List[Chunk]:
        """
        Load and process all documents from directory.
        
        Args:
            directory: Directory path
            category: Document category
            document_type: Document type
            
        Returns:
            List of chunks
        """
        documents = self.loader.load_documents_from_directory(
            directory,
            category=category,
            document_type=document_type
        )
        
        chunks = self.process_documents(documents)
        return chunks


__all__ = [
    'Document',
    'Chunk',
    'DocumentCleaner',
    'DocumentChunker',
    'DocumentLoader',
    'DocumentProcessor',
]
