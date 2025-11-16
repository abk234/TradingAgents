"""
Investment Intelligence System - RAG Module

Retrieval-Augmented Generation for historical context and pattern matching.
"""

from .embeddings import EmbeddingGenerator
from .context_retriever import ContextRetriever
from .prompt_formatter import PromptFormatter

__all__ = [
    'EmbeddingGenerator',
    'ContextRetriever',
    'PromptFormatter',
]
