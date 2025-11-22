# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Eddie's Agent Orchestration System

Enables Eddie to coordinate specialized trading agents for comprehensive analysis.
"""

from .agent_orchestrator import AgentOrchestrator, AgentOrchestrationResult

__all__ = [
    'AgentOrchestrator',
    'AgentOrchestrationResult',
]
