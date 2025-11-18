"""
Price Alert System - Phase 7

Monitors stock prices and triggers alerts when they hit key levels:
- Entry price targets (ideal buy points)
- Target prices (take profit)
- Stop loss prices (exit to limit losses)
- RSI extremes (oversold/overbought)
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal
import logging

import yfinance as yf

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class PriceAlertSystem:
    """Monitor prices and generate alerts."""

    def __init__(self):
        """Initialize price alert system."""
        self.db = get_db_connection()

    def check_all_alerts(self) -> List[Dict[str, Any]]:
        """
        Check all active recommendations for price alerts.

        Returns:
            List of triggered alerts
        """
        alerts = []

        # Get active recommendations (less than 90 days old, not completed)
        active_recs = self._get_active_recommendations()

        logger.info(f"Checking alerts for {len(active_recs)} active recommendations...")

        for rec in active_recs:
            # Fetch current price
            current_price = self._get_current_price(rec['symbol'])

            if current_price is None:
                continue

            # Check for various alert conditions
            rec_alerts = self._check_recommendation_alerts(rec, current_price)
            alerts.extend(rec_alerts)

        # Check RSI-based alerts
        rsi_alerts = self._check_rsi_alerts()
        alerts.extend(rsi_alerts)

        logger.info(f"Found {len(alerts)} active alerts")
        return alerts

    def _get_active_recommendations(self) -> List[Dict[str, Any]]:
        """Get all active recommendations that need monitoring."""
        query = """
            SELECT
                ro.outcome_id,
                t.symbol,
                ro.recommendation_date,
                ro.decision,
                ro.confidence,
                ro.recommended_entry_price,
                ro.target_price,
                ro.stop_loss_price,
                a.entry_price_target,
                a.analysis_id
            FROM recommendation_outcomes ro
            JOIN tickers t ON ro.ticker_id = t.ticker_id
            JOIN analyses a ON ro.analysis_id = a.analysis_id
            WHERE ro.recommendation_date >= CURRENT_DATE - INTERVAL '90 days'
            AND ro.evaluation_status IN ('PENDING', 'TRACKING')
            AND ro.decision IN ('BUY', 'STRONG_BUY')
            ORDER BY ro.recommendation_date DESC
        """

        return self.db.execute_dict_query(query) or []

    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current price for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.debug(f"Could not fetch price for {symbol}: {e}")

        return None

    def _check_recommendation_alerts(
        self, rec: Dict[str, Any], current_price: float
    ) -> List[Dict[str, Any]]:
        """Check if a recommendation has triggered any alerts."""
        alerts = []
        symbol = rec['symbol']
        entry_price = float(rec['recommended_entry_price'])

        # Alert 1: Hit target price (take profit)
        if rec.get('target_price'):
            target = float(rec['target_price'])
            if current_price >= target:
                gain_pct = ((current_price - entry_price) / entry_price) * 100
                alerts.append({
                    'type': 'TARGET_HIT',
                    'priority': 'HIGH',
                    'symbol': symbol,
                    'message': f'🎯 Target price ${target:.2f} reached! Current: ${current_price:.2f} (+{gain_pct:.1f}%)',
                    'action': 'Consider taking profits',
                    'current_price': current_price,
                    'trigger_price': target
                })

        # Alert 2: Hit stop loss (limit losses)
        if rec.get('stop_loss_price'):
            stop_loss = float(rec['stop_loss_price'])
            if current_price <= stop_loss:
                loss_pct = ((current_price - entry_price) / entry_price) * 100
                alerts.append({
                    'type': 'STOP_LOSS_HIT',
                    'priority': 'URGENT',
                    'symbol': symbol,
                    'message': f'🛑 Stop loss ${stop_loss:.2f} triggered! Current: ${current_price:.2f} ({loss_pct:.1f}%)',
                    'action': 'Exit position to limit losses',
                    'current_price': current_price,
                    'trigger_price': stop_loss
                })

        # Alert 3: Near entry price (good buy opportunity)
        if rec.get('entry_price_target'):
            ideal_entry = float(rec['entry_price_target'])
            # Alert if within 2% of ideal entry
            if abs(current_price - ideal_entry) / ideal_entry < 0.02:
                alerts.append({
                    'type': 'ENTRY_OPPORTUNITY',
                    'priority': 'MEDIUM',
                    'symbol': symbol,
                    'message': f'💰 Near ideal entry ${ideal_entry:.2f}! Current: ${current_price:.2f}',
                    'action': 'Good time to enter position',
                    'current_price': current_price,
                    'trigger_price': ideal_entry
                })

        # Alert 4: Significant move since recommendation
        price_change_pct = ((current_price - entry_price) / entry_price) * 100

        if price_change_pct >= 10:
            alerts.append({
                'type': 'SIGNIFICANT_GAIN',
                'priority': 'MEDIUM',
                'symbol': symbol,
                'message': f'📈 Up {price_change_pct:.1f}% since recommendation! Current: ${current_price:.2f}',
                'action': 'Review position - consider partial profit taking',
                'current_price': current_price,
                'trigger_price': entry_price
            })
        elif price_change_pct <= -8:
            alerts.append({
                'type': 'SIGNIFICANT_LOSS',
                'priority': 'HIGH',
                'symbol': symbol,
                'message': f'⚠️  Down {price_change_pct:.1f}% since recommendation. Current: ${current_price:.2f}',
                'action': 'Review thesis - consider cutting losses',
                'current_price': current_price,
                'trigger_price': entry_price
            })

        return alerts

    def _check_rsi_alerts(self) -> List[Dict[str, Any]]:
        """Check for RSI-based alerts from recent scans."""
        alerts = []

        # Get stocks with extreme RSI from today's scan
        query = """
            SELECT
                t.symbol,
                (ds.technical_signals->>'rsi')::float as rsi,
                ds.price as current_price,
                ds.scan_date
            FROM daily_scans ds
            JOIN tickers t ON ds.ticker_id = t.ticker_id
            WHERE ds.scan_date >= CURRENT_DATE - INTERVAL '1 day'
            AND (ds.technical_signals->>'rsi')::float IS NOT NULL
            AND ((ds.technical_signals->>'rsi')::float < 25 OR (ds.technical_signals->>'rsi')::float > 75)
            ORDER BY
                CASE
                    WHEN (ds.technical_signals->>'rsi')::float < 25 THEN (ds.technical_signals->>'rsi')::float
                    ELSE 100 - (ds.technical_signals->>'rsi')::float
                END ASC
            LIMIT 10
        """

        results = self.db.execute_dict_query(query) or []

        for row in results:
            symbol = row['symbol']
            rsi = row['rsi']
            price = row['current_price']

            if rsi < 25:
                alerts.append({
                    'type': 'RSI_OVERSOLD',
                    'priority': 'MEDIUM',
                    'symbol': symbol,
                    'message': f'🔵 Deeply oversold! RSI: {rsi:.1f}, Price: ${price:.2f}',
                    'action': 'Strong buy signal - investigate fundamentals',
                    'current_price': price,
                    'trigger_price': None
                })
            elif rsi > 75:
                alerts.append({
                    'type': 'RSI_OVERBOUGHT',
                    'priority': 'MEDIUM',
                    'symbol': symbol,
                    'message': f'🔴 Extremely overbought! RSI: {rsi:.1f}, Price: ${price:.2f}',
                    'action': 'Consider taking profits or waiting for pullback',
                    'current_price': price,
                    'trigger_price': None
                })

        return alerts

    def format_alerts(self, alerts: List[Dict[str, Any]]) -> str:
        """Format alerts into a readable report."""
        if not alerts:
            return "✅ No active alerts at this time."

        report = []
        report.append("=" * 80)
        report.append(f"🚨 PRICE ALERTS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # Group by priority
        urgent = [a for a in alerts if a.get('priority') == 'URGENT']
        high = [a for a in alerts if a.get('priority') == 'HIGH']
        medium = [a for a in alerts if a.get('priority') == 'MEDIUM']

        if urgent:
            report.append("🔴 URGENT ALERTS")
            report.append("-" * 80)
            for alert in urgent:
                report.append(f"• {alert['symbol']}: {alert['message']}")
                report.append(f"  → Action: {alert['action']}")
                report.append("")

        if high:
            report.append("🟡 HIGH PRIORITY ALERTS")
            report.append("-" * 80)
            for alert in high:
                report.append(f"• {alert['symbol']}: {alert['message']}")
                report.append(f"  → Action: {alert['action']}")
                report.append("")

        if medium:
            report.append("🟢 MEDIUM PRIORITY ALERTS")
            report.append("-" * 80)
            for alert in medium:
                report.append(f"• {alert['symbol']}: {alert['message']}")
                report.append(f"  → Action: {alert['action']}")
                report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def get_alert_summary(self) -> str:
        """Get a one-line summary of current alerts."""
        alerts = self.check_all_alerts()

        if not alerts:
            return "No alerts"

        urgent = len([a for a in alerts if a.get('priority') == 'URGENT'])
        high = len([a for a in alerts if a.get('priority') == 'HIGH'])
        total = len(alerts)

        summary_parts = []
        if urgent > 0:
            summary_parts.append(f"{urgent} urgent")
        if high > 0:
            summary_parts.append(f"{high} high priority")
        if total > urgent + high:
            summary_parts.append(f"{total - urgent - high} medium")

        return " | ".join(summary_parts) if summary_parts else f"{total} alerts"
