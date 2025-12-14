"""
RAG Service - Retrieval Augmented Generation.
Coordinates chunking, embedding, storage, and retrieval for document Q&A.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .chunking_service import ChunkingService, Chunk, create_chunking_service
from .embedding_service import EmbeddingService, get_embedding_service
from .vector_store import VectorStore, SearchResult, get_vector_store

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """Context retrieved for a query."""
    chunks: List[SearchResult]
    context_text: str
    sources: List[str]


class RAGService:
    """
    Retrieval Augmented Generation service.
    Handles document ingestion and semantic retrieval.
    """
    
    def __init__(
        self,
        chunking_service: ChunkingService = None,
        embedding_service: EmbeddingService = None,
        vector_store: VectorStore = None
    ):
        """
        Initialize RAG service.
        
        Args:
            chunking_service: Service for text chunking
            embedding_service: Service for text embeddings
            vector_store: Vector storage for retrieval
        """
        self.chunker = chunking_service or create_chunking_service()
        self.embedder = embedding_service or get_embedding_service()
        self.store = vector_store or get_vector_store(
            embedding_dim=self.embedder.embedding_dimension
        )
        
        self._indexed_sources: Dict[str, int] = {}  # source -> chunk count
    
    def index_documents(self, documents: List[Dict[str, str]]) -> int:
        """
        Index documents for retrieval.
        
        Args:
            documents: List of {"name": str, "content": str}
            
        Returns:
            Number of chunks indexed
        """
        if not documents:
            return 0
        
        # Chunk all documents
        all_chunks = self.chunker.chunk_documents(documents)
        
        if not all_chunks:
            logger.warning("No chunks created from documents")
            return 0
        
        # Extract texts and create metadata
        texts = [chunk.text for chunk in all_chunks]
        metadata = [
            {
                "source": chunk.source,
                "chunk_id": chunk.chunk_id,
                "start_idx": chunk.start_idx,
                "end_idx": chunk.end_idx,
                "token_count": chunk.token_count
            }
            for chunk in all_chunks
        ]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.embed_texts(texts)
        
        # Add to vector store
        self.store.add(texts, embeddings, metadata)
        
        # Track indexed sources
        for chunk in all_chunks:
            if chunk.source not in self._indexed_sources:
                self._indexed_sources[chunk.source] = 0
            self._indexed_sources[chunk.source] += 1
        
        logger.info(f"Indexed {len(all_chunks)} chunks from {len(documents)} documents")
        return len(all_chunks)
    
    def index_uploaded_files(
        self,
        uploaded_files: List[Dict],
        uploaded_images: List[Dict] = None
    ) -> int:
        """
        Index uploaded files from session state.
        
        Args:
            uploaded_files: List of {"name": str, "content": str} from session
            uploaded_images: List of image dicts (skipped, images not indexed)
            
        Returns:
            Number of chunks indexed
        """
        # Filter to text-based files only
        text_docs = [
            {"name": f.get("name", "file"), "content": f.get("content", "")}
            for f in uploaded_files
            if f.get("content")
        ]
        
        return self.index_documents(text_docs)
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.3
    ) -> RAGContext:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity threshold
            
        Returns:
            RAGContext with retrieved chunks and formatted context
        """
        if self.store.size == 0:
            return RAGContext(chunks=[], context_text="", sources=[])
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Search vector store
        results = self.store.search(query_embedding, top_k=top_k, min_score=min_score)
        
        if not results:
            return RAGContext(chunks=[], context_text="", sources=[])
        
        # Format context text with source citations
        context_parts = []
        sources = set()
        
        for i, result in enumerate(results):
            sources.add(result.source)
            context_parts.append(
                f"[Source: {result.source}, Chunk {result.chunk_id + 1}, Relevance: {result.score:.2f}]\n"
                f"{result.text}"
            )
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        logger.info(f"Retrieved {len(results)} chunks from {len(sources)} sources for query")
        
        return RAGContext(
            chunks=results,
            context_text=context_text,
            sources=list(sources)
        )
    
    def get_rag_prompt(self, query: str, context: RAGContext) -> str:
        """
        Build a RAG-enhanced prompt.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Enhanced prompt with context
        """
        if not context.chunks:
            return query
        
        return f"""I have retrieved the following relevant information from uploaded documents:

{context.context_text}

---

Based on the above context, please answer this question:
{query}

Important: 
- Use the provided context to answer accurately
- Cite sources when referencing specific information
- If the context doesn't contain the answer, say so clearly"""
    
    def clear(self):
        """Clear all indexed documents."""
        self.store.clear()
        self._indexed_sources = {}
        logger.info("RAG service cleared")
    
    @property
    def indexed_sources(self) -> Dict[str, int]:
        """Get indexed source files and their chunk counts."""
        return self._indexed_sources.copy()
    
    @property
    def total_chunks(self) -> int:
        """Get total number of indexed chunks."""
        return self.store.size
    
    def has_indexed_content(self) -> bool:
        """Check if any content is indexed."""
        return self.store.size > 0


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton."""
    global _rag_service
    
    if _rag_service is None:
        _rag_service = RAGService()
    
    return _rag_service


def reset_rag_service():
    """Reset the RAG service (clears all indexed content)."""
    global _rag_service
    if _rag_service:
        _rag_service.clear()
    _rag_service = None
