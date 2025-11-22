# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

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

