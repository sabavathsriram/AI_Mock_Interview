"""
RAG API Endpoints
Endpoints for searching knowledge base and generating answers.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Body, Query, Path
from pydantic import BaseModel, Field

from app.rag.service import rag_service, RAGServiceException
from app.rag.answer_generator import answer_generator, AnswerGenerationException
from app.rag.schemas import SearchRequest, SearchResponse, RAGContext
from app.auth.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class AnswerRequest(BaseModel):
    """Request to generate an answer."""
    query: str = Field(..., min_length=1, description="Question to answer")
    top_k: Optional[int] = Field(None, description="Number of documents to retrieve")
    similarity_threshold: Optional[float] = Field(None, description="Similarity threshold")
    category_filter: Optional[str] = Field(None, description="Filter by knowledge category")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="LLM temperature")
    min_confidence: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Min confidence threshold")


class AnswerResponse(BaseModel):
    """Response with generated answer."""
    success: bool
    query: str
    answer: str
    has_context: bool
    documents_used: int
    retrieval_confidence: dict
    citations: list
    sources: list
    insufficient_context: Optional[bool] = False
    low_confidence_warning: Optional[str] = None
    timestamp: str
    model: str


class SearchResponse(BaseModel):
    """Response with search results."""
    success: bool
    query: str
    documents: list
    total_documents: int
    similarity_threshold: float
    timestamp: str


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(
    request: SearchRequest,
    current_user: dict = None
):
    """
    Search the knowledge base.
    
    Args:
        request: Search request with query
        current_user: Current authenticated user
        
    Returns:
        Search results
    """
    try:
        logger.info(f"Knowledge base search: {request.query}")
        
        # Search with optional category filter
        context = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            category_filter=request.category_filter
        )
        
        # Format response
        documents = []
        for doc in context.retrieved_documents:
            documents.append({
                "id": doc.id,
                "content": doc.content,
                "similarity_score": doc.similarity_score,
                "source": doc.source,
                "category": doc.category,
                "title": doc.title,
                "document_type": doc.document_type,
                "chunk_index": doc.chunk_index
            })
        
        return SearchResponse(
            success=True,
            query=request.query,
            documents=documents,
            total_documents=len(documents),
            similarity_threshold=context.similarity_threshold_used,
            timestamp=context.retrieval_timestamp.isoformat()
        )
        
    except RAGServiceException as e:
        logger.error(f"RAG search error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/answer", response_model=AnswerResponse)
async def generate_answer(
    request: AnswerRequest,
    current_user: dict = None
):
    """
    Generate an answer from the knowledge base.
    
    Retrieves relevant documents and uses LLM to generate a cited answer.
    
    Args:
        request: Answer request with query and parameters
        current_user: Current authenticated user
        
    Returns:
        Generated answer with citations
    """
    try:
        logger.info(f"Generating answer for: {request.query}")
        
        # First, search for relevant documents
        context = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            category_filter=request.category_filter
        )
        
        # Generate answer from context
        result = await answer_generator.generate_answer_with_insufficient_context_handling(
            query=request.query,
            context=context,
            min_confidence_threshold=request.min_confidence
        )
        
        return AnswerResponse(
            success=result["success"],
            query=result["query"],
            answer=result["answer"],
            has_context=result["has_context"],
            documents_used=result["documents_used"],
            retrieval_confidence=result.get("retrieval_confidence", {}),
            citations=result.get("citations", []),
            sources=result.get("sources", []),
            insufficient_context=result.get("insufficient_context", False),
            low_confidence_warning=result.get("low_confidence_warning"),
            timestamp=result["timestamp"],
            model=result["model"]
        )
        
    except AnswerGenerationException as e:
        logger.error(f"Answer generation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RAGServiceException as e:
        logger.error(f"RAG service error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during answer generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statistics")
async def get_rag_statistics(current_user: dict = None):
    """
    Get statistics about the knowledge base.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Knowledge base statistics
    """
    try:
        stats = rag_service.get_statistics()
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error getting RAG statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/categories")
async def get_knowledge_categories(current_user: dict = None):
    """
    Get list of supported knowledge categories.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of categories
    """
    try:
        categories = {
            "supported_categories": [
                "programming",
                "data_structures",
                "algorithms",
                "databases",
                "operating_systems",
                "computer_networks",
                "oops",
                "system_design",
                "web_development",
                "javascript",
                "react",
                "nodejs",
                "python",
                "java",
                "ai_ml",
                "cloud",
                "interview_hr"
            ]
        }
        return {
            "success": True,
            "data": categories
        }
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


__all__ = ['router']
