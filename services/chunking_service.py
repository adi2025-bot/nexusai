"""
Text Chunking Service for RAG.
Splits documents into optimal chunks for embedding and retrieval.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    start_idx: int
    end_idx: int
    source: str
    chunk_id: int
    token_count: int


class ChunkingService:
    """
    Smart text chunking service.
    Creates overlapping chunks optimized for retrieval.
    """
    
    def __init__(
        self,
        target_chunk_size: int = 500,
        min_chunk_size: int = 100,
        max_chunk_size: int = 800,
        overlap_tokens: int = 50
    ):
        """
        Initialize chunking service.
        
        Args:
            target_chunk_size: Target tokens per chunk
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap_tokens: Overlap between chunks for context
        """
        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_tokens = overlap_tokens
        
        # Try to use tiktoken for accurate token counting
        self._tokenizer = None
        try:
            import tiktoken
            self._tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"tiktoken not available, using word-based estimation: {e}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self._tokenizer:
            return len(self._tokenizer.encode(text))
        # Fallback: estimate ~4 chars per token
        return len(text) // 4
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences preserving structure."""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Filter empty sentences
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def chunk_text(self, text: str, source: str = "document") -> List[Chunk]:
        """
        Split text into chunks optimized for retrieval.
        
        Args:
            text: Full document text
            source: Source filename/identifier
            
        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []
        
        chunks = []
        
        # First split by paragraphs to preserve structure
        paragraphs = self._split_into_paragraphs(text)
        
        current_chunk_text = ""
        current_chunk_start = 0
        chunk_id = 0
        char_position = 0
        
        for para in paragraphs:
            para_tokens = self.count_tokens(para)
            current_tokens = self.count_tokens(current_chunk_text)
            
            # If adding this paragraph would exceed max, save current chunk
            if current_chunk_text and (current_tokens + para_tokens) > self.max_chunk_size:
                if current_tokens >= self.min_chunk_size:
                    chunks.append(Chunk(
                        text=current_chunk_text.strip(),
                        start_idx=current_chunk_start,
                        end_idx=char_position,
                        source=source,
                        chunk_id=chunk_id,
                        token_count=current_tokens
                    ))
                    chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk_text)
                current_chunk_text = overlap_text + "\n\n" + para if overlap_text else para
                current_chunk_start = char_position
            else:
                # Add paragraph to current chunk
                if current_chunk_text:
                    current_chunk_text += "\n\n" + para
                else:
                    current_chunk_text = para
                    current_chunk_start = char_position
            
            char_position += len(para) + 2  # +2 for \n\n
        
        # Don't forget the last chunk
        if current_chunk_text and self.count_tokens(current_chunk_text) >= self.min_chunk_size:
            chunks.append(Chunk(
                text=current_chunk_text.strip(),
                start_idx=current_chunk_start,
                end_idx=char_position,
                source=source,
                chunk_id=chunk_id,
                token_count=self.count_tokens(current_chunk_text)
            ))
        
        logger.info(f"Created {len(chunks)} chunks from {source}")
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of current chunk."""
        if not text:
            return ""
        
        sentences = self._split_into_sentences(text)
        overlap_text = ""
        
        # Take sentences from end until we have enough overlap
        for sentence in reversed(sentences):
            test_text = sentence + " " + overlap_text if overlap_text else sentence
            if self.count_tokens(test_text) <= self.overlap_tokens:
                overlap_text = test_text
            else:
                break
        
        return overlap_text.strip()
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Chunk]:
        """
        Chunk multiple documents.
        
        Args:
            documents: List of {"name": str, "content": str}
            
        Returns:
            All chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            name = doc.get("name", "unknown")
            content = doc.get("content", "")
            chunks = self.chunk_text(content, source=name)
            all_chunks.extend(chunks)
        
        return all_chunks


# Factory function
def create_chunking_service(
    target_size: int = 500,
    overlap: int = 50
) -> ChunkingService:
    """Create a chunking service with default settings."""
    return ChunkingService(
        target_chunk_size=target_size,
        overlap_tokens=overlap
    )
