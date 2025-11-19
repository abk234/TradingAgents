"""
CLI Commands for Strategy System
"""

import argparse
import json
from typing import List, Optional
from datetime import date
import sys

from .comparator import StrategyComparator
from .data_collector import StrategyDataCollector
from .value import ValueStrategy
from .growth import GrowthStrategy
from .dividend import DividendStrategy
from .momentum import MomentumStrategy
from .contrarian import ContrarianStrategy
from .quantitative import QuantitativeStrategy
from .sector_rotation import SectorRotationStrategy

# Try to import integration (may not be available)
try:
    from ..integration.comparison_runner import ComparisonRunner
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    ComparisonRunner = None


def get_strategy_by_name(name: str):
    """Get strategy instance by name."""
    strategy_map = {
        "value": ValueStrategy,
        "growth": GrowthStrategy,
        "dividend": DividendStrategy,
        "momentum": MomentumStrategy,
        "contrarian": ContrarianStrategy,
        "quantitative": QuantitativeStrategy,
        "sector_rotation": SectorRotationStrategy,
    }
    
    strategy_class = strategy_map.get(name.lower())
    if strategy_class:
        return strategy_class()
    return None


def cmd_compare(args):
    """Compare multiple strategies."""
    ticker = args.ticker.upper()
    analysis_date = args.date or date.today().strftime("%Y-%m-%d")
    
    # Build strategy list
    strategies = []
    
    if args.strategies:
        for strategy_name in args.strategies:
            strategy = get_strategy_by_name(strategy_name)
            if strategy:
                strategies.append(strategy)
            else:
                print(f"Warning: Unknown strategy '{strategy_name}', skipping", file=sys.stderr)
    else:
        # Use all strategies
        strategies = [
            ValueStrategy(),
            GrowthStrategy(),
            DividendStrategy(),
            MomentumStrategy(),
            ContrarianStrategy(),
            QuantitativeStrategy(),
            SectorRotationStrategy(),
        ]
    
    if not strategies:
        print("Error: No strategies to compare", file=sys.stderr)
        return 1
    
    # Collect data
    print(f"Collecting data for {ticker}...")
    collector = StrategyDataCollector()
    try:
        data = collector.collect_all_data(ticker, analysis_date)
    except Exception as e:
        print(f"Error collecting data: {e}", file=sys.stderr)
        return 1
    
    # Run comparison
    print(f"Comparing {len(strategies)} strategies...")
    comparator = StrategyComparator(strategies)
    comparison = comparator.compare(
        ticker=ticker,
        market_data=data["market_data"],
        fundamental_data=data["fundamental_data"],
        technical_data=data["technical_data"],
        additional_data={
            "analysis_date": analysis_date,
            "dividend_data": data.get("dividend_data", {}),
            "news_data": data.get("news_data", {}),
        }
    )
    
    # Output results
    if args.json:
        print(json.dumps(comparison, indent=2, default=str))
    else:
        print_comparison_results(comparison)
    
    return 0


def cmd_single_strategy(args):
    """Run a single strategy."""
    ticker = args.ticker.upper()
    strategy_name = args.strategy.lower()
    analysis_date = args.date or date.today().strftime("%Y-%m-%d")
    
    # Get strategy
    strategy = get_strategy_by_name(strategy_name)
    if not strategy:
        print(f"Error: Unknown strategy '{strategy_name}'", file=sys.stderr)
        print(f"Available strategies: value, growth, dividend, momentum, contrarian, quantitative, sector_rotation")
        return 1
    
    # Collect data
    print(f"Collecting data for {ticker}...")
    collector = StrategyDataCollector()
    try:
        data = collector.collect_all_data(ticker, analysis_date)
    except Exception as e:
        print(f"Error collecting data: {e}", file=sys.stderr)
        return 1
    
    # Run strategy
    print(f"Running {strategy.get_strategy_name()}...")
    result = strategy.evaluate(
        ticker=ticker,
        market_data=data["market_data"],
        fundamental_data=data["fundamental_data"],
        technical_data=data["technical_data"],
        additional_data={
            "analysis_date": analysis_date,
            "dividend_data": data.get("dividend_data", {}),
            "news_data": data.get("news_data", {}),
        }
    )
    
    # Output results
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        print_single_strategy_result(result)
    
    return 0


def cmd_list(args):
    """List available strategies."""
    strategies = [
        ("value", "Value Investing", "Buffett-style value investing"),
        ("growth", "Growth Investing", "Growth at reasonable price (GARP)"),
        ("dividend", "Dividend Investing", "Income-focused investing"),
        ("momentum", "Momentum Trading", "Technical momentum trading"),
        ("contrarian", "Contrarian Investing", "Buy when others fear"),
        ("quantitative", "Quantitative Investing", "Factor-based systematic"),
        ("sector_rotation", "Sector Rotation", "Economic cycle-based"),
    ]
    
    print("Available Strategies:")
    print("=" * 60)
    for name, display_name, description in strategies:
        print(f"\n{display_name} ({name})")
        print(f"  {description}")
    
    if INTEGRATION_AVAILABLE:
        print("\n" + "=" * 60)
        print("\nIntegration Available:")
        print("  Use 'compare-with-existing' to include existing TradingAgents system")
    
    return 0


