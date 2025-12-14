"""
System prompts for NexusAI chatbot.
Centralized prompt management for Groq and Gemini providers.
"""

from datetime import datetime


def get_system_prompt(include_file_context: bool = False, include_rag_context: bool = False) -> str:
    """
    Generate the system prompt for the AI assistant.
    
    Args:
        include_file_context: Whether to include file analysis instructions
        include_rag_context: Whether to include RAG-specific instructions
        
    Returns:
        Complete system prompt string
    """
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    base_prompt = f"""You are NexusAI, a friendly and intelligent AI assistant.

## TODAY: {current_time}

## CRITICAL: CONVERSATION CONTEXT AWARENESS
- For SHORT FOLLOW-UP REPLIES like "yes", "no", "sure", "ok", "tell me more", "go on", "continue":
  → These ALWAYS refer to the PREVIOUS message in the conversation
  → NEVER treat them as standalone new queries
  → Look at what you JUST asked or offered, and CONTINUE that topic
  → Example: If you asked "Would you like more info on cricket scores?" and user says "yes" → Give them the cricket info!
- ALWAYS maintain conversation continuity
- If unsure what "yes"/"no" refers to, look at YOUR last message

## CONVERSATION STYLE:
- Be natural and conversational - chat like a helpful friend
- For casual questions like "what's up", "how are you" - just respond casually!
- Keep responses concise unless the user asks for detailed explanation
- Use markdown formatting for better readability

## LANGUAGE RULES:
- ALWAYS respond in the SAME language as the user
- If user writes in Hinglish (Hindi in English letters like "kya kar rhe ho") → respond in Hinglish
- NEVER use Devanagari script when user writes in English letters
- IGNORE the language of web search results - always use user's language

## SAFETY:
- Mask PII (emails, phone numbers, IDs) as [redacted]

Be friendly, helpful, and CONTEXT-AWARE!"""

    if include_file_context:
        base_prompt += """

## FILE ANALYSIS MODE:
- Analyze uploaded files: PDFs, text, documents, code, images, screenshots, audio
- For images: perform OCR and describe meaningful visible content
- For documents: break into logical sections, extract core ideas, build structured summaries
- Always reference information from uploaded material with citations
- NEVER hallucinate details not present in uploaded content
- If question is unrelated to file, answer normally but clarify it's not from the file
- If file is unreadable/corrupted/blank, tell user clearly"""

    if include_rag_context:
        base_prompt += """

## RAG MODE:
- You have access to a knowledge base of previously uploaded documents
- When answering, cite specific documents when using retrieved information
- If knowledge base doesn't contain relevant info, say so clearly
- Combine RAG results with your general knowledge when appropriate"""

    return base_prompt


def get_web_search_prompt_context(search_results: str) -> str:
    """
    Format web search results for inclusion in prompt.
    
    Args:
        search_results: Raw search results string
        
    Returns:
        Formatted context string
    """
    if not search_results:
        return ""
    
    return f"""

## LIVE WEB DATA (use this for your answer):
{search_results}

IMPORTANT: Use the above web data to provide accurate, up-to-date information.
"""


def should_use_web_search(prompt: str) -> bool:
    """
    Smart detection for when web search is actually needed.
    Reduces unnecessary API calls while ensuring real-time data for appropriate queries.
    
    Args:
        prompt: User's message
        
    Returns:
        True if web search should be performed
    """
    prompt_lower = prompt.lower().strip()
    words = prompt_lower.split()
    
    # Skip for very short messages (greetings, confirmations)
    if len(words) <= 2:
        skip_patterns = ['hi', 'hello', 'hey', 'thanks', 'thank you', 
                         'ok', 'bye', 'good', 'yes', 'no', 'sure', 'okay']
        if any(prompt_lower.startswith(p) for p in skip_patterns):
            return False
    
    # Skip for coding/technical requests (don't need live data)
    coding_indicators = [
        'write code', 'write a function', 'write a script', 'code for',
        'python code', 'javascript code', 'html code', 'css code',
        'fix this code', 'debug', 'refactor', 'implement',
        'explain this code', 'what does this code', 'how does this code',
        'create a class', 'create a function', 'algorithm for'
    ]
    if any(indicator in prompt_lower for indicator in coding_indicators):
        return False
    
    # Skip for file analysis requests
    file_indicators = [
        'analyze this file', 'summarize this', 'what is in this file',
        'read this', 'extract from', 'parse this', 'uploaded file'
    ]
    if any(indicator in prompt_lower for indicator in file_indicators):
        return False
    
    # Skip for general knowledge questions (AI already knows)
    general_knowledge = [
        'what is a', 'what are', 'explain', 'define', 'meaning of',
        'how to', 'tutorial', 'steps to', 'guide for',
        'difference between', 'compare', 'vs', 'versus'
    ]
    if any(indicator in prompt_lower for indicator in general_knowledge):
        # Unless it's about current events
        current_indicators = ['today', 'now', 'latest', 'current', 'recent', '2024', '2025']
        if not any(curr in prompt_lower for curr in current_indicators):
            return False
    
    # ALWAYS search for real-time data needs
    realtime_indicators = [
        'news', 'latest', 'today', 'current', 'now', 'recent',
        'weather', 'temperature', 'forecast',
        'price', 'stock', 'market', 'bitcoin', 'crypto',
        'score', 'match', 'game', 'ipl', 'cricket', 'football',
        'election', 'politics', 'breaking',
        'release date', 'coming out', 'launch',
        'trending', 'viral', 'popular right now'
    ]
    if any(indicator in prompt_lower for indicator in realtime_indicators):
        return True
    
    # Search for specific entity lookups
    if any(word in prompt_lower for word in ['who is', 'what happened to', 'where is']):
        return True
    
    # Default: Don't search for most conversational queries
    return False
