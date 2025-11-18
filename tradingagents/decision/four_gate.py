"""
Four-Gate Buy Decision Framework

Systematic decision framework with four gates that must pass for a BUY signal.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    """Result from a decision gate."""
    passed: bool
    score: int  # 0-100
    reasoning: str
    details: Dict[str, Any]


class FourGateFramework:
    """
    Four-gate buy decision framework.

    All gates must pass for a BUY recommendation.
    Gates:
    1. Fundamental Value
    2. Technical Entry
    3. Risk Assessment
    4. Timing Quality
    """

    # Gate thresholds (configurable)
    DEFAULT_THRESHOLDS = {
        'fundamental_min_score': 70,
        'technical_min_score': 65,
        'risk_min_score': 70,
        'timing_min_score': 60,  # Lower threshold (optimization, not requirement)
    }

    def __init__(self, thresholds: Dict[str, int] = None):
        """
        Initialize framework.

        Args:
            thresholds: Custom gate thresholds (optional)
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS

    def evaluate_fundamental_gate(
        self,
        fundamentals: Dict[str, Any],
        sector_avg: Dict[str, Any] = None,
        historical_avg: Dict[str, Any] = None
    ) -> GateResult:
        """
        Gate 1: Fundamental Value Assessment.

        Evaluates if the stock represents good fundamental value.

        Args:
            fundamentals: Current fundamental metrics
            sector_avg: Sector average metrics (optional)
            historical_avg: Historical average metrics (optional)

        Returns:
            GateResult with pass/fail and score
        """
        score = 50  # Neutral baseline
        details = {}
        reasons = []

        # P/E Ratio evaluation
        pe_ratio = fundamentals.get('pe_ratio')
        if pe_ratio:
            details['pe_ratio'] = pe_ratio

            if sector_avg and sector_avg.get('pe_ratio'):
                sector_pe = sector_avg['pe_ratio']
                details['sector_pe'] = sector_pe

                if pe_ratio < sector_pe * 0.8:
                    score += 20
                    reasons.append(f"P/E ({pe_ratio:.1f}) significantly below sector ({sector_pe:.1f})")
                elif pe_ratio < sector_pe:
                    score += 10
                    reasons.append(f"P/E below sector average")
                elif pe_ratio > sector_pe * 1.5:
                    score -= 10
                    reasons.append(f"P/E elevated vs sector")
            else:
                # Absolute P/E evaluation
                if pe_ratio < 15:
                    score += 15
                    reasons.append(f"Low P/E ({pe_ratio:.1f}) indicates value")
                elif pe_ratio < 25:
                    score += 5
                    reasons.append("Reasonable P/E valuation")
                elif pe_ratio > 50:
                    score -= 10
                    reasons.append(f"High P/E ({pe_ratio:.1f}) indicates premium valuation")

        # Forward P/E and PEG evaluation
        forward_pe = fundamentals.get('forward_pe')
        if forward_pe and pe_ratio:
            details['forward_pe'] = forward_pe
            peg_proxy = forward_pe / pe_ratio if pe_ratio > 0 else 1

            if peg_proxy < 0.8:
                score += 15
                reasons.append("Improving growth outlook (Forward P/E favorable)")
            elif peg_proxy < 1.0:
                score += 5

        # Growth metrics
        revenue_growth = fundamentals.get('revenue_growth_yoy')
        if revenue_growth is not None:
            details['revenue_growth'] = revenue_growth

            if revenue_growth > 0.20:  # 20%+
                score += 15
                reasons.append(f"Strong revenue growth ({revenue_growth:.1%})")
            elif revenue_growth > 0.10:  # 10-20%
                score += 10
                reasons.append(f"Good revenue growth ({revenue_growth:.1%})")
            elif revenue_growth < 0:
                score -= 15
                reasons.append("Declining revenue (concern)")

        # Balance sheet strength
        if fundamentals.get('debt_to_equity'):
            de_ratio = fundamentals['debt_to_equity']
            details['debt_to_equity'] = de_ratio

            if de_ratio < 0.5:
                score += 5
                reasons.append("Strong balance sheet (low debt)")
            elif de_ratio > 2.0:
                score -= 5
                reasons.append("High leverage (risk)")

        # Dividend yield consideration (bonus for dividend stocks)
        dividend_yield = fundamentals.get('dividend_yield')
        if dividend_yield is not None:
            details['dividend_yield'] = dividend_yield
            if dividend_yield >= 3.0:
                score += 10
                reasons.append(f"Attractive dividend yield ({dividend_yield:.2f}%)")
            elif dividend_yield >= 2.0:
                score += 5
                reasons.append(f"Moderate dividend yield ({dividend_yield:.2f}%)")

        # Final score adjustment
        score = max(0, min(100, score))
        passed = score >= self.thresholds['fundamental_min_score']

        reasoning = " | ".join(reasons) if reasons else "Insufficient fundamental data"

        return GateResult(
            passed=passed,
            score=score,
            reasoning=reasoning,
            details=details
        )

    def evaluate_technical_gate(
        self,
        signals: Dict[str, Any],
        price_data: Dict[str, Any],
        historical_context: Dict[str, Any] = None
    ) -> GateResult:
        """
        Gate 2: Technical Entry Point Assessment.

        Evaluates if this is a good technical entry point.

        Args:
            signals: Technical signals
            price_data: Price information
            historical_context: Historical similar setups (optional)

        Returns:
            GateResult with pass/fail and score
        """
        score = 50  # Neutral baseline
        details = {}
        reasons = []

        # Rule: Don't buy at 52-week highs (allow up to 5% below)
        current_price = price_data.get('current_price', 0)
        week_52_high = price_data.get('week_52_high')

        if week_52_high and current_price:
            pct_from_high = ((week_52_high - current_price) / week_52_high) * 100
            details['pct_from_52w_high'] = pct_from_high

            if pct_from_high < 5:
                score -= 20
                reasons.append(f"Too close to 52-week high ({pct_from_high:.1f}% below)")
            elif pct_from_high > 20:
                score += 10
                reasons.append(f"Good pullback from highs ({pct_from_high:.1f}% below)")

        # RSI evaluation
        rsi = signals.get('rsi')
        if rsi is not None:
            details['rsi'] = rsi

            if rsi < 30:
                score += 20
                reasons.append(f"RSI oversold ({rsi:.1f}) - potential bounce")
            elif 30 <= rsi <= 50:
                score += 10
                reasons.append(f"RSI favorable ({rsi:.1f})")
            elif rsi > 70:
                score -= 15
                reasons.append(f"RSI overbought ({rsi:.1f}) - caution")

        # MACD signals
        if signals.get('macd_bullish_crossover'):
            score += 15
            reasons.append("MACD bullish crossover (momentum building)")

        if signals.get('macd_bearish_crossover'):
            score -= 10
            reasons.append("MACD bearish crossover (momentum fading)")

        # Moving averages
        if signals.get('price_above_ma20'):
            score += 5
            reasons.append("Price above 20-day MA")

        if signals.get('price_above_ma50'):
            score += 5
            reasons.append("Price above 50-day MA")

        if signals.get('ma20_above_ma50'):
            score += 10
            reasons.append("20-day MA above 50-day MA (bullish trend)")

        # Support/resistance
        if signals.get('near_support'):
            score += 15
            reasons.append("Price near support level (good entry)")

        if signals.get('near_resistance'):
            score -= 10
            reasons.append("Price near resistance (may face selling)")

        # Volume confirmation
        volume_ratio = signals.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            score += 10
            reasons.append(f"Strong volume ({volume_ratio:.1f}x average)")

        # Historical pattern success rate
        if historical_context and historical_context.get('pattern_success_rate'):
            success_rate = historical_context['pattern_success_rate']
            details['historical_success_rate'] = success_rate

            if success_rate > 0.7:
                score += 10
                reasons.append(f"Similar setups succeeded {success_rate:.1%} of the time")
            elif success_rate < 0.4:
                score -= 10
                reasons.append(f"Similar setups have low success rate ({success_rate:.1%})")

        score = max(0, min(100, score))
        passed = score >= self.thresholds['technical_min_score']

        reasoning = " | ".join(reasons) if reasons else "Insufficient technical data"

        return GateResult(
            passed=passed,
            score=score,
            reasoning=reasoning,
            details=details
        )

    def evaluate_risk_gate(
        self,
        risk_analysis: Dict[str, Any],
        position_size_pct: float,
        portfolio_context: Dict[str, Any] = None,
        correlation_risk: Dict[str, Any] = None
    ) -> GateResult:
        """
        Gate 3: Risk Assessment.

        Evaluates if the risk profile is acceptable.

        Args:
            risk_analysis: Risk metrics and assessments
            position_size_pct: Proposed position size (% of portfolio)
            portfolio_context: Current portfolio state (optional)

        Returns:
            GateResult with pass/fail and score
        """
        score = 50  # Neutral baseline
        details = {}
        reasons = []

        # Position size check
        details['position_size_pct'] = position_size_pct

        if position_size_pct > 10:
            score -= 20
            reasons.append(f"Position size too large ({position_size_pct:.1f}% > 10% max)")
        elif position_size_pct > 7:
            score -= 10
            reasons.append(f"Position size elevated ({position_size_pct:.1f}%)")
        else:
            score += 5
            reasons.append(f"Position size appropriate ({position_size_pct:.1f}%)")

        # Max drawdown assessment
        max_drawdown = risk_analysis.get('max_expected_drawdown_pct')
        if max_drawdown is not None:
            details['max_drawdown'] = max_drawdown

            if max_drawdown > 20:
                score -= 20
                reasons.append(f"High expected drawdown ({max_drawdown:.1f}%)")
            elif max_drawdown > 15:
                score -= 10
                reasons.append(f"Moderate expected drawdown ({max_drawdown:.1f}%)")
            else:
                score += 10
                reasons.append(f"Acceptable drawdown risk ({max_drawdown:.1f}%)")

        # Risk/reward ratio
        risk_reward = risk_analysis.get('risk_reward_ratio')
        if risk_reward is not None:
            details['risk_reward_ratio'] = risk_reward

            if risk_reward > 3.0:
                score += 15
                reasons.append(f"Excellent risk/reward ({risk_reward:.1f}:1)")
            elif risk_reward > 2.0:
                score += 10
                reasons.append(f"Good risk/reward ({risk_reward:.1f}:1)")
            elif risk_reward < 1.5:
                score -= 15
                reasons.append(f"Poor risk/reward ({risk_reward:.1f}:1)")

        # Sector exposure check (enhanced enforcement)
        if portfolio_context:
            current_sector_exposure = portfolio_context.get('sector_exposure', 0)
            sector = portfolio_context.get('sector')
            sector_limit = portfolio_context.get('sector_limit', 35.0)  # Default 35%
            
            proposed_exposure = current_sector_exposure + position_size_pct
            
            if proposed_exposure > sector_limit:
                # Fail gate if would exceed limit
                score -= 25
                reasons.append(
                    f"Would exceed sector limit ({sector}: {proposed_exposure:.1f}% > {sector_limit:.1f}%)"
                )
            elif proposed_exposure > sector_limit * 0.9:  # Within 10% of limit
                score -= 10
                reasons.append(
                    f"Approaching sector limit ({sector}: {proposed_exposure:.1f}% of {sector_limit:.1f}%)"
                )
            elif current_sector_exposure < sector_limit * 0.5:  # Underweight sector
                score += 5
                reasons.append(f"Sector diversification opportunity ({sector}: {current_sector_exposure:.1f}% < {sector_limit * 0.5:.1f}%)")

        # Correlation risk check (High Impact 5)
        if correlation_risk:
            max_correlation = correlation_risk.get('max_correlation', 0.0)
            details['max_correlation'] = max_correlation
            
            if max_correlation > 0.75:
                score -= 20
                reasons.append(f"High correlation risk ({max_correlation:.2f} > 0.75)")
            elif max_correlation > 0.6:
                score -= 10
                reasons.append(f"Moderate correlation risk ({max_correlation:.2f})")
            elif max_correlation < 0.3:
                score += 5
                reasons.append(f"Good diversification (low correlation {max_correlation:.2f})")

        # Red flags from risk analysis
        risk_flags = risk_analysis.get('red_flags', [])
        if risk_flags:
            details['risk_flags'] = risk_flags
            score -= len(risk_flags) * 5
            reasons.append(f"{len(risk_flags)} risk flag(s): {', '.join(risk_flags[:2])}")

        score = max(0, min(100, score))
        passed = score >= self.thresholds['risk_min_score']

        reasoning = " | ".join(reasons) if reasons else "Risk assessment incomplete"

        return GateResult(
            passed=passed,
            score=score,
            reasoning=reasoning,
            details=details
        )

    def evaluate_timing_gate(
        self,
        current_situation: Dict[str, Any],
        historical_context: Dict[str, Any],
        catalyst_timeline: Dict[str, Any] = None
    ) -> GateResult:
        """
        Gate 4: Timing Quality Assessment.

        Evaluates if this is an optimal time to buy (optimization, not blocker).

        Args:
            current_situation: Current market situation
            historical_context: Historical analysis context
            catalyst_timeline: Expected catalysts and timing

        Returns:
            GateResult with score (not strictly pass/fail)
        """
        score = 50  # Neutral baseline
        details = {}
        reasons = []

        # Compare current price to historical analyses
        current_price = current_situation.get('price', 0)
        last_analysis = historical_context.get('last_analysis')

        if last_analysis and last_analysis.get('price'):
            last_price = last_analysis['price']
            price_change_pct = ((current_price - last_price) / last_price) * 100
            details['price_vs_last_analysis'] = price_change_pct

            if price_change_pct < -10:
                score += 15
                reasons.append(f"Price down {abs(price_change_pct):.1f}% since last analysis (opportunity)")
            elif price_change_pct > 10:
                score -= 10
                reasons.append(f"Price up {price_change_pct:.1f}% since last analysis (less attractive)")

        # Historical pattern matching
        similar_situations = historical_context.get('similar_situations', [])
        if similar_situations:
            # Check if similar setups were successful
            buy_signals = [s for s in similar_situations if s.get('final_decision') == 'BUY']

            if buy_signals:
                success_count = len(buy_signals)
                total_count = len(similar_situations)
                success_rate = success_count / total_count

                details['historical_success_rate'] = success_rate

                if success_rate > 0.7:
                    score += 15
                    reasons.append(f"Similar setups succeeded {success_rate:.1%} historically")
                elif success_rate < 0.3:
                    score -= 10
                    reasons.append(f"Similar setups had low success rate ({success_rate:.1%})")

        # Catalyst timeline
        if catalyst_timeline:
            days_to_catalyst = catalyst_timeline.get('days_to_next_catalyst')

            if days_to_catalyst is not None:
                details['days_to_catalyst'] = days_to_catalyst

                if 0 < days_to_catalyst < 30:
                    score += 10
                    reasons.append(f"Catalyst approaching in {days_to_catalyst} days")
                elif days_to_catalyst > 90:
                    score -= 5
                    reasons.append("No near-term catalysts")

        # Sector momentum
        sector_context = historical_context.get('sector_context', {})
        if sector_context.get('buy_signal_rate'):
            sector_buy_rate = sector_context['buy_signal_rate']
            details['sector_buy_rate'] = sector_buy_rate

            if sector_buy_rate > 0.5:
                score += 10
                reasons.append(f"Sector showing strength ({sector_buy_rate:.1%} buy rate)")
            elif sector_buy_rate < 0.2:
                score -= 5
                reasons.append("Sector weakness (low buy rate)")

        score = max(0, min(100, score))

        # Note: Timing gate is optimization, not hard requirement
        # We use a lower threshold
        passed = score >= self.thresholds['timing_min_score']

        reasoning = " | ".join(reasons) if reasons else "Timing assessment based on available data"

        return GateResult(
            passed=passed,
            score=score,
            reasoning=reasoning,
            details=details
        )

    def get_dynamic_thresholds(
        self, 
        confidence_score: int = None,
        market_regime: str = None,
        volatility_regime: str = None
    ) -> Dict[str, int]:
        """
        Get dynamic thresholds based on confidence score and market regime.
        
        Quick Win 1: Adjust gate thresholds based on confidence level.
        High Impact 1: Adjust thresholds based on market regime.
        
        - High confidence (>85): Lower thresholds (more permissive)
        - Low confidence (<60): Raise thresholds (more strict)
        - Bull market: Lower fundamental, raise technical
        - Bear market: Raise fundamental, lower technical
        - High volatility: Raise risk threshold
        
        Args:
            confidence_score: Overall confidence score (0-100)
            market_regime: 'bull', 'bear', or 'neutral' (optional)
            volatility_regime: 'high', 'low', or 'normal' (optional)
            
        Returns:
            Adjusted thresholds dictionary
        """
        thresholds = self.thresholds.copy()
        
        # Quick Win 1: Confidence-based adjustments
        if confidence_score is not None:
            if confidence_score > 85:
                # High confidence: Lower thresholds for more opportunities
                thresholds['fundamental_min_score'] = max(65, thresholds['fundamental_min_score'] - 5)
                thresholds['technical_min_score'] = max(60, thresholds['technical_min_score'] - 5)
            elif confidence_score < 60:
                # Low confidence: Raise thresholds for stricter filtering
                thresholds['fundamental_min_score'] = min(75, thresholds['fundamental_min_score'] + 5)
                thresholds['technical_min_score'] = min(70, thresholds['technical_min_score'] + 5)
        
        # High Impact 1: Market regime adjustments
        if market_regime == 'bull':
            thresholds['fundamental_min_score'] = max(65, thresholds['fundamental_min_score'] - 5)
            thresholds['technical_min_score'] = min(70, thresholds['technical_min_score'] + 5)
        elif market_regime == 'bear':
            thresholds['fundamental_min_score'] = min(75, thresholds['fundamental_min_score'] + 5)
            thresholds['technical_min_score'] = max(60, thresholds['technical_min_score'] - 5)
        
        if volatility_regime == 'high':
            thresholds['risk_min_score'] = min(75, thresholds['risk_min_score'] + 5)
        
        return thresholds

    def evaluate_all_gates(
        self,
        fundamentals: Dict[str, Any],
        signals: Dict[str, Any],
        price_data: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        position_size_pct: float,
        historical_context: Dict[str, Any],
        sector_avg: Dict[str, Any] = None,
        portfolio_context: Dict[str, Any] = None,
        catalyst_timeline: Dict[str, Any] = None,
        confidence_score: int = None,
        correlation_risk: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all four gates and generate final recommendation.

        Args:
            fundamentals: Fundamental metrics
            signals: Technical signals
            price_data: Price information
            risk_analysis: Risk assessment
            position_size_pct: Proposed position size
            historical_context: Historical analysis context
            sector_avg: Sector averages (optional)
            portfolio_context: Portfolio state (optional)
            catalyst_timeline: Catalyst timeline (optional)
            confidence_score: Overall confidence score for dynamic thresholds (optional)

        Returns:
            Complete evaluation with final recommendation
        """
        # Apply dynamic thresholds based on confidence (Quick Win 1)
        original_thresholds = self.thresholds
        if confidence_score is not None:
            self.thresholds = self.get_dynamic_thresholds(confidence_score)
        
        # Evaluate each gate
        gate1 = self.evaluate_fundamental_gate(fundamentals, sector_avg)
        gate2 = self.evaluate_technical_gate(signals, price_data, historical_context)
        gate3 = self.evaluate_risk_gate(risk_analysis, position_size_pct, portfolio_context, correlation_risk)
        gate4 = self.evaluate_timing_gate(price_data, historical_context, catalyst_timeline)
        
        # Restore original thresholds
        self.thresholds = original_thresholds

        # Determine final decision
        # Gates 1-3 must pass, Gate 4 is advisory
        all_gates_passed = gate1.passed and gate2.passed and gate3.passed

        if all_gates_passed:
            if gate4.passed:
                final_decision = "BUY"
                decision_confidence = (gate1.score + gate2.score + gate3.score + gate4.score) // 4
            else:
                final_decision = "WAIT"  # Consider waiting for better timing
                decision_confidence = (gate1.score + gate2.score + gate3.score + gate4.score) // 4
        else:
            final_decision = "PASS"
            decision_confidence = (gate1.score + gate2.score + gate3.score + gate4.score) // 4

        result = {
            'final_decision': final_decision,
            'confidence_score': decision_confidence,
            'gates': {
                'fundamental': {
                    'passed': gate1.passed,
                    'score': gate1.score,
                    'reasoning': gate1.reasoning,
                    'details': gate1.details
                },
                'technical': {
                    'passed': gate2.passed,
                    'score': gate2.score,
                    'reasoning': gate2.reasoning,
                    'details': gate2.details
                },
                'risk': {
                    'passed': gate3.passed,
                    'score': gate3.score,
                    'reasoning': gate3.reasoning,
                    'details': gate3.details
                },
                'timing': {
                    'passed': gate4.passed,
                    'score': gate4.score,
                    'reasoning': gate4.reasoning,
                    'details': gate4.details
                }
            },
            'summary': {
                'gates_passed': sum([gate1.passed, gate2.passed, gate3.passed, gate4.passed]),
                'total_gates': 4,
                'critical_gates_passed': sum([gate1.passed, gate2.passed, gate3.passed]),
                'recommendation': self._generate_recommendation(
                    final_decision,
                    gate1,
                    gate2,
                    gate3,
                    gate4
                )
            }
        }

        return result

    def _generate_recommendation(
        self,
        decision: str,
        gate1: GateResult,
        gate2: GateResult,
        gate3: GateResult,
        gate4: GateResult
    ) -> str:
        """Generate human-readable recommendation."""
        if decision == "BUY":
            return (
                f"STRONG BUY - All gates passed. "
                f"Fundamentals: {gate1.score}/100, Technical: {gate2.score}/100, "
                f"Risk: {gate3.score}/100, Timing: {gate4.score}/100"
            )
        elif decision == "WAIT":
            return (
                f"WAIT - Core gates passed but timing could be better. "
                f"Timing score: {gate4.score}/100 (below threshold {self.thresholds['timing_min_score']})"
            )
        else:
            failed_gates = []
            if not gate1.passed:
                failed_gates.append(f"Fundamental ({gate1.score}/100)")
            if not gate2.passed:
                failed_gates.append(f"Technical ({gate2.score}/100)")
            if not gate3.passed:
                failed_gates.append(f"Risk ({gate3.score}/100)")

            return (
                f"PASS - Failed gates: {', '.join(failed_gates)}. "
                f"Re-evaluate when conditions improve."
            )
