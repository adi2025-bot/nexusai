"""
Metrics & Analytics Service for NexusAI.
Tracks costs, errors, RAG performance, and provides admin export.
"""

import json
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import streamlit as st

logger = logging.getLogger("NexusAI.Metrics")


# =============================================================================
# COST CONFIGURATION
# =============================================================================
# Approximate costs per 1K tokens (USD)
MODEL_COSTS = {
    # Groq (free tier, but we track "virtual" cost)
    "llama-3.3-70b-versatile": {"input": 0.0, "output": 0.0},
    "llama-3.1-8b-instant": {"input": 0.0, "output": 0.0},
    "mixtral-8x7b-32768": {"input": 0.0, "output": 0.0},
    # Gemini (free tier usage)
    "gemini-2.0-flash-exp": {"input": 0.0, "output": 0.0},
    "gemini-1.5-flash": {"input": 0.0, "output": 0.0},
    "gemini-1.5-pro": {"input": 0.0, "output": 0.0},
    # Default for unknown models
    "default": {"input": 0.001, "output": 0.002},
}


@dataclass
class RequestMetrics:
    """Metrics for a single AI request."""
    request_id: str
    timestamp: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    success: bool
    error_type: Optional[str] = None
    cost_usd: float = 0.0


@dataclass 
class RAGMetrics:
    """Metrics for RAG retrieval."""
    request_id: str
    timestamp: str
    query_length: int
    chunks_retrieved: int
    top_score: float
    sources: List[str] = field(default_factory=list)
    hit: bool = False  # True if relevant chunks found


@dataclass
class SessionMetrics:
    """Aggregated metrics for a session."""
    session_id: str
    start_time: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    rag_hits: int = 0
    rag_misses: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    @property
    def error_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests
    
    @property
    def rag_hit_rate(self) -> float:
        total_rag = self.rag_hits + self.rag_misses
        if total_rag == 0:
            return 0.0
        return self.rag_hits / total_rag


class MetricsService:
    """
    Service for tracking and exporting metrics.
    Uses Streamlit session state for persistence within session.
    """
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize metrics in session state if not present."""
        if "metrics_requests" not in st.session_state:
            st.session_state.metrics_requests = []
        if "metrics_rag" not in st.session_state:
            st.session_state.metrics_rag = []
        if "metrics_session" not in st.session_state:
            st.session_state.metrics_session = SessionMetrics(
                session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
                start_time=datetime.now().isoformat()
            )
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for a request."""
        costs = MODEL_COSTS.get(model, MODEL_COSTS["default"])
        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (completion_tokens / 1000) * costs["output"]
        return input_cost + output_cost
    
    def record_request(
        self,
        request_id: str,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        success: bool,
        error_type: Optional[str] = None
    ):
        """Record metrics for an AI request."""
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        
        metrics = RequestMetrics(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            success=success,
            error_type=error_type,
            cost_usd=cost
        )
        
        st.session_state.metrics_requests.append(asdict(metrics))
        
        # Update session metrics
        session = st.session_state.metrics_session
        session.total_requests += 1
        session.total_tokens += prompt_tokens + completion_tokens
        session.total_cost_usd += cost
        
        if success:
            session.successful_requests += 1
        else:
            session.failed_requests += 1
            if error_type:
                session.errors_by_type[error_type] = session.errors_by_type.get(error_type, 0) + 1
        
        logger.info(f"[{request_id}] Recorded: {provider}/{model}, {prompt_tokens + completion_tokens} tokens, ${cost:.6f}")
    
    def record_rag(
        self,
        request_id: str,
        query_length: int,
        chunks_retrieved: int,
        top_score: float,
        sources: List[str]
    ):
        """Record RAG retrieval metrics."""
        hit = chunks_retrieved > 0 and top_score >= 0.3
        
        metrics = RAGMetrics(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            query_length=query_length,
            chunks_retrieved=chunks_retrieved,
            top_score=top_score,
            sources=sources,
            hit=hit
        )
        
        st.session_state.metrics_rag.append(asdict(metrics))
        
        # Update session metrics
        session = st.session_state.metrics_session
        if hit:
            session.rag_hits += 1
        else:
            session.rag_misses += 1
        
        logger.info(f"[{request_id}] RAG: {chunks_retrieved} chunks, score={top_score:.2f}, hit={hit}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary metrics for current session."""
        session = st.session_state.metrics_session
        return {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "total_requests": session.total_requests,
            "successful_requests": session.successful_requests,
            "failed_requests": session.failed_requests,
            "error_rate": f"{session.error_rate:.1%}",
            "total_tokens": session.total_tokens,
            "total_cost_usd": f"${session.total_cost_usd:.4f}",
            "rag_hits": session.rag_hits,
            "rag_misses": session.rag_misses,
            "rag_hit_rate": f"{session.rag_hit_rate:.1%}",
            "errors_by_type": session.errors_by_type
        }
    
    def export_json(self) -> str:
        """Export all metrics as JSON."""
        data = {
            "session": self.get_session_summary(),
            "requests": st.session_state.metrics_requests,
            "rag": st.session_state.metrics_rag,
            "export_time": datetime.now().isoformat()
        }
        return json.dumps(data, indent=2)
    
    def export_csv(self) -> str:
        """Export request metrics as CSV."""
        requests = st.session_state.metrics_requests
        
        if not requests:
            return "No data to export"
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=requests[0].keys())
        writer.writeheader()
        writer.writerows(requests)
        
        return output.getvalue()
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by provider and model."""
        breakdown = defaultdict(float)
        
        for req in st.session_state.metrics_requests:
            key = f"{req['provider']}/{req['model']}"
            breakdown[key] += req.get("cost_usd", 0)
        
        return dict(breakdown)
    
    def get_error_breakdown(self) -> Dict[str, int]:
        """Get breakdown of errors by type."""
        return st.session_state.metrics_session.errors_by_type.copy()
    
    def reset(self):
        """Reset all metrics."""
        st.session_state.metrics_requests = []
        st.session_state.metrics_rag = []
        st.session_state.metrics_session = SessionMetrics(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            start_time=datetime.now().isoformat()
        )


# Singleton instance
_metrics_service = None


def get_metrics_service() -> MetricsService:
    """Get or create the metrics service singleton."""
    global _metrics_service
    
    if _metrics_service is None:
        _metrics_service = MetricsService()
    
    return _metrics_service
