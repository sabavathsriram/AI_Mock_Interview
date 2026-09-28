"""
RAG Answer Generation Module
Generates answers using retrieved context and LLM with citation support.
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime

from app.llm.service import llm_service
from app.rag.schemas import RAGContext, RetrievedDocument
from app.rag.config import rag_settings

logger = logging.getLogger(__name__)


class AnswerGenerationException(Exception):
    """Exception for answer generation errors."""
    pass


class AnswerGenerator:
    """Generates answers from RAG context using LLM."""
    
    def __init__(self, llm_service_instance=None):
        """
        Initialize answer generator.
        
        Args:
            llm_service_instance: LLM service instance (uses global if None)
        """
        self.llm_service = llm_service_instance or llm_service
        self.logger = logger
    
    def _create_system_prompt(self) -> str:
        """
        Create system prompt for answer generation.
        
        Returns:
            System prompt string
        """
        return """You are a helpful technical interview assistant. Your task is to answer questions about technical topics based on the provided context.

IMPORTANT INSTRUCTIONS:
1. ALWAYS base your answer on the provided context. Do not use knowledge outside the context.
2. If the context does not contain information needed to answer the question, explicitly state: "The provided context does not contain sufficient information to answer this question."
3. Cite the source of information by referencing the document metadata provided.
4. For each fact or statement, indicate which source (document number) it comes from using [Source X] notation.
5. Structure your answer clearly with relevant sections if applicable.
6. Be concise but comprehensive.
7. If the question cannot be answered from the context, suggest what information would be needed.

