"""
HTML/XSS sanitization utilities for NexusAI.
Provides secure handling of user-controlled content.
"""

import html
import re
from typing import Optional


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return html.escape(text, quote=True)


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename for safe display in HTML.
    
    - Escapes HTML entities
    - Removes path separators
    - Truncates length
    - Removes null bytes and control chars
    """
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = filename.replace("\\", "/").split("/")[-1]
    
    # Remove null bytes and control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Truncate
    if len(filename) > max_length:
        name_parts = filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            filename = name[:max_length - len(ext) - 4] + "..." + "." + ext
        else:
            filename = filename[:max_length - 3] + "..."
    
    # HTML escape
    return escape_html(filename)


def sanitize_snippet(text: str, max_length: int = 300) -> str:
    """
    Sanitize text snippet for display.
    Strips HTML tags, escapes entities, truncates.
    """
    if not text:
        return ""
    
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode common entities
    text = html.unescape(text)
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Truncate
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    # Re-escape for safe display
    return escape_html(text)


def sanitize_for_prompt(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text before inserting into LLM prompts.
    Removes potential injection patterns and limits length.
    """
    if not text:
        return ""
    
    # Strip HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove common injection patterns
    text = re.sub(
        r'(ignore previous|disregard|forget all|new instructions)',
        '[filtered]',
        text,
        flags=re.I
    )
    
    # Truncate
    return text[:max_length]


def safe_html_content(user_content: str) -> str:
    """
    Prepare user content for st.markdown with unsafe_allow_html=True.
    Returns escaped content safe for embedding.
    """
    return escape_html(user_content)


def sanitize_log_message(message: str, max_length: int = 200) -> str:
    """
    Sanitize message for logging.
    Redacts potentially sensitive patterns.
    """
    if not message:
        return ""
    
    # Redact email patterns
    message = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[email]', message)
    
    # Redact phone patterns
    message = re.sub(r'\b\d{10,}\b', '[phone]', message)
    
    # Truncate
    if len(message) > max_length:
        message = message[:max_length] + "..."
    
    return message
