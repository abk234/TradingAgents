# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Sector Rotation Strategy

Focuses on investing in sectors that outperform based on economic cycle.
"""

from typing import Dict, Any, Optional
import logging

from .base import InvestmentStrategy, StrategyResult, Recommendation
from .utils import (
    safe_float,
    extract_metric,
    normalize_confidence,
    format_reasoning,
)

logger = logging.getLogger(__name__)


class SectorRotationStrategy(InvestmentStrategy):
    """
    Sector rotation investing strategy.
    
    Key principles:
    - Invest in sectors that outperform the market
    - Rotate between sectors based on economic cycle
    - Early cycle: Financials, Consumer Discretionary
    - Mid cycle: Technology, Industrials
    - Late cycle: Energy, Materials
    - Recession: Consumer Staples, Utilities, Healthcare
    """
    
    def get_strategy_name(self) -> str:
        return "Sector Rotation"
    
    def get_timeframe(self) -> str:
        return "Months to years"
    
    def evaluate(
        self,
        ticker: str,
        market_data: Dict[str, Any],
        fundamental_data: Dict[str, Any],
        technical_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None
    ) -> StrategyResult:
        """
        Evaluate stock using sector rotation principles.
        """
        # Validate data
        if not self.validate_data(market_data, fundamental_data, technical_data):
            return StrategyResult(
                recommendation=Recommendation.WAIT,
                confidence=0,
                reasoning="Insufficient data for sector rotation analysis",
                strategy_name=self.get_strategy_name()
            )
        
        # Extract sector information
        sector = fundamental_data.get("sector") or market_data.get("sector") or "Unknown"
        industry = fundamental_data.get("industry") or market_data.get("industry") or "Unknown"
        
        # Get sector data from additional_data if available
        sector_data = additional_data.get("sector_data", {}) if additional_data else {}
        sector_strength = sector_data.get("strength", 0.0)  # -1 to 1
        sector_momentum = sector_data.get("momentum", 0.0)  # -1 to 1
        
        # Detect economic cycle (simplified - would use macro indicators in full implementation)
        economic_cycle = self._detect_economic_cycle(market_data, additional_data)
        
        # Score the investment
        score = 50  # Neutral baseline
        reasons = []
        risks = []
        key_metrics = {
            "sector": sector,
            "industry": industry,
            "sector_strength": sector_strength,
            "sector_momentum": sector_momentum,
            "economic_cycle": economic_cycle,
        }
        
        # Sector strength scoring
        if sector_strength > 0.3:
            score += 25
            reasons.append(f"Strong sector performance (strength: {sector_strength:.2f})")
        elif sector_strength > 0.1:
            score += 10
            reasons.append(f"Moderate sector strength ({sector_strength:.2f})")
        elif sector_strength < -0.3:
            score -= 25
            reasons.append(f"Weak sector performance (strength: {sector_strength:.2f})")
            risks.append("Weak sector performance indicates headwinds")
        
        # Sector momentum scoring
        if sector_momentum > 0.3:
            score += 20
            reasons.append(f"Positive sector momentum ({sector_momentum:.2f})")
        elif sector_momentum < -0.3:
            score -= 20
            reasons.append(f"Negative sector momentum ({sector_momentum:.2f})")
            risks.append("Negative sector momentum suggests rotation away")
        
        # Economic cycle alignment scoring
        cycle_alignment = self._check_cycle_alignment(sector, economic_cycle)
        if cycle_alignment > 0.5:
            score += 20
            reasons.append(f"Sector aligns with economic cycle ({economic_cycle})")
        elif cycle_alignment < -0.5:
            score -= 15
            reasons.append(f"Sector misaligned with economic cycle ({economic_cycle})")
            risks.append("Sector may underperform in current economic cycle")
        
        # Determine recommendation
        confidence = normalize_confidence(score, 0, 100)
        
        if score >= 70:
            recommendation = Recommendation.BUY
        elif score >= 50:
            recommendation = Recommendation.HOLD
        elif score >= 30:
            recommendation = Recommendation.WAIT
        else:
            recommendation = Recommendation.SELL
        
        # Calculate target price (based on sector strength)
        target_price = None
        current_price = extract_metric(market_data, "current_price", 0.0)
        if current_price > 0 and sector_strength > 0:
            # Target: 15-25% above current if sector is strong
            target_price = current_price * (1 + min(sector_strength * 0.5, 0.25))
        
        return StrategyResult(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=format_reasoning(reasons),
            entry_price=current_price if current_price > 0 else None,
            target_price=target_price,
            holding_period="Months to years",
            key_metrics=key_metrics,
            risks=risks,
            strategy_name=self.get_strategy_name()
        )
    
    def _detect_economic_cycle(
        self,
        market_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]]
    ) -> str:
        """
        Detect current economic cycle.
        
        Simplified detection - would use macro indicators in full implementation.
        """
        # Default to mid-cycle (most common)
        return "mid_cycle"
    
    def _check_cycle_alignment(self, sector: str, cycle: str) -> float:
        """
        Check if sector aligns with economic cycle.
        
        Returns:
            Alignment score (-1 to 1, positive = aligned, negative = misaligned)
        """
        # Sector-cycle alignment mapping
        alignment_map = {
            "early_cycle": {
                "Financials": 0.8,
                "Consumer Discretionary": 0.7,
                "Technology": 0.6,
            },
            "mid_cycle": {
                "Technology": 0.8,
                "Industrials": 0.7,
                "Consumer Discretionary": 0.6,
            },
            "late_cycle": {
                "Energy": 0.8,
                "Materials": 0.7,
                "Industrials": 0.6,
            },
            "recession": {
                "Consumer Staples": 0.8,
                "Utilities": 0.7,
                "Healthcare": 0.7,
            },
        }
        
        cycle_sectors = alignment_map.get(cycle, {})
        return cycle_sectors.get(sector, 0.0)  # Default: neutral alignment

