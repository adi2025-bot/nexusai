"""
Embedding Service for RAG.
Converts text chunks to vector embeddings for semantic search.
"""

import logging
from typing import List, Optional, Union
import numpy as np
from dataclasses import dataclass
import hashlib
import os
import pickle

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding operation."""
    text: str
    embedding: np.ndarray
    model: str


class EmbeddingService:
    """
    Text embedding service using sentence-transformers.
    Supports caching for efficiency.
    """
    
    # Default model - good balance of speed and quality
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
    def __init__(
        self,
        model_name: str = None,
        cache_dir: str = None,
        use_cache: bool = True
    ):
        """
        Initialize embedding service.
        
        Args:
            model_name: Sentence-transformer model to use
            cache_dir: Directory to cache embeddings
            use_cache: Whether to use embedding cache
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.use_cache = use_cache
        self.cache_dir = cache_dir or ".embedding_cache"
        
        self._model = None
        self._cache = {}
        
        # Create cache directory
        if use_cache and cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
    
    @property
    def model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Model loaded successfully. Embedding dimension: {self._model.get_sentence_embedding_dimension()}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._model
    
    @property
    def embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.model.get_sentence_embedding_dimension()
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(f"{self.model_name}:{text}".encode()).hexdigest()
    
    def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from cache if available."""
        if not self.use_cache:
            return None
        
        cache_key = self._get_cache_key(text)
        
        # Check memory cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Check disk cache
        if self.cache_dir:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.npy")
            if os.path.exists(cache_file):
                try:
                    embedding = np.load(cache_file)
                    self._cache[cache_key] = embedding
                    return embedding
                except Exception:
                    pass
        
        return None
    
    def _cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache an embedding."""
        if not self.use_cache:
            return
        
        cache_key = self._get_cache_key(text)
        self._cache[cache_key] = embedding
        
        # Save to disk
        if self.cache_dir:
            try:
                cache_file = os.path.join(self.cache_dir, f"{cache_key}.npy")
                np.save(cache_file, embedding)
            except Exception as e:
                logger.warning(f"Failed to save embedding to cache: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        # Check cache
        cached = self._get_cached_embedding(text)
        if cached is not None:
            return cached
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Cache result
        self._cache_embedding(text, embedding)
        
        return embedding
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding
            
        Returns:
            Array of embeddings (n_texts x embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Check cache for each text
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        for i, text in enumerate(texts):
            cached = self._get_cached_embedding(text)
            if cached is not None:
                embeddings.append((i, cached))
            else:
                texts_to_embed.append(text)
                indices_to_embed.append(i)
        
        # Embed uncached texts
        if texts_to_embed:
            logger.info(f"Embedding {len(texts_to_embed)} texts (batch size: {batch_size})")
            new_embeddings = self.model.encode(
                texts_to_embed,
                convert_to_numpy=True,
                batch_size=batch_size,
                show_progress_bar=len(texts_to_embed) > 10
            )
            
            # Cache new embeddings
            for text, embedding in zip(texts_to_embed, new_embeddings):
                self._cache_embedding(text, embedding)
                embeddings.append((indices_to_embed[texts_to_embed.index(text)], embedding))
        
        # Sort by original index and extract embeddings
        embeddings.sort(key=lambda x: x[0])
        return np.array([e[1] for e in embeddings])
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache = {}
        if self.cache_dir and os.path.exists(self.cache_dir):
            import shutil
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)


# Singleton instance
_embedding_service = None


def get_embedding_service(model_name: str = None) -> EmbeddingService:
    """Get or create the embedding service singleton."""
    global _embedding_service
    
    if _embedding_service is None or (model_name and model_name != _embedding_service.model_name):
        _embedding_service = EmbeddingService(
            model_name=model_name,
            cache_dir=".embedding_cache"
        )
    
    return _embedding_service
