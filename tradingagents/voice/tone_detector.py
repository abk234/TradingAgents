# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Tone Detector - Determines Emotional Tone from Context

Eddie v2.0's tone detector determines the appropriate emotional tone
for TTS based on market conditions, user state, and message content.
"""

from typing import Optional, Dict, Any
from enum import Enum
import logging

from .tts_engine import EmotionalTone

logger = logging.getLogger(__name__)


class ToneDetector:
    """
    Detects appropriate emotional tone based on context.
    
    Factors:
    - Market conditions (crash, volatility, all-time highs)
    - User emotional state (stressed, calm, excited)
    - System health (errors, warnings)
    - Message content (technical, emotional, urgent)
    """
    
    def detect_tone(
        self,
        market_conditions: Optional[Dict[str, Any]] = None,
        user_emotional_state: Optional[str] = None,
        system_health: Optional[str] = None,
        message_content: Optional[str] = None,
        cognitive_mode: Optional[str] = None
    ) -> EmotionalTone:
        """
        Detect appropriate tone from context.
        
        Args:
            market_conditions: Market state (e.g., {"spy_change": -3.0})
            user_emotional_state: Detected user emotion
            system_health: System health status
            message_content: User's message text
            cognitive_mode: Current cognitive mode (empathetic, analyst, engineer)
        
        Returns:
            Appropriate EmotionalTone
        """
        # Priority 1: System health issues -> Technical tone
        if system_health == "CRITICAL":
            return EmotionalTone.TECHNICAL
        
        # Priority 2: User emotional state
        if user_emotional_state in ["stressed", "anxious", "worried"]:
            return EmotionalTone.CALM
        
        # Priority 3: Market crash -> Calm/reassuring
        if market_conditions:
            spy_change = market_conditions.get("spy_change", 0)
            if spy_change < -3.0:  # Market crash
                return EmotionalTone.CALM
            elif spy_change > 2.0:  # Strong rally
                return EmotionalTone.ENERGETIC
        
        # Priority 4: Cognitive mode
        if cognitive_mode == "empathetic":
            return EmotionalTone.REASSURING
        elif cognitive_mode == "engineer":
            return EmotionalTone.TECHNICAL
        
        # Priority 5: Message content analysis
        if message_content:
            message_lower = message_content.lower()
            
            # Technical keywords
            if any(kw in message_lower for kw in ["error", "bug", "system", "diagnostic"]):
                return EmotionalTone.TECHNICAL
            
            # Stress indicators
            if any(kw in message_lower for kw in ["worried", "scared", "nervous", "panic"]):
                return EmotionalTone.CALM
            
            # Excitement indicators
            if any(kw in message_lower for kw in ["great", "amazing", "excited", "wow"]):
                return EmotionalTone.ENERGETIC
        
        # Default: Professional
        return EmotionalTone.PROFESSIONAL


# Global instance
_tone_detector: Optional[ToneDetector] = None


def get_tone_detector() -> ToneDetector:
    """Get the global tone detector instance."""
    global _tone_detector
    if _tone_detector is None:
        _tone_detector = ToneDetector()
    return _tone_detector

