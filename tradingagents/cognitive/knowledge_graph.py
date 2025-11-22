# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Knowledge Graph - Semantic Memory System

Eddie v2.0's semantic memory stores concepts, relationships, and domain knowledge
as a graph structure. This complements episodic memory (RAG) with structured knowledge.
"""

import networkx as nx
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph representing a concept."""
    id: str
    label: str
    node_type: str  # concept, entity, pattern, rule, strategy
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0  # 0-1, how confident we are in this knowledge
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "type": self.node_type,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "confidence": self.confidence
        }


@dataclass
class KnowledgeEdge:
    """An edge in the knowledge graph representing a relationship."""
    source: str
    target: str
    relationship_type: str  # relates_to, causes, indicates, similar_to, part_of, etc.
    weight: float = 1.0  # Strength of relationship
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.relationship_type,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at.isoformat()
        }


class KnowledgeGraph:
    """
    Semantic memory system using NetworkX graph.
    
    Stores:
    - Concepts: "Death Cross", "RSI Oversold", "Earnings Risk"
    - Entities: Stock tickers, sectors, market conditions
    - Patterns: Recurring market patterns
    - Rules: Trading rules and heuristics
    - Strategies: Successful trading strategies
    """
    
    def __init__(self):
        """Initialize empty knowledge graph."""
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
    
    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> KnowledgeNode:
        """
        Add a node to the knowledge graph.
        
        Args:
            node_id: Unique identifier
            label: Human-readable label
            node_type: Type of node (concept, entity, pattern, rule, strategy)
            properties: Additional properties
            confidence: Confidence in this knowledge (0-1)
        
        Returns:
            Created KnowledgeNode
        """
        node = KnowledgeNode(
            id=node_id,
            label=label,
            node_type=node_type,
            properties=properties or {},
            confidence=confidence
        )
        
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.to_dict())
        
        logger.debug(f"Added knowledge node: {node_id} ({node_type})")
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None
    ) -> KnowledgeEdge:
        """
        Add an edge (relationship) between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Type of relationship
            weight: Strength of relationship (0-1)
            properties: Additional properties
        
        Returns:
            Created KnowledgeEdge
        """
        # Ensure nodes exist
        if source_id not in self.nodes:
            raise ValueError(f"Source node {source_id} does not exist")
        if target_id not in self.nodes:
            raise ValueError(f"Target node {target_id} does not exist")
        
        edge = KnowledgeEdge(
            source=source_id,
            target=target_id,
            relationship_type=relationship_type,
            weight=weight,
            properties=properties or {}
        )
        
        self.edges.append(edge)
        self.graph.add_edge(
            source_id,
            target_id,
            **edge.to_dict()
        )
        
        logger.debug(f"Added knowledge edge: {source_id} --{relationship_type}--> {target_id}")
        return edge
    
    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def find_nodes(
        self,
        label_pattern: Optional[str] = None,
        node_type: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[KnowledgeNode]:
        """
        Find nodes matching criteria.
        
        Args:
            label_pattern: Pattern to match in label (substring)
            node_type: Filter by node type
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of matching nodes
        """
        results = []
        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue
            if node.confidence < min_confidence:
                continue
            if label_pattern and label_pattern.lower() not in node.label.lower():
                continue
            results.append(node)
        return results
    
    def get_related_nodes(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        max_depth: int = 1
    ) -> List[Tuple[KnowledgeNode, str, int]]:
        """
        Get nodes related to a given node.
        
        Args:
            node_id: Starting node ID
            relationship_type: Filter by relationship type
            max_depth: Maximum depth to traverse
        
        Returns:
            List of (node, relationship_type, depth) tuples
        """
        if node_id not in self.nodes:
            return []
        
        related = []
        visited = set()
        
        def traverse(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            # Get outgoing edges
            for target_id in self.graph.successors(current_id):
                edge_data = self.graph[current_id][target_id]
                rel_type = edge_data.get('type', '')
                
                if relationship_type and rel_type != relationship_type:
                    continue
                
                if target_id in self.nodes:
                    related.append((self.nodes[target_id], rel_type, depth))
                    traverse(target_id, depth + 1)
            
            # Get incoming edges (reverse relationships)
            for source_id in self.graph.predecessors(current_id):
                edge_data = self.graph[source_id][current_id]
                rel_type = edge_data.get('type', '')
                
                if relationship_type and rel_type != relationship_type:
                    continue
                
                if source_id in self.nodes:
                    related.append((self.nodes[source_id], rel_type, depth))
                    traverse(source_id, depth + 1)
        
        traverse(node_id, 1)
        return related
    
    def query(
        self,
        query_text: str,
        max_results: int = 10
    ) -> List[KnowledgeNode]:
        """
        Query the knowledge graph by text.
        
        Simple keyword matching for now. Could be enhanced with semantic search.
        
        Args:
            query_text: Query string
            max_results: Maximum number of results
        
        Returns:
            List of matching nodes
        """
        query_lower = query_text.lower()
        results = []
        
        for node in self.nodes.values():
            score = 0.0
            
            # Check label
            if query_lower in node.label.lower():
                score += 2.0
            
            # Check properties
            for key, value in node.properties.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 1.0
            
            if score > 0:
                results.append((node, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [node for node, _ in results[:max_results]]
    
    def initialize_trading_knowledge(self):
        """Initialize the graph with basic trading knowledge."""
        logger.info("Initializing trading knowledge graph...")
        
        # Core Concepts
        self.add_node("rsi_oversold", "RSI Oversold", "concept", {
            "description": "RSI below 30 indicates oversold condition",
            "indicator": "RSI",
            "threshold": 30
        })
        
        self.add_node("rsi_overbought", "RSI Overbought", "concept", {
            "description": "RSI above 70 indicates overbought condition",
            "indicator": "RSI",
            "threshold": 70
        })
        
        self.add_node("macd_bullish", "MACD Bullish Crossover", "concept", {
            "description": "MACD line crosses above signal line",
            "indicator": "MACD"
        })
        
        self.add_node("death_cross", "Death Cross", "concept", {
            "description": "50-day MA crosses below 200-day MA",
            "indicator": "Moving Average"
        })
        
        self.add_node("golden_cross", "Golden Cross", "concept", {
            "description": "50-day MA crosses above 200-day MA",
            "indicator": "Moving Average"
        })
        
        # Relationships
        self.add_edge("rsi_oversold", "macd_bullish", "indicates", weight=0.8, properties={
            "context": "Strong buy signal when both occur together"
        })
        
        self.add_edge("death_cross", "rsi_overbought", "relates_to", weight=0.6, properties={
            "context": "Bearish pattern combination"
        })
        
        # Rules
        self.add_node("earnings_risk_rule", "Earnings Risk Rule", "rule", {
            "description": "Avoid new positions within 7 days of earnings",
            "action": "AVOID",
            "timeframe": "7 days"
        })
        
        self.add_edge("earnings_risk_rule", "rsi_oversold", "overrides", weight=0.9, properties={
            "context": "Earnings risk takes precedence over technical signals"
        })
        
        logger.info(f"Initialized knowledge graph with {len(self.nodes)} nodes and {len(self.edges)} edges")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary."""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "stats": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges)
            }
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Import graph from dictionary."""
        self.nodes.clear()
        self.edges.clear()
        self.graph.clear()
        
        # Load nodes
        for node_data in data.get("nodes", []):
            node = KnowledgeNode(
                id=node_data["id"],
                label=node_data["label"],
                node_type=node_data["type"],
                properties=node_data.get("properties", {}),
                confidence=node_data.get("confidence", 1.0)
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.to_dict())
        
        # Load edges
        for edge_data in data.get("edges", []):
            edge = KnowledgeEdge(
                source=edge_data["source"],
                target=edge_data["target"],
                relationship_type=edge_data["type"],
                weight=edge_data.get("weight", 1.0),
                properties=edge_data.get("properties", {})
            )
            self.edges.append(edge)
            self.graph.add_edge(edge.source, edge.target, **edge.to_dict())


# Global instance
_knowledge_graph: Optional[KnowledgeGraph] = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get the global knowledge graph instance."""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
        _knowledge_graph.initialize_trading_knowledge()
    return _knowledge_graph

