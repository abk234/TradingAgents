# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Prompt Formatter Module

Formats historical context for injection into LLM prompts.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PromptFormatter:
    """Format context for LLM prompts."""

    @staticmethod
    def format_analysis_context(
        context: Dict[str, Any],
        include_section: str = "all"
    ) -> str:
        """
        Format historical context for analysis prompts.

        Args:
            context: Context dictionary
            include_section: Which sections to include ("all", "ticker", "similar", "sector")

        Returns:
            Formatted context string
        """
        sections = []

        # Header
        symbol = context.get('symbol', 'Unknown')
        sections.append(f"\n{'='*70}")
        sections.append(f"HISTORICAL INTELLIGENCE FOR {symbol}")
        sections.append(f"{'='*70}\n")

        # Ticker history section
        if include_section in ["all", "ticker"]:
            ticker_section = PromptFormatter._format_ticker_history(context)
            if ticker_section:
                sections.append(ticker_section)

        # Similar situations section
        if include_section in ["all", "similar"]:
            similar_section = PromptFormatter._format_similar_situations(context)
            if similar_section:
                sections.append(similar_section)

        # Cross-ticker patterns
        if include_section in ["all", "cross"]:
            cross_section = PromptFormatter._format_cross_ticker(context)
            if cross_section:
                sections.append(cross_section)

        # Sector context
        if include_section in ["all", "sector"]:
            sector_section = PromptFormatter._format_sector_context(context)
            if sector_section:
                sections.append(sector_section)

        # Footer
        sections.append(f"\n{'='*70}")
        sections.append("END HISTORICAL INTELLIGENCE")
        sections.append(f"{'='*70}\n")

        return "\n".join(sections)

    @staticmethod
    def _format_ticker_history(context: Dict[str, Any]) -> str:
        """Format ticker's own analysis history."""
        history = context.get('ticker_history', [])
        last = context.get('last_analysis')

        if not history and not last:
            return ""

        lines = ["\n## TICKER ANALYSIS HISTORY\n"]

        if last:
            lines.append(f"**Most Recent Analysis**: {last['date']}")
            lines.append(f"  - Decision: **{last['decision']}**")
            lines.append(f"  - Confidence: {last['confidence']}/100")
            lines.append(f"  - Price: ${last['price']:.2f}")
            lines.append("")

        if len(history) > 1:
            lines.append(f"**Past {min(len(history)-1, 4)} Analyses**:")
            for analysis in history[1:5]:  # Skip first (already shown)
                date_str = str(analysis.get('analysis_date', 'Unknown'))
                decision = analysis.get('final_decision', 'N/A')
                conf = analysis.get('confidence_score', 0)
                lines.append(f"  - {date_str}: {decision} (confidence: {conf}/100)")

        return "\n".join(lines)

    @staticmethod
    def _format_similar_situations(context: Dict[str, Any]) -> str:
        """Format similar past situations."""
        similar = context.get('similar_situations', [])

        if not similar:
            return "\n## SIMILAR PAST SITUATIONS\nNo similar past analyses found in database. This is normal for new databases or when analyzing stocks for the first time.\n"

        lines = ["\n## SIMILAR PAST SITUATIONS\n"]
        lines.append(f"We've found {len(similar)} similar past situation(s):\n")

        for i, situation in enumerate(similar[:3], 1):
            similarity = situation.get('similarity', 0)
            date_str = str(situation.get('analysis_date', 'Unknown'))
            decision = situation.get('final_decision', 'N/A')
            conf = situation.get('confidence_score', 0)

            lines.append(f"**{i}. {date_str}** (Similarity: {similarity:.1%})")
            lines.append(f"  - Decision: **{decision}** (Confidence: {conf}/100)")

            if situation.get('executive_summary'):
                summary = situation['executive_summary']
                # Truncate if too long
                if len(summary) > 200:
                    summary = summary[:197] + "..."
                lines.append(f"  - Summary: {summary}")

            if situation.get('expected_return_pct'):
                lines.append(f"  - Expected Return: {situation['expected_return_pct']:.1f}%")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_cross_ticker(context: Dict[str, Any]) -> str:
        """Format cross-ticker patterns."""
        cross = context.get('cross_ticker_patterns', [])

        if not cross:
            return ""

        lines = ["\n## SIMILAR PATTERNS IN OTHER STOCKS\n"]
        lines.append("Similar setups observed in:\n")

        for i, pattern in enumerate(cross[:3], 1):
            symbol = pattern.get('symbol', 'Unknown')
            sector = pattern.get('sector', 'Unknown')
            similarity = pattern.get('similarity', 0)
            decision = pattern.get('final_decision', 'N/A')

            lines.append(f"**{i}. {symbol}** ({sector}) - Similarity: {similarity:.1%}")
            lines.append(f"  - Decision: {decision}")

            if pattern.get('executive_summary'):
                summary = pattern['executive_summary'][:150]
                lines.append(f"  - Context: {summary}...")

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_sector_context(context: Dict[str, Any]) -> str:
        """Format sector analysis context."""
        sector_ctx = context.get('sector_context')

        if not sector_ctx or sector_ctx.get('total_analyses', 0) == 0:
            return ""

        lines = [f"\n## SECTOR ANALYSIS: {sector_ctx['sector']}\n"]

        total = sector_ctx['total_analyses']
        buys = sector_ctx['buy_signals']
        buy_rate = sector_ctx['buy_signal_rate']
        avg_conf = sector_ctx['average_confidence']

        lines.append(f"Recent sector activity (last 30 days):")
        lines.append(f"  - Total analyses: {total}")
        lines.append(f"  - Buy signals: {buys} ({buy_rate:.1%} of analyses)")
        lines.append(f"  - Average confidence: {avg_conf:.1f}/100")

        recent = sector_ctx.get('recent_analyses', [])
        if recent:
            lines.append(f"\n  Recent {sector_ctx['sector']} decisions:")
            for analysis in recent[:3]:
                symbol = analysis.get('symbol', 'Unknown')
                decision = analysis.get('final_decision', 'N/A')
                lines.append(f"    - {symbol}: {decision}")

        return "\n".join(lines)

    @staticmethod
    def format_buy_decision_context(
        context: Dict[str, Any],
        current_price: float,
        pattern_matched: str = None
    ) -> str:
        """
        Format context specifically for buy decision evaluation.

        Args:
            context: Historical context
            current_price: Current stock price
            pattern_matched: Identified pattern (optional)

        Returns:
            Formatted context for buy decision
        """
        lines = []

        lines.append("\n" + "="*70)
        lines.append("BUY DECISION EVALUATION - HISTORICAL CONTEXT")
        lines.append("="*70 + "\n")

        # Current vs historical price comparison
        last = context.get('last_analysis')
        if last and last.get('price'):
            last_price = last['price']
            price_change = ((current_price - last_price) / last_price) * 100
            direction = "up" if price_change > 0 else "down"

            lines.append(f"**Price Comparison**:")
            lines.append(f"  - Current: ${current_price:.2f}")
            lines.append(f"  - Last Analysis: ${last_price:.2f}")
            lines.append(f"  - Change: {abs(price_change):.1f}% {direction}")
            lines.append("")

        # Pattern matching
        if pattern_matched:
            lines.append(f"**Pattern Identified**: {pattern_matched}\n")

        # Historical success of similar setups
        similar = context.get('similar_situations', [])
        if similar:
            successful = sum(1 for s in similar if s.get('final_decision') == 'BUY')
            success_rate = successful / len(similar) if similar else 0

            lines.append(f"**Similar Setup History**:")
            lines.append(f"  - Found {len(similar)} similar situations")
            lines.append(f"  - Buy signals: {successful} ({success_rate:.1%})")
            lines.append("")

        # Sector momentum
        sector_ctx = context.get('sector_context')
        if sector_ctx and sector_ctx.get('total_analyses', 0) > 0:
            buy_rate = sector_ctx['buy_signal_rate']

            lines.append(f"**Sector Momentum** ({sector_ctx['sector']}):")

            if buy_rate > 0.5:
                lines.append(f"  - ✓ Strong: {buy_rate:.1%} buy signal rate (bullish sector)")
            elif buy_rate > 0.3:
                lines.append(f"  - ≈ Moderate: {buy_rate:.1%} buy signal rate")
            else:
                lines.append(f"  - ✗ Weak: {buy_rate:.1%} buy signal rate (cautious)")

            lines.append("")

        lines.append("="*70)

        return "\n".join(lines)

    @staticmethod
    def format_for_agent(
        agent_type: str,
        context: Dict[str, Any],
        focus_areas: List[str] = None
    ) -> str:
        """
        Format context for specific agent types.

        Args:
            agent_type: Type of agent ("bull", "bear", "risk", "trader")
            context: Historical context
            focus_areas: Specific areas to emphasize

        Returns:
            Agent-specific formatted context
        """
        if agent_type == "bull":
            return PromptFormatter._format_for_bull(context, focus_areas)
        elif agent_type == "bear":
            return PromptFormatter._format_for_bear(context, focus_areas)
        elif agent_type == "risk":
            return PromptFormatter._format_for_risk(context, focus_areas)
        elif agent_type == "trader":
            return PromptFormatter._format_for_trader(context, focus_areas)
        else:
            return PromptFormatter.format_analysis_context(context)

    @staticmethod
    def _format_for_bull(context: Dict[str, Any], focus_areas: List[str]) -> str:
        """Format context emphasizing bullish opportunities."""
        lines = ["\n## BULLISH HISTORICAL CONTEXT\n"]

        # Highlight successful buy signals
        similar = context.get('similar_situations', [])
        successful_buys = [s for s in similar if s.get('final_decision') == 'BUY']

        if successful_buys:
            lines.append("**Past Successful Buy Signals**:")
            for buy in successful_buys[:2]:
                lines.append(f"  - {buy.get('analysis_date')}: Bought with {buy.get('confidence_score')}/100 confidence")

        return "\n".join(lines)

    @staticmethod
    def _format_for_bear(context: Dict[str, Any], focus_areas: List[str]) -> str:
        """Format context emphasizing risks and cautions."""
        lines = ["\n## BEARISH HISTORICAL CONTEXT\n"]

        # Highlight failed signals or cautious decisions
        similar = context.get('similar_situations', [])
        cautious = [s for s in similar if s.get('final_decision') in ['WAIT', 'PASS']]

        if cautious:
            lines.append("**Past Cautious Decisions**:")
            for caution in cautious[:2]:
                lines.append(f"  - {caution.get('analysis_date')}: {caution.get('final_decision')}")
                if caution.get('risk_factors'):
                    risks = ', '.join(caution['risk_factors'][:2])
                    lines.append(f"    Risks noted: {risks}")

        return "\n".join(lines)

    @staticmethod
    def _format_for_risk(context: Dict[str, Any], focus_areas: List[str]) -> str:
        """Format context emphasizing risk factors."""
        lines = ["\n## RISK MANAGEMENT HISTORICAL CONTEXT\n"]

        # Aggregate risk factors from similar situations
        similar = context.get('similar_situations', [])
        all_risks = []

        for situation in similar:
            if situation.get('risk_factors'):
                all_risks.extend(situation['risk_factors'])

        if all_risks:
            # Count frequency
            from collections import Counter
            risk_counts = Counter(all_risks)

            lines.append("**Common Risk Factors in Similar Situations**:")
            for risk, count in risk_counts.most_common(5):
                lines.append(f"  - {risk} (appeared {count} time(s))")

        return "\n".join(lines)

    @staticmethod
    def _format_for_trader(context: Dict[str, Any], focus_areas: List[str]) -> str:
        """Format context for trading execution."""
        lines = ["\n## TRADING EXECUTION HISTORICAL CONTEXT\n"]

        # Focus on entry points and timing
        similar = context.get('similar_situations', [])

        if similar:
            lines.append("**Historical Entry Points**:")
            for situation in similar[:3]:
                price = situation.get('price_at_analysis')
                decision = situation.get('final_decision')
                if price and decision:
                    lines.append(f"  - Entry at ${price:.2f}: {decision}")

        return "\n".join(lines)
