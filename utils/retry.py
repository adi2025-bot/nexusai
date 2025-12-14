"""
Robust retry decorator with exponential backoff and jitter.
Handles transient API failures gracefully.
"""

import time
import random
import functools
import logging
from typing import Type, Tuple, Callable, Any, Optional

logger = logging.getLogger("NexusAI.retry")


class RetryExhausted(Exception):
    """Raised when all retry attempts fail."""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for retrying functions with exponential backoff and jitter.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        exponential_base: Multiplier for exponential growth
        jitter: Add randomness to prevent thundering herd
        retryable_exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback(exception, attempt) called on each retry
    
    Example:
        @retry_with_backoff(max_retries=3, retryable_exceptions=(ConnectionError,))
        def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"All {max_retries} retries exhausted for {func.__name__}"
                        )
                        raise RetryExhausted(
                            f"Failed after {max_retries} retries: {str(e)}"
                        ) from e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter (±25%)
                    if jitter:
                        delay = delay * (0.75 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s. Error: {type(e).__name__}: {str(e)[:100]}"
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    time.sleep(delay)
            
            raise last_exception  # Should never reach here
        
        return wrapper
    return decorator


def api_retry(func: Callable) -> Callable:
    """
    Pre-configured retry decorator for API calls.
    Handles common transient errors.
    """
    return retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=15.0,
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
        ),
    )(func)


def web_retry(func: Callable) -> Callable:
    """
    Pre-configured retry for web/search operations.
    Shorter delays, fewer retries.
    """
    return retry_with_backoff(
        max_retries=2,
        base_delay=0.5,
        max_delay=5.0,
        retryable_exceptions=(
            ConnectionError,
            TimeoutError,
        ),
    )(func)
