# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Document Processor

Main processor that orchestrates document parsing and data extraction.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from .parser import DocumentParser, DocumentType
from .extractor import FinancialDataExtractor

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main document processing pipeline"""
    
    def __init__(self):
        self.parser = DocumentParser()
        self.extractor = FinancialDataExtractor()
    
    def process(
        self,
        content: bytes,
        filename: str,
        ticker: Optional[str] = None,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a document: parse and extract financial data.
        
        Args:
            content: Document content as bytes
            filename: Original filename
            ticker: Associated ticker symbol (optional)
            document_type: Document type override (optional)
            
        Returns:
            Dictionary with processed document data
        """
        try:
            # Detect document type
            if document_type:
                doc_type = DocumentType(document_type.lower())
            else:
                doc_type = self.parser.detect_type(filename, content)
            
            if doc_type == DocumentType.UNKNOWN:
                logger.warning(f"Unknown document type for {filename}, attempting to parse as text")
                doc_type = DocumentType.TXT
            
            # Parse document
            logger.info(f"Parsing {doc_type.value} document: {filename}")
            parsed = self.parser.parse(content, doc_type, filename)
            
            # Extract financial data
            logger.info(f"Extracting financial data from {filename}")
            extracted = self.extractor.extract(parsed["text"], doc_type.value)
            
            # Combine results
            result = {
                "filename": filename,
                "ticker": ticker,
                "document_type": doc_type.value,
                "processed_at": datetime.now().isoformat(),
                "text": parsed["text"],
                "metadata": parsed.get("metadata", {}),
                "financial_data": extracted,
                "summary": self._generate_summary(parsed, extracted)
            }
            
            logger.info(f"Successfully processed document: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}", exc_info=True)
            raise
    
    def _generate_summary(self, parsed: Dict[str, Any], extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the processed document"""
        summary = {
            "text_length": len(parsed.get("text", "")),
            "metrics_found": len(extracted.get("metrics", {})),
            "tickers_found": len(extracted.get("tickers", [])),
            "filing_type": extracted.get("filing_type"),
            "insights_count": len(extracted.get("key_insights", []))
        }
        
        # Add top metrics
        metrics = extracted.get("metrics", {})
        if metrics:
            summary["top_metrics"] = dict(list(metrics.items())[:5])
        
        # Add detected tickers
        tickers = extracted.get("tickers", [])
        if tickers:
            summary["detected_tickers"] = tickers[:10]  # Top 10
        
        return summary