def cmd_compare_with_existing(args):
    """Compare new strategies with existing system."""
    if not INTEGRATION_AVAILABLE:
        print("Error: Integration module not available", file=sys.stderr)
        return 1
    
    ticker = args.ticker.upper()
    analysis_date = args.date or date.today().strftime("%Y-%m-%d")
    
    print(f"Comparing strategies with existing system for {ticker}...")
    
    runner = ComparisonRunner(include_existing=True)
    comparison = runner.compare_both_systems(ticker, analysis_date)
    
    if "error" in comparison:
        print(f"Error: {comparison['error']}", file=sys.stderr)
        return 1
    
    # Output results
    if args.json:
        print(json.dumps(comparison, indent=2, default=str))
    else:
        print_comparison_results(comparison)
    
    return 0


def print_comparison_results(comparison: dict):
    """Print comparison results in human-readable format."""
    ticker = comparison.get("ticker", "UNKNOWN")
    consensus = comparison.get("consensus", {})
    strategies = comparison.get("strategies", {})
    insights = comparison.get("insights", [])
    
    print("\n" + "=" * 70)
    print(f"Strategy Comparison Results: {ticker}")
    print("=" * 70)
    
    # Consensus
    print(f"\n📊 Consensus:")
    print(f"   Recommendation: {consensus.get('recommendation', 'N/A')}")
    print(f"   Agreement Level: {consensus.get('agreement_level', 0):.1f}%")
    print(f"   Votes: BUY={consensus.get('buy_count', 0)}, "
          f"SELL={consensus.get('sell_count', 0)}, "
          f"HOLD={consensus.get('hold_count', 0)}, "
          f"WAIT={consensus.get('wait_count', 0)}")
    
    # Individual strategies
    print(f"\n📈 Strategy Results:")
    for strategy_name, result in strategies.items():
        rec = result.get("recommendation", "N/A")
        conf = result.get("confidence", 0)
        print(f"\n   {strategy_name}:")
        print(f"      Recommendation: {rec}")
        print(f"      Confidence: {conf}%")
        reasoning = result.get("reasoning", "")
        if reasoning:
            # Truncate long reasoning
            if len(reasoning) > 150:
                reasoning = reasoning[:147] + "..."
            print(f"      Reasoning: {reasoning}")
    
    # Insights
    if insights:
        print(f"\n💡 Insights:")
        for insight in insights:
            print(f"   • {insight}")
    
    print("\n" + "=" * 70)


def print_single_strategy_result(result):
    """Print single strategy result in human-readable format."""
    print("\n" + "=" * 70)
    print(f"Strategy Result: {result.strategy_name}")
    print("=" * 70)
    
    print(f"\nRecommendation: {result.recommendation.value}")
    print(f"Confidence: {result.confidence}%")
    print(f"\nReasoning:\n{result.reasoning}")
    
    if result.entry_price:
        print(f"\nEntry Price: ${result.entry_price:.2f}")
    if result.target_price:
        print(f"Target Price: ${result.target_price:.2f}")
    if result.stop_loss:
        print(f"Stop Loss: ${result.stop_loss:.2f}")
    if result.holding_period:
        print(f"Holding Period: {result.holding_period}")
    
    if result.key_metrics:
        print(f"\nKey Metrics:")
        for key, value in result.key_metrics.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"   {key}: {value:.2f}")
                else:
                    print(f"   {key}: {value}")
    
    if result.risks:
        print(f"\nRisks:")
        for risk in result.risks:
            print(f"   • {risk}")
    
    print("\n" + "=" * 70)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Strategy Investment Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare all strategies
  python -m tradingagents.strategies compare AAPL
  
  # Compare specific strategies
  python -m tradingagents.strategies compare AAPL --strategies value growth
  
  # Run single strategy
  python -m tradingagents.strategies value AAPL
  
  # List available strategies
  python -m tradingagents.strategies list
  
  # Compare with existing system
  python -m tradingagents.strategies compare-with-existing AAPL
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare multiple strategies")
    compare_parser.add_argument("ticker", help="Stock ticker symbol")
    compare_parser.add_argument("--date", help="Analysis date (YYYY-MM-DD)")
    compare_parser.add_argument("--strategies", nargs="+", help="Strategy names to compare")
    compare_parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    # Single strategy command
    single_parser = subparsers.add_parser("run", help="Run a single strategy")
    single_parser.add_argument("strategy", help="Strategy name (value, growth, etc.)")
    single_parser.add_argument("ticker", help="Stock ticker symbol")
    single_parser.add_argument("--date", help="Analysis date (YYYY-MM-DD)")
    single_parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available strategies")
    
    # Compare with existing command
    if INTEGRATION_AVAILABLE:
        existing_parser = subparsers.add_parser(
            "compare-with-existing",
            help="Compare with existing TradingAgents system"
        )
        existing_parser.add_argument("ticker", help="Stock ticker symbol")
        existing_parser.add_argument("--date", help="Analysis date (YYYY-MM-DD)")
        existing_parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    if args.command == "compare":
        return cmd_compare(args)
    elif args.command == "run":
        return cmd_single_strategy(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "compare-with-existing":
        return cmd_compare_with_existing(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

