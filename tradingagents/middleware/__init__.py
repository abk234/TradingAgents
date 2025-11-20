"""
TradingAgents Middleware System

Provides extensible middleware pattern for adding capabilities to agents
without modifying agent code directly.

Inspired by deepagents architecture patterns.
"""

from .base import TradingMiddleware
from .token_tracking import TokenTrackingMiddleware
from .summarization import SummarizationMiddleware
from .todolist import TodoListMiddleware
from .filesystem import FilesystemMiddleware
from .subagent import SubAgentMiddleware, SubAgentDefinition

__all__ = [
    "TradingMiddleware",
    "TokenTrackingMiddleware",
    "SummarizationMiddleware",
    "TodoListMiddleware",
    "FilesystemMiddleware",
    "SubAgentMiddleware",
    "SubAgentDefinition",
]

