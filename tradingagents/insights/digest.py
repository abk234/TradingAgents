# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Daily Market Digest - Phase 7

Generates automated morning reports with:
- Top opportunities from screener
- Recent analyses and recommendations
- Portfolio updates (if available)
- Important alerts and notifications
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class MarketDigest:
    """Generate daily market digest reports."""

    def __init__(self):
        """Initialize market digest generator."""
        self.db = get_db_connection()

    def generate_digest(self, target_date: Optional[date] = None) -> str:
        """
        Generate comprehensive daily market digest.

        Args:
            target_date: Date for the digest (default: today)

        Returns:
            Formatted digest report string
        """
        if target_date is None:
            target_date = date.today()

        digest = []
        digest.append("=" * 80)
        digest.append(f"📊 DAILY MARKET DIGEST - {target_date.strftime('%A, %B %d, %Y')}")
        digest.append("=" * 80)
        digest.append("")

        # Section 1: Top Opportunities
        top_opps = self._get_top_opportunities(target_date)
        if top_opps:
            digest.append("🔥 TOP OPPORTUNITIES")
            digest.append("-" * 80)
            for i, opp in enumerate(top_opps[:5], 1):
                digest.append(f"{i}. {opp['symbol']} - {opp['decision']} (Confidence: {opp['confidence']}/100)")
                if opp.get('position_amount'):
                    digest.append(f"   💰 Recommended: ${opp['position_amount']:,.0f} ({opp['position_pct']:.1f}% of portfolio)")
                if opp.get('timing'):
                    digest.append(f"   ⏰ Timing: {opp['timing']}")
                digest.append(f"   📊 Priority Score: {opp['priority_score']}")
                if opp.get('entry_price'):
                    digest.append(f"   💵 Entry: ${opp['entry_price']:.2f}")
                if opp.get('target_price'):
                    digest.append(f"   🎯 Target: ${opp['target_price']:.2f} (+{opp.get('expected_return', 0):.1f}%)")
                digest.append("")
        else:
            digest.append("🔥 TOP OPPORTUNITIES")
            digest.append("-" * 80)
            digest.append("No new analyses today. Run screener to find opportunities!")
            digest.append("")

        # Section 2: Recent Performance
        recent_perf = self._get_recent_performance()
        if recent_perf and recent_perf.get('count', 0) > 0:
            digest.append("📈 RECENT PERFORMANCE")
            digest.append("-" * 80)
            digest.append(f"Active Recommendations: {recent_perf['count']}")
            if recent_perf.get('avg_return_7d') is not None:
                digest.append(f"Avg 7-day Return: {recent_perf['avg_return_7d']:+.2f}%")
            if recent_perf.get('winners'):
                digest.append(f"Winners (7d): {recent_perf['winners']}")
            if recent_perf.get('losers'):
                digest.append(f"Losers (7d): {recent_perf['losers']}")
            digest.append("")

        # Section 3: Alerts & Warnings
        alerts = self._get_alerts(target_date)
        if alerts:
            digest.append("⚠️  ALERTS & NOTIFICATIONS")
            digest.append("-" * 80)
            for alert in alerts:
                digest.append(f"• {alert['type']}: {alert['symbol']} - {alert['message']}")
            digest.append("")

        # Section 4: Market Scans
        scan_summary = self._get_scan_summary(target_date)
        if scan_summary:
            digest.append("📊 MARKET SCAN SUMMARY")
            digest.append("-" * 80)
            digest.append(f"Tickers Scanned: {scan_summary['total_scanned']}")
            digest.append(f"Average Score: {scan_summary['avg_score']:.1f}")
            if scan_summary.get('oversold_count'):
                digest.append(f"Oversold Stocks (RSI < 30): {scan_summary['oversold_count']}")
            if scan_summary.get('overbought_count'):
                digest.append(f"Overbought Stocks (RSI > 70): {scan_summary['overbought_count']}")
            digest.append("")

        # Section 5: Upcoming Events
        events = self._get_upcoming_events()
        if events:
            digest.append("📅 UPCOMING EVENTS")
            digest.append("-" * 80)
            for event in events:
                digest.append(f"• {event['date']}: {event['symbol']} - {event['event']}")
            digest.append("")

        digest.append("=" * 80)
        digest.append("💡 TIP: Run './scripts/run_daily_analysis.sh' to get fresh recommendations!")
        digest.append("=" * 80)

        return "\n".join(digest)

    def _get_top_opportunities(self, target_date: date) -> List[Dict[str, Any]]:
        """Get top opportunities from recent analyses."""
        query = """
            SELECT
                t.symbol,
                a.final_decision as decision,
                a.confidence_score as confidence,
                a.entry_price_target as entry_price,
                a.stop_loss_price,
                a.expected_return_pct as expected_return,
                pr.recommended_amount as position_amount,
                pr.position_size_pct as position_pct,
                pr.target_price,
                ds.priority_score,
                a.analysis_date
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            LEFT JOIN position_recommendations pr ON a.analysis_id = pr.analysis_id
            LEFT JOIN daily_scans ds ON t.ticker_id = ds.ticker_id
                AND DATE(a.analysis_date) = ds.scan_date
            WHERE DATE(a.analysis_date) >= %s - INTERVAL '7 days'
            AND a.final_decision IN ('BUY', 'STRONG_BUY')
            ORDER BY a.confidence_score DESC, ds.priority_score DESC
            LIMIT 10
        """

        results = self.db.execute_dict_query(query, (target_date,))

        # Add timing info (simplified for now)
        for result in results or []:
            # You could add more sophisticated timing logic here
            result['timing'] = "Review entry conditions"

        return results or []

    def _get_recent_performance(self) -> Dict[str, Any]:
        """Get performance of recent recommendations."""
        query = """
            SELECT
                COUNT(*) as count,
                AVG(return_7days_pct) as avg_return_7d,
                COUNT(CASE WHEN return_7days_pct > 0 THEN 1 END) as winners,
                COUNT(CASE WHEN return_7days_pct < 0 THEN 1 END) as losers
            FROM recommendation_outcomes
            WHERE recommendation_date >= CURRENT_DATE - INTERVAL '30 days'
            AND return_7days_pct IS NOT NULL
        """

        return self.db.execute_dict_query(query, fetch_one=True) or {}

    def _get_alerts(self, target_date: date) -> List[Dict[str, str]]:
        """Get important alerts and notifications."""
        alerts = []

        # Alert 1: Stocks hitting oversold (from today's scan)
        oversold_query = """
            SELECT t.symbol, (ds.technical_signals->>'rsi')::float as rsi
            FROM daily_scans ds
            JOIN tickers t ON ds.ticker_id = t.ticker_id
            WHERE ds.scan_date = %s
            AND (ds.technical_signals->>'rsi')::float < 30
            ORDER BY (ds.technical_signals->>'rsi')::float ASC
            LIMIT 5
        """
        oversold = self.db.execute_dict_query(oversold_query, (target_date,))

        for stock in oversold or []:
            alerts.append({
                'type': 'OVERSOLD',
                'symbol': stock['symbol'],
                'message': f"RSI {stock['rsi']:.1f} - Potential buying opportunity"
            })

        # Alert 2: Stocks hitting overbought
        overbought_query = """
            SELECT t.symbol, (ds.technical_signals->>'rsi')::float as rsi
            FROM daily_scans ds
            JOIN tickers t ON ds.ticker_id = t.ticker_id
            WHERE ds.scan_date = %s
            AND (ds.technical_signals->>'rsi')::float > 70
            ORDER BY (ds.technical_signals->>'rsi')::float DESC
            LIMIT 5
        """
        overbought = self.db.execute_dict_query(overbought_query, (target_date,))

        for stock in overbought or []:
            alerts.append({
                'type': 'OVERBOUGHT',
                'symbol': stock['symbol'],
                'message': f"RSI {stock['rsi']:.1f} - Consider taking profits"
            })

        return alerts

    def _get_scan_summary(self, target_date: date) -> Optional[Dict[str, Any]]:
        """Get summary of today's market scan."""
        query = """
            SELECT
                COUNT(*) as total_scanned,
                AVG(priority_score) as avg_score,
                COUNT(CASE WHEN (technical_signals->>'rsi')::float < 30 THEN 1 END) as oversold_count,
                COUNT(CASE WHEN (technical_signals->>'rsi')::float > 70 THEN 1 END) as overbought_count
            FROM daily_scans
            WHERE scan_date = %s
        """

        result = self.db.execute_dict_query(query, (target_date,), fetch_one=True)
        return result if result and result.get('total_scanned', 0) > 0 else None

    def _get_upcoming_events(self) -> List[Dict[str, str]]:
        """Get upcoming events (earnings, dividends, etc.)."""
        # Placeholder for future enhancement
        # Could integrate with earnings calendar API
        return []

    def generate_quick_summary(self) -> str:
        """Generate a quick 1-paragraph summary for notifications."""
        today = date.today()
        top_opps = self._get_top_opportunities(today)
        scan_summary = self._get_scan_summary(today)

        summary_parts = []

        if scan_summary:
            summary_parts.append(f"📊 Scanned {scan_summary['total_scanned']} stocks")

        if top_opps:
            summary_parts.append(f"🔥 Top pick: {top_opps[0]['symbol']} (confidence {top_opps[0]['confidence']}/100)")

        if scan_summary and scan_summary.get('oversold_count', 0) > 0:
            summary_parts.append(f"⚠️  {scan_summary['oversold_count']} oversold opportunities")

        if summary_parts:
            return " | ".join(summary_parts)
        else:
            return "No new market data today. Run screener for updates!"
