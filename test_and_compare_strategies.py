#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Strategy Testing and Comparison Script

Comprehensive tool for testing and comparing trading strategies.
Supports single stock analysis, multi-stock comparison, and backtesting.
"""

import argparse
import json
import sys
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich library not available. Install with: pip install rich")
    print("Falling back to basic output...")

from tradingagents.strategies import (
    StrategyComparator,
    StrategyDataCollector,
    ValueStrategy,
    GrowthStrategy,
    DividendStrategy,
    MomentumStrategy,
    ContrarianStrategy,
    QuantitativeStrategy,
    SectorRotationStrategy,
)

# Try to import Market Structure and Cloud Trend strategy
try:
    from tradingagents.strategies.market_structure_cloud_trend import MarketStructureCloudTrendStrategy
    MARKET_STRUCTURE_AVAILABLE = True
except ImportError:
    MARKET_STRUCTURE_AVAILABLE = False
    MarketStructureCloudTrendStrategy = None

# Initialize console if rich is available
console = Console() if RICH_AVAILABLE else None


def get_all_strategies():
    """Get all available strategies."""
    strategies = [
        ValueStrategy(),
        GrowthStrategy(),
        DividendStrategy(),
        MomentumStrategy(),
        ContrarianStrategy(),
        QuantitativeStrategy(),
        SectorRotationStrategy(),
    ]
    # Add Market Structure and Cloud Trend if available
    if MARKET_STRUCTURE_AVAILABLE:
        strategies.append(MarketStructureCloudTrendStrategy())
    return strategies


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
    
    # Add Market Structure and Cloud Trend if available
    if MARKET_STRUCTURE_AVAILABLE and name.lower() in ["market_structure", "market-structure", "cloud_trend", "cloud-trend", "msct"]:
        return MarketStructureCloudTrendStrategy()
    
    strategy_class = strategy_map.get(name.lower())
    if strategy_class:
        return strategy_class()
    return None


def compare_single_stock(
    ticker: str,
    strategies: Optional[List] = None,
    analysis_date: Optional[str] = None,
    output_json: bool = False
) -> Dict[str, Any]:
    """Compare strategies on a single stock."""
    
    if strategies is None:
        strategies = get_all_strategies()
    
    if analysis_date is None:
        analysis_date = date.today().strftime("%Y-%m-%d")
    
    if console:
        console.print(f"\n[cyan]Analyzing {ticker}...[/cyan]")
    else:
        print(f"\nAnalyzing {ticker}...")
    
    # Collect data
    collector = StrategyDataCollector()
    try:
        if console:
            with console.status(f"[green]Collecting data for {ticker}..."):
                data = collector.collect_all_data(ticker, analysis_date)
        else:
            print(f"Collecting data for {ticker}...")
            data = collector.collect_all_data(ticker, analysis_date)
    except Exception as e:
        error_msg = f"Error collecting data for {ticker}: {e}"
        if console:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)
        return {"error": error_msg}
    
    # Run comparison
    comparator = StrategyComparator(strategies)
    # Prepare additional data (include ticker for AI Pine Script)
    additional_data = {
        "analysis_date": analysis_date,
        "dividend_data": data.get("dividend_data", {}),
        "news_data": data.get("news_data", {}),
        "ticker": ticker,  # For Market Structure and Cloud Trend historical data fetch
    }
    
    comparison = comparator.compare(
        ticker=ticker,
        market_data=data["market_data"],
        fundamental_data=data["fundamental_data"],
        technical_data=data["technical_data"],
        additional_data=additional_data
    )
    
    if output_json:
        return comparison
    
    # Display results
    display_comparison_results(comparison)
    
    return comparison


def compare_multiple_stocks(
    tickers: List[str],
    strategies: Optional[List] = None,
    analysis_date: Optional[str] = None,
    output_json: bool = False
) -> Dict[str, Any]:
    """Compare strategies across multiple stocks."""
    
    if strategies is None:
        strategies = get_all_strategies()
    
    if analysis_date is None:
        analysis_date = date.today().strftime("%Y-%m-%d")
    
    collector = StrategyDataCollector()
    comparator = StrategyComparator(strategies)
    
    results_by_ticker = {}
    errors = []
    
    if console:
        console.print(f"\n[cyan]Comparing {len(tickers)} stocks with {len(strategies)} strategies...[/cyan]\n")
    else:
        print(f"\nComparing {len(tickers)} stocks with {len(strategies)} strategies...\n")
    
    # Analyze each ticker
    for ticker in tickers:
        try:
            if console:
                with console.status(f"[green]Analyzing {ticker}..."):
                    data = collector.collect_all_data(ticker, analysis_date)
                    comparison = comparator.compare(
                        ticker=ticker,
                        market_data=data["market_data"],
                        fundamental_data=data["fundamental_data"],
                        technical_data=data["technical_data"],
                        additional_data={
                            "analysis_date": analysis_date,
                            "dividend_data": data.get("dividend_data", {}),
                            "news_data": data.get("news_data", {}),
                            "ticker": ticker,  # For Market Structure and Cloud Trend historical data fetch
                        }
                    )
            else:
                print(f"Analyzing {ticker}...")
                data = collector.collect_all_data(ticker, analysis_date)
                comparison = comparator.compare(
                    ticker=ticker,
                    market_data=data["market_data"],
                    fundamental_data=data["fundamental_data"],
                    technical_data=data["technical_data"],
                    additional_data={
                        "analysis_date": analysis_date,
                        "dividend_data": data.get("dividend_data", {}),
                        "news_data": data.get("news_data", {}),
                        "ticker": ticker,  # For Market Structure and Cloud Trend historical data fetch
                    }
                )
            
            results_by_ticker[ticker] = comparison
            
        except Exception as e:
            error_msg = f"Error analyzing {ticker}: {e}"
            errors.append(error_msg)
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            continue
    
    if output_json:
        return {
            "results": results_by_ticker,
            "errors": errors
        }
    
    # Display summary
    display_multi_stock_summary(results_by_ticker, strategies)
    
    return {
        "results": results_by_ticker,
        "errors": errors
    }


def display_comparison_results(comparison: Dict[str, Any]):
    """Display comparison results in a formatted table."""
    
    ticker = comparison.get("ticker", "UNKNOWN")
    consensus = comparison.get("consensus", {})
    strategies = comparison.get("strategies", {})
    insights = comparison.get("insights", [])
    
    if console:
        # Use rich formatting
        console.print(Panel.fit(
            f"[bold green]Strategy Comparison: {ticker}[/bold green]",
            border_style="green"
        ))
        
        # Consensus table
        consensus_table = Table(title="Consensus", box=box.ROUNDED)
        consensus_table.add_column("Metric", style="cyan")
        consensus_table.add_column("Value", style="green")
        
        consensus_table.add_row("Recommendation", consensus.get('recommendation', 'N/A'))
        consensus_table.add_row("Agreement Level", f"{consensus.get('agreement_level', 0):.1f}%")
        consensus_table.add_row("BUY Votes", str(consensus.get('buy_count', 0)))
        consensus_table.add_row("SELL Votes", str(consensus.get('sell_count', 0)))
        consensus_table.add_row("HOLD Votes", str(consensus.get('hold_count', 0)))
        consensus_table.add_row("WAIT Votes", str(consensus.get('wait_count', 0)))
        
        console.print(consensus_table)
        
        # Strategy results table
        strategy_table = Table(title="Strategy Results", box=box.ROUNDED, show_header=True)
        strategy_table.add_column("Strategy", style="cyan", width=25)
        strategy_table.add_column("Recommendation", style="green", width=15)
        strategy_table.add_column("Confidence", style="yellow", width=12)
        strategy_table.add_column("Target Price", style="magenta", width=15)
        
        for strategy_name, result in strategies.items():
            rec = result.get("recommendation", "N/A")
            conf = result.get("confidence", 0)
            target = f"${result['target_price']:.2f}" if result.get('target_price') else "N/A"
            
            strategy_table.add_row(strategy_name, rec, f"{conf}%", target)
        
        console.print(strategy_table)
        
        # Insights
        if insights:
            console.print("\n[cyan]Insights:[/cyan]")
            for insight in insights:
                console.print(f"  • {insight}")
        
    else:
        # Basic formatting
        print(f"\n{'='*80}")
        print(f"Strategy Comparison: {ticker}")
        print(f"{'='*80}\n")
        
        print("Consensus:")
        print(f"  Recommendation: {consensus.get('recommendation', 'N/A')}")
        print(f"  Agreement Level: {consensus.get('agreement_level', 0):.1f}%")
        print(f"  Votes: BUY={consensus.get('buy_count', 0)}, "
              f"SELL={consensus.get('sell_count', 0)}, "
              f"HOLD={consensus.get('hold_count', 0)}, "
              f"WAIT={consensus.get('wait_count', 0)}")
        
        print(f"\n{'='*80}")
        print("Strategy Results:")
        print(f"{'='*80}")
        
        for strategy_name, result in strategies.items():
            rec = result.get("recommendation", "N/A")
            conf = result.get("confidence", 0)
            target = f"${result['target_price']:.2f}" if result.get('target_price') else "N/A"
            
            print(f"\n{strategy_name}:")
            print(f"  Recommendation: {rec}")
            print(f"  Confidence: {conf}%")
            print(f"  Target Price: {target}")
        
        if insights:
            print(f"\n{'='*80}")
            print("Insights:")
            print(f"{'='*80}")
            for insight in insights:
                print(f"  • {insight}")


def display_multi_stock_summary(results_by_ticker: Dict[str, Dict], strategies: List):
    """Display summary table for multiple stocks."""
    
    if console:
        # Create summary table
        summary_table = Table(title="Multi-Stock Strategy Comparison", box=box.ROUNDED)
        summary_table.add_column("Ticker", style="cyan", width=10)
        
        # Add columns for each strategy
        strategy_names = [s.get_strategy_name() for s in strategies]
        for name in strategy_names:
            summary_table.add_column(name, style="green", width=15)
        
        summary_table.add_column("Consensus", style="yellow", width=15)
        
        # Add rows
        for ticker, comparison in results_by_ticker.items():
            row = [ticker]
            strategies_results = comparison.get('strategies', {})
            
            for strategy_name in strategy_names:
                rec = strategies_results.get(strategy_name, {}).get('recommendation', 'N/A')
                row.append(rec)
            
            consensus = comparison.get('consensus', {}).get('recommendation', 'N/A')
            row.append(consensus)
            
            summary_table.add_row(*row)
        
        console.print(summary_table)
        
        # Count recommendations
        buy_counts = {}
        for ticker, comparison in results_by_ticker.items():
            for strategy_name, result in comparison.get('strategies', {}).items():
                rec = result.get('recommendation', 'WAIT')
                if rec == 'BUY':
                    buy_counts[strategy_name] = buy_counts.get(strategy_name, 0) + 1
        
        if buy_counts:
            count_table = Table(title="BUY Recommendation Counts", box=box.SIMPLE)
            count_table.add_column("Strategy", style="cyan")
            count_table.add_column("BUY Count", style="green")
            count_table.add_column("Total Stocks", style="yellow")
            
            for strategy_name, count in sorted(buy_counts.items(), key=lambda x: x[1], reverse=True):
                count_table.add_row(strategy_name, str(count), str(len(results_by_ticker)))
            
            console.print(count_table)
    
    else:
        # Basic formatting
        print(f"\n{'='*80}")
        print("Multi-Stock Strategy Comparison Summary")
        print(f"{'='*80}\n")
        
        strategy_names = [s.get_strategy_name() for s in strategies]
        header = f"{'Ticker':<10}"
        for name in strategy_names:
            header += f" {name[:14]:<15}"
        header += f" {'Consensus':<15}"
        print(header)
        print("-" * 80)
        
        for ticker, comparison in results_by_ticker.items():
            row = f"{ticker:<10}"
            strategies_results = comparison.get('strategies', {})
            
            for strategy_name in strategy_names:
                rec = strategies_results.get(strategy_name, {}).get('recommendation', 'N/A')
                row += f" {rec:<15}"
            
            consensus = comparison.get('consensus', {}).get('recommendation', 'N/A')
            row += f" {consensus:<15}"
            print(row)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test and compare trading strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare all strategies on a single stock
  python test_and_compare_strategies.py compare AAPL
  
  # Compare specific strategies
  python test_and_compare_strategies.py compare AAPL --strategies value growth momentum
  
  # Compare multiple stocks
  python test_and_compare_strategies.py compare-multi AAPL MSFT GOOGL
  
  # Output JSON format
  python test_and_compare_strategies.py compare AAPL --json
  
  # Use historical date
  python test_and_compare_strategies.py compare AAPL --date 2024-01-15
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare strategies on a single stock")
    compare_parser.add_argument("ticker", help="Stock ticker symbol")
    compare_parser.add_argument("--strategies", nargs="+", help="Strategy names to use (default: all)")
    compare_parser.add_argument("--date", help="Analysis date (YYYY-MM-DD, default: today)")
    compare_parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    # Compare multiple stocks
    multi_parser = subparsers.add_parser("compare-multi", help="Compare strategies across multiple stocks")
    multi_parser.add_argument("tickers", nargs="+", help="Stock ticker symbols")
    multi_parser.add_argument("--strategies", nargs="+", help="Strategy names to use (default: all)")
    multi_parser.add_argument("--date", help="Analysis date (YYYY-MM-DD, default: today)")
    multi_parser.add_argument("--json", action="store_true", help="Output JSON format")
    
    # List strategies
    list_parser = subparsers.add_parser("list", help="List available strategies")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "list":
        strategies = get_all_strategies()
        if console:
            table = Table(title="Available Strategies", box=box.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="green")
            
            strategy_descriptions = {
                "Value Investing": "Buffett-style value investing",
                "Growth Investing": "Growth at reasonable price (GARP)",
                "Dividend Investing": "Income-focused investing",
                "Momentum Trading": "Technical momentum trading",
                "Contrarian Investing": "Buy when others fear",
                "Quantitative Investing": "Factor-based systematic",
                "Sector Rotation": "Economic cycle-based",
                "Market Structure and Cloud Trend": "Market Structure & Cloud Trend",
            }
            
            for strategy in strategies:
                name = strategy.get_strategy_name()
                desc = strategy_descriptions.get(name, "Investment strategy")
                table.add_row(name, desc)
            
            console.print(table)
        else:
            print("Available Strategies:")
            print("=" * 60)
            for strategy in strategies:
                print(f"  • {strategy.get_strategy_name()}")
                print(f"    Timeframe: {strategy.get_timeframe()}")
        return 0
    
    elif args.command == "compare":
        # Get strategies
        if args.strategies:
            strategies = []
            for name in args.strategies:
                strategy = get_strategy_by_name(name)
                if strategy:
                    strategies.append(strategy)
                else:
                    print(f"Warning: Unknown strategy '{name}', skipping", file=sys.stderr)
            
            if not strategies:
                print("Error: No valid strategies specified", file=sys.stderr)
                return 1
        else:
            strategies = get_all_strategies()
        
        # Run comparison
        result = compare_single_stock(
            ticker=args.ticker.upper(),
            strategies=strategies,
            analysis_date=args.date,
            output_json=args.json
        )
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        
        return 0 if "error" not in result else 1
    
    elif args.command == "compare-multi":
        # Get strategies
        if args.strategies:
            strategies = []
            for name in args.strategies:
                strategy = get_strategy_by_name(name)
                if strategy:
                    strategies.append(strategy)
                else:
                    print(f"Warning: Unknown strategy '{name}', skipping", file=sys.stderr)
            
            if not strategies:
                print("Error: No valid strategies specified", file=sys.stderr)
                return 1
        else:
            strategies = get_all_strategies()
        
        # Run comparison
        result = compare_multiple_stocks(
            tickers=[t.upper() for t in args.tickers],
            strategies=strategies,
            analysis_date=args.date,
            output_json=args.json
        )
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        if console:
            console.print("\n[yellow]Interrupted by user[/yellow]")
        else:
            print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        if console:
            console.print(f"\n[red]Error: {e}[/red]")
        else:
            print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

