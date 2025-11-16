"""
Performance Evaluation Module

Track recommendation outcomes, calculate win rates, and validate AI predictions.
"""

from .outcome_tracker import OutcomeTracker
from .performance import PerformanceAnalyzer

__all__ = ['OutcomeTracker', 'PerformanceAnalyzer']
