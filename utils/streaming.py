"""
Normalized streaming adapters for Groq and Gemini.
Provides consistent chunk handling across providers.
"""

from typing import Generator, Any, Iterator, Optional, Dict
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("NexusAI.streaming")


@dataclass
class StreamChunk:
    """Normalized chunk from any provider."""
    text: str
    is_final: bool = False
    usage: Optional[Dict[str, int]] = None


class GroqStreamAdapter:
    """Adapter for Groq streaming responses."""
    
    def __init__(self, stream_response: Iterator[Any], chunk_size: int = 20):
        self._stream = stream_response
        self._chunk_size = chunk_size  # Yield every N chars for smooth UI
    
    def stream(self) -> Generator[StreamChunk, None, None]:
        """Yield normalized chunks from Groq stream."""
        buffer = ""
        usage_data = None
        
        try:
            for chunk in self._stream:
                if not chunk.choices:
                    continue
                    
                delta = chunk.choices[0].delta
                
                if hasattr(delta, 'content') and delta.content:
                    buffer += delta.content
                    
                    # Yield when buffer reaches threshold
                    while len(buffer) >= self._chunk_size:
                        yield StreamChunk(text=buffer[:self._chunk_size])
                        buffer = buffer[self._chunk_size:]
                
                # Check for finish
                finish_reason = chunk.choices[0].finish_reason
                if finish_reason:
                    # Try to extract usage stats
                    if hasattr(chunk, 'usage') and chunk.usage:
                        usage_data = {
                            "prompt_tokens": getattr(chunk.usage, 'prompt_tokens', 0),
                            "completion_tokens": getattr(chunk.usage, 'completion_tokens', 0),
                        }
                    break
        except Exception as e:
            logger.error(f"Groq stream error: {e}")
            if buffer:
                yield StreamChunk(text=buffer, is_final=True)
            raise
        
        # Flush remaining buffer
        if buffer:
            yield StreamChunk(text=buffer, is_final=True, usage=usage_data)
        else:
            yield StreamChunk(text="", is_final=True, usage=usage_data)


class GeminiStreamAdapter:
    """Adapter for Gemini streaming responses."""
    
    def __init__(self, stream_response: Iterator[Any], chunk_size: int = 20):
        self._stream = stream_response
        self._chunk_size = chunk_size
    
    def stream(self) -> Generator[StreamChunk, None, None]:
        """Yield normalized chunks from Gemini stream."""
        buffer = ""
        
        try:
            for chunk in self._stream:
                if hasattr(chunk, 'text') and chunk.text:
                    buffer += chunk.text
                    
                    while len(buffer) >= self._chunk_size:
                        yield StreamChunk(text=buffer[:self._chunk_size])
                        buffer = buffer[self._chunk_size:]
        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            if buffer:
                yield StreamChunk(text=buffer, is_final=True)
            raise
        
        # Flush remaining
        if buffer:
            yield StreamChunk(text=buffer, is_final=True)
        else:
            yield StreamChunk(text="", is_final=True)


def create_stream_adapter(provider: str, stream_response: Iterator[Any]) -> Any:
    """Factory to create appropriate adapter."""
    if provider == "groq":
        return GroqStreamAdapter(stream_response)
    elif provider == "gemini":
        return GeminiStreamAdapter(stream_response)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def stream_response_text(adapter) -> Generator[str, None, Optional[Dict]]:
    """
    Stream text from adapter, accumulating the full response.
    
    Yields:
        Accumulated text so far (for progressive display)
    
    Returns (via generator.value after StopIteration):
        Usage stats dict if available, else None
    
    Usage:
        gen = stream_response_text(adapter)
        full_text = ""
        for text in gen:
            full_text = text
            placeholder.markdown(text + "▌")
        # After loop, full_text contains complete response
    """
    full_text = ""
    usage = None
    
    for chunk in adapter.stream():
        if chunk.text:
            full_text += chunk.text
            yield full_text
        
        if chunk.usage:
            usage = chunk.usage
        
        if chunk.is_final:
            break
    
    return usage
