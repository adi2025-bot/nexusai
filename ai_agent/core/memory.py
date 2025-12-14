import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from ai_agent.config.settings import settings
from typing import List, Dict
import uuid
from datetime import date
import logging
import os

logger = logging.getLogger("Atlas.Memory")

class MemoryManager:
    def __init__(self):
        # Initialize vector DB for long-term memory
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.chroma_client.get_or_create_collection(name="atlas_long_term_memory")
        
        # Embedding Model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # In-memory store for short-term session history
        self._short_term_memory: Dict[str, List[Dict[str, str]]] = {}

    # --- Short-Term Memory ---
    def add_interaction(self, session_id: str, role: str, content: str):
        if session_id not in self._short_term_memory:
            self._short_term_memory[session_id] = []
        self._short_term_memory[session_id].append({"role": role, "content": content})
        # Trim to limit
        if len(self._short_term_memory[session_id]) > settings.SHORT_TERM_MEMORY_LIMIT:
            self._short_term_memory[session_id] = self._short_term_memory[session_id][-settings.SHORT_TERM_MEMORY_LIMIT:]

    def get_recent_context(self, session_id: str) -> List[Dict[str, str]]:
        return self._short_term_memory.get(session_id, [])

    # --- Long-Term Memory (RAG) ---
    def _get_embedding(self, text: str) -> List[float]:
        return self.embedding_model.encode([text])[0].tolist()

    def save_important_fact(self, fact: str, source: str):
        """Saves a specific piece of information to long-term memory."""
        embedding = self._get_embedding(fact)
        self.collection.add(
            documents=[fact],
            embeddings=[embedding],
            metadatas=[{"source": source, "timestamp": str(date.today())}],
            ids=[str(uuid.uuid4())]
        )

    def retrieve_relevant_memory(self, query: str, limit: int = 3) -> str:
        """Queries long-term memory for relevant historical facts."""
        try:
            embedding = self._get_embedding(query)
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit
            )
            if not results['documents'] or not results['documents'][0]:
                return ""
            
            formatted_memories = [f"- {doc} (Source: {meta.get('source', 'Unknown')})" 
                                for doc, meta in zip(results['documents'][0], results['metadatas'][0])]
            return "Relevant Long-Term Memories:\n" + "\n".join(formatted_memories) + "\n\n"
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return ""
