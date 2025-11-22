# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Cognitive Architecture - Eddie v2.0

Unified memory system combining:
- Episodic Memory: RAG system (existing)
- Semantic Memory: Knowledge Graph (new)
- Procedural Memory: Tool usage patterns (new)
- Cognitive Controller: Mode decision system (new)
"""

from .knowledge_graph import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeEdge,
    get_knowledge_graph
)

from .procedural_memory import (
    ProceduralMemory,
    ToolUsagePattern,
    Workflow,
    get_procedural_memory
)

from .cognitive_controller import (
    CognitiveController,
    CognitiveMode,
    ModeDecision,
    get_cognitive_controller
)

__all__ = [
    # Knowledge Graph
    'KnowledgeGraph',
    'KnowledgeNode',
    'KnowledgeEdge',
    'get_knowledge_graph',
    
    # Procedural Memory
    'ProceduralMemory',
    'ToolUsagePattern',
    'Workflow',
    'get_procedural_memory',
    
    # Cognitive Controller
    'CognitiveController',
    'CognitiveMode',
    'ModeDecision',
    'get_cognitive_controller',
]

