"""
Lazy-initialized API clients for Groq and Gemini.
Uses @st.cache_resource for efficient caching across Streamlit reruns.
"""

import streamlit as st
import os
import logging
from typing import Optional, Any

logger = logging.getLogger("NexusAI.clients")


def _get_api_key(key_name: str) -> str:
    """
    Get API key from st.secrets (production) or environment (local dev).
    """
    # Try st.secrets first (production Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    
    # Fallback to environment variable (local dev with .env)
    return os.getenv(key_name, "")


@st.cache_resource(show_spinner=False)
def get_groq_client() -> Optional[Any]:
    """
    Lazily initialize Groq client.
    Cached across Streamlit reruns.
    
    Returns:
        Groq client instance or None if not configured
    """
    try:
        from groq import Groq
        
        api_key = _get_api_key("GROQ_API_KEY")
        
        if api_key:
            logger.info("Groq client initialized (cached)")
            return Groq(api_key=api_key)
        else:
            logger.warning("GROQ_API_KEY not found")
            
    except ImportError:
        logger.warning("Groq package not installed. Run: pip install groq")
    except Exception as e:
        logger.error(f"Failed to init Groq client: {e}")
    
    return None


@st.cache_resource(show_spinner=False)
def get_gemini_module() -> Optional[Any]:
    """
    Lazily initialize Gemini configuration.
    Returns the configured genai module.
    
    Returns:
        Configured google.generativeai module or None if not configured
    """
    try:
        import google.generativeai as genai
        
        api_key = _get_api_key("GEMINI_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            logger.info("Gemini configured (cached)")
            return genai
        else:
            logger.warning("GEMINI_API_KEY not found")
            
    except ImportError:
        logger.warning("Google Generative AI not installed. Run: pip install google-generativeai")
    except Exception as e:
        logger.error(f"Failed to init Gemini: {e}")
    
    return None


def is_groq_available() -> bool:
    """Check if Groq client is available and configured."""
    return get_groq_client() is not None


def is_gemini_available() -> bool:
    """Check if Gemini is available and configured."""
    return get_gemini_module() is not None


def get_api_status() -> dict:
    """
    Get status of all API configurations.
    Returns masked key info for diagnostics.
    """
    status = {}
    
    # Check Groq
    groq_key = _get_api_key("GROQ_API_KEY")
    if groq_key:
        masked = f"{groq_key[:4]}...{groq_key[-4:]}" if len(groq_key) > 8 else "****"
        status["groq"] = {"configured": True, "key_preview": masked}
    else:
        status["groq"] = {"configured": False, "key_preview": None}
    
    # Check Gemini
    gemini_key = _get_api_key("GEMINI_API_KEY")
    if gemini_key:
        masked = f"{gemini_key[:4]}...{gemini_key[-4:]}" if len(gemini_key) > 8 else "****"
        status["gemini"] = {"configured": True, "key_preview": masked}
    else:
        status["gemini"] = {"configured": False, "key_preview": None}
    
    return status


def clear_client_cache():
    """Clear cached clients (useful if API keys change)."""
    get_groq_client.clear()
    get_gemini_module.clear()
    logger.info("Client cache cleared")
