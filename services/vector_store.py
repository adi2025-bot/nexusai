"""
Vector Store Service for RAG.
FAISS-based vector storage for fast semantic search.
"""

import logging
import os
import pickle
from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Result from vector search."""
    text: str
    source: str
    chunk_id: int
    score: float
    metadata: Dict = field(default_factory=dict)


class VectorStore:
    """
    FAISS-based vector store for fast semantic search.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize vector store.
        
        Args:
            embedding_dim: Dimension of embeddings (384 for MiniLM)
        """
        self.embedding_dim = embedding_dim
        self._index = None
        self._texts: List[str] = []
        self._metadata: List[Dict] = []
        
        # Try to import FAISS
        try:
            import faiss
            self._faiss = faiss
            self._init_index()
            logger.info(f"FAISS vector store initialized (dim={embedding_dim})")
        except ImportError:
            logger.warning("FAISS not available, using numpy fallback")
            self._faiss = None
            self._embeddings = []
    
    def _init_index(self):
        """Initialize FAISS index."""
        if self._faiss:
            # Use IndexFlatIP for cosine similarity (after normalization)
            self._index = self._faiss.IndexFlatIP(self.embedding_dim)
    
    def add(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadata: Optional[List[Dict]] = None
    ):
        """
        Add texts and their embeddings to the store.
        
        Args:
            texts: List of text strings
            embeddings: Embedding matrix (n_texts x embedding_dim)
            metadata: Optional metadata for each text
        """
        if len(texts) == 0:
            return
        
        # Normalize embeddings for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        normalized = embeddings / norms
        
        if self._faiss and self._index is not None:
            self._index.add(normalized.astype(np.float32))
        else:
            # Numpy fallback
            self._embeddings.extend(normalized.tolist())
        
        self._texts.extend(texts)
        
        if metadata:
            self._metadata.extend(metadata)
        else:
            self._metadata.extend([{} for _ in texts])
        
        logger.info(f"Added {len(texts)} vectors to store (total: {len(self._texts)})")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Search for similar texts.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            min_score: Minimum similarity score threshold
            
        Returns:
            List of SearchResult objects
        """
        if len(self._texts) == 0:
            return []
        
        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_normalized = query_embedding / query_norm
        else:
            return []
        
        if self._faiss and self._index is not None:
            # FAISS search
            query_normalized = query_normalized.reshape(1, -1).astype(np.float32)
            k = min(top_k, len(self._texts))
            scores, indices = self._index.search(query_normalized, k)
            scores = scores[0]
            indices = indices[0]
        else:
            # Numpy fallback
            embeddings = np.array(self._embeddings)
            scores = np.dot(embeddings, query_normalized)
            indices = np.argsort(scores)[::-1][:top_k]
            scores = scores[indices]
        
        results = []
        for score, idx in zip(scores, indices):
            if idx < 0 or score < min_score:
                continue
            
            meta = self._metadata[idx] if idx < len(self._metadata) else {}
            results.append(SearchResult(
                text=self._texts[idx],
                source=meta.get("source", "unknown"),
                chunk_id=meta.get("chunk_id", idx),
                score=float(score),
                metadata=meta
            ))
        
        return results
    
    def clear(self):
        """Clear all vectors from the store."""
        self._texts = []
        self._metadata = []
        
        if self._faiss:
            self._init_index()
        else:
            self._embeddings = []
        
        logger.info("Vector store cleared")
    
    def save(self, path: str):
        """Save vector store to disk."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        
        data = {
            "texts": self._texts,
            "metadata": self._metadata,
            "embedding_dim": self.embedding_dim
        }
        
        if self._faiss and self._index is not None:
            # Save FAISS index separately
            index_path = path + ".faiss"
            self._faiss.write_index(self._index, index_path)
            data["index_path"] = index_path
        else:
            data["embeddings"] = self._embeddings
        
        with open(path, "wb") as f:
            pickle.dump(data, f)
        
        logger.info(f"Vector store saved to {path}")
    
    def load(self, path: str):
        """Load vector store from disk."""
        if not os.path.exists(path):
            logger.warning(f"Vector store file not found: {path}")
            return
        
        with open(path, "rb") as f:
            data = pickle.load(f)
        
        self._texts = data.get("texts", [])
        self._metadata = data.get("metadata", [])
        self.embedding_dim = data.get("embedding_dim", 384)
        
        if self._faiss and "index_path" in data:
            index_path = data["index_path"]
            if os.path.exists(index_path):
                self._index = self._faiss.read_index(index_path)
        else:
            self._embeddings = data.get("embeddings", [])
        
        logger.info(f"Vector store loaded from {path} ({len(self._texts)} vectors)")
    
    @property
    def size(self) -> int:
        """Get number of vectors in store."""
        return len(self._texts)


# Singleton instance
_vector_store = None


def get_vector_store(embedding_dim: int = 384) -> VectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore(embedding_dim=embedding_dim)
    
    return _vector_store


def clear_vector_store():
    """Clear and reset the vector store."""
    global _vector_store
    if _vector_store:
        _vector_store.clear()
    _vector_store = None
