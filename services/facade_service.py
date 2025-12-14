"""
Unified Service Facades for NexusAI.
Clean, high-level APIs that orchestrate underlying services.
"""

import logging
from typing import Dict, List, Optional, Generator, Any
from dataclasses import dataclass

logger = logging.getLogger("NexusAI.Facades")


# =============================================================================
# LLM SERVICE FACADE
# =============================================================================

class LLMFacade:
    """
    Unified facade for LLM operations.
    Combines AI service with caching, metrics, and fallback logic.
    """
    
    def __init__(self):
        self._ai_service = None
        self._metrics_service = None
    
    @property
    def ai_service(self):
        if self._ai_service is None:
            from services import create_ai_service
            self._ai_service = create_ai_service()
        return self._ai_service
    
    @property
    def metrics(self):
        if self._metrics_service is None:
            from services.metrics_service import get_metrics_service
            self._metrics_service = get_metrics_service()
        return self._metrics_service
    
    def chat(
        self,
        prompt: str,
        history: List[Dict] = None,
        system_prompt: str = None,
        provider: str = None,
        model: str = None,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """
        Send a chat message and stream the response.
        Automatically handles metrics recording.
        
        Args:
            prompt: User message
            history: Previous messages
            system_prompt: System instructions
            provider: AI provider (groq/gemini)
            model: Model name
            temperature: Response randomness
            
        Yields:
            Response text chunks
        """
        import time
        import uuid
        
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Configure service
        if provider:
            self.ai_service.current_provider = provider
        if model:
            self.ai_service.current_model = model
        self.ai_service.temperature = temperature
        
        # Collect response for metrics
        full_response = []
        success = True
        error_type = None
        
        try:
            for chunk in self.ai_service.stream(prompt, history, system_prompt):
                full_response.append(chunk)
                yield chunk
                
        except Exception as e:
            success = False
            from services.ai_service import classify_error
            error_type = classify_error(e).value
            yield f"❌ Error: {str(e)}"
        
        finally:
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            response_text = "".join(full_response)
            
            try:
                self.metrics.record_request(
                    request_id=request_id,
                    provider=self.ai_service.current_provider or "unknown",
                    model=self.ai_service.current_model or "unknown",
                    prompt_tokens=len(prompt) // 4,
                    completion_tokens=len(response_text) // 4,
                    latency_ms=latency_ms,
                    success=success,
                    error_type=error_type
                )
            except:
                pass
    
    def is_ready(self) -> bool:
        """Check if any LLM provider is configured."""
        return self.ai_service.is_ready()
    
    def get_providers(self) -> List[str]:
        """Get available provider names."""
        return self.ai_service.get_available_providers()


# =============================================================================
# SEARCH SERVICE FACADE
# =============================================================================

class SearchFacade:
    """
    Unified facade for search operations.
    Combines web search with caching and RAG integration.
    """
    
    def __init__(self):
        self._search_service = None
    
    @property
    def search_service(self):
        if self._search_service is None:
            from services import get_search_service
            self._search_service = get_search_service()
        return self._search_service
    
    def web_search(self, query: str, max_results: int = 5) -> str:
        """
        Perform a web search and return formatted results.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Formatted search results
        """
        if not self.search_service.is_configured():
            return ""
        
        try:
            results = self.search_service.search(query, max_results)
            if not results:
                return ""
            
            return "\n\n".join([
                f"**{r.title}**\n{r.snippet}\n[Source]({r.url})"
                for r in results
            ])
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return ""
    
    def is_configured(self) -> bool:
        """Check if search is configured."""
        return self.search_service.is_configured()


# =============================================================================
# RAG SERVICE FACADE
# =============================================================================

class RAGFacade:
    """
    Unified facade for RAG operations.
    Combines chunking, embedding, and retrieval with caching.
    """
    
    def __init__(self):
        self._rag_service = None
        self._metrics_service = None
    
    @property
    def rag_service(self):
        if self._rag_service is None:
            from services import get_rag_service
            self._rag_service = get_rag_service()
        return self._rag_service
    
    @property
    def metrics(self):
        if self._metrics_service is None:
            from services.metrics_service import get_metrics_service
            self._metrics_service = get_metrics_service()
        return self._metrics_service
    
    def index_files(self, files: List[Dict]) -> int:
        """
        Index files for RAG retrieval.
        
        Args:
            files: List of {"name": str, "content": str}
            
        Returns:
            Number of chunks indexed
        """
        return self.rag_service.index_uploaded_files(files)
    
    def query(self, query: str, top_k: int = 5) -> Dict:
        """
        Query indexed documents with RAG.
        Records metrics for hit/miss tracking.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            Dict with context_text, sources, and chunks
        """
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        context = self.rag_service.retrieve(query, top_k=top_k)
        
        # Record RAG metrics
        try:
            top_score = context.chunks[0].score if context.chunks else 0.0
            self.metrics.record_rag(
                request_id=request_id,
                query_length=len(query),
                chunks_retrieved=len(context.chunks),
                top_score=top_score,
                sources=context.sources
            )
        except:
            pass
        
        return {
            "context_text": context.context_text,
            "sources": context.sources,
            "chunks": context.chunks
        }
    
    def has_content(self) -> bool:
        """Check if any content is indexed."""
        return self.rag_service.has_indexed_content()
    
    def clear(self):
        """Clear all indexed content."""
        self.rag_service.clear()


# =============================================================================
# UNIFIED NEXUS SERVICE
# =============================================================================

class NexusService:
    """
    Master facade that combines all services.
    Single entry point for all NexusAI operations.
    """
    
    def __init__(self):
        self._llm = None
        self._search = None
        self._rag = None
    
    @property
    def llm(self) -> LLMFacade:
        if self._llm is None:
            self._llm = LLMFacade()
        return self._llm
    
    @property
    def search(self) -> SearchFacade:
        if self._search is None:
            self._search = SearchFacade()
        return self._search
    
    @property
    def rag(self) -> RAGFacade:
        if self._rag is None:
            self._rag = RAGFacade()
        return self._rag
    
    def chat_with_context(
        self,
        prompt: str,
        history: List[Dict] = None,
        system_prompt: str = None,
        use_web_search: bool = False,
        use_rag: bool = True
    ) -> Generator[str, None, None]:
        """
        Enhanced chat that combines LLM, RAG, and web search.
        
        Args:
            prompt: User message
            history: Previous messages
            system_prompt: System instructions
            use_web_search: Whether to search the web
            use_rag: Whether to use RAG context
            
        Yields:
            Response text chunks
        """
        enhanced_prompt = prompt
        context_parts = []
        
        # Add RAG context if available
        if use_rag and self.rag.has_content():
            rag_result = self.rag.query(prompt)
            if rag_result["context_text"]:
                context_parts.append(f"**Document Context:**\n{rag_result['context_text']}")
        
        # Add web search context if enabled
        if use_web_search and self.search.is_configured():
            search_results = self.search.web_search(prompt)
            if search_results:
                context_parts.append(f"**Web Search Results:**\n{search_results}")
        
        # Combine contexts
        if context_parts:
            enhanced_prompt = "\n\n".join(context_parts) + f"\n\n**User Question:** {prompt}"
        
        # Generate response
        yield from self.llm.chat(
            enhanced_prompt,
            history=history,
            system_prompt=system_prompt
        )


# =============================================================================
# SINGLETON
# =============================================================================

_nexus_service = None


def get_nexus_service() -> NexusService:
    """Get or create the NexusService singleton."""
    global _nexus_service
    
    if _nexus_service is None:
        _nexus_service = NexusService()
    
    return _nexus_service
