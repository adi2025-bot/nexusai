"""
Document Analysis Service
Enhanced PDF and document processing for NexusAI.
"""

import io
import re
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("NexusAI.DocumentService")


@dataclass
class DocumentChunk:
    """A chunk of document content."""
    text: str
    page: Optional[int] = None
    chunk_index: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DocumentAnalysis:
    """Result of document analysis."""
    filename: str
    file_type: str
    total_pages: int
    total_chars: int
    total_words: int
    chunks: List[DocumentChunk]
    summary: str = ""
    error: Optional[str] = None
    
    @property
    def full_text(self) -> str:
        """Get all text combined."""
        return "\n\n".join(chunk.text for chunk in self.chunks)


class PDFExtractor:
    """Enhanced PDF text extraction."""
    
    def __init__(self):
        self._has_pypdf = None
        self._has_pdfplumber = None
    
    @property
    def has_pypdf(self) -> bool:
        if self._has_pypdf is None:
            try:
                import PyPDF2
                self._has_pypdf = True
            except ImportError:
                self._has_pypdf = False
        return self._has_pypdf
    
    @property
    def has_pdfplumber(self) -> bool:
        if self._has_pdfplumber is None:
            try:
                import pdfplumber
                self._has_pdfplumber = True
            except ImportError:
                self._has_pdfplumber = False
        return self._has_pdfplumber
    
    def extract(self, file_bytes: bytes, filename: str = "document.pdf") -> DocumentAnalysis:
        """
        Extract text from PDF with multiple fallback methods.
        
        Args:
            file_bytes: PDF file as bytes
            filename: Original filename
        
        Returns:
            DocumentAnalysis with extracted text and metadata
        """
        chunks = []
        total_pages = 0
        error = None
        
        # Try pdfplumber first (better for tables/complex layouts)
        if self.has_pdfplumber:
            try:
                import pdfplumber
                
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    total_pages = len(pdf.pages)
                    
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ""
                        
                        # Also try to extract tables
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                table_text = self._format_table(table)
                                if table_text:
                                    text += f"\n\n[Table on page {i+1}]\n{table_text}"
                        
                        if text.strip():
                            chunks.append(DocumentChunk(
                                text=text.strip(),
                                page=i + 1,
                                chunk_index=i
                            ))
                
                if chunks:
                    return self._create_analysis(filename, "pdf", total_pages, chunks)
                    
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}")
                error = str(e)
        
        # Fallback to PyPDF2
        if self.has_pypdf:
            try:
                import PyPDF2
                
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                total_pages = len(reader.pages)
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        chunks.append(DocumentChunk(
                            text=text.strip(),
                            page=i + 1,
                            chunk_index=i
                        ))
                
                if chunks:
                    return self._create_analysis(filename, "pdf", total_pages, chunks)
                    
            except Exception as e:
                logger.warning(f"PyPDF2 failed: {e}")
                error = str(e)
        
        # Return error result
        return DocumentAnalysis(
            filename=filename,
            file_type="pdf",
            total_pages=total_pages,
            total_chars=0,
            total_words=0,
            chunks=[],
            error=error or "No PDF library available. Install pypdf2 or pdfplumber."
        )
    
    def _format_table(self, table: list) -> str:
        """Format a table as markdown."""
        if not table or not table[0]:
            return ""
        
        lines = []
        for row in table:
            cells = [str(cell) if cell else "" for cell in row]
            lines.append("| " + " | ".join(cells) + " |")
            if len(lines) == 1:
                lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
        
        return "\n".join(lines)
    
    def _create_analysis(
        self, 
        filename: str, 
        file_type: str, 
        total_pages: int, 
        chunks: List[DocumentChunk]
    ) -> DocumentAnalysis:
        """Create DocumentAnalysis from extracted chunks."""
        full_text = "\n\n".join(c.text for c in chunks)
        
        return DocumentAnalysis(
            filename=filename,
            file_type=file_type,
            total_pages=total_pages,
            total_chars=len(full_text),
            total_words=len(full_text.split()),
            chunks=chunks
        )


class DocumentAnalyzer:
    """Main document analysis service."""
    
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pdf_extractor = PDFExtractor()
    
    def analyze(self, file_bytes: bytes, filename: str) -> DocumentAnalysis:
        """
        Analyze a document and extract structured content.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
        
        Returns:
            DocumentAnalysis with text and metadata
        """
        file_ext = filename.lower().split(".")[-1]
        
        if file_ext == "pdf":
            return self.pdf_extractor.extract(file_bytes, filename)
        elif file_ext in ("txt", "md", "py", "js", "json", "csv", "html", "css"):
            return self._analyze_text(file_bytes, filename, file_ext)
        else:
            return DocumentAnalysis(
                filename=filename,
                file_type=file_ext,
                total_pages=0,
                total_chars=0,
                total_words=0,
                chunks=[],
                error=f"Unsupported file type: {file_ext}"
            )
    
    def _analyze_text(self, file_bytes: bytes, filename: str, file_ext: str) -> DocumentAnalysis:
        """Analyze plain text files."""
        try:
            # Try different encodings
            text = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text = file_bytes.decode(encoding)
                    break
                except:
                    continue
            
            if text is None:
                return DocumentAnalysis(
                    filename=filename,
                    file_type=file_ext,
                    total_pages=1,
                    total_chars=0,
                    total_words=0,
                    chunks=[],
                    error="Could not decode file"
                )
            
            # Create chunks for large files
            chunks = self._chunk_text(text)
            
            return DocumentAnalysis(
                filename=filename,
                file_type=file_ext,
                total_pages=1,
                total_chars=len(text),
                total_words=len(text.split()),
                chunks=chunks
            )
            
        except Exception as e:
            return DocumentAnalysis(
                filename=filename,
                file_type=file_ext,
                total_pages=0,
                total_chars=0,
                total_words=0,
                chunks=[],
                error=str(e)
            )
    
    def _chunk_text(self, text: str) -> List[DocumentChunk]:
        """Split text into chunks for processing."""
        if len(text) <= self.chunk_size:
            return [DocumentChunk(text=text, chunk_index=0)]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to end at a sentence or paragraph
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break > start + self.chunk_size // 2:
                    end = para_break
                else:
                    # Look for sentence end
                    sentence_end = max(
                        text.rfind(". ", start, end),
                        text.rfind("! ", start, end),
                        text.rfind("? ", start, end)
                    )
                    if sentence_end > start + self.chunk_size // 2:
                        end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    chunk_index=chunk_index
                ))
                chunk_index += 1
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def get_context_for_ai(self, analysis: DocumentAnalysis, max_tokens: int = 8000) -> str:
        """
        Get document content formatted for AI context.
        
        Args:
            analysis: DocumentAnalysis result
            max_tokens: Approximate max tokens (chars / 4)
        
        Returns:
            Formatted string for AI context
        """
        max_chars = max_tokens * 4
        
        header = f"""📄 **Document: {analysis.filename}**
Type: {analysis.file_type.upper()} | Pages: {analysis.total_pages} | Words: {analysis.total_words:,}
---

"""
        
        content = ""
        for chunk in analysis.chunks:
            page_info = f"[Page {chunk.page}]\n" if chunk.page else ""
            chunk_text = page_info + chunk.text + "\n\n"
            
            if len(header) + len(content) + len(chunk_text) > max_chars:
                content += "\n... (content truncated due to length)"
                break
            
            content += chunk_text
        
        return header + content


# Singleton instance
_analyzer = None

def get_document_analyzer() -> DocumentAnalyzer:
    """Get the document analyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = DocumentAnalyzer()
    return _analyzer
