"""
Tests for the retry decorator with exponential backoff.
"""

import pytest
import time
from utils.retry import retry_with_backoff, RetryExhausted


class TestRetryDecorator:
    """Test cases for retry_with_backoff decorator."""
    
    def test_succeeds_first_try(self):
        """Test that function works normally without retries."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def success():
            nonlocal call_count
            call_count += 1
            return "ok"
        
        result = success()
        assert result == "ok"
        assert call_count == 1
    
    def test_succeeds_after_retries(self):
        """Test that function succeeds after transient failures."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01, jitter=False)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("transient failure")
            return "ok"
        
        result = flaky()
        assert result == "ok"
        assert call_count == 3
    
    def test_exhausts_retries(self):
        """Test that RetryExhausted is raised when all retries fail."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01, jitter=False)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent failure")
        
        with pytest.raises(RetryExhausted) as exc_info:
            always_fails()
        
        assert "Failed after 2 retries" in str(exc_info.value)
        assert call_count == 3  # Initial + 2 retries
    
    def test_respects_retryable_exceptions(self):
        """Test that only specified exceptions trigger retries."""
        call_count = 0
        
        @retry_with_backoff(
            max_retries=3,
            retryable_exceptions=(ConnectionError,),
            base_delay=0.01
        )
        def raises_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("not retryable")
        
        with pytest.raises(ValueError):
            raises_value_error()
        
        # Should only be called once (no retries for ValueError)
        assert call_count == 1
    
    def test_exponential_backoff_timing(self):
        """Test that delays increase exponentially."""
        delays = []
        call_count = 0
        last_call_time = [time.time()]
        
        @retry_with_backoff(
            max_retries=3,
            base_delay=0.05,
            exponential_base=2.0,
            jitter=False,
            retryable_exceptions=(ConnectionError,)
        )
        def timed_failure():
            nonlocal call_count
            now = time.time()
            if call_count > 0:
                delays.append(now - last_call_time[0])
            last_call_time[0] = now
            call_count += 1
            if call_count <= 3:
                raise ConnectionError("retry me")
            return "ok"
        
        result = timed_failure()
        assert result == "ok"
        
        # Check delays are approximately exponential (with tolerance)
        assert len(delays) == 3
        assert delays[0] >= 0.04  # ~0.05 base
        assert delays[1] >= 0.08  # ~0.10 (0.05 * 2)
        assert delays[2] >= 0.15  # ~0.20 (0.05 * 4)
    
    def test_on_retry_callback(self):
        """Test that on_retry callback is called correctly."""
        retry_info = []
        
        def track_retry(exc, attempt):
            retry_info.append((type(exc).__name__, attempt))
        
        @retry_with_backoff(
            max_retries=2,
            base_delay=0.01,
            on_retry=track_retry,
            retryable_exceptions=(ConnectionError,)
        )
        def flaky():
            if len(retry_info) < 2:
                raise ConnectionError("retry")
            return "ok"
        
        result = flaky()
        assert result == "ok"
        assert len(retry_info) == 2
        assert retry_info[0] == ("ConnectionError", 0)
        assert retry_info[1] == ("ConnectionError", 1)
    
    def test_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @retry_with_backoff(max_retries=1)
        def documented_function():
            """This is a docstring."""
            return "ok"
        
        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
