# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Position Sizing Calculator

Calculates optimal position sizes based on:
- Portfolio configuration (value, risk tolerance, position limits)
- Analysis results (confidence, volatility, price targets)
- Entry timing recommendations
"""

from typing import Dict, Any, Tuple, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Calculate position sizes and entry timing for stock recommendations.

    This class implements risk-based position sizing that adjusts for:
    - Analyst confidence level
    - Stock volatility
    - Portfolio risk tolerance
    - Maximum position limits
    - Cash reserve requirements
    """

    # Risk tolerance multipliers
    RISK_MULTIPLIERS = {
        'conservative': Decimal('0.5'),  # 50% of normal position
        'moderate': Decimal('1.0'),      # 100% (baseline)
        'aggressive': Decimal('1.5')     # 150% of normal position
    }

    # Confidence-based position sizing (Enhanced - Quick Win 2)
    # Maps confidence level (0-100) to position size percentage
    # Updated to allow larger positions for high-confidence trades
    CONFIDENCE_RANGES = [
        (90, 100, Decimal('1.2')),   # Very high confidence: 120% position (up to 12% of portfolio)
        (80, 89, Decimal('0.8')),    # High confidence: 80% position (up to 8% of portfolio)
        (75, 79, Decimal('0.75')),   # High confidence: 75% position
        (60, 74, Decimal('0.50')),   # Medium confidence: 50% position
        (50, 59, Decimal('0.35')),   # Low-medium confidence: 35% position
        (0, 49, Decimal('0.25'))     # Low confidence: 25% position
    ]

    def __init__(
        self,
        portfolio_value: Decimal,
        max_position_pct: Decimal = Decimal('10.0'),
        risk_tolerance: str = 'moderate',
        cash_reserve_pct: Decimal = Decimal('20.0')
    ):
        """
        Initialize position sizer.

        Args:
            portfolio_value: Total portfolio value in USD
            max_position_pct: Maximum position size as % of portfolio (default 10%)
            risk_tolerance: 'conservative', 'moderate', or 'aggressive'
            cash_reserve_pct: Minimum cash reserve % (default 20%)
        """
        self.portfolio_value = portfolio_value
        self.max_position_pct = max_position_pct
        self.risk_tolerance = risk_tolerance
        self.cash_reserve_pct = cash_reserve_pct

        # Calculate investable amount (after cash reserve)
        self.investable_amount = portfolio_value * (Decimal('100') - cash_reserve_pct) / Decimal('100')

        logger.info(
            f"Position sizer initialized: ${portfolio_value:,.2f} portfolio, "
            f"{risk_tolerance} risk, {max_position_pct}% max position"
        )

    def calculate_position_size(
        self,
        confidence: int,
        current_price: Decimal,
        volatility: Decimal = None,
        target_price: Decimal = None,
        annual_dividend_yield: Decimal = None,
        gate_scores: Dict[str, int] = None,
        timing_passed: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate optimal position size.

        Args:
            confidence: Analyst confidence (0-100)
            current_price: Current stock price
            volatility: Stock volatility (optional, for adjustment)
            target_price: Price target (optional, for upside calculation)

        Returns:
            Dict with position sizing details:
            - position_size_pct: Position size as % of portfolio
            - recommended_amount: Dollar amount to invest
            - recommended_shares: Number of shares to buy
            - max_loss_amount: Maximum potential loss
            - sizing_reasoning: Explanation of sizing logic
        """
        # Step 1: Base position size from confidence
        confidence_multiplier = self._get_confidence_multiplier(confidence)

        # Step 2: Apply risk tolerance
        risk_multiplier = self.RISK_MULTIPLIERS.get(
            self.risk_tolerance,
            self.RISK_MULTIPLIERS['moderate']
        )

        # Step 3: Volatility adjustment (if provided)
        volatility_multiplier = Decimal('1.0')
        if volatility is not None:
            volatility_multiplier = self._get_volatility_multiplier(volatility)

        # Step 4: Calculate final position size
        base_position_pct = self.max_position_pct * confidence_multiplier
        adjusted_position_pct = base_position_pct * risk_multiplier * volatility_multiplier

        # High Impact 2: Adjust based on gate scores (if provided)
        if gate_scores:
            avg_gate_score = sum(gate_scores.values()) / len(gate_scores)
            if avg_gate_score > 85:
                # Exceptional gate scores - boost position by 20%
                adjusted_position_pct *= Decimal('1.2')
            elif avg_gate_score < 60:
                # Weak gate scores - reduce position by 20%
                adjusted_position_pct *= Decimal('0.8')
        
        # High Impact 2: Reduce position if timing gate failed
        if not timing_passed:
            adjusted_position_pct *= Decimal('0.7')  # Reduce by 30%

        # Cap at max position size (Quick Win 2: Allow up to 12% for very high confidence)
        max_allowed = self.max_position_pct
        if confidence >= 90:
            # Allow up to 12% for very high confidence trades
            max_allowed = min(Decimal('12.0'), self.max_position_pct * Decimal('1.2'))
        elif confidence >= 80:
            # Allow up to 8% for high confidence trades
            max_allowed = min(Decimal('8.0'), self.max_position_pct * Decimal('0.8'))
        
        position_size_pct = min(adjusted_position_pct, max_allowed)

        # Step 5: Calculate dollar amounts
        recommended_amount = (self.portfolio_value * position_size_pct / Decimal('100')).quantize(Decimal('0.01'))
        recommended_shares = int(recommended_amount / current_price)

        # Adjust amount to actual shares purchased
        actual_amount = Decimal(recommended_shares) * current_price

        # Step 6: Calculate risk metrics (including dividend yield)
        expected_return_pct = None
        risk_reward_ratio = None
        price_appreciation_pct = None
        dividend_contribution_pct = None
        
        if target_price:
            # Price appreciation component
            price_appreciation_pct = ((target_price - current_price) / current_price * Decimal('100')).quantize(Decimal('0.01'))
            
            # Dividend yield component (annual, prorated for expected holding period)
            if annual_dividend_yield is not None:
                # Assume 1 year holding period for dividend calculation
                dividend_contribution_pct = annual_dividend_yield.quantize(Decimal('0.01'))
            else:
                dividend_contribution_pct = Decimal('0.0')
            
            # Total expected return = price appreciation + dividend yield
            expected_return_pct = (price_appreciation_pct + dividend_contribution_pct).quantize(Decimal('0.01'))

            # Assume 10% stop loss if not specified
            stop_loss_pct = Decimal('10.0')
            risk_reward_ratio = (expected_return_pct / stop_loss_pct).quantize(Decimal('0.01'))

        # Step 7: Generate sizing reasoning
        sizing_reasoning = self._generate_sizing_reasoning(
            confidence=confidence,
            confidence_multiplier=confidence_multiplier,
            risk_multiplier=risk_multiplier,
            volatility_multiplier=volatility_multiplier,
            position_size_pct=position_size_pct,
            volatility=volatility
        )

        return {
            'position_size_pct': position_size_pct,
            'recommended_amount': actual_amount,
            'recommended_shares': recommended_shares,
            'expected_return_pct': expected_return_pct,
            'price_appreciation_pct': price_appreciation_pct,
            'dividend_yield_pct': dividend_contribution_pct if annual_dividend_yield else None,
            'risk_reward_ratio': risk_reward_ratio,
            'sizing_reasoning': sizing_reasoning
        }

    def calculate_entry_timing(
        self,
        current_price: Decimal,
        support_level: Decimal = None,
        resistance_level: Decimal = None,
        moving_avg_50: Decimal = None,
        moving_avg_200: Decimal = None,
        rsi: Decimal = None,
        trend: str = None
    ) -> Dict[str, Any]:
        """
        Determine optimal entry timing.

        Args:
            current_price: Current stock price
            support_level: Support price level
            resistance_level: Resistance price level
            moving_avg_50: 50-day moving average
            moving_avg_200: 200-day moving average
            rsi: RSI indicator value
            trend: Trend direction ('uptrend', 'downtrend', 'sideways')

        Returns:
            Dict with timing recommendation:
            - timing: 'BUY_NOW', 'WAIT_FOR_DIP', 'WAIT_FOR_BREAKOUT', 'WAIT'
            - ideal_entry_min: Minimum ideal entry price
            - ideal_entry_max: Maximum ideal entry price
            - timing_reasoning: Explanation of timing logic
        """
        timing = 'BUY_NOW'
        ideal_entry_min = None
        ideal_entry_max = None
        reasoning_parts = []

        # Default: buy now with 5% range around current price
        ideal_entry_min = (current_price * Decimal('0.95')).quantize(Decimal('0.01'))
        ideal_entry_max = (current_price * Decimal('1.05')).quantize(Decimal('0.01'))

        # Check RSI - if overbought, wait for dip
        if rsi is not None:
            if rsi > Decimal('70'):
                timing = 'WAIT_FOR_DIP'
                # Suggest waiting for 5-10% pullback
                ideal_entry_min = (current_price * Decimal('0.90')).quantize(Decimal('0.01'))
                ideal_entry_max = (current_price * Decimal('0.95')).quantize(Decimal('0.01'))
                reasoning_parts.append(f"RSI is overbought at {rsi}, suggesting waiting for a pullback to ${ideal_entry_min}-${ideal_entry_max}")
            elif rsi < Decimal('30'):
                timing = 'BUY_NOW'
                reasoning_parts.append(f"RSI is oversold at {rsi}, presenting a good entry opportunity")

        # Check price vs moving averages
        if moving_avg_50 and moving_avg_200:
            if current_price > moving_avg_50 and moving_avg_50 > moving_avg_200:
                # Golden cross - strong uptrend
                if timing == 'BUY_NOW':
                    reasoning_parts.append(f"Price ${current_price} is above both 50-MA (${moving_avg_50}) and 200-MA (${moving_avg_200}), confirming uptrend")
            elif current_price < moving_avg_50 and current_price < moving_avg_200:
                # Below both MAs - wait for reversal
                if timing == 'BUY_NOW':
                    timing = 'WAIT_FOR_BREAKOUT'
                    ideal_entry_min = moving_avg_50
                    ideal_entry_max = (moving_avg_50 * Decimal('1.02')).quantize(Decimal('0.01'))
                    reasoning_parts.append(f"Price is below key moving averages. Wait for breakout above 50-MA at ${moving_avg_50}")

        # Check support/resistance levels
        if support_level and resistance_level:
            # Calculate distance to support and resistance
            distance_to_support = ((current_price - support_level) / support_level * Decimal('100')).quantize(Decimal('0.1'))
            distance_to_resistance = ((resistance_level - current_price) / current_price * Decimal('100')).quantize(Decimal('0.1'))

            if distance_to_support < Decimal('5'):
                # Near support - good entry
                timing = 'BUY_NOW'
                ideal_entry_min = support_level
                ideal_entry_max = (support_level * Decimal('1.03')).quantize(Decimal('0.01'))
                reasoning_parts.append(f"Price near support at ${support_level} ({distance_to_support}% away), offering good risk/reward")
            elif distance_to_resistance < Decimal('3'):
                # Near resistance - wait for breakout
                if timing == 'BUY_NOW':
                    timing = 'WAIT_FOR_BREAKOUT'
                    ideal_entry_min = resistance_level
                    ideal_entry_max = (resistance_level * Decimal('1.05')).quantize(Decimal('0.01'))
                    reasoning_parts.append(f"Price near resistance at ${resistance_level}. Wait for confirmed breakout")

        # Trend check
        if trend == 'downtrend' and timing == 'BUY_NOW':
            timing = 'WAIT'
            reasoning_parts.append("Stock is in downtrend. Wait for trend reversal before entering")

        # Generate final reasoning
        if not reasoning_parts:
            reasoning_parts.append(f"Current price ${current_price} offers a reasonable entry point")

        timing_reasoning = '. '.join(reasoning_parts)

        return {
            'timing': timing,
            'ideal_entry_min': ideal_entry_min,
            'ideal_entry_max': ideal_entry_max,
            'timing_reasoning': timing_reasoning
        }

    def calculate_trailing_stop(
        self,
        entry_price: Decimal,
        current_price: Decimal,
        highest_price: Decimal = None
    ) -> Dict[str, Any]:
        """
        Calculate trailing stop loss (Quick Win 3).
        
        Trails stop loss up as price rises, protecting profits.
        Stop loss trails 8% below the highest price reached.
        
        Args:
            entry_price: Original entry price
            current_price: Current stock price
            highest_price: Highest price reached since entry (optional)
            
        Returns:
            Dict with trailing stop information:
            - trailing_stop: Current trailing stop price
            - stop_loss_pct: Stop loss percentage from entry
            - profit_protected_pct: Profit protected by trailing stop
            - should_exit: Whether stop loss has been hit
        """
        if highest_price is None:
            highest_price = current_price
        
        # Update highest price if current is higher
        if current_price > highest_price:
            highest_price = current_price
        
        # Trail stop 8% below highest price
        trailing_stop = highest_price * Decimal('0.92')
        
        # Ensure trailing stop never goes below entry stop (initial 8% stop)
        initial_stop = entry_price * Decimal('0.92')
        trailing_stop = max(trailing_stop, initial_stop)
        
        # Calculate metrics
        stop_loss_pct = ((entry_price - trailing_stop) / entry_price * Decimal('100')).quantize(Decimal('0.01'))
        profit_protected_pct = ((highest_price - trailing_stop) / entry_price * Decimal('100')).quantize(Decimal('0.01'))
        
        # Check if stop has been hit
        should_exit = current_price <= trailing_stop
        
        return {
            'trailing_stop': trailing_stop.quantize(Decimal('0.01')),
            'stop_loss_pct': stop_loss_pct,
            'profit_protected_pct': profit_protected_pct,
            'highest_price': highest_price.quantize(Decimal('0.01')),
            'should_exit': should_exit,
            'reasoning': f"Trailing stop at ${trailing_stop:.2f} (8% below highest ${highest_price:.2f})"
        }

    def should_take_partial_profit(
        self,
        entry_price: Decimal,
        current_price: Decimal
    ) -> Dict[str, Any]:
        """
        Determine if partial profits should be taken (High Impact 3).
        
        Takes partial profits at:
        - 5% gain: 25% of position
        - 10% gain: 25% of position (total 50% sold)
        - 15% gain: 50% of position (total 100% sold)
        
        Args:
            entry_price: Original entry price
            current_price: Current stock price
            
        Returns:
            Dict with partial profit recommendation:
            - should_take_profit: Whether to take partial profit
            - profit_pct: Percentage of position to sell
            - gain_pct: Current gain percentage
            - reasoning: Explanation
        """
        gain_pct = ((current_price - entry_price) / entry_price * Decimal('100')).quantize(Decimal('0.01'))
        
        should_take_profit = False
        profit_pct = Decimal('0.0')
        reasoning = ""
        
        if gain_pct >= Decimal('15'):
            should_take_profit = True
            profit_pct = Decimal('0.5')  # Sell 50% (remaining position)
            reasoning = f"Strong gain of {gain_pct}% - take 50% profit to lock in gains"
        elif gain_pct >= Decimal('10'):
            should_take_profit = True
            profit_pct = Decimal('0.25')  # Sell 25%
            reasoning = f"Good gain of {gain_pct}% - take 25% profit"
        elif gain_pct >= Decimal('5'):
            should_take_profit = True
            profit_pct = Decimal('0.25')  # Sell 25%
            reasoning = f"Moderate gain of {gain_pct}% - take 25% profit"
        else:
            reasoning = f"Gain of {gain_pct}% - hold for higher targets"
        
        return {
            'should_take_profit': should_take_profit,
            'profit_pct': profit_pct,
            'gain_pct': gain_pct,
            'reasoning': reasoning
        }

    def _get_confidence_multiplier(self, confidence: int) -> Decimal:
        """Get position size multiplier based on confidence level."""
        for min_conf, max_conf, multiplier in self.CONFIDENCE_RANGES:
            if min_conf <= confidence <= max_conf:
                return multiplier
        return Decimal('0.25')  # Default to minimum

    def _get_volatility_multiplier(self, volatility: Decimal) -> Decimal:
        """
        Adjust position size based on volatility.

        Higher volatility = smaller position (more risk)
        Lower volatility = larger position (less risk)

        Args:
            volatility: Annualized volatility as percentage (e.g., 25.0 for 25%)

        Returns:
            Multiplier to apply to position size (0.5 to 1.5)
        """
        if volatility < Decimal('15'):
            # Low volatility - can increase position
            return Decimal('1.2')
        elif volatility < Decimal('25'):
            # Normal volatility - no adjustment
            return Decimal('1.0')
        elif volatility < Decimal('40'):
            # High volatility - reduce position
            return Decimal('0.8')
        else:
            # Very high volatility - significantly reduce
            return Decimal('0.6')

    def _generate_sizing_reasoning(
        self,
        confidence: int,
        confidence_multiplier: Decimal,
        risk_multiplier: Decimal,
        volatility_multiplier: Decimal,
        position_size_pct: Decimal,
        volatility: Decimal = None
    ) -> str:
        """Generate human-readable explanation of position sizing."""
        reasons = []

        # Confidence explanation
        if confidence >= 90:
            reasons.append(f"Very high analyst confidence ({confidence}%) supports a full position")
        elif confidence >= 75:
            reasons.append(f"High analyst confidence ({confidence}%) justifies a {int(confidence_multiplier * 100)}% position")
        elif confidence >= 60:
            reasons.append(f"Moderate confidence ({confidence}%) warrants a {int(confidence_multiplier * 100)}% position")
        else:
            reasons.append(f"Lower confidence ({confidence}%) suggests a conservative {int(confidence_multiplier * 100)}% position")

        # Risk tolerance
        if self.risk_tolerance == 'aggressive':
            reasons.append("Aggressive risk tolerance allows for larger position")
        elif self.risk_tolerance == 'conservative':
            reasons.append("Conservative risk tolerance reduces position size by 50%")

        # Volatility adjustment
        if volatility:
            if volatility_multiplier < Decimal('1.0'):
                reasons.append(f"High volatility ({volatility}%) reduces position size for risk management")
            elif volatility_multiplier > Decimal('1.0'):
                reasons.append(f"Low volatility ({volatility}%) allows for slightly larger position")

        # Final size
        reasons.append(f"Final position: {position_size_pct:.1f}% of portfolio (${self.portfolio_value * position_size_pct / Decimal('100'):,.2f})")

        return '. '.join(reasons) + '.'
