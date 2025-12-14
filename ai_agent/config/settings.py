import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    AGENT DEFINITION
    ================
    Name: Atlas
    Role: Autonomous Research & Task Assistant
    Goal: Automate complex information gathering, analysis, and multi-step tasks.
    """
    # --- Model Config ---
    # Using Groq as primary for speed and performance
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Models
    PRIMARY_MODEL: str = "llama-3.3-70b-versatile" # Smartest model on Groq
    FAST_MODEL: str = "llama-3.1-8b-instant"       # Faster model for sub-tasks
    
    # Embedding Model (Local)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # --- Tool Config ---
    # DuckDuckGo fallback if Tavily not present
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # --- Memory Config ---
    CHROMA_PERSIST_DIR: str = "./data/chroma_db_atlas"
    SHORT_TERM_MEMORY_LIMIT: int = 10 

    # --- Execution Config ---
    MAX_REASONING_STEPS: int = 10

settings = Settings()
