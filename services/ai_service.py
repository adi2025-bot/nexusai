"""
AI Service Layer
Unified interface for all AI providers with streaming support.
Features: Request IDs, token limits, graceful fallbacks, structured logging.
"""

import time
import logging
import uuid
from typing import Generator, List, Dict, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger("NexusAI.AIService")


# =============================================================================
# ERROR CLASSIFICATION
# =============================================================================
class LLMErrorType(Enum):
    """Classification of LLM errors for better handling."""
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    TIMEOUT = "timeout"
    CONTENT_BLOCKED = "content_blocked"
    MODEL_ERROR = "model_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


def classify_error(error: Exception) -> LLMErrorType:
    """Classify an LLM error for appropriate handling."""
    error_msg = str(error).lower()
    
    if "rate" in error_msg or "limit" in error_msg or "429" in str(error):
        return LLMErrorType.RATE_LIMIT
    elif "api_key" in error_msg or "invalid" in error_msg or "auth" in error_msg or "401" in str(error):
        return LLMErrorType.AUTH_ERROR
    elif "timeout" in error_msg or "timed out" in error_msg:
        return LLMErrorType.TIMEOUT
    elif "blocked" in error_msg or "safety" in error_msg or "filter" in error_msg:
        return LLMErrorType.CONTENT_BLOCKED
    elif "model" in error_msg and ("not found" in error_msg or "unavailable" in error_msg):
        return LLMErrorType.MODEL_ERROR
    elif "network" in error_msg or "connect" in error_msg:
        return LLMErrorType.NETWORK_ERROR
    else:
        return LLMErrorType.UNKNOWN


# =============================================================================
# TOKEN BUDGET
# =============================================================================
MAX_TOKEN_BUDGET = 8000  # Max tokens for context (conservative)
MAX_HISTORY_MESSAGES = 10  # Max messages to keep in history


def estimate_tokens(text: str) -> int:
    """Estimate token count (~4 chars per token for English)."""
    return len(text) // 4


def trim_to_token_budget(messages: List['ChatMessage'], budget: int = MAX_TOKEN_BUDGET) -> List['ChatMessage']:
    """Trim messages to fit within token budget, keeping most recent."""
    if not messages:
        return messages
    
    total_tokens = sum(estimate_tokens(m.content) for m in messages)
    
    # If within budget, return as-is
    if total_tokens <= budget:
        return messages
    
    # Keep system prompt (first) and most recent messages
    result = []
    current_tokens = 0
    
    # Always keep system prompt if present
    if messages and messages[0].role == "system":
        system_msg = messages[0]
        result.append(system_msg)
        current_tokens = estimate_tokens(system_msg.content)
        messages = messages[1:]
    
    # Add messages from end until budget exceeded
    for msg in reversed(messages):
        msg_tokens = estimate_tokens(msg.content)
        if current_tokens + msg_tokens <= budget:
            result.insert(1 if result else 0, msg)
            current_tokens += msg_tokens
        else:
            break
    
    logger.info(f"Trimmed context from {total_tokens} to {current_tokens} tokens")
    return result


# =============================================================================
# DATA CLASSES
# =============================================================================
@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class AIResponse:
    """Represents an AI response with metadata."""
    content: str
    provider: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency: float = 0.0
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate(self, messages: List[ChatMessage], **kwargs) -> AIResponse:
        """Generate a response synchronously."""
        pass
    
    @abstractmethod
    def stream(self, messages: List[ChatMessage], **kwargs) -> Generator[str, None, None]:
        """Stream response chunks."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available."""
        pass


