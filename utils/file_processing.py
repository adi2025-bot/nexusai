"""
File selection and processing utilities.
Handles secure reading and text extraction from various file types.
"""

import io
import logging
from typing import Optional

logger = logging.getLogger("NexusAI.file_processing")


def extract_text_from_file(uploaded_file) -> str:
    """
    Extract text content from an uploaded file.
    Handles PDF specific extraction and falls back to text decoding.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Extracted text string
    """
    if not uploaded_file:
        return ""
        
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        # PDF Handling
        if file_type == 'pdf':
            return _read_pdf(uploaded_file)
            
        # Text/Code Handling
        else:
            # Try UTF-8 first
            content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset pointer
            return content.decode("utf-8", errors="ignore")
            
    except Exception as e:
        logger.error(f"Error reading file {uploaded_file.name}: {e}")
        return f"[Error extracting text from {uploaded_file.name}]"


def _read_pdf(uploaded_file) -> str:
    """Extract text from PDF using pypdf."""
    try:
        import pypdf
        
        # Read into BytesIO structure that pypdf expects
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = []
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
                
        return "\n\n".join(text)
        
    except ImportError:
        return "[Error: pypdf not installed. Please run: pip install pypdf]"
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return f"[Error parsing PDF: {str(e)}]"
