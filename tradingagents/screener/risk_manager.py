# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Enhanced Risk Management & Position Sizing

Professional-grade risk management system that calculates optimal position sizes
based on volatility, market regime, and account parameters.
"""

from typing import Dict, Any, Optional
import numpy as np


class RiskManager:
    """
    Professional risk management and position sizing calculator.

    Uses Kelly Criterion, ATR-based sizing, and regime adjustments to calculate
    optimal position sizes that maximize long-term growth while managing drawdown risk.
    """

    def __init__(self, account_size: float = 100000, max_risk_per_trade_pct: float = 2.0):
        """
        Initialize risk manager.

        Args:
            account_size: Total account value in dollars
            max_risk_per_trade_pct: Maximum % of account to risk per trade (default 2%)
        """
        self.account_size = account_size
        self.max_risk_per_trade_pct = max_risk_per_trade_pct

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        technical_signals: Dict[str, Any],
        market_regime: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal position size using multiple risk management approaches.

        Args:
            entry_price: Intended entry price
            stop_loss: Stop loss price
            technical_signals: Technical indicator signals from screener
            market_regime: Current market regime (BULL_MARKET, BEAR_MARKET, etc.)

        Returns:
            Dictionary with position sizing recommendations
        """
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss)

        if risk_per_share == 0:
            return {
                'error': 'Invalid stop loss - must be different from entry price',
                'position_size': 0,
                'shares': 0
            }

        # Method 1: Fixed Risk Position Sizing
        fixed_risk_size = self._fixed_risk_sizing(entry_price, risk_per_share)

        # Method 2: Volatility-Adjusted Sizing (using ATR)
        volatility_adjusted_size = self._volatility_adjusted_sizing(
            entry_price,
            risk_per_share,
            technical_signals
        )

        # Method 3: Kelly Criterion (for confident setups)
        kelly_size = self._kelly_criterion_sizing(
            entry_price,
            stop_loss,
            technical_signals
        )

        # Method 4: Regime-Adjusted Sizing
        regime_adjusted_size = self._regime_adjusted_sizing(
            fixed_risk_size,
            market_regime,
            technical_signals
        )

        # Determine final recommendation
        recommended_size = self._determine_final_size(
            fixed_risk_size,
            volatility_adjusted_size,
            kelly_size,
            regime_adjusted_size,
            technical_signals
        )

        # Calculate shares
        shares = int(recommended_size / entry_price)
        actual_position_value = shares * entry_price
        actual_risk_dollars = shares * risk_per_share
        actual_risk_pct = (actual_risk_dollars / self.account_size) * 100

        # Calculate R-multiples for targets
        risk_reward_1r = entry_price + risk_per_share
        risk_reward_2r = entry_price + (risk_per_share * 2)
        risk_reward_3r = entry_price + (risk_per_share * 3)

        # Position management recommendations
        scaling_plan = self._get_scaling_plan(shares, technical_signals)

        return {
            'recommended_shares': shares,
            'recommended_position_value': actual_position_value,
            'position_as_pct_of_account': (actual_position_value / self.account_size) * 100,
            'risk_per_share': risk_per_share,
            'total_risk_dollars': actual_risk_dollars,
            'total_risk_pct': actual_risk_pct,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'stop_loss_pct': ((entry_price - stop_loss) / entry_price) * 100,

            # Targets
            'target_1r': risk_reward_1r,
            'target_2r': risk_reward_2r,
            'target_3r': risk_reward_3r,

            # Different sizing methods
            'sizing_methods': {
                'fixed_risk': fixed_risk_size,
                'volatility_adjusted': volatility_adjusted_size,
                'kelly_criterion': kelly_size,
                'regime_adjusted': regime_adjusted_size
            },

            # Position management
            'scaling_plan': scaling_plan,
            'max_shares_allowed': self._calculate_max_shares(entry_price),
            'confidence_level': self._calculate_confidence(technical_signals)
        }

    def _fixed_risk_sizing(self, entry_price: float, risk_per_share: float) -> float:
        """Fixed risk sizing - risk fixed % of account per trade."""
        max_risk_dollars = self.account_size * (self.max_risk_per_trade_pct / 100)
        max_shares = max_risk_dollars / risk_per_share
        position_value = max_shares * entry_price

        # Don't exceed 20% of account in any single position
        max_position_value = self.account_size * 0.20
        return min(position_value, max_position_value)

    def _volatility_adjusted_sizing(
        self,
        entry_price: float,
        risk_per_share: float,
        technical_signals: Dict[str, Any]
    ) -> float:
        """Adjust position size based on volatility (ATR)."""

        atr_pct = technical_signals.get('atr_pct', 2.0)

        # Higher volatility = smaller position
        # Lower volatility = larger position
        if atr_pct > 5.0:
            # Very high volatility - reduce size by 50%
            volatility_multiplier = 0.5
        elif atr_pct > 3.0:
            # High volatility - reduce size by 30%
            volatility_multiplier = 0.7
        elif atr_pct < 1.0:
            # Low volatility - increase size by 20%
            volatility_multiplier = 1.2
        else:
            # Normal volatility
            volatility_multiplier = 1.0

        base_size = self._fixed_risk_sizing(entry_price, risk_per_share)
        return base_size * volatility_multiplier

    def _kelly_criterion_sizing(
        self,
        entry_price: float,
        stop_loss: float,
        technical_signals: Dict[str, Any]
    ) -> float:
        """
        Kelly Criterion sizing for optimal growth.

        Kelly % = (Win Rate * Avg Win - Loss Rate * Avg Loss) / Avg Win

        For high-probability setups only.
        """
        # Estimate win rate based on signal strength
        confidence = self._calculate_confidence(technical_signals)

        if confidence < 0.65:
            # Kelly only for high-confidence trades
            return 0

        # Estimate parameters based on historical patterns
        win_rate = confidence  # 65-85%
        loss_rate = 1 - win_rate

        # Assume 2:1 reward:risk ratio for strong setups
        risk_per_share = abs(entry_price - stop_loss)
        avg_win = risk_per_share * 2  # 2R target
        avg_loss = risk_per_share  # 1R loss

        # Kelly formula
        kelly_pct = (win_rate * avg_win - loss_rate * avg_loss) / avg_win

        # Use fractional Kelly (more conservative)
        fractional_kelly = kelly_pct * 0.5  # Use half Kelly

        # Apply to account
        position_value = self.account_size * max(0, min(fractional_kelly, 0.15))  # Cap at 15%
        return position_value

    def _regime_adjusted_sizing(
        self,
        base_size: float,
        market_regime: Optional[str],
        technical_signals: Dict[str, Any]
    ) -> float:
        """Adjust sizing based on market regime."""

        if not market_regime:
            # Try to infer from multi-timeframe analysis
            mtf_alignment = technical_signals.get('mtf_alignment', '')
            if 'BULLISH' in mtf_alignment:
                market_regime = 'BULL_MARKET'
            elif 'BEARISH' in mtf_alignment:
                market_regime = 'BEAR_MARKET'
            elif 'HIGH_VOLATILITY' in mtf_alignment:
                market_regime = 'HIGH_VOLATILITY_ENVIRONMENT'
            else:
                market_regime = 'NEUTRAL_CHOPPY'

        regime_multipliers = {
            'BULL_MARKET': 1.2,  # Increase size 20% in bull markets
            'BEAR_MARKET': 0.6,  # Reduce size 40% in bear markets
            'HIGH_VOLATILITY_ENVIRONMENT': 0.5,  # Reduce size 50% in high vol
            'NEUTRAL_CHOPPY': 0.8,  # Reduce size 20% in choppy markets
        }

        multiplier = regime_multipliers.get(market_regime, 1.0)
        return base_size * multiplier

    def _determine_final_size(
        self,
        fixed_risk: float,
        volatility_adjusted: float,
        kelly: float,
        regime_adjusted: float,
        technical_signals: Dict[str, Any]
    ) -> float:
        """Determine final position size using weighted average of methods."""

        confidence = self._calculate_confidence(technical_signals)

        if confidence >= 0.80:
            # High confidence - weight Kelly more heavily
            sizes = [regime_adjusted, volatility_adjusted]
            if kelly > 0:
                sizes.append(kelly)
            final_size = np.mean(sizes)

        elif confidence >= 0.65:
            # Medium confidence - balanced approach
            final_size = np.mean([regime_adjusted, volatility_adjusted])

        else:
            # Low confidence - conservative
            final_size = min(regime_adjusted, volatility_adjusted) * 0.7

        # Safety cap: never exceed 25% of account
        max_allowed = self.account_size * 0.25
        return min(final_size, max_allowed)

    def _calculate_confidence(self, technical_signals: Dict[str, Any]) -> float:
        """
        Calculate confidence level based on signal alignment.

        Returns: Confidence from 0.0 to 1.0
        """
        confidence_score = 0.5  # Start at neutral

        # Multi-timeframe alignment boost
        mtf_confidence = technical_signals.get('mtf_confidence', 0)
        if mtf_confidence > 0:
            confidence_score = mtf_confidence

        # Pattern recognition boost
        if technical_signals.get('rsi_bullish_divergence'):
            confidence_score += 0.10
        if technical_signals.get('bb_squeeze_detected'):
            confidence_score += 0.05
        if technical_signals.get('institutional_accumulation'):
            confidence_score += 0.10

        # Volume confirmation
        volume_ratio = technical_signals.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            confidence_score += 0.05

        # VWAP confirmation
        vwap_dist = technical_signals.get('vwap_distance_pct', 0)
        if -2 < vwap_dist < -0.5:  # Below VWAP (good entry)
            confidence_score += 0.05

        # Cap at 95%
        return min(confidence_score, 0.95)

    def _calculate_max_shares(self, entry_price: float) -> int:
        """Calculate maximum shares allowed (25% of account)."""
        max_position_value = self.account_size * 0.25
        return int(max_position_value / entry_price)

    def _get_scaling_plan(
        self,
        total_shares: int,
        technical_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate position scaling plan.

        Professional traders scale in/out rather than all-in/all-out.
        """
        if total_shares < 3:
            # Too small to scale
            return {
                'can_scale': False,
                'reason': 'Position too small to scale effectively',
                'initial_shares': total_shares,
                'scale_in_plan': [],
                'scale_out_plan': []
            }

        confidence = self._calculate_confidence(technical_signals)

        if confidence >= 0.80:
            # High confidence - can enter full position
            initial_pct = 100
        elif confidence >= 0.65:
            # Medium confidence - scale in 50% initially
            initial_pct = 50
        else:
            # Low confidence - scale in 33% initially
            initial_pct = 33

        initial_shares = int(total_shares * (initial_pct / 100))
        remaining_shares = total_shares - initial_shares

        scale_in_plan = []
        if remaining_shares > 0:
            # Scale in additional shares if entry proves correct
            scale_in_plan.append({
                'trigger': 'Price moves in favor by 0.5R',
                'shares': int(remaining_shares * 0.5),
                'reason': 'Confirm trade thesis'
            })
            scale_in_plan.append({
                'trigger': 'Price moves in favor by 1R',
                'shares': remaining_shares - int(remaining_shares * 0.5),
                'reason': 'Full conviction after 1R gain'
            })

        # Scale out plan (take profits)
        third = int(total_shares / 3)
        scale_out_plan = [
            {
                'target': '1R (100% gain on risk)',
                'shares': third,
                'action': 'Take 1/3 off, move stop to breakeven'
            },
            {
                'target': '2R (200% gain on risk)',
                'shares': third,
                'action': 'Take another 1/3 off, trail stop'
            },
            {
                'target': '3R+ (300% gain on risk)',
                'shares': total_shares - (third * 2),
                'action': 'Let runner continue with trailing stop'
            }
        ]

        return {
            'can_scale': True,
            'initial_shares': initial_shares,
            'initial_pct': initial_pct,
            'remaining_shares': remaining_shares,
            'scale_in_plan': scale_in_plan,
            'scale_out_plan': scale_out_plan,
            'recommendation': f"Enter with {initial_pct}% ({initial_shares} shares) initially, " +
                            f"scale in remaining {100 - initial_pct}% if trade confirms."
        }

    def calculate_portfolio_risk(
        self,
        current_positions: list,
        new_position: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate total portfolio risk including new position.

        Ensures portfolio doesn't become over-concentrated or over-risked.
        """
        # Calculate current portfolio risk
        total_current_risk = sum(
            pos.get('risk_dollars', 0) for pos in current_positions
        )

        # Add new position risk
        new_risk = new_position.get('total_risk_dollars', 0)
        total_risk = total_current_risk + new_risk
        total_risk_pct = (total_risk / self.account_size) * 100

        # Calculate sector concentration
        sectors = {}
        for pos in current_positions:
            sector = pos.get('sector', 'Unknown')
            sectors[sector] = sectors.get(sector, 0) + pos.get('position_value', 0)

        new_sector = new_position.get('sector', 'Unknown')
        sectors[new_sector] = sectors.get(new_sector, 0) + new_position.get('recommended_position_value', 0)

        max_sector_exposure = max(sectors.values()) if sectors else 0
        max_sector_pct = (max_sector_exposure / self.account_size) * 100

        # Warnings
        warnings = []
        if total_risk_pct > 10:
            warnings.append(f"CRITICAL: Total portfolio risk ({total_risk_pct:.1f}%) exceeds 10% - reduce position sizes")
        elif total_risk_pct > 6:
            warnings.append(f"WARNING: Total portfolio risk ({total_risk_pct:.1f}%) exceeds 6% - consider reducing")

        if max_sector_pct > 40:
            warnings.append(f"WARNING: Sector concentration ({max_sector_pct:.1f}%) exceeds 40% - diversify")

        if len(current_positions) + 1 > 10:
            warnings.append(f"WARNING: Too many positions ({len(current_positions) + 1}) - hard to manage effectively")

        return {
            'total_portfolio_risk_dollars': total_risk,
            'total_portfolio_risk_pct': total_risk_pct,
            'max_sector_exposure_pct': max_sector_pct,
            'number_of_positions': len(current_positions) + 1,
            'warnings': warnings,
            'recommended_action': 'SAFE_TO_ADD' if not warnings else 'REVIEW_RISK_BEFORE_ADDING'
        }
