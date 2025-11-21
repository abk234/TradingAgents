"""
Cognitive Controller - Mode Decision System

Eddie v2.0's cognitive controller decides which "mode" Eddie should operate in:
- Empathetic: User is stressed, needs reassurance
- Analyst: Standard analytical mode
- Engineer: System diagnostics, technical issues
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import re

logger = logging.getLogger(__name__)


class CognitiveMode(Enum):
    """Eddie's cognitive operating modes."""
    EMPATHETIC = "empathetic"  # Calm, reassuring, conservative
    ANALYST = "analyst"        # Standard analytical mode
    ENGINEER = "engineer"      # Technical diagnostics, system issues


@dataclass
class ModeDecision:
    """Decision about which mode to use."""
    mode: CognitiveMode
    confidence: float  # 0-1, how confident we are in this decision
    reasoning: str
    factors: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mode": self.mode.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "factors": self.factors,
            "timestamp": self.timestamp.isoformat()
        }


class CognitiveController:
    """
    Decides which cognitive mode Eddie should use based on context.
    
    Factors considered:
    - User emotional state (from voice/text analysis)
    - Market conditions (crash, volatility)
    - System health (errors, data issues)
    - Query type (technical vs emotional)
    """
    
    def __init__(self):
        """Initialize cognitive controller."""
        self.current_mode = CognitiveMode.ANALYST
        self.mode_history: List[ModeDecision] = []
    
    def decide_mode(
        self,
        user_message: str,
        market_conditions: Optional[Dict[str, Any]] = None,
        system_health: Optional[str] = None,
        user_emotional_state: Optional[str] = None
    ) -> ModeDecision:
        """
        Decide which mode Eddie should use.
        
        Args:
            user_message: User's message
            market_conditions: Current market conditions (e.g., {"spy_change": -3.0})
            system_health: System health status (HEALTHY, WARNING, CRITICAL)
            user_emotional_state: Detected emotional state (stressed, calm, excited)
        
        Returns:
            ModeDecision with chosen mode and reasoning
        """
        factors = {}
        mode_scores = {
            CognitiveMode.EMPATHETIC: 0.0,
            CognitiveMode.ANALYST: 0.0,
            CognitiveMode.ENGINEER: 0.0
        }
        
        # Factor 1: User emotional state
        if user_emotional_state:
            if user_emotional_state in ["stressed", "anxious", "worried"]:
                mode_scores[CognitiveMode.EMPATHETIC] += 0.8
                factors["user_emotion"] = 0.8
            elif user_emotional_state == "excited":
                mode_scores[CognitiveMode.ANALYST] += 0.3
                factors["user_emotion"] = 0.3
        
        # Factor 2: Market crash detection
        if market_conditions:
            spy_change = market_conditions.get("spy_change", 0)
            if spy_change < -3.0:  # Market crash (>3% drop)
                mode_scores[CognitiveMode.EMPATHETIC] += 0.7
                factors["market_crash"] = 0.7
            elif spy_change < -1.0:  # Market decline
                mode_scores[CognitiveMode.EMPATHETIC] += 0.4
                factors["market_decline"] = 0.4
        
        # Factor 3: System health issues
        if system_health:
            if system_health == "CRITICAL":
                mode_scores[CognitiveMode.ENGINEER] += 0.9
                factors["system_critical"] = 0.9
            elif system_health == "WARNING":
                mode_scores[CognitiveMode.ENGINEER] += 0.5
                factors["system_warning"] = 0.5
        
        # Factor 4: Query type analysis
        message_lower = user_message.lower()
        
        # Technical/system queries
        technical_keywords = ["error", "bug", "broken", "not working", "system", "diagnostic", "health", "doctor"]
        if any(keyword in message_lower for keyword in technical_keywords):
            mode_scores[CognitiveMode.ENGINEER] += 0.6
            factors["technical_query"] = 0.6
        
        # Emotional/stress indicators
        stress_keywords = ["worried", "scared", "nervous", "panic", "help", "what should i do", "afraid"]
        if any(keyword in message_lower for keyword in stress_keywords):
            mode_scores[CognitiveMode.EMPATHETIC] += 0.7
            factors["stress_indicators"] = 0.7
        
        # Question words that suggest need for reassurance
        reassurance_patterns = ["should i", "is it safe", "am i", "will i lose"]
        if any(pattern in message_lower for pattern in reassurance_patterns):
            mode_scores[CognitiveMode.EMPATHETIC] += 0.5
            factors["reassurance_needed"] = 0.5
        
        # Default to analyst mode if no strong signals
        if max(mode_scores.values()) < 0.3:
            mode_scores[CognitiveMode.ANALYST] = 0.5
            factors["default"] = 0.5
        
        # Choose mode with highest score
        chosen_mode = max(mode_scores.items(), key=lambda x: x[1])[0]
        confidence = min(mode_scores[chosen_mode], 1.0)
        
        # Generate reasoning
        reasoning_parts = []
        if factors.get("user_emotion"):
            reasoning_parts.append("User emotional state detected")
        if factors.get("market_crash"):
            reasoning_parts.append("Market crash conditions")
        if factors.get("system_critical"):
            reasoning_parts.append("System health critical")
        if factors.get("technical_query"):
            reasoning_parts.append("Technical query detected")
        if factors.get("stress_indicators"):
            reasoning_parts.append("Stress indicators in message")
        if not reasoning_parts:
            reasoning_parts.append("Standard analytical mode")
        
        reasoning = "; ".join(reasoning_parts)
        
        decision = ModeDecision(
            mode=chosen_mode,
            confidence=confidence,
            reasoning=reasoning,
            factors=factors
        )
        
        self.current_mode = chosen_mode
        self.mode_history.append(decision)
        
        # Keep only last 100 decisions
        if len(self.mode_history) > 100:
            self.mode_history = self.mode_history[-100:]
        
        logger.info(f"Cognitive mode decision: {chosen_mode.value} (confidence: {confidence:.2f}) - {reasoning}")
        return decision
    
    def get_mode_prompt_addition(self, mode: Optional[CognitiveMode] = None) -> str:
        """
        Get prompt addition based on mode.
        
        Args:
            mode: Mode to use (defaults to current mode)
        
        Returns:
            Prompt text to add to system prompt
        """
        if mode is None:
            mode = self.current_mode
        
        mode_prompts = {
            CognitiveMode.EMPATHETIC: """
## Current Mode: EMPATHETIC

You are in empathetic mode. The user may be stressed or the market conditions are volatile.
- Use a calm, reassuring tone
- Be more conservative in recommendations
- Emphasize risk management
- Acknowledge concerns and validate feelings
- Slow down your pace, be more deliberate
- Avoid aggressive recommendations
""",
            CognitiveMode.ANALYST: """
## Current Mode: ANALYST

You are in standard analyst mode. Provide professional, data-driven analysis.
- Use analytical, professional tone
- Focus on data and facts
- Provide balanced bull/bear cases
- Make recommendations based on analysis
""",
            CognitiveMode.ENGINEER: """
## Current Mode: ENGINEER

You are in engineer/diagnostic mode. Focus on system health and technical issues.
- Use technical, precise language
- Focus on diagnostics and system health
- Run System Doctor checks
- Explain technical issues clearly
- Prioritize system reliability over trading recommendations
"""
        }
        
        return mode_prompts.get(mode, "")
    
    def get_current_mode(self) -> CognitiveMode:
        """Get current cognitive mode."""
        return self.current_mode
    
    def get_mode_history(self, limit: int = 10) -> List[ModeDecision]:
        """Get recent mode decisions."""
        return self.mode_history[-limit:]


# Global instance
_cognitive_controller: Optional[CognitiveController] = None


def get_cognitive_controller() -> CognitiveController:
    """Get the global cognitive controller instance."""
    global _cognitive_controller
    if _cognitive_controller is None:
        _cognitive_controller = CognitiveController()
    return _cognitive_controller

