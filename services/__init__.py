"""Services package initialization."""
from .ai_service import AIService, AIProvider, ChatMessage, AIResponse, create_ai_service
from .search_service import SearchService, SearchResult, get_search_service
from .image_service import (
    ImageService,
    ImageProvider,
    PollinationsProvider,
    ClipdropProvider,
    GeneratedImage,
    create_image_service,
)
from .code_service import (
    CodeExecutor,
    ExecutionResult,
    get_executor,
    extract_code_blocks,
    format_execution_result,
)
from .document_service import (
    DocumentAnalyzer,
    DocumentAnalysis,
    DocumentChunk,
    get_document_analyzer,
)
from .export_service import ChatExporter, get_exporter
from .auth_service import AuthService, User, create_auth_service
from .database_service import DatabaseService, Conversation, Message, create_database_service
from .rag_service import RAGService, RAGContext, get_rag_service, reset_rag_service
from .chunking_service import ChunkingService, Chunk, create_chunking_service
from .embedding_service import EmbeddingService, get_embedding_service
from .vector_store import VectorStore, SearchResult as VectorSearchResult, get_vector_store
from .metrics_service import MetricsService, get_metrics_service, RequestMetrics, RAGMetrics
from .background_service import BackgroundTaskService, get_background_service, BackgroundTask
from .facade_service import LLMFacade, SearchFacade, RAGFacade, NexusService, get_nexus_service

__all__ = [
    "AIService",
    "AIProvider", 
    "ChatMessage",
    "AIResponse",
    "create_ai_service",
    "SearchService",
    "SearchResult",
    "get_search_service",
    "ImageService",
    "ImageProvider",
    "PollinationsProvider",
    "ClipdropProvider",
    "GeneratedImage",
    "create_image_service",
    "CodeExecutor",
    "ExecutionResult",
    "get_executor",
    "extract_code_blocks",
    "format_execution_result",
    "DocumentAnalyzer",
    "DocumentAnalysis",
    "DocumentChunk",
    "get_document_analyzer",
    "ChatExporter",
    "get_exporter",
    "AuthService",
    "User",
    "create_auth_service",
    "DatabaseService",
    "Conversation",
    "Message",
    "create_database_service",
    # RAG Services
    "RAGService",
    "RAGContext",
    "get_rag_service",
    "reset_rag_service",
    "ChunkingService",
    "Chunk",
    "create_chunking_service",
    "EmbeddingService",
    "get_embedding_service",
    "VectorStore",
    "VectorSearchResult",
    "get_vector_store",
]

