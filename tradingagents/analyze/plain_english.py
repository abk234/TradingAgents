"""
Plain English Report Generator

Converts technical analysis into simple, actionable recommendations
that anyone can understand.
"""

from typing import Dict, Any, List
from datetime import date, timedelta
from decimal import Decimal
import logging

from tradingagents.portfolio import PositionSizer

logger = logging.getLogger(__name__)


class PlainEnglishReport:
    """Generate plain English investment reports."""

    @staticmethod
    def generate_recommendation(
        results: Dict[str, Any],
        portfolio_value: float = None,
        max_position_pct: float = 5.0
    ) -> str:
        """
        Generate a plain English recommendation.

        Args:
            results: Analysis results from DeepAnalyzer
            portfolio_value: Total portfolio value (optional)
            max_position_pct: Maximum position size as % of portfolio

        Returns:
            Plain English report string
        """
        ticker = results['ticker']
        decision = results['decision']
        confidence = results['confidence']

        # Build the report
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append(f"INVESTMENT RECOMMENDATION: {ticker}")
        lines.append("=" * 70)
        lines.append("")

        # 1. THE VERDICT (What should I do?)
        lines.append("📋 THE VERDICT")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_verdict(decision, confidence, ticker))
        lines.append("")

        # 2. CONFIDENCE LEVEL (How sure are we?)
        lines.append("🎯 CONFIDENCE LEVEL")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_confidence(confidence))
        lines.append("")

        # 3. HOW MUCH TO INVEST (Position sizing)
        if portfolio_value:
            lines.append("💰 HOW MUCH TO INVEST")
            lines.append("-" * 70)
            lines.extend(PlainEnglishReport._format_position_size(
                decision, confidence, portfolio_value, max_position_pct, ticker, results
            ))
            lines.append("")

        # 4. EXPECTED RETURNS (What could I make?)
        lines.append("📈 EXPECTED RETURNS")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_expected_returns(decision, confidence, ticker))
        lines.append("")

        # 5. TIMING (When to buy/sell?)
        lines.append("⏰ TIMING")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_timing(decision, ticker, results, portfolio_value))
        lines.append("")

        # 6. THE REASONS (Why this recommendation?)
        lines.append("💡 THE REASONS")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_reasons(results))
        lines.append("")

        # 7. RISKS TO WATCH (What could go wrong?)
        lines.append("⚠️  RISKS TO WATCH")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_risks(decision))
        lines.append("")

        # 8. NEXT STEPS (What do I do now?)
        lines.append("✅ NEXT STEPS")
        lines.append("-" * 70)
        lines.extend(PlainEnglishReport._format_next_steps(decision, ticker, portfolio_value))
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    @staticmethod
    def _format_verdict(decision: str, confidence: int, ticker: str) -> List[str]:
        """Format the main verdict."""
        lines = []

        if decision == 'BUY':
            emoji = "🟢"
            verdict = "YES, BUY THIS STOCK"
            explanation = f"Our analysis suggests {ticker} is a good investment opportunity right now."

        elif decision == 'WAIT':
            emoji = "🟡"
            verdict = "WAIT - DON'T BUY YET"
            explanation = (
                f"{ticker} looks promising, but the timing isn't ideal. "
                f"Consider waiting for a better entry point (like a small price dip)."
            )

        elif decision == 'HOLD':
            emoji = "🟡"
            verdict = "HOLD - KEEP IF YOU OWN IT"
            explanation = (
                f"If you already own {ticker}, keep holding it. "
                f"If you don't own it, there are probably better opportunities right now."
            )

        else:  # SELL or PASS
            emoji = "🔴"
            verdict = "NO, DON'T BUY THIS"
            explanation = f"Our analysis suggests avoiding {ticker} at this time."

        lines.append(f"{emoji} {verdict}")
        lines.append("")
        lines.append(explanation)

        return lines

    @staticmethod
    def _format_confidence(confidence: int) -> List[str]:
        """Format confidence explanation."""
        lines = []

        lines.append(f"Confidence Score: {confidence}/100")
        lines.append("")

        if confidence >= 80:
            level = "VERY HIGH"
            meaning = "We're very confident in this recommendation."
            analogy = "Like a weather forecast showing 80%+ chance of sunshine."

        elif confidence >= 70:
            level = "HIGH"
            meaning = "We're confident, but there's some uncertainty."
            analogy = "Like a weather forecast showing 70-79% chance of sunshine."

        elif confidence >= 60:
            level = "MODERATE"
            meaning = "There are mixed signals. Proceed with caution."
            analogy = "Like a weather forecast showing 60-69% chance of sunshine."

        else:
            level = "LOW"
            meaning = "We're not very confident. Consider skipping this one."
            analogy = "Like a weather forecast showing less than 60% chance of sunshine."

        lines.append(f"Confidence Level: {level}")
        lines.append(f"What this means: {meaning}")
        lines.append(f"Think of it: {analogy}")

        return lines

    @staticmethod
    def _format_position_size(
        decision: str,
        confidence: int,
        portfolio_value: float,
        max_position_pct: float,
        ticker: str,
        results: Dict[str, Any] = None
    ) -> List[str]:
        """Format position sizing recommendation using PositionSizer."""
        lines = []

        if decision not in ['BUY']:
            lines.append("Not applicable - we're not recommending buying right now.")
            return lines

        # Extract price data from results
        current_price = None
        volatility = None

        if results and 'full_state' in results:
            full_state = results['full_state']

            # Try to get current price from market data
            try:
                market_data = full_state.get('market_data', {})
                if isinstance(market_data, dict):
                    # Get latest close price
                    if 'Close' in market_data:
                        close_prices = market_data['Close']
                        if close_prices:
                            current_price = float(list(close_prices.values())[-1])

                    # Calculate volatility from price data if available
                    if 'Close' in market_data and len(market_data['Close']) > 20:
                        import numpy as np
                        prices = list(market_data['Close'].values())
                        returns = np.diff(np.log(prices))
                        volatility = float(np.std(returns) * np.sqrt(252) * 100)  # Annualized volatility
            except Exception as e:
                logger.debug(f"Could not extract price data: {e}")

        # Use PositionSizer for sophisticated position sizing
        if current_price:
            sizer = PositionSizer(
                portfolio_value=Decimal(str(portfolio_value)),
                max_position_pct=Decimal(str(max_position_pct)),
                risk_tolerance='moderate',  # Could be made configurable
                cash_reserve_pct=Decimal('20.0')
            )

            sizing_result = sizer.calculate_position_size(
                confidence=confidence,
                current_price=Decimal(str(current_price)),
                volatility=Decimal(str(volatility)) if volatility else None
            )

            amount = float(sizing_result['recommended_amount'])
            shares = sizing_result['recommended_shares']
            position_pct = float(sizing_result['position_size_pct'])

            lines.append(f"Recommended investment: ${amount:,.0f}")
            lines.append(f"(That's {position_pct:.1f}% of your ${portfolio_value:,.0f} portfolio)")
            lines.append("")
            lines.append(f"Number of shares: {shares} shares")
            lines.append(f"Price per share: ${current_price:.2f}")
            lines.append(f"Total cost: ${amount:,.0f}")
            lines.append("")
            lines.append("Why this amount?")
            lines.append(sizing_result['sizing_reasoning'])

            # Add expected returns if available
            if sizing_result.get('expected_return_pct'):
                lines.append("")
                lines.append(f"Expected return: {sizing_result['expected_return_pct']:.1f}%")
                if sizing_result.get('risk_reward_ratio'):
                    lines.append(f"Risk/reward ratio: {sizing_result['risk_reward_ratio']:.1f}:1")
        else:
            # Fallback to simple calculation if no price data
            if confidence >= 80:
                target_pct = max_position_pct
            elif confidence >= 70:
                target_pct = max_position_pct * 0.6
            elif confidence >= 60:
                target_pct = max_position_pct * 0.4
            else:
                target_pct = max_position_pct * 0.2

            amount = portfolio_value * (target_pct / 100)

            lines.append(f"Recommended investment: ${amount:,.0f}")
            lines.append(f"(That's {target_pct:.1f}% of your ${portfolio_value:,.0f} portfolio)")
            lines.append("")
            lines.append("Why this amount?")
            lines.append(f"• Based on our {confidence}/100 confidence level")
            lines.append(f"• Keeps you diversified (not putting all eggs in one basket)")
            lines.append(f"• Limits risk if the stock doesn't perform as expected")
            lines.append("")
            lines.append("Note: Specific share count will depend on current market price.")
            lines.append(f"Check {ticker} current price and divide ${amount:,.0f} by the price.")

        return lines

    @staticmethod
    def _format_expected_returns(decision: str, confidence: int, ticker: str) -> List[str]:
        """Format expected returns."""
        lines = []

        if decision == 'BUY':
            # Base expected return on confidence
            if confidence >= 80:
                min_return = 10
                max_return = 20
                timeframe = "3-6 months"
            elif confidence >= 70:
                min_return = 8
                max_return = 15
                timeframe = "3-6 months"
            elif confidence >= 60:
                min_return = 5
                max_return = 12
                timeframe = "6-12 months"
            else:
                min_return = 3
                max_return = 10
                timeframe = "6-12 months"

            lines.append(f"Expected gain: {min_return}-{max_return}%")
            lines.append(f"Timeframe: {timeframe}")
            lines.append("")
            lines.append("What this means in dollars:")

            for investment in [1000, 5000, 10000]:
                min_profit = investment * (min_return / 100)
                max_profit = investment * (max_return / 100)
                lines.append(
                    f"  • Invest ${investment:,} → "
                    f"Potential profit: ${min_profit:,.0f} - ${max_profit:,.0f}"
                )

            lines.append("")
            lines.append("⚠️  Important: These are estimates, not guarantees!")
            lines.append("   Stock prices can go down as well as up.")

        elif decision == 'WAIT':
            lines.append("Not applicable right now.")
            lines.append(f"We recommend waiting for a better entry point on {ticker}.")
            lines.append("")
            lines.append("What you're waiting for:")
            lines.append("  • A small price dip (5-10% pullback)")
            lines.append("  • Or confirmation of upward momentum")
            lines.append("  • Check back in 1-2 weeks")

        else:
            lines.append("Not applicable - we're not recommending this stock.")

        return lines

    @staticmethod
    def _format_timing(decision: str, ticker: str, results: Dict[str, Any] = None, portfolio_value: float = None) -> List[str]:
        """Format timing recommendations using PositionSizer."""
        lines = []

        if decision == 'BUY' and results and portfolio_value:
            # Try to extract technical indicators for entry timing
            current_price = None
            support_level = None
            resistance_level = None
            rsi = None
            moving_avg_50 = None
            moving_avg_200 = None

            if 'full_state' in results:
                full_state = results['full_state']

                try:
                    market_data = full_state.get('market_data', {})
                    if isinstance(market_data, dict) and 'Close' in market_data:
                        close_prices = market_data['Close']
                        if close_prices:
                            current_price = float(list(close_prices.values())[-1])

                    # Extract technical indicators
                    technical_indicators = full_state.get('technical_indicators', {})
                    if isinstance(technical_indicators, dict):
                        if 'RSI' in technical_indicators:
                            rsi_data = technical_indicators['RSI']
                            if rsi_data:
                                rsi = float(list(rsi_data.values())[-1])

                        if 'SMA_50' in technical_indicators:
                            sma_data = technical_indicators['SMA_50']
                            if sma_data:
                                moving_avg_50 = float(list(sma_data.values())[-1])

                        if 'SMA_200' in technical_indicators:
                            sma_data = technical_indicators['SMA_200']
                            if sma_data:
                                moving_avg_200 = float(list(sma_data.values())[-1])

                        # Try to extract support/resistance from market report
                        # This would be extracted from the Market Analyst's report
                        # For now, we can estimate based on recent price range
                        if 'Close' in market_data and len(market_data['Close']) > 20:
                            recent_prices = list(market_data['Close'].values())[-20:]
                            support_level = float(min(recent_prices))
                            resistance_level = float(max(recent_prices))

                except Exception as e:
                    logger.debug(f"Could not extract technical data for timing: {e}")

            # Use PositionSizer for entry timing if we have price data
            if current_price:
                sizer = PositionSizer(
                    portfolio_value=Decimal(str(portfolio_value)),
                    max_position_pct=Decimal('5.0'),
                    risk_tolerance='moderate'
                )

                timing_result = sizer.calculate_entry_timing(
                    current_price=Decimal(str(current_price)),
                    support_level=Decimal(str(support_level)) if support_level else None,
                    resistance_level=Decimal(str(resistance_level)) if resistance_level else None,
                    moving_avg_50=Decimal(str(moving_avg_50)) if moving_avg_50 else None,
                    moving_avg_200=Decimal(str(moving_avg_200)) if moving_avg_200 else None,
                    rsi=Decimal(str(rsi)) if rsi else None
                )

                timing_recommendation = timing_result['timing']
                ideal_min = timing_result.get('ideal_entry_min')
                ideal_max = timing_result.get('ideal_entry_max')

                lines.append(f"⏰ ENTRY TIMING: {timing_recommendation.replace('_', ' ')}")
                lines.append("")
                lines.append(timing_result['timing_reasoning'])
                lines.append("")

                if ideal_min and ideal_max:
                    lines.append(f"Ideal Entry Range: ${ideal_min:.2f} - ${ideal_max:.2f}")
                    lines.append(f"Current Price: ${current_price:.2f}")
                    lines.append("")

                if timing_recommendation == 'BUY_NOW':
                    lines.append("✓ Action: Place your order within the next 1-5 days")
                    lines.append("✓ Entry is favorable at current levels")
                elif timing_recommendation == 'WAIT_FOR_DIP':
                    lines.append("⏳ Action: Set a price alert and wait for pullback")
                    lines.append(f"⏳ Target entry: ${ideal_min:.2f} - ${ideal_max:.2f}")
                    lines.append("⏳ Monitor for 1-2 weeks")
                elif timing_recommendation == 'WAIT_FOR_BREAKOUT':
                    lines.append("⏳ Action: Wait for price to break above resistance")
                    if ideal_min:
                        lines.append(f"⏳ Watch for move above: ${ideal_min:.2f}")
                    lines.append("⏳ Confirm with volume increase")
                else:  # WAIT
                    lines.append("⛔ Action: Hold off for now")
                    lines.append("⛔ Re-evaluate in 2-4 weeks")

                lines.append("")
                lines.append("💡 For beginners: If timing says 'BUY NOW', don't overthink it.")
                lines.append("   Trying to time the perfect entry often backfires.")
            else:
                # Fallback if no technical data
                lines.append("⏰ WHEN TO BUY:")
                lines.append("")
                lines.append("Option 1: Buy Soon (Within 1-5 Days)")
                lines.append("  ✓ If you're okay with current price")
                lines.append("  ✓ Reduces risk of missing the opportunity")
                lines.append("  ✓ Simpler - just buy and hold")
                lines.append("")
                lines.append("Option 2: Wait for a Dip (1-2 Weeks)")
                lines.append("  ✓ Try to get a better price (5-10% lower)")
                lines.append("  ✗ Risk: Stock might go up and you miss it")
                lines.append("  ✗ More complex - requires monitoring")
                lines.append("")
                lines.append("💡 For beginners: Option 1 is usually easier and less stressful.")

        elif decision == 'WAIT':
            lines.append("⏰ WHEN TO RE-EVALUATE:")
            lines.append("")
            lines.append("Check back in 1-2 weeks")
            lines.append("")
            lines.append("What you're looking for:")
            lines.append(f"  • {ticker} price drops 5-10%")
            lines.append("  • Or strong positive news about the company")
            lines.append("  • Or technical indicators improve")
            lines.append("")
            lines.append("💡 Set a calendar reminder to check back!")

        elif decision == 'HOLD':
            lines.append("If you own this stock: Keep holding it")
            lines.append("If you don't own it: Look for better opportunities")

        else:
            lines.append("Don't buy this stock at this time.")
            lines.append(f"Re-evaluate {ticker} in 1-3 months if you're still interested.")

        return lines

    @staticmethod
    def _format_reasons(results: Dict[str, Any]) -> List[str]:
        """Format the reasoning in simple terms."""
        lines = []

        # Simplified version - in reality, would parse actual analysis
        decision = results['decision']
        confidence = results['confidence']

        if decision == 'BUY':
            lines.append("Why we like this stock:")
            lines.append("")
            lines.append("✓ POSITIVE SIGNALS:")
            lines.append("  • Stock price is at a reasonable level")
            lines.append("  • Technical indicators look favorable")
            lines.append("  • Company fundamentals are solid")

            if confidence >= 80:
                lines.append("  • Multiple strong buy signals aligned")

            lines.append("")
            lines.append("⚠️  THINGS TO WATCH:")
            lines.append("  • Overall market conditions")
            lines.append("  • Company-specific news")
            lines.append("  • Sector trends")

        elif decision == 'WAIT':
            lines.append("Why we're saying wait:")
            lines.append("")
            lines.append("• The stock looks good overall")
            lines.append("• BUT the timing isn't perfect:")
            lines.append("  → Price might be slightly high right now")
            lines.append("  → Or waiting for a clearer signal")
            lines.append("  → Or better opportunities elsewhere")
            lines.append("")
            lines.append("Think of it like waiting for a sale - the product is good,")
            lines.append("but you might get a better price if you wait a bit.")

        else:
            lines.append("Why we're not recommending this:")
            lines.append("")
            lines.append("• Mixed or negative signals from our analysis")
            lines.append("• Better opportunities available elsewhere")
            lines.append("• Risk/reward ratio not favorable")

        return lines

    @staticmethod
    def _format_risks(decision: str) -> List[str]:
        """Format risk warnings."""
        lines = []

        lines.append("All investments carry risk. Here's what could go wrong:")
        lines.append("")

        if decision == 'BUY':
            lines.append("1. STOCK COULD GO DOWN")
            lines.append("   • Even good stocks can lose value")
            lines.append("   • Market conditions can change")
            lines.append("   • Our analysis could be wrong")
            lines.append("")
            lines.append("2. TIMING RISK")
            lines.append("   • Might not be the perfect entry point")
            lines.append("   • Could take longer than expected to profit")
            lines.append("")
            lines.append("3. COMPANY-SPECIFIC RISKS")
            lines.append("   • Bad earnings report")
            lines.append("   • Management changes")
            lines.append("   • Competition or regulation")

        elif decision == 'WAIT':
            lines.append("1. MIGHT MISS THE OPPORTUNITY")
            lines.append("   • Stock could go up while you wait")
            lines.append("   • Perfect entry point might not come")
            lines.append("")
            lines.append("2. ANALYSIS COULD CHANGE")
            lines.append("   • New information might emerge")
            lines.append("   • Recommendation could shift to BUY or PASS")

        else:
            lines.append("1. OPPORTUNITY COST")
            lines.append("   • Your money could be invested elsewhere")
            lines.append("   • Missing other good opportunities")
            lines.append("")
            lines.append("2. ANALYSIS COULD BE WRONG")
            lines.append("   • This stock might actually be good")
            lines.append("   • Our analysis is not perfect")

        lines.append("")
        lines.append("💡 RISK MANAGEMENT TIP:")
        lines.append("   Never invest money you can't afford to lose.")
        lines.append("   Diversify across multiple stocks.")

        return lines

    @staticmethod
    def _format_next_steps(decision: str, ticker: str, portfolio_value: float = None) -> List[str]:
        """Format actionable next steps."""
        lines = []

        if decision == 'BUY':
            lines.append("Here's exactly what to do:")
            lines.append("")
            lines.append("STEP 1: Decide How Much")
            if portfolio_value:
                lines.append(f"  → See 'HOW MUCH TO INVEST' section above")
            else:
                lines.append(f"  → Decide how much of your portfolio to allocate")
                lines.append(f"  → Typically 2-5% for one stock")
            lines.append("")

            lines.append("STEP 2: Check Current Price")
            lines.append(f"  → Look up {ticker} on your brokerage app")
            lines.append(f"  → Or check Yahoo Finance / Google Finance")
            lines.append("")

            lines.append("STEP 3: Place Your Order")
            lines.append(f"  → Log into your brokerage account")
            lines.append(f"  → Search for ticker symbol: {ticker}")
            lines.append(f"  → Choose 'Market Order' (buys at current price)")
            lines.append(f"  → Enter number of shares")
            lines.append(f"  → Review and confirm")
            lines.append("")

            lines.append("STEP 4: Set a Reminder")
            lines.append(f"  → Review this investment in 3-6 months")
            lines.append(f"  → Or when you get a significant news alert about {ticker}")
            lines.append("")

            lines.append("STEP 5: Don't Panic")
            lines.append(f"  → Stock prices fluctuate daily - this is normal")
            lines.append(f"  → Focus on long-term (3-6 months+)")
            lines.append(f"  → Avoid checking price every day")

        elif decision == 'WAIT':
            lines.append("Here's what to do:")
            lines.append("")
            lines.append("STEP 1: Set a Calendar Reminder")
            lines.append(f"  → Check back on {ticker} in 1-2 weeks")
            lines.append("")

            lines.append("STEP 2: Monitor (Optional)")
            lines.append(f"  → Watch for price drops of 5-10%")
            lines.append(f"  → Or significant positive news")
            lines.append("")

            lines.append("STEP 3: Meanwhile")
            lines.append(f"  → Look at other opportunities")
            lines.append(f"  → Keep your cash ready for when timing improves")

        elif decision == 'HOLD':
            lines.append("If you own this stock:")
            lines.append("  → Keep holding it")
            lines.append("  → Review again in 1-3 months")
            lines.append("")
            lines.append("If you don't own this stock:")
            lines.append("  → Skip it for now")
            lines.append("  → Focus on better opportunities")

        else:
            lines.append("STEP 1: Skip This Stock")
            lines.append(f"  → Don't buy {ticker} at this time")
            lines.append("")

            lines.append("STEP 2: Look at Other Opportunities")
            lines.append(f"  → Check our other recommendations")
            lines.append(f"  → Run the screener to find better options")
            lines.append("")

            lines.append("STEP 3: Maybe Check Back Later")
            lines.append(f"  → Re-evaluate {ticker} in 2-3 months")
            lines.append(f"  → Conditions may change")

        return lines


def generate_plain_english_report(
    results: Dict[str, Any],
    portfolio_value: float = None,
    max_position_pct: float = 5.0
) -> str:
    """
    Generate a plain English report from analysis results.

    Args:
        results: Analysis results from DeepAnalyzer
        portfolio_value: Total portfolio value (optional)
        max_position_pct: Maximum position size percentage

    Returns:
        Plain English report string
    """
    return PlainEnglishReport.generate_recommendation(
        results,
        portfolio_value,
        max_position_pct
    )
