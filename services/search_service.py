"""
Search Service
Web search integration for real-time information.
Uses Tavily AI for best results, DuckDuckGo as fallback.
"""

import os
import logging
from typing import Optional, List, Dict
from functools import lru_cache
import hashlib

logger = logging.getLogger("NexusAI.SearchService")


class SearchResult:
    """Represents a single search result."""
    
    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet
    
    def __str__(self) -> str:
        return f"**{self.title}**\n{self.snippet}\nSource: {self.url}"


class SearchService:
    """
    Web search service with multiple providers.
    Priority: Tavily AI > DuckDuckGo
    """
    
    def __init__(self, cache_size: int = 100):
        self._cache: Dict[str, List[SearchResult]] = {}
        self._cache_size = cache_size
        self._tavily_key = os.getenv("TAVILY_API_KEY", "")
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search the web for a query.
        Priority: Tavily AI > SearXNG (free/unlimited) > DuckDuckGo
        """
        # Check cache
        cache_key = self._get_cache_key(query, max_results)
        if cache_key in self._cache:
            logger.debug(f"Cache hit for query: {query[:50]}")
            return self._cache[cache_key]
        
        results = []
        
        # Try Tavily first (best for current data, but limited)
        if self._tavily_key:
            results = self._search_tavily(query, max_results)
            if results:
                self._cache[cache_key] = results
                return results
        
        # Try SearXNG (FREE, UNLIMITED, CURRENT DATA)
        results = self._search_searxng(query, max_results)
        if results:
            self._cache[cache_key] = results
            return results
        
        # Final fallback to DuckDuckGo
        results = self._search_duckduckgo(query, max_results)
        
        # Cache results
        if len(self._cache) >= self._cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[cache_key] = results
        
        return results
    
    def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Tavily AI - best for current/real-time data."""
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self._tavily_key)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True
            )
            
            results = []
            
            # Add the direct answer if available
            if response.get("answer"):
                results.append(SearchResult(
                    title="Direct Answer",
                    url="Tavily AI",
                    snippet=response["answer"]
                ))
            
            # Add search results
            for r in response.get("results", []):
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", "")
                ))
            
            logger.info(f"Tavily search returned {len(results)} results")
            return results
            
        except ImportError:
            logger.warning("Tavily package not installed. Install with: pip install tavily-python")
            return []
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []
    
    def _search_searxng(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using SearXNG - FREE and UNLIMITED with current data."""
        import requests
        
        # Public SearXNG instances (try multiple for reliability)
        instances = [
            "https://searx.be",
            "https://search.sapti.me", 
            "https://searx.tiekoetter.com",
            "https://search.bus-hit.me",
        ]
        
        for instance in instances:
            try:
                response = requests.get(
                    f"{instance}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "categories": "general",
                    },
                    headers={"User-Agent": "NexusAI/1.0"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for r in data.get("results", [])[:max_results]:
                        results.append(SearchResult(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            snippet=r.get("content", "")
                        ))
                    
                    if results:
                        logger.info(f"SearXNG ({instance}) returned {len(results)} results")
                        return results
                        
            except Exception as e:
                logger.debug(f"SearXNG instance {instance} failed: {e}")
                continue
        
        return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        """Fallback search using DuckDuckGo."""
        try:
            from duckduckgo_search import DDGS
            
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results))
            
            results = []
            for r in raw_results:
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", r.get("link", "")),
                    snippet=r.get("body", r.get("snippet", ""))
                ))
            
            return results
            
        except ImportError:
            logger.error("duckduckgo-search package not installed")
            return []
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def format_for_context(self, results: List[SearchResult]) -> str:
        """Format search results for inclusion in AI prompt."""
        if not results:
            return ""
        
        formatted = [
            "=" * 60,
            "🔍 LIVE WEB SEARCH RESULTS (USE THIS DATA TO ANSWER)",
            "=" * 60,
            "",
            "IMPORTANT: The following is REAL-TIME data from the web.",
            "Use these search results to provide accurate, up-to-date answers.",
            "Extract specific facts, dates, and numbers from below:",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            formatted.append(f"--- Result {i} ---")
            formatted.append(f"Title: {result.title}")
            formatted.append(f"Content: {result.snippet}")
            formatted.append(f"Source: {result.url}")
            formatted.append("")
        
        formatted.append("=" * 60)
        formatted.append("Use the above search results to answer the user's question accurately.")
        formatted.append("=" * 60)
        formatted.append("")
        
        return "\n".join(formatted)
    
    def should_search(self, query: str) -> bool:
        """
        Determine if a query would benefit from web search.
        More aggressive - searches for most factual questions.
        
        Args:
            query: User's query
            
        Returns:
            True if web search would be helpful
        """
        query_lower = query.lower().strip()
        words = query_lower.split()
        
        # Skip patterns - commands and simple interactions
        skip_patterns = [
            '/run', '/image', 'generate image', 'draw a', 'create image',
            'make image', 'imagine', 'picture of'
        ]
        if any(query_lower.startswith(p) for p in skip_patterns):
            return False
        
        # Skip simple greetings (very short messages)
        simple_greetings = [
            'hi', 'hello', 'hey', 'thanks', 'thank you', 
            'ok', 'okay', 'bye', 'goodbye', 'good morning',
            'good night', 'how are you', 'yes', 'no', 'sure',
            'great', 'awesome', 'cool', 'nice', 'good'
        ]
        if len(words) <= 3 and any(query_lower.startswith(g) for g in simple_greetings):
            return False
        
        # Skip pure code-related requests (let AI handle these)
        code_patterns = [
            'write code', 'write a code', 'write python', 'write javascript',
            'fix this code', 'debug this', 'explain this code',
            'what does this code', 'convert this code'
        ]
        if any(p in query_lower for p in code_patterns):
            return False
        
        # ALWAYS search for these (definite real-time data)
        always_search = [
            # Time-sensitive
            'latest', 'recent', 'news', 'today', 'current', 'now', 'live',
            'upcoming', 'tomorrow', 'this week', 'this month', 'this year',
            '2023', '2024', '2025', '2026',
            
            # Questions that need facts
            'release date', 'when will', 'when is', 'when does', 'when did',
            'who is', 'who was', 'who are', 'what is', 'what are', 'what was',
            'where is', 'where are', 'how much', 'how many', 'how to',
            
            # Entertainment
            'movie', 'film', 'trailer', 'cast', 'actor', 'actress', 'director',
            'song', 'album', 'artist', 'singer', 'series', 'episode', 'season',
            'ott', 'netflix', 'amazon prime', 'disney', 'streaming',
            
            # Sports
            'score', 'match', 'game', 'tournament', 'winner', 'champion',
            'ipl', 'world cup', 'cricket', 'football', 'fifa', 'nba',
            
            # Finance & Products
            'price', 'cost', 'stock', 'share', 'market', 'crypto', 'bitcoin',
            'launch', 'announced', 'specs', 'features', 'review', 'buy',
            
            # Weather & Location
            'weather', 'temperature', 'forecast', 'located', 'capital', 'population',
            
            # People
            'born', 'died', 'age', 'net worth', 'biography', 'married', 'wife', 'husband',
            'president', 'prime minister', 'ceo', 'founder',
            
            # Events
            'election', 'results', 'update', 'announcement'
        ]
        
        if any(indicator in query_lower for indicator in always_search):
            return True
        
        # Search if query looks like a question (5+ words asking something)
        question_starters = ['tell', 'show', 'find', 'search', 'get', 'give', 'explain', 'describe']
        if len(words) >= 4 and any(query_lower.startswith(q) for q in question_starters):
            return True
        
        # Search if query contains a proper noun (capitalized word) - likely asking about something specific
        if len(words) >= 3 and any(w[0].isupper() for w in query.split() if len(w) > 2):
            return True
        
        # Default: search if query is 5+ words (likely a real question)
        if len(words) >= 5:
            return True
        
        return False
    
    def _get_cache_key(self, query: str, max_results: int) -> str:
        """Generate a cache key for the query."""
        normalized = query.lower().strip()
        return hashlib.md5(f"{normalized}:{max_results}".encode()).hexdigest()
    
    def clear_cache(self):
        """Clear the search cache."""
        self._cache.clear()


# Singleton instance
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get the singleton search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
