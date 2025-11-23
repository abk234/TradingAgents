# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Document Parser

Parses various document formats (PDF, HTML, TXT) and extracts text content.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import io

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    DOCX = "docx"
    UNKNOWN = "unknown"


class DocumentParser:
    """Parser for various document formats"""
    
    def __init__(self):
        self._pdf_parser = None
        self._docx_parser = None
    
    def detect_type(self, filename: str, content: Optional[bytes] = None) -> DocumentType:
        """
        Detect document type from filename or content.
        
        Args:
            filename: File name
            content: File content (optional)
            
        Returns:
            DocumentType enum
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return DocumentType.PDF
        elif filename_lower.endswith('.html') or filename_lower.endswith('.htm'):
            return DocumentType.HTML
        elif filename_lower.endswith('.txt'):
            return DocumentType.TXT
        elif filename_lower.endswith('.docx'):
            return DocumentType.DOCX
        else:
            return DocumentType.UNKNOWN
    
    def parse(self, content: bytes, doc_type: DocumentType, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse document content and extract text.
        
        Args:
            content: Document content as bytes
            doc_type: Document type
            filename: Original filename (optional)
            
        Returns:
            Dictionary with parsed content and metadata
        """
        try:
            if doc_type == DocumentType.PDF:
                return self._parse_pdf(content, filename)
            elif doc_type == DocumentType.HTML:
                return self._parse_html(content, filename)
            elif doc_type == DocumentType.TXT:
                return self._parse_txt(content, filename)
            elif doc_type == DocumentType.DOCX:
                return self._parse_docx(content, filename)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
        except Exception as e:
            logger.error(f"Error parsing document: {e}", exc_info=True)
            raise
    
    def _parse_pdf(self, content: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """Parse PDF document"""
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            num_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
            
            full_text = "\n\n".join(text_parts)
            
            return {
                "text": full_text,
                "metadata": {
                    "type": "pdf",
                    "filename": filename,
                    "num_pages": num_pages,
                    "num_chars": len(full_text)
                }
            }
        except ImportError:
            logger.warning("PyPDF2 not installed, trying alternative PDF parser")
            # Fallback to basic text extraction
            return {
                "text": content.decode('utf-8', errors='ignore'),
                "metadata": {
                    "type": "pdf",
                    "filename": filename,
                    "note": "Basic text extraction (PyPDF2 not available)"
                }
            }
    
    def _parse_html(self, content: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """Parse HTML document"""
        try:
            from bs4 import BeautifulSoup
            
            html_content = content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else None
            
            return {
                "text": text,
                "metadata": {
                    "type": "html",
                    "filename": filename,
                    "title": title_text,
                    "num_chars": len(text)
                }
            }
        except ImportError:
            logger.warning("BeautifulSoup not installed, using basic HTML parsing")
            # Basic HTML tag removal
            import re
            html_content = content.decode('utf-8', errors='ignore')
            text = re.sub(r'<[^>]+>', '', html_content)
            return {
                "text": text,
                "metadata": {
                    "type": "html",
                    "filename": filename,
                    "note": "Basic HTML parsing (BeautifulSoup not available)"
                }
            }
    
    def _parse_txt(self, content: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """Parse plain text document"""
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    text = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = content.decode('utf-8', errors='ignore')
        
        return {
            "text": text,
            "metadata": {
                "type": "txt",
                "filename": filename,
                "num_chars": len(text),
                "num_lines": len(text.splitlines())
            }
        }
    
    def _parse_docx(self, content: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        """Parse DOCX document"""
        try:
            import docx
            
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = "\n".join(text_parts)
            
            return {
                "text": full_text,
                "metadata": {
                    "type": "docx",
                    "filename": filename,
                    "num_paragraphs": len(text_parts),
                    "num_chars": len(full_text)
                }
            }
        except ImportError:
            logger.warning("python-docx not installed, cannot parse DOCX")
            raise ValueError("DOCX parsing requires python-docx package")
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise

