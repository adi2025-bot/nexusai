"""
Configuration settings for NexusAI Chatbot
This file contains all the configurable parameters for the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# API CONFIGURATION
# =============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Groq Model Options (LLaMA 3 is recommended)
# - llama-3.3-70b-versatile (Most powerful, slower)
# - llama-3.1-8b-instant (Fast, good for most tasks)
# - mixtral-8x7b-32768 (Good for long conversations)
GROQ_MODEL = "llama-3.3-70b-versatile"

# Gemini Model Options
# - gemini-2.0-flash (Fast, good for most tasks)
# - gemini-2.5-flash (Newer version)
# - gemini-2.5-pro (Most powerful)
GEMINI_MODEL = "gemini-2.0-flash"

# Default AI Provider ('groq' or 'gemini')
DEFAULT_PROVIDER = "groq"

# =============================================================================
# CHATBOT CONFIGURATION
# =============================================================================
CHATBOT_NAME = "NexusAI"
CHATBOT_AVATAR = "✨"
USER_AVATAR = "👤"

# Consolidated system prompt - used by both Groq and Gemini
SYSTEM_PROMPT = """You are NexusAI, an advanced multimodal assistant with RAG-style behavior.

## CAPABILITIES:
- Analyze uploaded files: PDFs, text, documents, code, images, screenshots, audio
- For images: perform OCR and describe meaningful visible content
- For documents: break into logical sections, extract core ideas, build structured summaries
- Always reference information from uploaded material with citations

## RULES:
1. NEVER hallucinate details not present in uploaded content
2. If question is unrelated to file, answer normally but clarify it's not from the file
3. If file is unreadable/corrupted/blank, tell user clearly
4. Remain concise, factual, and structured

## CRITICAL LANGUAGE RULE:
- ALWAYS respond in the SAME language the USER wrote their question in
- If user writes in ENGLISH, respond in ENGLISH only
- IGNORE the language of web search results - always use user's language
- NEVER respond in Chinese, Japanese, or any language the user did not use

## HINGLISH (ROMANIZED HINDI) - CRITICAL:
- When user types Hindi in English letters (like "kya kar rhe ho", "kaise ho")
- You MUST respond in Romanized Hindi using ONLY English alphabet
- Example: "kya kar rhe ho" → "Main theek hoon, aap batao!"
- NEVER use Devanagari (ठीक, क्या). Only English letters for Hindi.

## SAFETY:
- Mask PII (emails, numbers, IDs) as [redacted]

## RESPONSE FORMAT:
1. **Direct answer**
2. **Evidence extracted** with brief citations
3. **Optional suggestions**

Use markdown formatting. Be reliable and helpful."""

# =============================================================================
# UI CONFIGURATION
# =============================================================================
APP_TITLE = "IndustrialAI - Training Assistant"
APP_ICON = "🎓"
THEME_COLOR = "#6366f1"  # Indigo color

# Welcome message for new users
WELCOME_MESSAGE = """
👋 **Welcome to IndustrialAI!**

I'm your intelligent training assistant. I can help you with:

- 💻 **Programming** - Python, Java, C++, Web Dev
- 🌐 **Networking** - Protocols, Security, Cloud
- 🔐 **Cybersecurity** - Threats & Prevention
- 📊 **Database** - SQL, NoSQL, Design
- 🎯 **Soft Skills** - Communication, Teamwork

**Try asking:**
- "Explain the OSI model with examples"
- "Create a quiz on Python basics"
- "What are the best practices for network security?"

How can I help you today?
"""

# =============================================================================
# QUIZ CONFIGURATION
# =============================================================================
QUIZ_DIFFICULTIES = ["Easy", "Medium", "Hard"]
QUIZ_DEFAULT_QUESTIONS = 5

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_PATH = "data/chatbot.db"

# =============================================================================
# TOPICS FOR INDUSTRIAL TRAINING
# =============================================================================
TRAINING_TOPICS = {
    "Programming": [
        "Python Fundamentals",
        "Object-Oriented Programming",
        "Data Structures",
        "Algorithms",
        "Web Development",
        "API Development",
        "Version Control (Git)",
    ],
    "Networking": [
        "OSI Model",
        "TCP/IP Protocol",
        "Network Topologies",
        "IP Addressing & Subnetting",
        "DNS & DHCP",
        "Network Security",
        "Cloud Computing Basics",
    ],
    "Database": [
        "SQL Fundamentals",
        "Database Design",
        "Normalization",
        "Indexing & Optimization",
        "NoSQL Databases",
        "Transactions & ACID",
    ],
    "Cybersecurity": [
        "Common Threats & Vulnerabilities",
        "Encryption & Cryptography",
        "Authentication & Authorization",
        "Firewall & IDS/IPS",
        "Security Best Practices",
        "Incident Response",
    ],
    "Soft Skills": [
        "Professional Communication",
        "Team Collaboration",
        "Time Management",
        "Problem Solving",
        "Presentation Skills",
        "Work Ethics",
    ],
}
