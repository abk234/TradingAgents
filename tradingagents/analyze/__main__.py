"""
Deep Analysis CLI

Command-line interface for running RAG-enhanced deep analysis.

Usage:
    # Analyze a single ticker
    python -m tradingagents.analyze AAPL

    # Analyze with specific date
    python -m tradingagents.analyze AAPL --date 2024-01-15

    # Analyze multiple tickers
    python -m tradingagents.analyze AAPL GOOGL MSFT

    # Analyze without RAG (faster but no historical context)
    python -m tradingagents.analyze AAPL --no-rag

    # Verbose output with full reports
    python -m tradingagents.analyze AAPL --verbose

    # Don't store results to database
    python -m tradingagents.analyze AAPL --no-store
"""

import argparse
import sys
import logging
from datetime import datetime, date
from typing import List

from tradingagents.analyze import DeepAnalyzer
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.utils import display_next_steps
from tradingagents.database import get_db_connection, TickerOperations
from tradingagents.screener.data_fetcher import DataFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Deep Analysis CLI - RAG-enhanced investment analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'tickers',
        nargs='+',
        help='Stock ticker symbol(s) to analyze'
    )

    parser.add_argument(
        '--date',
        type=str,
        default=None,
        help='Analysis date (YYYY-MM-DD). Defaults to today.'
    )

    parser.add_argument(
        '--no-rag',
        action='store_true',
        help='Disable RAG historical context (faster but less informed)'
    )

    parser.add_argument(
        '--no-store',
        action='store_true',
        help='Do not store analysis results to database'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show full analyst reports and debates'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with detailed tracing'
    )

    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom config file (JSON)'
    )

    parser.add_argument(
        '--plain-english',
        action='store_true',
        help='Show results in plain English (easy to understand for non-technical users)'
    )

    parser.add_argument(
        '--portfolio-value',
        type=float,
        default=None,
        help='Your total portfolio value (e.g., 100000 for $100k) - used for position sizing'
    )

    parser.add_argument(
        '--refresh-data',
        action='store_true',
        help='Fetch fresh price and fundamental data before analysis (slower but ensures latest data)'
    )

    parser.add_argument(
        '--use-cache',
        action='store_true',
        default=True,
        help='Use cached/database data (default: True, faster)'
    )

    return parser.parse_args()


def parse_date(date_str: str) -> date:
    """Parse date string to date object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        logger.error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
        sys.exit(1)


def load_custom_config(config_path: str):
    """Load custom configuration from JSON file and merge with DEFAULT_CONFIG."""
    import json
    import copy

    try:
        with open(config_path, 'r') as f:
            custom_config = json.load(f)
        
        # Merge with DEFAULT_CONFIG - custom config values override defaults
        merged_config = copy.deepcopy(DEFAULT_CONFIG)
        
        # Deep merge nested dictionaries (like data_vendors, tool_vendors, validation)
        for key, value in custom_config.items():
            if isinstance(value, dict) and key in merged_config and isinstance(merged_config[key], dict):
                merged_config[key].update(value)
            else:
                merged_config[key] = value
        
        logger.info(f"Loaded config from {config_path} and merged with defaults")
        return merged_config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        sys.exit(1)


def analyze_ticker(
    analyzer: DeepAnalyzer,
    ticker: str,
    analysis_date: date,
    store_results: bool,
    verbose: bool,
    plain_english: bool = False,
    portfolio_value: float = None
):
    """
    Analyze a single ticker.

    Args:
        analyzer: DeepAnalyzer instance
        ticker: Ticker symbol
        analysis_date: Date to analyze
        store_results: Whether to store results
        verbose: Whether to show detailed output
        plain_english: Whether to show plain English report
        portfolio_value: Portfolio value for position sizing
    """
    try:
        # Run analysis
        results = analyzer.analyze(
            ticker=ticker.upper(),
            analysis_date=analysis_date,
            store_results=store_results
        )

        # Print results
        analyzer.print_results(results, verbose=verbose, plain_english=plain_english, portfolio_value=portfolio_value)

        return results

    except KeyboardInterrupt:
        logger.info("\n\nAnalysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}", exc_info=True)
        return None


def refresh_ticker_data(ticker: str):
    """Refresh price and fundamental data for a ticker."""
    try:
        db = get_db_connection()
        ticker_ops = TickerOperations(db)
        data_fetcher = DataFetcher(db)
        
        ticker_info = ticker_ops.get_ticker_by_symbol(ticker.upper())
        if not ticker_info:
            logger.warning(f"Ticker {ticker} not found in database")
            return False
        
        ticker_id = ticker_info['ticker_id']
        logger.info(f"Refreshing data for {ticker}...")
        data_fetcher.update_ticker_prices(ticker_id, ticker.upper())
        logger.info(f"✓ Data refreshed for {ticker}")
        return True
    except Exception as e:
        logger.warning(f"Error refreshing data for {ticker}: {e}")
        return False


def main():
    """Main CLI entry point."""
    args = parse_args()

    # Parse date
    analysis_date = parse_date(args.date) if args.date else date.today()

    # Refresh data if requested
    if args.refresh_data:
        print("\n" + "="*70)
        print("REFRESHING DATA")
        print("="*70)
        for ticker in args.tickers:
            refresh_ticker_data(ticker)
        print("="*70 + "\n")

    # Load config
    if args.config:
        config = load_custom_config(args.config)
    else:
        config = DEFAULT_CONFIG

    # Print header
    print("\n" + "="*70)
    print("INVESTMENT INTELLIGENCE SYSTEM - DEEP ANALYSIS")
    print("="*70)
    print(f"Date: {analysis_date}")
    print(f"Tickers: {', '.join(args.tickers)}")
    print(f"RAG: {'Disabled' if args.no_rag else 'Enabled'}")
    print(f"Store Results: {'No' if args.no_store else 'Yes'}")
    print(f"Data Refresh: {'Yes' if args.refresh_data else 'No (using cache)'}")
    print("="*70 + "\n")

    # Initialize analyzer
    try:
        analyzer = DeepAnalyzer(
            config=config,
            enable_rag=not args.no_rag,
            debug=args.debug
        )
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}")
        sys.exit(1)

    # Analyze each ticker
    results_list = []
    for ticker in args.tickers:
        result = analyze_ticker(
            analyzer=analyzer,
            ticker=ticker,
            analysis_date=analysis_date,
            store_results=not args.no_store,
            verbose=args.verbose,
            plain_english=args.plain_english,
            portfolio_value=args.portfolio_value
        )
        if result:
            results_list.append(result)

    # Summary if multiple tickers
    if len(args.tickers) > 1:
        print("\n" + "="*70)
        print("SUMMARY OF ALL ANALYSES")
        print("="*70)

        for result in results_list:
            if result:
                decision_emoji = {
                    'BUY': '🟢',
                    'SELL': '🔴',
                    'HOLD': '🟡',
                    'WAIT': '⚪'
                }.get(result['decision'], '❓')

                print(f"{decision_emoji} {result['ticker']:6s} - {result['decision']:4s} "
                      f"(Confidence: {result['confidence']}/100)")

        print()

    # Cleanup
    analyzer.close()

    # Display next steps and recommendations
    if results_list:
        ticker = results_list[0].get('ticker', args.tickers[0] if args.tickers else 'TICKER')
        display_next_steps('analyze', context={'ticker': ticker})

    logger.info("Analysis complete!")


if __name__ == '__main__':
    main()