When citing sources:
- Use format: [Source X] for references
- Include the document category and title when relevant
- Provide confidence level if multiple sources discuss the topic differently"""
    
    def _create_user_prompt(self, query: str, context: RAGContext) -> str:
        """
        Create user prompt with question and context.
        
        Args:
            query: User's question
            context: RAG context with retrieved documents
            
        Returns:
            Formatted user prompt
        """
        # Build context section
        context_text = "RETRIEVED CONTEXT:\n"
        context_text += "=" * 50 + "\n\n"
        
        if not context.retrieved_documents:
            context_text += "No relevant context found.\n"
        else:
            for i, doc in enumerate(context.retrieved_documents, 1):
                # Format source information
                source_info = f"[Source {i}]"
                if doc.source:
                    source_info += f" {doc.source}"
                if doc.category:
                    source_info += f" ({doc.category})"
                if doc.title:
                    source_info += f" - {doc.title}"
                if doc.similarity_score:
                    source_info += f" [Confidence: {doc.similarity_score:.0%}]"
                
                context_text += source_info + "\n"
                context_text += "-" * 40 + "\n"
                context_text += doc.content + "\n"
                context_text += "\n"
        
        context_text += "=" * 50 + "\n\n"
        
        # Build user question
        user_prompt = f"{context_text}USER QUESTION:\n{query}\n\nPLEASE PROVIDE A DETAILED ANSWER BASED ON THE CONTEXT ABOVE."
        
        return user_prompt
    
    async def generate_answer(
        self,
        query: str,
        context: RAGContext,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 2048
    ) -> Dict:
        """
        Generate an answer from query and RAG context.
        
        Args:
            query: User's question
            context: RAG context with retrieved documents
            temperature: LLM temperature (0-2)
            max_tokens: Maximum output tokens
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            if not query or not query.strip():
                raise AnswerGenerationException("Query cannot be empty")
            
            # Check if we have context
            has_relevant_context = len(context.retrieved_documents) > 0
            
            self.logger.info(
                f"Generating answer for query with {len(context.retrieved_documents)} "
                f"retrieved documents (confidence: {context.similarity_scores})"
            )
            
            # Create prompts
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(query, context)
            
            # Generate answer using LLM
            llm_response = await self.llm_service.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            answer_text = llm_response.text
            
            # Extract citations from the answer
            citations = self._extract_citations(answer_text, context)
            
            result = {
                "success": True,
                "query": query,
                "answer": answer_text,
                "has_context": has_relevant_context,
                "documents_used": len(context.retrieved_documents),
                "retrieval_confidence": {
                    "min": min(context.similarity_scores) if context.similarity_scores else 0.0,
                    "max": max(context.similarity_scores) if context.similarity_scores else 0.0,
                    "avg": sum(context.similarity_scores) / len(context.similarity_scores) 
                           if context.similarity_scores else 0.0
                },
                "citations": citations,
                "sources": [
                    {
                        "id": doc.id,
                        "source": doc.source,
                        "category": doc.category,
                        "title": doc.title,
                        "confidence": doc.similarity_score
                    }
                    for doc in context.retrieved_documents
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "model": llm_response.model
            }
            
            self.logger.info(
                f"Answer generated successfully: {len(answer_text)} chars, "
                f"{len(citations)} citations found"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Answer generation failed: {str(e)}")
            raise AnswerGenerationException(f"Failed to generate answer: {str(e)}")
    
    def _extract_citations(self, answer_text: str, context: RAGContext) -> List[Dict]:
        """
        Extract and validate citations from the answer.
        
        Args:
            answer_text: Generated answer text
            context: RAG context with sources
            
        Returns:
            List of citations with source information
        """
        citations = []
        
        # Simple regex to find [Source X] patterns
        import re
        pattern = r'\[Source\s+(\d+)\]'
        matches = re.finditer(pattern, answer_text)
        
        for match in matches:
            source_num = int(match.group(1))
            
            # Validate source number
            if 1 <= source_num <= len(context.retrieved_documents):
                doc = context.retrieved_documents[source_num - 1]
                citations.append({
                    "source_number": source_num,
                    "source": doc.source,
                    "category": doc.category,
                    "title": doc.title,
                    "confidence": doc.similarity_score,
                    "chunk_index": doc.chunk_index
                })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_citations = []
        for cite in citations:
            key = (cite["source_number"], cite["source"])
            if key not in seen:
                unique_citations.append(cite)
                seen.add(key)
        
        return unique_citations
    
    async def generate_answer_with_insufficient_context_handling(
        self,
        query: str,
        context: RAGContext,
        min_confidence_threshold: float = 0.5
    ) -> Dict:
        """
        Generate answer with explicit handling for insufficient context.
        
        Args:
            query: User's question
            context: RAG context
            min_confidence_threshold: Minimum average confidence required
            
        Returns:
            Dictionary with answer or insufficient context message
        """
        try:
            # Check if we have sufficient context
            if not context.retrieved_documents:
                self.logger.warning("No documents retrieved for query")
                return {
                    "success": True,
                    "query": query,
                    "answer": "I don't have any information in my knowledge base related to your question. Please rephrase your question or ask about a different topic that's covered in my training data.",
                    "has_context": False,
                    "documents_used": 0,
                    "insufficient_context": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Check average confidence
            avg_confidence = sum(context.similarity_scores) / len(context.similarity_scores)
            if avg_confidence < min_confidence_threshold:
                self.logger.warning(
                    f"Low confidence context: {avg_confidence} < {min_confidence_threshold}"
                )
                # Still generate answer but flag it
                result = await self.generate_answer(query, context)
                result["insufficient_context"] = True
                result["low_confidence_warning"] = (
                    f"The provided context has a low confidence score ({avg_confidence:.0%}). "
                    "The answer may not be entirely accurate."
                )
                return result
            
            # Generate answer normally
            return await self.generate_answer(query, context)
            
        except Exception as e:
            self.logger.error(f"Answer generation with context handling failed: {str(e)}")
            raise AnswerGenerationException(f"Failed to generate answer: {str(e)}")


# Global answer generator instance
answer_generator = AnswerGenerator()

__all__ = [
    'AnswerGenerator',
    'AnswerGenerationException',
    'answer_generator',
]