class GroqProvider(AIProvider):
    """Groq API provider with LLaMA models and vision support."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None
    
    @property
    def client(self):
        """Lazy load the Groq client."""
        if self._client is None and self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                logger.error("Groq package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        return self._client
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def generate(
        self, 
        messages: List[ChatMessage], 
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AIResponse:
        """Generate a response from Groq."""
        if not self.is_available():
            raise ValueError("Groq API not available")
        
        start_time = time.time()
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        latency = time.time() - start_time
        
        usage = response.usage
        return AIResponse(
            content=response.choices[0].message.content,
            provider="groq",
            model=model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency=latency
        )
    
    def stream(
        self, 
        messages: List[ChatMessage],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream response chunks from Groq."""
        if not self.is_available():
            yield "⚠️ Groq API not configured."
            return
        
        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=[m.to_dict() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            yield f"❌ Error: {str(e)}"
    
    def analyze_image(
        self,
        image_data: bytes,
        prompt: str = "Describe this image in detail.",
        model: str = "llama-3.2-11b-vision-instruct"
    ) -> Generator[str, None, None]:
        """
        Analyze an image using Groq's vision model (LLaMA 3.2 Vision).
        
        Args:
            image_data: Raw image bytes (PNG, JPG, etc.)
            prompt: Question or instruction about the image
            model: Vision model to use
        
        Yields:
            Response text chunks
        """
        if not self.is_available():
            yield "⚠️ Groq API not configured."
            return
        
        try:
            import base64
            
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine image type from data
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                media_type = "image/png"
            elif image_data[:2] == b'\xff\xd8':
                media_type = "image/jpeg"
            elif image_data[:6] in (b'GIF87a', b'GIF89a'):
                media_type = "image/gif"
            else:
                media_type = "image/png"  # Default
            
            # Create message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Stream response
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4096,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            error_msg = str(e).lower()
            if "rate" in error_msg or "limit" in error_msg or "429" in str(e):
                yield "📊 Rate limit reached. Please try again in a moment."
            elif "too large" in error_msg:
                yield "❌ Image is too large. Please use a smaller image."
            else:
                logger.error(f"Groq vision error: {e}")
                yield f"❌ Error analyzing image: {str(e)}"


class GeminiProvider(AIProvider):
    """Google Gemini API provider with vision support."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._module = None
    
    @property
    def module(self):
        """Lazy load the Gemini module."""
        if self._module is None and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._module = genai
            except ImportError:
                logger.error("Google GenerativeAI package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
        return self._module
    
    def is_available(self) -> bool:
        return self.module is not None
    
    def generate(
        self, 
        messages: List[ChatMessage],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Generate a response from Gemini."""
        if not self.is_available():
            raise ValueError("Gemini API not available")
        
        start_time = time.time()
        
        # Convert messages to Gemini format
        gemini_model = self.module.GenerativeModel(model)
        
        # Build prompt from messages
        prompt_parts = []
        for msg in messages:
            prefix = "" if msg.role == "user" else f"[{msg.role}]: "
            prompt_parts.append(f"{prefix}{msg.content}")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        response = gemini_model.generate_content(full_prompt)
        latency = time.time() - start_time
        
        content = ""
        if hasattr(response, 'text'):
            content = response.text
        elif hasattr(response, 'parts'):
            content = ''.join(part.text for part in response.parts)
        
        return AIResponse(
            content=content,
            provider="gemini",
            model=model,
            latency=latency
        )
    
    def stream(
        self, 
        messages: List[ChatMessage],
        model: str = "gemini-2.0-flash-exp",
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream response chunks from Gemini."""
        if not self.is_available():
            yield "⚠️ Gemini API not configured."
            return
        
        try:
            gemini_model = self.module.GenerativeModel(model)
            
            # Build prompt
            prompt_parts = []
            for msg in messages:
                prefix = "" if msg.role == "user" else f"[{msg.role}]: "
                prompt_parts.append(f"{prefix}{msg.content}")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            response = gemini_model.generate_content(full_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            error_msg = str(e).lower()
            if "api_key_invalid" in error_msg or "invalid" in error_msg:
                yield "❌ Invalid Gemini API key."
            elif "quota" in error_msg:
                yield "📊 Quota exceeded. Please try again later."
            elif "blocked" in error_msg:
                yield "🚫 Content blocked by safety filters."
            else:
                logger.error(f"Gemini streaming error: {e}")
                yield f"❌ Error: {str(e)}"
    
    def analyze_image(
        self,
        image_data: bytes,
        prompt: str = "Describe this image in detail.",
        model: str = "gemini-2.0-flash-exp"
    ) -> Generator[str, None, None]:
        """
        Analyze an image using Gemini's vision capabilities.
        
        Args:
            image_data: Raw image bytes (PNG, JPG, etc.)
            prompt: Question or instruction about the image
            model: Model to use (must support vision)
        
        Yields:
            Response text chunks
        """
        if not self.is_available():
            yield "⚠️ Gemini API not configured."
            return
        
        try:
            import PIL.Image
            import io
            
            # Load image from bytes
            image = PIL.Image.open(io.BytesIO(image_data))
            
            # Create model
            gemini_model = self.module.GenerativeModel(model)
            
            # Generate content with image
            response = gemini_model.generate_content(
                [prompt, image],
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg:
                yield "📊 Quota exceeded. Please try again later."
            elif "blocked" in error_msg:
                yield "🚫 Content blocked by safety filters."
            elif "unsupported" in error_msg or "image" in error_msg:
                yield "❌ This image format is not supported."
            else:
                logger.error(f"Gemini vision error: {e}")
                yield f"❌ Error analyzing image: {str(e)}"


class AIService:
    """
    Main AI service that manages providers and handles requests.
    Implements the facade pattern for simple API access.
    """
    
    def __init__(self, groq_key: str = "", gemini_key: str = ""):
        self.providers: Dict[str, AIProvider] = {}
        
        if groq_key:
            self.providers["groq"] = GroqProvider(groq_key)
        if gemini_key:
            self.providers["gemini"] = GeminiProvider(gemini_key)
        
        self._current_provider = "groq" if groq_key else ("gemini" if gemini_key else None)
        self._current_model = "llama-3.3-70b-versatile"
        self._temperature = 0.7
    
    @property
    def current_provider(self) -> Optional[str]:
        return self._current_provider
    
    @current_provider.setter
    def current_provider(self, value: str):
        if value in self.providers:
            self._current_provider = value
    
    @property
    def current_model(self) -> str:
        return self._current_model
    
    @current_model.setter
    def current_model(self, value: str):
        self._current_model = value
    
    @property
    def temperature(self) -> float:
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: float):
        self._temperature = max(0.0, min(2.0, value))
    
    def get_provider(self, name: str = None) -> Optional[AIProvider]:
        """Get a provider by name, or the current provider."""
        name = name or self._current_provider
        return self.providers.get(name)
    
    def is_ready(self) -> bool:
        """Check if at least one provider is available."""
        return any(p.is_available() for p in self.providers.values())
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [name for name, p in self.providers.items() if p.is_available()]
    
    def generate(
        self, 
        prompt: str, 
        history: List[Dict] = None,
        system_prompt: str = None,
        **kwargs
    ) -> AIResponse:
        """Generate a response using the current provider."""
        provider = self.get_provider()
        if not provider or not provider.is_available():
            raise ValueError("No AI provider available")
        
        messages = self._build_messages(prompt, history, system_prompt)
        
        return provider.generate(
            messages,
            model=self._current_model,
            temperature=self._temperature,
            **kwargs
        )
    
    def stream(
        self, 
        prompt: str, 
        history: List[Dict] = None,
        system_prompt: str = None,
        enable_fallback: bool = True,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a response using the current provider.
        Features graceful fallback to alternate provider on failure.
        """
        request_id = str(uuid.uuid4())[:8]
        logger.info(f"[{request_id}] Starting stream request")
        
        provider = self.get_provider()
        if not provider or not provider.is_available():
            # Try fallback providers
            if enable_fallback:
                for fallback_name in self.get_available_providers():
                    if fallback_name != self._current_provider:
                        provider = self.providers.get(fallback_name)
                        if provider and provider.is_available():
                            logger.info(f"[{request_id}] Using fallback provider: {fallback_name}")
                            break
        
        if not provider or not provider.is_available():
            yield "⚠️ No AI provider configured."
            return
        
        # Build and trim messages to token budget
        messages = self._build_messages(prompt, history, system_prompt)
        messages = trim_to_token_budget(messages)
        
        # Try primary provider
        try:
            yield from provider.stream(
                messages,
                model=self._current_model,
                temperature=self._temperature,
                **kwargs
            )
            logger.info(f"[{request_id}] Stream completed successfully")
            
        except Exception as e:
            error_type = classify_error(e)
            logger.error(f"[{request_id}] Primary provider failed: {error_type.value} - {e}")
            
            # If fallback is enabled and we have alternate providers, try them
            if enable_fallback:
                for fallback_name in self.get_available_providers():
                    if fallback_name != self._current_provider:
                        fallback_provider = self.providers.get(fallback_name)
                        if fallback_provider and fallback_provider.is_available():
                            logger.info(f"[{request_id}] Trying fallback provider: {fallback_name}")
                            try:
                                # Get default model for fallback provider
                                fallback_model = "llama-3.3-70b-versatile" if fallback_name == "groq" else "gemini-2.0-flash-exp"
                                yield from fallback_provider.stream(
                                    messages,
                                    model=fallback_model,
                                    temperature=self._temperature,
                                    **kwargs
                                )
                                logger.info(f"[{request_id}] Fallback to {fallback_name} succeeded")
                                return
                            except Exception as fallback_e:
                                logger.error(f"[{request_id}] Fallback to {fallback_name} also failed: {fallback_e}")
                                continue
            
            # All providers failed - show user-friendly error
            if error_type == LLMErrorType.RATE_LIMIT:
                yield "📊 Rate limit reached. Please wait a moment and try again."
            elif error_type == LLMErrorType.AUTH_ERROR:
                yield "🔑 API key error. Please check your configuration."
            elif error_type == LLMErrorType.CONTENT_BLOCKED:
                yield "🚫 Content was blocked by safety filters."
            elif error_type == LLMErrorType.TIMEOUT:
                yield "⏱️ Request timed out. Please try again."
            else:
                yield f"❌ An error occurred: {str(e)}"
    
    def _build_messages(
        self, 
        prompt: str, 
        history: List[Dict] = None,
        system_prompt: str = None
    ) -> List[ChatMessage]:
        """Build the message list for the API call."""
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        
        # Add history
        if history:
            for msg in history[-10:]:  # Limit history
                messages.append(ChatMessage(
                    role=msg.get("role", "user"),
                    content=msg.get("content", "")
                ))
        
        # Add current prompt
        messages.append(ChatMessage(role="user", content=prompt))
        
        return messages


# Factory function for easy initialization
def create_ai_service() -> AIService:
    """Create an AI service with settings from environment."""
    from config.settings import settings
    
    return AIService(
        groq_key=settings.ai.groq_api_key,
        gemini_key=settings.ai.gemini_api_key
    )
