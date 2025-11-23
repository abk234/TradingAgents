# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Financial Data Extractor

Extracts financial data, metrics, and insights from parsed documents.
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class FinancialDataExtractor:
    """Extract financial data from documents"""
    
    def __init__(self):
        # Common financial metrics patterns
        self.metric_patterns = {
            'revenue': r'(?:revenue|sales|net sales)[:\s]*\$?([\d,]+(?:\.\d+)?)\s*(?:million|billion|M|B)?',
            'net_income': r'(?:net income|profit|earnings)[:\s]*\$?([\d,]+(?:\.\d+)?)\s*(?:million|billion|M|B)?',
            'eps': r'(?:earnings per share|EPS)[:\s]*\$?([\d,]+(?:\.\d+)?)',
            'pe_ratio': r'(?:P/E|price[-\s]to[-\s]earnings|PE ratio)[:\s]*([\d,]+(?:\.\d+)?)',
            'market_cap': r'(?:market cap|market capitalization)[:\s]*\$?([\d,]+(?:\.\d+)?)\s*(?:million|billion|M|B)?',
            'dividend': r'(?:dividend|dividend yield)[:\s]*\$?([\d,]+(?:\.\d+)?)\s*(?:%|percent)?',
        }
        
        # SEC filing patterns
        self.filing_patterns = {
            'form_10k': r'(?:Form\s+)?10[-\s]?K',
            'form_10q': r'(?:Form\s+)?10[-\s]?Q',
            'form_8k': r'(?:Form\s+)?8[-\s]?K',
            'earnings_release': r'(?:earnings|quarterly|Q[1-4]|fiscal)',
        }
    
    def extract(self, text: str, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract financial data from document text.
        
        Args:
            text: Document text
            doc_type: Document type (optional)
            
        Returns:
            Dictionary with extracted financial data
        """
        extracted = {
            "metrics": {},
            "tickers": [],
            "filing_type": None,
            "key_insights": [],
            "tables": []
        }
        
        # Extract metrics
        extracted["metrics"] = self._extract_metrics(text)
        
        # Extract ticker symbols
        extracted["tickers"] = self._extract_tickers(text)
        
        # Detect filing type
        extracted["filing_type"] = self._detect_filing_type(text)
        
        # Extract key insights (simple keyword-based)
        extracted["key_insights"] = self._extract_insights(text)
        
        # Try to extract tables (basic pattern matching)
        extracted["tables"] = self._extract_tables(text)
        
        return extracted
    
    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extract financial metrics"""
        metrics = {}
        
        for metric_name, pattern in self.metric_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    # Store the first match found
                    if metric_name not in metrics:
                        metrics[metric_name] = value
                except ValueError:
                    continue
        
        return metrics
    
    def _extract_tickers(self, text: str) -> List[str]:
        """Extract ticker symbols from text"""
        # Pattern for ticker symbols (1-5 uppercase letters, possibly with $ prefix)
        ticker_pattern = r'\$?([A-Z]{1,5})\b'
        
        # Common words to exclude
        excluded = {
            'THE', 'AND', 'OR', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
            'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS',
            'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE',
            'TWO', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE',
            'TOO', 'USE', 'YEAR', 'YET', 'MAN', 'WAY', 'MEN', 'ANY', 'ASK',
            'BIG', 'BUY', 'CUT', 'FAR', 'FEW', 'FIT', 'FIX', 'FLY', 'GOT',
            'HAD', 'HAS', 'HOT', 'ITS', 'JOB', 'KEY', 'LAW', 'LOW', 'MAP',
            'MAY', 'NET', 'NEW', 'NOW', 'OIL', 'OLD', 'OWN', 'PAY', 'PUT',
            'RAW', 'RED', 'ROW', 'RUN', 'SAY', 'SET', 'SHE', 'SHY', 'SIT',
            'SIX', 'SKY', 'SON', 'SUN', 'TAN', 'TAP', 'TAR', 'TEA', 'TEN',
            'THE', 'TIE', 'TIP', 'TOE', 'TOO', 'TOP', 'TOW', 'TOY', 'TRY',
            'TUB', 'TUG', 'TWO', 'USE', 'VAN', 'VAT', 'VET', 'VIA', 'VIE',
            'WAD', 'WAG', 'WAR', 'WAS', 'WAX', 'WAY', 'WEB', 'WED', 'WET',
            'WHO', 'WHY', 'WIG', 'WIN', 'WIT', 'WOE', 'WOK', 'WON', 'WOO',
            'YES', 'YET', 'YOU', 'ZAP', 'ZEN', 'ZIP', 'ZOO'
        }
        
        matches = re.finditer(ticker_pattern, text)
        tickers = set()
        
        for match in matches:
            ticker = match.group(1)
            if ticker not in excluded and len(ticker) >= 1:
                tickers.add(ticker)
        
        return sorted(list(tickers))
    
    def _detect_filing_type(self, text: str) -> Optional[str]:
        """Detect SEC filing type"""
        text_upper = text.upper()
        
        for filing_type, pattern in self.filing_patterns.items():
            if re.search(pattern, text_upper):
                return filing_type.replace('_', '-')
        
        return None
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract key insights (simple keyword-based)"""
        insights = []
        
        # Look for common financial insight keywords
        insight_keywords = {
            'growth': ['growth', 'increased', 'expanded', 'growing'],
            'decline': ['declined', 'decreased', 'reduced', 'down'],
            'profitability': ['profit', 'profitable', 'earnings', 'income'],
            'risk': ['risk', 'risky', 'uncertainty', 'concern'],
            'opportunity': ['opportunity', 'potential', 'promising', 'upside'],
        }
        
        text_lower = text.lower()
        for category, keywords in insight_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    insights.append(f"{category.capitalize()} mentioned")
                    break
        
        return insights[:10]  # Limit to 10 insights
    
    def _extract_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extract table-like structures (basic pattern matching)"""
        tables = []
        
        # Look for lines with multiple numbers separated by spaces/tabs
        lines = text.split('\n')
        table_candidates = []
        
        for line in lines:
            # Check if line has multiple numbers (potential table row)
            numbers = re.findall(r'[\d,]+\.?\d*', line)
            if len(numbers) >= 3:  # At least 3 numbers suggests a table row
                table_candidates.append(line)
        
        if table_candidates:
            tables.append({
                "type": "detected",
                "rows": len(table_candidates),
                "sample": table_candidates[:5]  # First 5 rows
            })
        
        return tables

