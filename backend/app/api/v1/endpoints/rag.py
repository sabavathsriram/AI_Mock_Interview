"""
RAG API Endpoints
Provides endpoints for testing RAG ingestion and search functionality.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies.auth import get_current_active_user
from app.auth.models.user import UserWithPassword as User
from app.rag import (
    rag_service,
    RAGServiceException,
    IngestionRequest,
    IngestionResponse,
    SearchRequest,
    SearchResponse,
    RAGContext,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
    dependencies=[Depends(get_current_active_user)]
)


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_documents(
    request: IngestionRequest,
    current_user: User = Depends(get_current_active_user)
) -> IngestionResponse:
    """
    Ingest documents into the knowledge base.
    
    Args:
        request: Ingestion request
        current_user: Authenticated user
        
    Returns:
        IngestionResponse with results
    """
    try:
        logger.info(
            f"User {current_user.id} requested document ingestion: {request.document_path}"
        )
        
        chunks_created, added = rag_service.ingest_from_directory(
            directory=request.document_path,
            category=request.category,
            document_type=request.document_type
        )
        
        return IngestionResponse(
            success=True,
            documents_ingested=1,
            chunks_created=chunks_created,
            message=f"Successfully ingested {chunks_created} chunks"
        )
        
    except RAGServiceException as e:
        logger.error(f"Ingestion failed: {str(e)}")
        return IngestionResponse(
            success=False,
            message=str(e),
            errors=[str(e)]
        )
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ingestion failed"
        )


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_base(
    request: SearchRequest,
    current_user: User = Depends(get_current_active_user)
) -> SearchResponse:
    """
    Search the knowledge base.
    
    Args:
        request: Search request
        current_user: Authenticated user
        
    Returns:
        SearchResponse with RAG context
    """
    try:
        logger.info(f"User {current_user.id} searched: {request.query}")
        
        context = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        return SearchResponse(
            success=True,
            context=context,
            message=f"Found {len(context.retrieved_documents)} relevant documents"
        )
        
    except RAGServiceException as e:
        logger.error(f"Search failed: {str(e)}")
        return SearchResponse(
            success=False,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/stats")
async def get_statistics(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Get knowledge base statistics.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Statistics dictionary
    """
    try:
        stats = rag_service.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


__all__ = ['router']
