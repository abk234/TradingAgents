"""
Procedural Memory System

Eddie v2.0's procedural memory stores "how to do things" - tool usage patterns,
successful workflows, and learned procedures.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolUsagePattern:
    """A pattern of tool usage."""
    pattern_id: str
    tool_sequence: List[str]  # Ordered list of tools used
    context: str  # When this pattern is used
    success_rate: float = 0.0  # 0-1, how often this pattern succeeds
    usage_count: int = 0
    last_used: Optional[datetime] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def record_usage(self, success: bool = True):
        """Record a usage of this pattern."""
        self.usage_count += 1
        self.last_used = datetime.now(timezone.utc)
        
        if success:
            # Update success rate (exponential moving average)
            alpha = 0.1
            self.success_rate = alpha * 1.0 + (1 - alpha) * self.success_rate
        else:
            alpha = 0.1
            self.success_rate = alpha * 0.0 + (1 - alpha) * self.success_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "tool_sequence": self.tool_sequence,
            "context": self.context,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "properties": self.properties
        }


@dataclass
class Workflow:
    """A complete workflow procedure."""
    workflow_id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]  # List of steps with tool calls
    success_count: int = 0
    failure_count: int = 0
    last_executed: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    def record_execution(self, success: bool = True):
        """Record workflow execution."""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.last_executed = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None
        }


class ProceduralMemory:
    """
    Stores procedural knowledge - how to accomplish tasks.
    
    Tracks:
    - Tool usage patterns (which tools are used together)
    - Successful workflows (complete procedures)
    - Tool effectiveness (which tools work best in which contexts)
    """
    
    def __init__(self):
        """Initialize procedural memory."""
        self.tool_patterns: Dict[str, ToolUsagePattern] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.tool_effectiveness: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        # tool_effectiveness[tool_name][context] = success_rate
    
    def record_tool_usage(
        self,
        tool_name: str,
        context: str,
        previous_tools: Optional[List[str]] = None,
        success: bool = True
    ):
        """
        Record a tool usage for pattern learning.
        
        Args:
            tool_name: Name of tool used
            context: Context of usage (e.g., "stock_analysis", "data_validation")
            previous_tools: Tools used before this one (for pattern detection)
            success: Whether the usage was successful
        """
        # Update tool effectiveness
        self.tool_effectiveness[tool_name][context] = (
            0.9 * self.tool_effectiveness[tool_name][context] + 0.1 * (1.0 if success else 0.0)
        )
        
        # Detect patterns if we have previous tools
        if previous_tools:
            pattern_key = " -> ".join(previous_tools + [tool_name])
            
            if pattern_key not in self.tool_patterns:
                self.tool_patterns[pattern_key] = ToolUsagePattern(
                    pattern_id=pattern_key,
                    tool_sequence=previous_tools + [tool_name],
                    context=context
                )
            
            self.tool_patterns[pattern_key].record_usage(success)
    
    def get_recommended_tools(
        self,
        context: str,
        previous_tools: Optional[List[str]] = None,
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get recommended next tools based on patterns.
        
        Args:
            context: Current context
            previous_tools: Tools already used
            top_n: Number of recommendations
        
        Returns:
            List of (tool_name, confidence) tuples
        """
        recommendations = []
        
        # Look for patterns that start with previous_tools
        if previous_tools:
            pattern_prefix = " -> ".join(previous_tools)
            for pattern_id, pattern in self.tool_patterns.items():
                if pattern_id.startswith(pattern_prefix) and pattern.context == context:
                    next_tool = pattern.tool_sequence[len(previous_tools)]
                    confidence = pattern.success_rate * (pattern.usage_count / (pattern.usage_count + 1))
                    recommendations.append((next_tool, confidence))
        else:
            # No previous tools - recommend based on context effectiveness
            for tool_name, contexts in self.tool_effectiveness.items():
                if context in contexts:
                    confidence = contexts[context]
                    recommendations.append((tool_name, confidence))
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]
    
    def register_workflow(
        self,
        workflow_id: str,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> Workflow:
        """
        Register a workflow procedure.
        
        Args:
            workflow_id: Unique identifier
            name: Human-readable name
            description: Description of what the workflow does
            steps: List of steps (each step has tool name and parameters)
        
        Returns:
            Created Workflow
        """
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            steps=steps
        )
        self.workflows[workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow_id} ({name})")
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def find_workflows(
        self,
        name_pattern: Optional[str] = None,
        min_success_rate: float = 0.0
    ) -> List[Workflow]:
        """
        Find workflows matching criteria.
        
        Args:
            name_pattern: Pattern to match in name
            min_success_rate: Minimum success rate
        
        Returns:
            List of matching workflows
        """
        results = []
        for workflow in self.workflows.values():
            if workflow.success_rate < min_success_rate:
                continue
            if name_pattern and name_pattern.lower() not in workflow.name.lower():
                continue
            results.append(workflow)
        
        # Sort by success rate
        results.sort(key=lambda w: w.success_rate, reverse=True)
        return results
    
    def initialize_default_workflows(self):
        """Initialize with default trading workflows."""
        logger.info("Initializing default workflows...")
        
        # Stock Analysis Workflow
        self.register_workflow(
            "stock_analysis_full",
            "Full Stock Analysis",
            "Comprehensive analysis with all agents",
            [
                {"tool": "run_screener", "description": "Get market context"},
                {"tool": "analyze_stock", "description": "Deep analysis with all agents"},
                {"tool": "check_earnings_risk", "description": "Validate earnings risk"},
                {"tool": "validate_price_sources", "description": "Validate price data"}
            ]
        )
        
        # Quick Check Workflow
        self.register_workflow(
            "quick_check",
            "Quick Stock Check",
            "Fast single-aspect check",
            [
                {"tool": "get_stock_summary", "description": "Get basic info"},
                {"tool": "quick_technical_check", "description": "Quick technicals"}
            ]
        )
        
        # Pre-Trade Validation Workflow
        self.register_workflow(
            "pre_trade_validation",
            "Pre-Trade Validation",
            "Validate before making trade recommendation",
            [
                {"tool": "check_earnings_risk", "description": "Check earnings proximity"},
                {"tool": "validate_price_sources", "description": "Validate prices"},
                {"tool": "check_data_quality", "description": "Check data quality"},
                {"tool": "run_system_doctor_check", "description": "System health check"}
            ]
        )
        
        logger.info(f"Initialized {len(self.workflows)} default workflows")
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "tool_patterns": {k: v.to_dict() for k, v in self.tool_patterns.items()},
            "workflows": {k: v.to_dict() for k, v in self.workflows.items()},
            "tool_effectiveness": dict(self.tool_effectiveness)
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Import from dictionary."""
        # Load tool patterns
        self.tool_patterns.clear()
        for pattern_id, pattern_data in data.get("tool_patterns", {}).items():
            pattern = ToolUsagePattern(
                pattern_id=pattern_data["pattern_id"],
                tool_sequence=pattern_data["tool_sequence"],
                context=pattern_data["context"],
                success_rate=pattern_data.get("success_rate", 0.0),
                usage_count=pattern_data.get("usage_count", 0),
                properties=pattern_data.get("properties", {})
            )
            if pattern_data.get("last_used"):
                pattern.last_used = datetime.fromisoformat(pattern_data["last_used"])
            self.tool_patterns[pattern_id] = pattern
        
        # Load workflows
        self.workflows.clear()
        for workflow_id, workflow_data in data.get("workflows", {}).items():
            workflow = Workflow(
                workflow_id=workflow_data["workflow_id"],
                name=workflow_data["name"],
                description=workflow_data["description"],
                steps=workflow_data["steps"],
                success_count=workflow_data.get("success_count", 0),
                failure_count=workflow_data.get("failure_count", 0)
            )
            if workflow_data.get("last_executed"):
                workflow.last_executed = datetime.fromisoformat(workflow_data["last_executed"])
            self.workflows[workflow_id] = workflow
        
        # Load tool effectiveness
        self.tool_effectiveness = defaultdict(lambda: defaultdict(float))
        for tool_name, contexts in data.get("tool_effectiveness", {}).items():
            self.tool_effectiveness[tool_name] = defaultdict(float, contexts)


# Global instance
_procedural_memory: Optional[ProceduralMemory] = None


def get_procedural_memory() -> ProceduralMemory:
    """Get the global procedural memory instance."""
    global _procedural_memory
    if _procedural_memory is None:
        _procedural_memory = ProceduralMemory()
        _procedural_memory.initialize_default_workflows()
    return _procedural_memory

