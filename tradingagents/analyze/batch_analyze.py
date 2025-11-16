"""
Batch Analysis Tool

Automatically analyzes top N opportunities from the daily screener.
Connects screener → deep analysis → results storage.

Usage:
    # Analyze top 5 from today's scan
    python -m tradingagents.analyze.batch_analyze --top 5

    # Analyze top 10 with minimum priority score
    python -m tradingagents.analyze.batch_analyze --top 10 --min-score 70

    # Analyze all with BUY-related alerts
    python -m tradingagents.analyze.batch_analyze --alerts MACD_BULLISH_CROSS,RSI_OVERSOLD
"""

import argparse
import sys
import logging
from datetime import date
from typing import List, Dict, Any, Optional

from tradingagents.database import get_db_connection, ScanOperations
from tradingagents.analyze import DeepAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchAnalyzer:
    """Automated batch analysis of screener opportunities."""

    def __init__(self, enable_rag: bool = True, debug: bool = False):
        """
        Initialize batch analyzer.

        Args:
            enable_rag: Whether to enable RAG
            debug: Debug mode
        """
        self.db = get_db_connection()
        self.scan_ops = ScanOperations(self.db)
        self.analyzer = DeepAnalyzer(enable_rag=enable_rag, db=self.db, debug=debug)
        self.enable_rag = enable_rag

    def get_top_opportunities(
        self,
        scan_date: date,
        top_n: int = 5,
        min_score: float = 0,
        required_alerts: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top opportunities from daily scan.

        Args:
            scan_date: Date of scan
            top_n: Number of top results to return
            min_score: Minimum priority score
            required_alerts: List of required alerts (any match)

        Returns:
            List of opportunity dictionaries
        """
        # Get scan results
        results = self.scan_ops.get_scan_results(scan_date)

        if not results:
            logger.warning(f"No scan results found for {scan_date}")
            return []

        # Filter by minimum score
        if min_score > 0:
            results = [r for r in results if r['priority_score'] >= min_score]

        # Filter by required alerts
        if required_alerts:
            filtered = []
            for result in results:
                alerts = result.get('triggered_alerts', [])
                if any(alert in alerts for alert in required_alerts):
                    filtered.append(result)
            results = filtered

        # Sort by priority score (descending)
        results.sort(key=lambda x: x['priority_score'], reverse=True)

        # Return top N
        return results[:top_n]

    def analyze_opportunities(
        self,
        opportunities: List[Dict[str, Any]],
        analysis_date: date,
        store_results: bool = True,
        plain_english: bool = False,
        portfolio_value: float = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze list of opportunities.

        Args:
            opportunities: List of screener results
            analysis_date: Date to analyze
            store_results: Whether to store results
            plain_english: Whether to use plain English reports
            portfolio_value: Portfolio value for position sizing

        Returns:
            List of analysis results
        """
        all_results = []

        print(f"\n{'='*70}")
        print(f"BATCH DEEP ANALYSIS")
        print(f"{'='*70}")
        print(f"Date: {analysis_date}")
        print(f"Opportunities: {len(opportunities)}")
        print(f"RAG: {'Enabled' if self.enable_rag else 'Disabled'}")
        print(f"Store Results: {'Yes' if store_results else 'No'}")
        print(f"{'='*70}\n")

        for i, opp in enumerate(opportunities, 1):
            ticker = opp['symbol']
            score = opp['priority_score']
            rank = opp.get('priority_rank', i)

            print(f"\n{'='*70}")
            print(f"[{i}/{len(opportunities)}] Analyzing {ticker} (Rank: {rank}, Score: {score:.1f})")
            print(f"{'='*70}\n")

            try:
                # Run deep analysis
                results = self.analyzer.analyze(
                    ticker=ticker,
                    analysis_date=analysis_date,
                    store_results=store_results
                )

                # Add screener metadata
                results['screener_rank'] = rank
                results['screener_score'] = score
                results['screener_alerts'] = opp.get('triggered_alerts', [])

                all_results.append(results)

                # Print detailed report if plain English mode
                if plain_english:
                    self.analyzer.print_results(
                        results,
                        verbose=False,
                        plain_english=True,
                        portfolio_value=portfolio_value
                    )
                else:
                    # Print summary
                    decision_emoji = {
                        'BUY': '🟢',
                        'SELL': '🔴',
                        'HOLD': '🟡',
                        'WAIT': '⚪'
                    }.get(results['decision'], '❓')

                    print(f"\n{decision_emoji} {ticker} - {results['decision']} (Confidence: {results['confidence']}/100)")

            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                all_results.append({
                    'ticker': ticker,
                    'error': str(e),
                    'screener_rank': rank,
                    'screener_score': score
                })

        return all_results

    def print_summary(self, results: List[Dict[str, Any]], portfolio_value: float = None):
        """
        Print summary of batch analysis.

        Args:
            results: List of analysis results
            portfolio_value: Portfolio value for recommendations
        """
        print(f"\n{'='*70}")
        print("BATCH ANALYSIS SUMMARY")
        print(f"{'='*70}\n")

        # Group by decision
        by_decision = {}
        for result in results:
            if 'error' not in result:
                decision = result['decision']
                if decision not in by_decision:
                    by_decision[decision] = []
                by_decision[decision].append(result)

        # Print by decision type
        for decision in ['BUY', 'WAIT', 'HOLD', 'SELL']:
            if decision in by_decision:
                print(f"\n{decision} Signals ({len(by_decision[decision])}):")
                print("-" * 70)

                for result in sorted(by_decision[decision], key=lambda x: x['confidence'], reverse=True):
                    ticker = result['ticker']
                    conf = result['confidence']
                    rank = result.get('screener_rank', '?')
                    score = result.get('screener_score', 0)
                    alerts = result.get('screener_alerts', [])

                    print(f"  {ticker:6s} | Confidence: {conf:2d}/100 | Screener: #{rank} ({score:.1f})")
                    if alerts:
                        print(f"         | Alerts: {', '.join(alerts[:3])}")

        # Print errors if any
        errors = [r for r in results if 'error' in r]
        if errors:
            print(f"\n\nErrors ({len(errors)}):")
            print("-" * 70)
            for result in errors:
                print(f"  {result['ticker']:6s} | {result['error']}")

        # Statistics
        total = len(results) - len(errors)
        if total > 0:
            buy_count = len(by_decision.get('BUY', []))
            wait_count = len(by_decision.get('WAIT', []))
            avg_confidence = sum(r['confidence'] for r in results if 'error' not in r) / total

            print(f"\n\nStatistics:")
            print("-" * 70)
            print(f"  Total Analyzed: {total}")
            print(f"  BUY Signals: {buy_count} ({buy_count/total*100:.1f}%)")
            print(f"  WAIT Signals: {wait_count} ({wait_count/total*100:.1f}%)")
            print(f"  Average Confidence: {avg_confidence:.1f}/100")
            print(f"  RAG Context Used: {sum(1 for r in results if r.get('historical_context_used'))}/{total}")

        print()

    def print_recommendations(self, results: List[Dict[str, Any]], portfolio_value: float = None):
        """
        Print actionable recommendations based on analysis results.

        Args:
            results: List of analysis results
            portfolio_value: Portfolio value for position sizing
        """
        print(f"\n{'='*70}")
        print("🎯 RECOMMENDED ACTIONS")
        print(f"{'='*70}\n")

        # Filter valid results
        valid_results = [r for r in results if 'error' not in r]
        if not valid_results:
            print("No actionable recommendations - all analyses had errors.\n")
            return

        # Group by decision
        buy_signals = [r for r in valid_results if r['decision'] == 'BUY']
        wait_signals = [r for r in valid_results if r['decision'] == 'WAIT']

        # Sort by confidence
        buy_signals = sorted(buy_signals, key=lambda x: x['confidence'], reverse=True)
        wait_signals = sorted(wait_signals, key=lambda x: x['confidence'], reverse=True)

        # Generate recommendations
        if buy_signals:
            print(f"✅ IMMEDIATE ACTIONS ({len(buy_signals)} BUY opportunities)")
            print("-" * 70)

            total_investment = 0
            for i, result in enumerate(buy_signals, 1):
                ticker = result['ticker']
                conf = result['confidence']

                # Calculate position size (5% for high confidence, 3% for moderate)
                if conf >= 80:
                    position_pct = 5.0
                elif conf >= 70:
                    position_pct = 3.0
                else:
                    position_pct = 2.0

                if portfolio_value:
                    investment = portfolio_value * (position_pct / 100)
                    total_investment += investment
                    print(f"\n{i}. {ticker} (Confidence: {conf}/100)")
                    print(f"   → Invest: ${investment:,.0f} ({position_pct}% of portfolio)")
                    print(f"   → Action: Buy within 1-5 days")
                    print(f"   → Expected return: 10-20% in 3-6 months")
                    print(f"   → Potential profit: ${investment*0.10:,.0f} - ${investment*0.20:,.0f}")
                else:
                    print(f"\n{i}. {ticker} (Confidence: {conf}/100)")
                    print(f"   → Recommended position: {position_pct}% of portfolio")
                    print(f"   → Action: Buy within 1-5 days")

            if portfolio_value and total_investment > 0:
                print(f"\n💰 TOTAL INVESTMENT: ${total_investment:,.0f} ({total_investment/portfolio_value*100:.1f}% of portfolio)")
                print(f"   Expected total profit: ${total_investment*0.10:,.0f} - ${total_investment*0.20:,.0f}")
                remaining = portfolio_value - total_investment
                print(f"   Remaining cash: ${remaining:,.0f} ({remaining/portfolio_value*100:.1f}%)")

        if wait_signals:
            print(f"\n\n⏰ WATCH LIST ({len(wait_signals)} stocks to monitor)")
            print("-" * 70)
            print("These stocks look promising but timing isn't optimal yet:")
            for result in wait_signals:
                ticker = result['ticker']
                conf = result['confidence']
                print(f"  • {ticker} (Confidence: {conf}/100) - Check again in 1-2 weeks")

        # Next steps
        print(f"\n\n📋 YOUR NEXT STEPS:")
        print("-" * 70)

        if buy_signals:
            print("\n1. REVIEW THE RECOMMENDATIONS ABOVE")
            print("   → Read the detailed plain English report for each BUY signal")
            print("   → Understand the risks and reasons")

            print("\n2. DECIDE YOUR INVESTMENT AMOUNTS")
            if portfolio_value:
                print(f"   → Suggested total: ${total_investment:,.0f} across {len(buy_signals)} stocks")
            print("   → Adjust based on your risk tolerance")
            print("   → Never invest money you can't afford to lose")

            print("\n3. PLACE YOUR ORDERS")
            print("   → Log into your brokerage account")
            print("   → Search for each ticker symbol")
            print("   → Use 'Market Order' to buy at current price")
            print("   → Review and confirm each purchase")

            print("\n4. SET REMINDERS")
            print("   → Review investments in 3-6 months")
            print("   → Don't check prices daily (avoid panic)")
            print("   → Focus on long-term growth")
        else:
            print("\n1. NO IMMEDIATE BUY SIGNALS")
            print("   → Consider analyzing more stocks from the screener")
            print("   → Or wait for better opportunities")

            print("\n2. RUN SCREENER DAILY")
            print("   → Market conditions change daily")
            print("   → New opportunities emerge regularly")

        if wait_signals:
            print(f"\n5. MONITOR WATCH LIST")
            print("   → Re-analyze wait list stocks in 1-2 weeks")
            print("   → Watch for price dips or improved signals")

        # Daily workflow
        print(f"\n\n📅 SUGGESTED DAILY WORKFLOW:")
        print("-" * 70)
        print("\nMorning (5 minutes):")
        print("  python -m tradingagents.screener run")
        print("  python -m tradingagents.screener top 5")

        print("\nWhen opportunities found:")
        if portfolio_value:
            print(f"  PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \\")
            print(f"    .venv/bin/python -m tradingagents.analyze.batch_analyze \\")
            print(f"    --top 5 --plain-english --portfolio-value {int(portfolio_value)}")
        else:
            print("  PYTHONPATH=/Users/lxupkzwjs/Developer/eval/TradingAgents \\")
            print("    .venv/bin/python -m tradingagents.analyze.batch_analyze \\")
            print("    --top 5 --plain-english --portfolio-value YOUR_PORTFOLIO")

        print("\nMake decisions:")
        print("  → Read plain English reports")
        print("  → Follow recommended actions above")
        print("  → Invest based on your comfort level")

        # Risk reminder
        print(f"\n\n⚠️  IMPORTANT REMINDERS:")
        print("-" * 70)
        print("  • Diversify: Don't put more than 5-10% in any single stock")
        print("  • Be Patient: Hold for 3-6 months minimum")
        print("  • Stay Calm: Daily price swings are normal")
        print("  • Risk Management: Only invest money you can afford to lose")
        print("  • Review Regularly: Check portfolio quarterly (every 3 months)")

        print(f"\n{'='*70}\n")

    def close(self):
        """Clean up resources."""
        self.analyzer.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Batch analysis of top screener opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--top',
        type=int,
        default=5,
        help='Number of top opportunities to analyze (default: 5)'
    )

    parser.add_argument(
        '--min-score',
        type=float,
        default=0,
        help='Minimum priority score to consider (default: 0)'
    )

    parser.add_argument(
        '--alerts',
        type=str,
        default=None,
        help='Comma-separated list of required alerts (e.g., "MACD_BULLISH_CROSS,RSI_OVERSOLD")'
    )

    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Analysis date (YYYY-MM-DD, default: today)'
    )

    parser.add_argument(
        '--no-rag',
        action='store_true',
        help='Disable RAG (faster but no historical context)'
    )

    parser.add_argument(
        '--no-store',
        action='store_true',
        help='Do not store results to database'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    parser.add_argument(
        '--plain-english',
        action='store_true',
        help='Show results in plain English (easy to understand for beginners)'
    )

    parser.add_argument(
        '--portfolio-value',
        type=float,
        default=None,
        help='Your total portfolio value (e.g., 100000 for $100k) - enables position sizing'
    )

    args = parser.parse_args()

    # Parse date
    from datetime import datetime
    if args.date:
        try:
            analysis_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Expected YYYY-MM-DD")
            sys.exit(1)
    else:
        analysis_date = date.today()

    # Parse alerts
    required_alerts = None
    if args.alerts:
        required_alerts = [a.strip() for a in args.alerts.split(',')]

    # Initialize batch analyzer
    try:
        batch_analyzer = BatchAnalyzer(
            enable_rag=not args.no_rag,
            debug=args.debug
        )
    except Exception as e:
        logger.error(f"Failed to initialize batch analyzer: {e}")
        sys.exit(1)

    # Get top opportunities
    logger.info(f"Fetching top {args.top} opportunities from {analysis_date} scan...")
    opportunities = batch_analyzer.get_top_opportunities(
        scan_date=analysis_date,
        top_n=args.top,
        min_score=args.min_score,
        required_alerts=required_alerts
    )

    if not opportunities:
        logger.error(f"No opportunities found. Have you run the screener today?")
        logger.info("Run: python -m tradingagents.screener run")
        batch_analyzer.close()
        sys.exit(1)

    logger.info(f"Found {len(opportunities)} opportunities to analyze")

    # Analyze opportunities
    results = batch_analyzer.analyze_opportunities(
        opportunities=opportunities,
        analysis_date=analysis_date,
        store_results=not args.no_store,
        plain_english=args.plain_english,
        portfolio_value=args.portfolio_value
    )

    # Print summary
    batch_analyzer.print_summary(results, portfolio_value=args.portfolio_value)

    # Print actionable recommendations (especially useful in plain English mode)
    if args.plain_english:
        batch_analyzer.print_recommendations(results, portfolio_value=args.portfolio_value)

    # Cleanup
    batch_analyzer.close()

    logger.info("Batch analysis complete!")


if __name__ == '__main__':
    main()
