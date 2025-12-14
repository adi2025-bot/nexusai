"""
Performance Utilities Module
Caching, error handling, retry mechanisms, and optimization utilities.
"""

import time
import hashlib
import logging
import functools
from typing import Any, Callable, Dict, Optional, TypeVar
from dataclasses import dataclass

logger = logging.getLogger("NexusAI.Performance")

T = TypeVar('T')


# =============================================================================
# LRU CACHE WITH TTL
# =============================================================================
class TTLCache:
    """
    Time-based LRU cache for API responses.
    Useful for caching identical queries within a time window.
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self._cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._max_size = max_size
        self._ttl = ttl_seconds
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create a cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cached value if it exists and hasn't expired."""
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Cache a value with current timestamp."""
        # Evict oldest if at capacity
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
    
    @property
    def size(self) -> int:
        """Current cache size."""
        return len(self._cache)


def cached(cache: TTLCache):
    """Decorator to cache function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            key = cache._make_key(func.__name__, *args, **kwargs)
            cached_result = cache.get(key)
            
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator


# =============================================================================
# RETRY MECHANISM
# =============================================================================
@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0
    retryable_exceptions: tuple = (Exception,)


def retry(config: Optional[RetryConfig] = None):
    """
    Decorator to retry failed function calls with exponential backoff.
    
    Usage:
        @retry(RetryConfig(max_attempts=3))
        def api_call():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        delay = min(
                            config.base_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
            
            logger.error(f"All {config.max_attempts} attempts failed for {func.__name__}")
            raise last_exception
        
        return wrapper
    return decorator


# =============================================================================
# ERROR BOUNDARY
# =============================================================================
def safe_execute(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    error_handler: Optional[Callable[[Exception], None]] = None,
    **kwargs
) -> T:
    """
    Execute a function safely, returning a default on error.
    
    Args:
        func: Function to execute
        default: Value to return on error
        error_handler: Optional callback for error handling
        *args, **kwargs: Arguments to pass to func
    
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        if error_handler:
            error_handler(e)
        return default


def error_boundary(default_return: Any = None, log_error: bool = True):
    """
    Decorator to catch and handle exceptions gracefully.
    
    Usage:
        @error_boundary(default_return="Error occurred")
        def risky_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        
        return wrapper
    return decorator


# =============================================================================
# DEBOUNCE & THROTTLE
# =============================================================================
class Debouncer:
    """
    Debounce function calls - only execute after a quiet period.
    Useful for search-as-you-type functionality.
    """
    
    def __init__(self, wait: float = 0.3):
        self._wait = wait
        self._last_call = 0.0
        self._pending_result = None
    
    def should_execute(self) -> bool:
        """Check if enough time has passed since last call."""
        now = time.time()
        if now - self._last_call >= self._wait:
            self._last_call = now
            return True
        return False
    
    def debounce(self, func: Callable[..., T]) -> Callable[..., Optional[T]]:
        """Decorator to debounce function calls."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            if self.should_execute():
                return func(*args, **kwargs)
            return self._pending_result
        
        return wrapper


class Throttler:
    """
    Throttle function calls - limit to one call per time window.
    Useful for rate-limited APIs.
    """
    
    def __init__(self, calls_per_second: float = 1.0):
        self._min_interval = 1.0 / calls_per_second
        self._last_call = 0.0
    
    def throttle(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to throttle function calls."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            now = time.time()
            elapsed = now - self._last_call
            
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            
            self._last_call = time.time()
            return func(*args, **kwargs)
        
        return wrapper


# =============================================================================
# PERFORMANCE METRICS
# =============================================================================
@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    total_requests: int = 0
    total_errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_latency_ms: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return (self.total_errors / self.total_requests * 100) if self.total_requests > 0 else 0.0


def timed(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to log function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    
    return wrapper


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================
# Shared cache for search results (5 min TTL)
search_cache = TTLCache(max_size=50, ttl_seconds=300)

# Shared cache for AI responses (10 min TTL)
response_cache = TTLCache(max_size=100, ttl_seconds=600)

# API throttler (2 calls per second)
api_throttler = Throttler(calls_per_second=2.0)

# Performance metrics
metrics = PerformanceMetrics()
