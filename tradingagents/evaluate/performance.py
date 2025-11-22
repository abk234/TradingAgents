# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Performance Analyzer - Phase 6

Analyzes recommendation outcomes and generates performance reports.
Calculates win rates, average returns, and compares to benchmarks.
"""

from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import logging

from tradingagents.database import get_db_connection

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze performance of stock recommendations."""

    def __init__(self):
        """Initialize performance analyzer."""
        self.db = get_db_connection()

    def get_overall_stats(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Get overall recommendation performance statistics.

        Args:
            days_back: Look at recommendations from last N days

        Returns:
            Dictionary with performance metrics
        """
        query = """
            SELECT
                COUNT(*) as total_recommendations,
                COUNT(CASE WHEN decision = 'BUY' THEN 1 END) as buy_recs,
                COUNT(CASE WHEN decision = 'WAIT' THEN 1 END) as wait_recs,
                COUNT(CASE WHEN decision = 'SELL' THEN 1 END) as sell_recs,

                -- Win/Loss stats (for recommendations with 30-day data)
                COUNT(CASE WHEN return_30days_pct IS NOT NULL THEN 1 END) as evaluated_recs,
                COUNT(CASE WHEN was_correct = true THEN 1 END) as wins,
                COUNT(CASE WHEN was_correct = false THEN 1 END) as losses,
                ROUND(100.0 * COUNT(CASE WHEN was_correct = true THEN 1 END) /
                      NULLIF(COUNT(CASE WHEN return_30days_pct IS NOT NULL THEN 1 END), 0), 1) as win_rate_pct,

                -- Return statistics
                ROUND(AVG(return_30days_pct), 2) as avg_return_30days,
                ROUND(MAX(return_30days_pct), 2) as best_return_30days,
                ROUND(MIN(return_30days_pct), 2) as worst_return_30days,

                -- Peak/trough stats
                ROUND(AVG(peak_return_pct), 2) as avg_peak_return,
                ROUND(AVG(trough_return_pct), 2) as avg_trough_return,

                -- Benchmark comparison
                ROUND(AVG(sp500_return_30days_pct), 2) as avg_sp500_return_30days,
                ROUND(AVG(alpha_30days_pct), 2) as avg_alpha_30days,

                -- Quality distribution
                COUNT(CASE WHEN outcome_quality = 'EXCELLENT' THEN 1 END) as excellent_count,
                COUNT(CASE WHEN outcome_quality = 'GOOD' THEN 1 END) as good_count,
                COUNT(CASE WHEN outcome_quality = 'NEUTRAL' THEN 1 END) as neutral_count,
                COUNT(CASE WHEN outcome_quality = 'POOR' THEN 1 END) as poor_count,
                COUNT(CASE WHEN outcome_quality = 'FAILED' THEN 1 END) as failed_count

            FROM recommendation_outcomes
            WHERE recommendation_date >= CURRENT_DATE - INTERVAL '%s days'
        """

        result = self.db.execute_dict_query(query, (days_back,), fetch_one=True)
        return result if result else {}

    def get_performance_by_confidence(self, days_back: int = 90) -> List[Dict[str, Any]]:
        """
        Get win rate and returns grouped by confidence level.

        Args:
            days_back: Look at recommendations from last N days

        Returns:
            List of dictionaries with performance by confidence range
        """
        query = """
            SELECT
                CASE
                    WHEN confidence >= 90 THEN '90-100'
                    WHEN confidence >= 80 THEN '80-89'
                    WHEN confidence >= 70 THEN '70-79'
                    WHEN confidence >= 60 THEN '60-69'
                    ELSE '0-59'
                END as confidence_range,
                COUNT(*) as total_recs,
                COUNT(CASE WHEN was_correct THEN 1 END) as wins,
                COUNT(CASE WHEN was_correct = false THEN 1 END) as losses,
                ROUND(100.0 * COUNT(CASE WHEN was_correct THEN 1 END) /
                      NULLIF(COUNT(*), 0), 1) as win_rate_pct,
                ROUND(AVG(return_30days_pct), 2) as avg_return_30days,
                ROUND(AVG(alpha_30days_pct), 2) as avg_alpha
            FROM recommendation_outcomes
            WHERE recommendation_date >= CURRENT_DATE - INTERVAL '%s days'
            AND return_30days_pct IS NOT NULL
            GROUP BY confidence_range
            ORDER BY confidence_range DESC
        """

        return self.db.execute_dict_query(query, (days_back,))

    def get_top_performers(self, limit: int = 10, days_back: int = 90) -> List[Dict[str, Any]]:
        """
        Get top performing recommendations.

        Args:
            limit: Number of top performers to return
            days_back: Look at recommendations from last N days

        Returns:
            List of top performing stocks
        """
        query = """
            SELECT
                t.symbol,
                t.company_name,
                ro.recommendation_date,
                ro.confidence,
                ro.recommended_entry_price,
                ro.price_after_30days,
                ro.return_30days_pct,
                ro.peak_return_pct,
                ro.outcome_quality,
                ro.alpha_30days_pct
            FROM recommendation_outcomes ro
            JOIN tickers t ON ro.ticker_id = t.ticker_id
            WHERE ro.recommendation_date >= CURRENT_DATE - INTERVAL '%s days'
            AND ro.decision = 'BUY'
            AND ro.return_30days_pct IS NOT NULL
            ORDER BY ro.return_30days_pct DESC
            LIMIT %s
        """

        return self.db.execute_dict_query(query, (days_back, limit))

    def get_worst_performers(self, limit: int = 10, days_back: int = 90) -> List[Dict[str, Any]]:
        """
        Get worst performing recommendations.

        Args:
            limit: Number of worst performers to return
            days_back: Look at recommendations from last N days

        Returns:
            List of worst performing stocks
        """
        query = """
            SELECT
                t.symbol,
                t.company_name,
                ro.recommendation_date,
                ro.confidence,
                ro.recommended_entry_price,
                ro.price_after_30days,
                ro.return_30days_pct,
                ro.trough_return_pct,
                ro.outcome_quality,
                ro.alpha_30days_pct
            FROM recommendation_outcomes ro
            JOIN tickers t ON ro.ticker_id = t.ticker_id
            WHERE ro.recommendation_date >= CURRENT_DATE - INTERVAL '%s days'
            AND ro.decision = 'BUY'
            AND ro.return_30days_pct IS NOT NULL
            ORDER BY ro.return_30days_pct ASC
            LIMIT %s
        """

        return self.db.execute_dict_query(query, (days_back, limit))

    def get_recent_outcomes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent recommendation outcomes.

        Args:
            limit: Number of recent outcomes to return

        Returns:
            List of recent outcomes
        """
        query = """
            SELECT
                t.symbol,
                ro.recommendation_date,
                ro.decision,
                ro.confidence,
                ro.recommended_entry_price,
                ro.return_1day_pct,
                ro.return_7days_pct,
                ro.return_30days_pct,
                ro.outcome_quality,
                ro.was_correct,
                ro.evaluation_status
            FROM recommendation_outcomes ro
            JOIN tickers t ON ro.ticker_id = t.ticker_id
            ORDER BY ro.recommendation_date DESC
            LIMIT %s
        """

        return self.db.execute_dict_query(query, (limit,))

    def generate_report(self, days_back: int = 90) -> str:
        """
        Generate a comprehensive performance report.

        Args:
            days_back: Look at recommendations from last N days

        Returns:
            Formatted report string
        """
        stats = self.get_overall_stats(days_back)
        by_confidence = self.get_performance_by_confidence(days_back)
        top_performers = self.get_top_performers(limit=5, days_back=days_back)
        worst_performers = self.get_worst_performers(limit=5, days_back=days_back)

        report = []
        report.append("=" * 80)
        report.append(f"RECOMMENDATION PERFORMANCE REPORT (Last {days_back} Days)")
        report.append("=" * 80)
        report.append("")

        # Overall statistics
        report.append("📊 OVERALL STATISTICS")
        report.append("-" * 80)
        report.append(f"Total Recommendations:     {stats.get('total_recommendations', 0)}")
        report.append(f"  • BUY:  {stats.get('buy_recs', 0)}")
        report.append(f"  • WAIT: {stats.get('wait_recs', 0)}")
        report.append(f"  • SELL: {stats.get('sell_recs', 0)}")
        report.append("")

        evaluated = stats.get('evaluated_recs', 0)
        if evaluated > 0:
            report.append(f"Evaluated (30+ days old):  {evaluated}")
            report.append(f"  ✅ Wins:   {stats.get('wins', 0)} ({stats.get('win_rate_pct', 0)}%)")
            report.append(f"  ❌ Losses: {stats.get('losses', 0)}")
            report.append("")

            # Return statistics
            avg_return = stats.get('avg_return_30days', 0)
            avg_sp500 = stats.get('avg_sp500_return_30days', 0)
            avg_alpha = stats.get('avg_alpha_30days', 0)

            report.append(f"Average Return (30 days):  {avg_return:+.2f}%")
            report.append(f"  • Best:  {stats.get('best_return_30days', 0):+.2f}%")
            report.append(f"  • Worst: {stats.get('worst_return_30days', 0):+.2f}%")
            report.append("")

            if avg_sp500 is not None:
                report.append(f"📈 BENCHMARK COMPARISON")
                report.append("-" * 80)
                report.append(f"Your Avg Return:           {avg_return:+.2f}%")
                report.append(f"S&P 500 Avg Return:        {avg_sp500:+.2f}%")
                report.append(f"Alpha (Outperformance):    {avg_alpha:+.2f}%")
                report.append("")

                if avg_alpha > 0:
                    report.append(f"✅ You're beating the market by {avg_alpha:.2f}%!")
                else:
                    report.append(f"⚠️  You're underperforming the market by {abs(avg_alpha):.2f}%")
                report.append("")

            # Quality distribution
            total_quality = (stats.get('excellent_count', 0) + stats.get('good_count', 0) +
                           stats.get('neutral_count', 0) + stats.get('poor_count', 0) +
                           stats.get('failed_count', 0))

            if total_quality > 0:
                report.append(f"🎯 OUTCOME QUALITY")
                report.append("-" * 80)
                report.append(f"  ⭐⭐⭐ EXCELLENT: {stats.get('excellent_count', 0)} ({100 * stats.get('excellent_count', 0) / total_quality:.1f}%)")
                report.append(f"  ⭐⭐  GOOD:      {stats.get('good_count', 0)} ({100 * stats.get('good_count', 0) / total_quality:.1f}%)")
                report.append(f"  ⭐   NEUTRAL:   {stats.get('neutral_count', 0)} ({100 * stats.get('neutral_count', 0) / total_quality:.1f}%)")
                report.append(f"  ⚠️   POOR:      {stats.get('poor_count', 0)} ({100 * stats.get('poor_count', 0) / total_quality:.1f}%)")
                report.append(f"  ❌   FAILED:    {stats.get('failed_count', 0)} ({100 * stats.get('failed_count', 0) / total_quality:.1f}%)")
                report.append("")
        else:
            report.append("⏳ No recommendations old enough for evaluation yet (need 30+ days)")
            report.append("")

        # Performance by confidence level
        if by_confidence:
            report.append(f"📊 PERFORMANCE BY CONFIDENCE LEVEL")
            report.append("-" * 80)
            report.append(f"{'Confidence':<15} {'Count':<8} {'Win Rate':<12} {'Avg Return':<14} {'Alpha':<10}")
            report.append("-" * 80)

            for row in by_confidence:
                conf_range = row['confidence_range']
                total = row['total_recs']
                win_rate = row.get('win_rate_pct', 0) or 0
                avg_ret = row.get('avg_return_30days', 0) or 0
                alpha = row.get('avg_alpha', 0) or 0

                report.append(f"{conf_range:<15} {total:<8} {win_rate:.1f}%{'':<7} {avg_ret:+.2f}%{'':<8} {alpha:+.2f}%")

            report.append("")

        # Top performers
        if top_performers:
            report.append(f"🏆 TOP PERFORMERS (Best 5)")
            report.append("-" * 80)
            report.append(f"{'Symbol':<8} {'Date':<12} {'Conf':<6} {'Entry':<10} {'Return':<12} {'Alpha':<10} {'Quality'}")
            report.append("-" * 80)

            for p in top_performers:
                symbol = p['symbol']
                rec_date = p['recommendation_date'].strftime('%Y-%m-%d') if p['recommendation_date'] else 'N/A'
                conf = p['confidence']
                entry = f"${p['recommended_entry_price']:.2f}"
                ret = f"{p['return_30days_pct']:+.2f}%"
                alpha = f"{p.get('alpha_30days_pct', 0) or 0:+.2f}%"
                quality = p.get('outcome_quality', 'N/A')

                report.append(f"{symbol:<8} {rec_date:<12} {conf:<6} {entry:<10} {ret:<12} {alpha:<10} {quality}")

            report.append("")

        # Worst performers
        if worst_performers:
            report.append(f"⚠️  WORST PERFORMERS (Bottom 5)")
            report.append("-" * 80)
            report.append(f"{'Symbol':<8} {'Date':<12} {'Conf':<6} {'Entry':<10} {'Return':<12} {'Alpha':<10} {'Quality'}")
            report.append("-" * 80)

            for p in worst_performers:
                symbol = p['symbol']
                rec_date = p['recommendation_date'].strftime('%Y-%m-%d') if p['recommendation_date'] else 'N/A'
                conf = p['confidence']
                entry = f"${p['recommended_entry_price']:.2f}"
                ret = f"{p['return_30days_pct']:+.2f}%"
                alpha = f"{p.get('alpha_30days_pct', 0) or 0:+.2f}%"
                quality = p.get('outcome_quality', 'N/A')

                report.append(f"{symbol:<8} {rec_date:<12} {conf:<6} {entry:<10} {ret:<12} {alpha:<10} {quality}")

            report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def get_signal_performance(self, days_back: int = 90) -> List[Dict[str, Any]]:
        """
        Get performance of different technical signals.

        Args:
            days_back: Look at signals from last N days

        Returns:
            List of signal performance metrics
        """
        # This would require storing which signals triggered each recommendation
        # For now, return empty - can be implemented later
        return []
