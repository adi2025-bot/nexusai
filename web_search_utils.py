"""
Cached, sanitized web search using DuckDuckGo.
Provides rate-limited, safe search results for LLM context.
"""

import streamlit as st
import re
import logging
from typing import Optional

logger = logging.getLogger("NexusAI.search")

# Cache TTL in seconds (5 minutes)
CACHE_TTL = 300


def _sanitize_snippet(text: str, max_length: int = 300) -> str:
    """Remove HTML tags and limit length."""
    if not text:
        return ""
    
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text


@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def cached_web_search(
    query: str,
    max_results: int = 5,
    max_snippet_length: int = 200,
    max_total_chars: int = 3000
) -> str:
    """
    Cached, sanitized web search using DuckDuckGo.
    
    Args:
        query: Search query
        max_results: Number of results to fetch
        max_snippet_length: Max chars per snippet
        max_total_chars: Total char limit for all results
    
    Returns:
        Sanitized search results as formatted string
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        logger.warning("duckduckgo_search not installed")
        return ""
    
    # Normalize query for caching
    query = query.strip()[:200]
    
    if not query:
        return ""
    
    try:
        logger.info(f"Web search: '{query[:50]}...'")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                region='wt-wt',
                safesearch='moderate',
                max_results=max_results
            ))
        
        if not results:
            # Try with different region
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    region='in-en',
                    max_results=max_results
                ))
        
        if not results:
            logger.info("No web results found")
            return ""
        
        logger.info(f"Found {len(results)} web results")
        
        # Sanitize and format
        formatted = []
        total_chars = 0
        
        for i, r in enumerate(results, 1):
            if total_chars >= max_total_chars:
                break
            
            title = _sanitize_snippet(r.get('title', ''), max_length=100)
            body = _sanitize_snippet(r.get('body', ''), max_length=max_snippet_length)
            source = r.get('href', '')[:200]
            
            entry = f"{i}. {title}\n   {body}\n   Source: {source}"
            
            if total_chars + len(entry) > max_total_chars:
                break
            
            formatted.append(entry)
            total_chars += len(entry)
        
        return "\n\n".join(formatted)
        
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
        return ""


def should_search(prompt: str) -> bool:
    """
    Determine if query warrants a web search.
    Skip for simple greetings and very short messages.
    """
    prompt_lower = prompt.lower().strip()
    
    # Skip patterns
    skip_patterns = [
        'hi', 'hello', 'hey', 'thanks', 'thank you', 
        'ok', 'bye', 'good', 'yes', 'no', 'sure'
    ]
    
    # If message is very short (under 3 words) and is a greeting, skip
    words = prompt_lower.split()
    if len(words) <= 2:
        for p in skip_patterns:
            if prompt_lower.startswith(p):
                return False
    
    return True


def get_search_context(prompt: str, enabled: bool = True) -> str:
    """
    Get web search context for a prompt.
    
    Args:
        prompt: User's query
        enabled: Whether search is enabled (from sidebar toggle)
    
    Returns:
        Formatted search context or empty string
    """
    if not enabled:
        return ""
    
    if not should_search(prompt):
        return ""
    
    results = cached_web_search(prompt)
    
    if results:
        return f"\n\n## LIVE WEB DATA (use this for your answer):\n{results}\n\n"
    
    return ""


def render_search_toggle() -> bool:
    """
    Render search toggle in sidebar.
    
    Returns:
        Whether search is enabled
    """
    return st.sidebar.toggle(
        "🔍 Web Search",
        value=True,
        help="Search the web for live data"
    )


def clear_search_cache():
    """Clear the search cache."""
    cached_web_search.clear()
    logger.info("Search cache cleared")
