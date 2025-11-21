"""
Eddie v2.0 State Tracker

Tracks Eddie's internal state for UI visualization:
- Listening, Processing, Speaking, Error states
- Confidence levels
- System health status
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EddieState(Enum):
    """Eddie's current operational state."""
    IDLE = "idle"                    # Waiting for input
    LISTENING = "listening"          # 🔵 Blue Pulse - Receiving user input
    PROCESSING = "processing"        # 🟣 Purple Spin - Thinking/Searching
    SPEAKING = "speaking"            # 🟢 Green Steady - Responding
    ERROR = "error"                  # 🔴 Red Border - System Error / Data Desync
    VALIDATING = "validating"         # 🟡 Yellow Pulse - Running validation checks


@dataclass
class ConfidenceMetrics:
    """Multi-factor confidence metrics."""
    data_freshness_score: float = 0.0  # 0-10, based on data age
    math_verification_score: float = 0.0  # 0-10, based on indicator audits
    ai_confidence_score: float = 0.0  # 0-100, based on agent consensus
    overall_confidence: float = 0.0  # 0-100, weighted average
    
    def calculate_overall(self):
        """Calculate overall confidence from components."""
        # Weighted average: AI confidence (70%), Data freshness (20%), Math verification (10%)
        self.overall_confidence = (
            self.ai_confidence_score * 0.7 +
            (self.data_freshness_score / 10) * 100 * 0.2 +
            (self.math_verification_score / 10) * 100 * 0.1
        )
        return self.overall_confidence
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for API response."""
        return {
            "data_freshness": self.data_freshness_score,
            "math_verification": self.math_verification_score,
            "ai_confidence": self.ai_confidence_score,
            "overall": self.overall_confidence
        }


@dataclass
class EddieStateInfo:
    """Complete state information for Eddie."""
    state: EddieState = EddieState.IDLE
    confidence: ConfidenceMetrics = field(default_factory=ConfidenceMetrics)
    current_ticker: Optional[str] = None
    active_tools: list[str] = field(default_factory=list)
    system_health: str = "HEALTHY"  # HEALTHY, WARNING, CRITICAL
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""  # Current status message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API/UI consumption."""
        return {
            "state": self.state.value,
            "confidence": self.confidence.to_dict(),
            "current_ticker": self.current_ticker,
            "active_tools": self.active_tools,
            "system_health": self.system_health,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message
        }


class EddieStateTracker:
    """
    Tracks and broadcasts Eddie's state for UI visualization.
    
    Singleton pattern to maintain state across requests.
    """
    
    _instance: Optional['EddieStateTracker'] = None
    _state: EddieStateInfo
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._state = EddieStateInfo()
        return cls._instance
    
    def set_state(self, state: EddieState, message: str = ""):
        """Update Eddie's current state."""
        self._state.state = state
        self._state.message = message
        self._state.timestamp = datetime.now(timezone.utc)
        logger.debug(f"Eddie state changed to: {state.value} - {message}")
    
    def set_confidence(self, confidence: ConfidenceMetrics):
        """Update confidence metrics."""
        self._state.confidence = confidence
        confidence.calculate_overall()
    
    def update_confidence_scores(
        self,
        data_freshness: Optional[float] = None,
        math_verification: Optional[float] = None,
        ai_confidence: Optional[float] = None
    ):
        """Update individual confidence scores."""
        if data_freshness is not None:
            self._state.confidence.data_freshness_score = data_freshness
        if math_verification is not None:
            self._state.confidence.math_verification_score = math_verification
        if ai_confidence is not None:
            self._state.confidence.ai_confidence_score = ai_confidence
        self._state.confidence.calculate_overall()
    
    def set_current_ticker(self, ticker: Optional[str]):
        """Set the current ticker being analyzed."""
        self._state.current_ticker = ticker
    
    def add_active_tool(self, tool_name: str):
        """Add an active tool to the list."""
        if tool_name not in self._state.active_tools:
            self._state.active_tools.append(tool_name)
    
    def remove_active_tool(self, tool_name: str):
        """Remove a tool from the active list."""
        if tool_name in self._state.active_tools:
            self._state.active_tools.remove(tool_name)
    
    def clear_active_tools(self):
        """Clear all active tools."""
        self._state.active_tools.clear()
    
    def set_system_health(self, health: str):
        """Set system health status."""
        self._state.system_health = health
        if health == "CRITICAL":
            self.set_state(EddieState.ERROR, "System health critical - data desync detected")
        elif health == "WARNING":
            self.set_state(EddieState.VALIDATING, "System health warning - running diagnostics")
    
    def get_state(self) -> EddieStateInfo:
        """Get current state information."""
        return self._state
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary."""
        return self._state.to_dict()
    
    def reset(self):
        """Reset state to idle."""
        self._state = EddieStateInfo()
        logger.info("Eddie state reset to idle")


# Global instance
_state_tracker = EddieStateTracker()


def get_state_tracker() -> EddieStateTracker:
    """Get the global state tracker instance."""
    return _state_tracker

