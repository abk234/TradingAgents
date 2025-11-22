# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Embedding Generation Module

Generates vector embeddings using Ollama's nomic-embed-text model.
"""

from typing import List, Dict, Any, Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using Ollama's nomic-embed-text model."""

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize embedding generator.

        Args:
            model: Embedding model name
            base_url: Ollama API base URL
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/embeddings"

    def generate(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector or None on error
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            payload = {
                "model": self.model,
                "prompt": text
            }

            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                embedding = data.get('embedding')

                if embedding and len(embedding) == 768:
                    return embedding
                else:
                    logger.error(f"Invalid embedding dimensions: {len(embedding) if embedding else 0}")
                    return None
            else:
                logger.error(f"Embedding API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error generating embedding: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def generate_batch(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress

        Returns:
            List of embedding vectors (same length as input)
        """
        embeddings = []

        for i, text in enumerate(texts):
            if show_progress and (i + 1) % 10 == 0:
                logger.info(f"Generated {i + 1}/{len(texts)} embeddings")

            embedding = self.generate(text)
            embeddings.append(embedding)

        return embeddings

    def embed_analysis(self, analysis_data: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for an analysis.

        Combines key information from the analysis into a single embedding.

        Args:
            analysis_data: Analysis dictionary

        Returns:
            Embedding vector or None
        """
        # Compile key information for embedding
        parts = []

        # Executive summary
        if analysis_data.get('executive_summary'):
            parts.append(f"Summary: {analysis_data['executive_summary']}")

        # Bull and bear cases
        if analysis_data.get('bull_case'):
            parts.append(f"Bull case: {analysis_data['bull_case']}")

        if analysis_data.get('bear_case'):
            parts.append(f"Bear case: {analysis_data['bear_case']}")

        # Key catalysts
        if analysis_data.get('key_catalysts'):
            catalysts = ', '.join(analysis_data['key_catalysts'])
            parts.append(f"Catalysts: {catalysts}")

        # Risk factors
        if analysis_data.get('risk_factors'):
            risks = ', '.join(analysis_data['risk_factors'])
            parts.append(f"Risks: {risks}")

        # Decision and reasoning
        decision = analysis_data.get('final_decision', '')
        if decision:
            parts.append(f"Decision: {decision}")

        # Combine all parts
        text = " | ".join(parts)

        if not text:
            logger.warning("No content to embed from analysis")
            return None

        return self.generate(text)

    def embed_buy_signal(self, signal_data: Dict[str, Any]) -> Optional[List[float]]:
        """
        Generate embedding for a buy signal.

        Args:
            signal_data: Buy signal dictionary

        Returns:
            Embedding vector or None
        """
        parts = []

        # Signal reasoning
        if signal_data.get('reasoning'):
            parts.append(signal_data['reasoning'])

        # Pattern matched
        if signal_data.get('pattern_matched'):
            parts.append(f"Pattern: {signal_data['pattern_matched']}")

        # Risk factors
        if signal_data.get('risk_factors'):
            risks_json = signal_data['risk_factors']
            if isinstance(risks_json, str):
                parts.append(f"Risks: {risks_json}")
            elif isinstance(risks_json, dict):
                risk_str = ', '.join(f"{k}: {v}" for k, v in risks_json.items())
                parts.append(f"Risks: {risk_str}")

        text = " | ".join(parts)

        if not text:
            logger.warning("No content to embed from signal")
            return None

        return self.generate(text)

    def embed_market_situation(
        self,
        ticker: str,
        price: float,
        signals: Dict[str, Any],
        fundamentals: Dict[str, Any] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for current market situation.

        Args:
            ticker: Ticker symbol
            price: Current price
            signals: Technical signals
            fundamentals: Fundamental metrics (optional)

        Returns:
            Embedding vector or None
        """
        parts = [f"Stock: {ticker}", f"Price: ${price:.2f}"]

        # Technical signals
        if signals.get('rsi'):
            parts.append(f"RSI: {signals['rsi']:.1f}")

        if signals.get('macd_bullish_crossover'):
            parts.append("MACD: Bullish crossover")
        elif signals.get('macd_bearish_crossover'):
            parts.append("MACD: Bearish crossover")

        # Moving averages
        if signals.get('price_above_ma20'):
            parts.append("Price above 20-day MA")

        if signals.get('ma20_above_ma50'):
            parts.append("20-day MA above 50-day MA (bullish)")

        # Volume
        volume_ratio = signals.get('volume_ratio')
        if volume_ratio and volume_ratio > 1.5:
            parts.append(f"Volume spike: {volume_ratio:.1f}x average")

        # Fundamentals
        if fundamentals:
            if fundamentals.get('pe_ratio'):
                parts.append(f"P/E: {fundamentals['pe_ratio']:.1f}")

            if fundamentals.get('forward_pe'):
                parts.append(f"Forward P/E: {fundamentals['forward_pe']:.1f}")

        text = " | ".join(parts)
        return self.generate(text)

    def test_connection(self) -> bool:
        """
        Test connection to Ollama API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            embedding = self.generate("test")
            if embedding and len(embedding) == 768:
                logger.info("✓ Embedding generator connection successful")
                return True
            else:
                logger.error("✗ Invalid embedding returned")
                return False
        except Exception as e:
            logger.error(f"✗ Embedding generator connection failed: {e}")
            return False
