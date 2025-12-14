"""
AI Engine - Multi-Provider Support (Groq + Gemini)
This module handles all communication with AI APIs for LLM capabilities.
Supports both Groq Cloud and Google Gemini APIs.
"""

from typing import Generator, List, Dict, Optional
import logging

# Safe imports with fallbacks
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False
    logging.warning("Groq package not installed. Install with: pip install groq")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not installed. Install with: pip install google-generativeai")

import config


class AIEngine:
    """
    AI Engine class that supports multiple AI providers.
    - Groq Cloud (LLaMA 3) - Fast inference
    - Google Gemini - Multimodal capabilities
    """
    
    def __init__(self, provider: str = "groq", api_key: str = None):
        """
        Initialize the AI Engine with specified provider.
        
        Args:
            provider: 'groq' or 'gemini'
            api_key: API key for the selected provider
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.client = None
        self.model = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider."""
        if self.provider == "groq":
            if self.api_key and GROQ_AVAILABLE and Groq:
                self.client = Groq(api_key=self.api_key)
                self.model = config.GROQ_MODEL
            elif not GROQ_AVAILABLE:
                logging.error("Cannot use Groq: package not installed")
        elif self.provider == "gemini":
            if self.api_key and GEMINI_AVAILABLE and genai:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(config.GEMINI_MODEL)
                self.model = config.GEMINI_MODEL
            elif not GEMINI_AVAILABLE:
                logging.error("Cannot use Gemini: package not installed")
    
    def set_provider(self, provider: str, api_key: str):
        """
        Switch AI provider.
        
        Args:
            provider: 'groq' or 'gemini'
            api_key: API key for the new provider
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self._initialize_client()
    
    def is_configured(self) -> bool:
        """Check if the API key is configured."""
        return bool(self.api_key and self.client)
    
    def get_provider_info(self) -> Dict:
        """Get information about current provider."""
        return {
            "provider": self.provider,
            "model": self.model,
            "configured": self.is_configured()
        }
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate a response from the AI model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to override default
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            AI generated response text
        """
        if not self.is_configured():
            return f"❌ **API Key Not Configured**\n\nPlease add your {self.provider.title()} API key in the sidebar."
        
        try:
            if self.provider == "groq":
                return self._generate_groq(messages, system_prompt, temperature, max_tokens)
            elif self.provider == "gemini":
                return self._generate_gemini(messages, system_prompt, temperature, max_tokens)
            else:
                return "❌ Unknown provider"
                
        except Exception as e:
            return f"❌ **Error generating response:** {str(e)}"
    
    def _generate_groq(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate response using Groq API."""
        full_messages = []
        
        # Add system prompt
        system = system_prompt or config.SYSTEM_PROMPT
        full_messages.append({
            "role": "system",
            "content": system
        })
        
        # Add conversation messages
        full_messages.extend(messages)
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _generate_gemini(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate response using Gemini API."""
        # Build conversation history for Gemini
        system = system_prompt or config.SYSTEM_PROMPT
        
        # Combine system prompt with messages
        chat_history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({
                "role": role,
                "parts": [msg["content"]]
            })
        
        # Start chat with system prompt as context
        chat = self.client.start_chat(history=chat_history[:-1] if len(chat_history) > 1 else [])
        
        # Add system prompt to the user's message
        user_message = messages[-1]["content"] if messages else ""
        full_message = f"[Context: {system}]\n\n{user_message}"
        
        # Generate response
        response = chat.send_message(
            full_message,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        )
        
        return response.text
    
    def generate_response_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Generator[str, None, None]:
        """
        Generate a streaming response from the AI model.
        
        Yields:
            Chunks of the AI response as they're generated
        """
        if not self.is_configured():
            yield f"❌ **API Key Not Configured**\n\nPlease add your {self.provider.title()} API key."
            return
        
        try:
            if self.provider == "groq":
                yield from self._stream_groq(messages, system_prompt, temperature, max_tokens)
            elif self.provider == "gemini":
                yield from self._stream_gemini(messages, system_prompt, temperature, max_tokens)
                    
        except Exception as e:
            yield f"❌ **Error:** {str(e)}"
    
    def _stream_groq(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Generator[str, None, None]:
        """Stream response from Groq API."""
        full_messages = []
        
        system = system_prompt or config.SYSTEM_PROMPT
        full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _stream_gemini(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Generator[str, None, None]:
        """Stream response from Gemini API."""
        system = system_prompt or config.SYSTEM_PROMPT
        
        user_message = messages[-1]["content"] if messages else ""
        full_message = f"[Context: {system}]\n\n{user_message}"
        
        response = self.client.generate_content(
            full_message,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            ),
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def generate_quiz(
        self,
        topic: str,
        difficulty: str = "Medium",
        num_questions: int = 5
    ) -> str:
        """
        Generate a quiz on a specific topic.
        
        Args:
            topic: The subject for the quiz
            difficulty: Easy, Medium, or Hard
            num_questions: Number of questions
            
        Returns:
            Formatted quiz with questions and answers
        """
        quiz_prompt = f"""Create a {difficulty} difficulty quiz on "{topic}" with exactly {num_questions} multiple choice questions.

Format each question like this:
### Question X
[Question text]

A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]

**Correct Answer:** [Letter]
**Explanation:** [Brief explanation why this is correct]

---

Make sure questions are educational and test understanding, not just memorization.
"""
        
        messages = [{"role": "user", "content": quiz_prompt}]
        return self.generate_response(messages, temperature=0.5)
    
    def analyze_document(self, text: str, query: str = None) -> str:
        """
        Analyze a document and optionally answer a question about it.
        
        Args:
            text: The document text
            query: Optional question about the document
            
        Returns:
            Analysis or answer
        """
        if query:
            prompt = f"""Based on the following document, answer this question: {query}

Document:
{text[:8000]}

Provide a clear, accurate answer based only on the document content.
"""
        else:
            prompt = f"""Analyze the following document and provide:
1. A brief summary (2-3 sentences)
2. Key points (bullet list)
3. Main topics covered

Document:
{text[:8000]}
"""
        
        messages = [{"role": "user", "content": prompt}]
        return self.generate_response(messages, temperature=0.3)


# Create a global instance with default provider
ai_engine = AIEngine()


def test_connection(provider: str = "groq"):
    """Test the API connection."""
    print(f"Testing {provider} connection...")
    if not ai_engine.is_configured():
        print("❌ API key not configured!")
        return False
    
    try:
        response = ai_engine.generate_response([
            {"role": "user", "content": "Say 'Connection successful!' in one line."}
        ])
        print(f"✅ {response}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
