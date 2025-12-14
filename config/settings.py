"""
NexusAI Configuration Settings
Centralized configuration management with environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AIConfig:
    """AI Provider configuration."""
    
    # API Keys (from environment)
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))  # For real-time search
    clipdrop_api_key: str = field(default_factory=lambda: os.getenv("CLIPDROP_API_KEY", ""))  # 100 free images/month
    
    # Supabase (Auth & Database)
    supabase_url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))
    
    # Default provider settings
    default_provider: str = "groq"
    default_temperature: float = 0.7
    max_tokens: int = 4096
    max_history: int = 10
    
    # Available models
    groq_models: List[str] = field(default_factory=lambda: [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ])
    
    gemini_models: List[str] = field(default_factory=lambda: [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ])


@dataclass
class AppConfig:
    """Application configuration."""
    
    app_name: str = "NexusAI"
    app_version: str = "4.0.0"
    app_icon: str = "✨"
    
    # UI Settings
    theme: str = "dark"
    layout: str = "wide"
    show_sidebar: bool = True
    
    # Feature flags
    enable_web_search: bool = True
    enable_voice_input: bool = True
    enable_file_upload: bool = True
    enable_tts: bool = True
    enable_rag: bool = True
    enable_image_generation: bool = True  # Pollinations AI (free)
    
    # Cache settings
    cache_ttl: int = 3600  # 1 hour


@dataclass
class DatabaseConfig:
    """Database configuration (for future use)."""
    
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    supabase_url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))


class Settings:
    """
    Singleton settings manager.
    Access configuration via Settings.get()
    """
    
    _instance: Optional['Settings'] = None
    
    def __init__(self):
        self.ai = AIConfig()
        self.app = AppConfig()
        self.db = DatabaseConfig()
    
    @classmethod
    def get(cls) -> 'Settings':
        """Get the singleton settings instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @staticmethod
    def mask_key(key: str, show_chars: int = 4) -> str:
        """
        Mask an API key for safe logging.
        Shows first N chars and masks the rest.
        
        Example: "sk-1234567890" -> "sk-1****"
        """
        if not key:
            return "[NOT SET]"
        if len(key) <= show_chars + 4:
            return key[:show_chars] + "****"
        return key[:show_chars] + "****" + key[-2:]
    
    def validate_keys(self) -> dict:
        """
        Validate all API keys on startup.
        Returns dict with validation status for each key.
        """
        results = {
            "groq": {"valid": False, "message": ""},
            "gemini": {"valid": False, "message": ""},
            "tavily": {"valid": False, "message": ""},
            "supabase": {"valid": False, "message": ""},
        }
        
        # Validate Groq key
        if self.ai.groq_api_key:
            if len(self.ai.groq_api_key) >= 20:
                results["groq"] = {"valid": True, "message": f"Key: {self.mask_key(self.ai.groq_api_key)}"}
            else:
                results["groq"] = {"valid": False, "message": "Key too short (invalid format)"}
        else:
            results["groq"] = {"valid": False, "message": "Not configured"}
        
        # Validate Gemini key
        if self.ai.gemini_api_key:
            if len(self.ai.gemini_api_key) >= 20:
                results["gemini"] = {"valid": True, "message": f"Key: {self.mask_key(self.ai.gemini_api_key)}"}
            else:
                results["gemini"] = {"valid": False, "message": "Key too short (invalid format)"}
        else:
            results["gemini"] = {"valid": False, "message": "Not configured"}
        
        # Validate Tavily key
        if self.ai.tavily_api_key:
            if len(self.ai.tavily_api_key) >= 10:
                results["tavily"] = {"valid": True, "message": f"Key: {self.mask_key(self.ai.tavily_api_key)}"}
            else:
                results["tavily"] = {"valid": False, "message": "Key too short"}
        else:
            results["tavily"] = {"valid": False, "message": "Not configured (web search disabled)"}
        
        # Validate Supabase
        if self.ai.supabase_url and self.ai.supabase_key:
            if "supabase.co" in self.ai.supabase_url:
                results["supabase"] = {"valid": True, "message": f"URL: {self.ai.supabase_url[:30]}..."}
            else:
                results["supabase"] = {"valid": False, "message": "Invalid Supabase URL format"}
        else:
            results["supabase"] = {"valid": False, "message": "Not configured (auth disabled)"}
        
        return results
    
    def get_startup_status(self) -> str:
        """Get a formatted startup status message with masked keys."""
        validation = self.validate_keys()
        
        lines = ["🔑 API Key Status:"]
        for service, status in validation.items():
            icon = "✅" if status["valid"] else "⚠️"
            lines.append(f"  {icon} {service.upper()}: {status['message']}")
        
        return "\n".join(lines)
    
    def has_any_llm_provider(self) -> bool:
        """Check if at least one LLM provider is configured."""
        return self.is_groq_configured() or self.is_gemini_configured()
    
    def is_groq_configured(self) -> bool:
        """Check if Groq API is configured."""
        return bool(self.ai.groq_api_key)
    
    def is_gemini_configured(self) -> bool:
        """Check if Gemini API is configured."""
        return bool(self.ai.gemini_api_key)
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured AI providers."""
        providers = []
        if self.is_groq_configured():
            providers.append("groq")
        if self.is_gemini_configured():
            providers.append("gemini")
        return providers


# Global settings instance
settings = Settings.get()
