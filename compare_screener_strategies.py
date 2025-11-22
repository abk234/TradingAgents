#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Compare Strategies on Screener Results

Takes top stocks from screener and runs all strategies on them for comparison.
"""

import sys
import argparse
from datetime import date
from typing import List, Dict, Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from tradingagents.screener import DailyScreener
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

console = Console() if RICH_AVAILABLE else None


def get_all_strategies():
    """Get all available strategies."""
    return [
        ValueStrategy(),
        GrowthStrategy(),
        DividendStrategy(),
        MomentumStrategy(),
        ContrarianStrategy(),
        QuantitativeStrategy(),
        SectorRotationStrategy(),
    ]


def get_top_stocks_from_screener(
    limit: int = 20,
    scan_date: date = None,
    run_screener: bool = False
) -> List[str]:
    """
    Get top stock symbols from screener.
    
    Args:
        limit: Number of top stocks to get
        scan_date: Date to get results from (defaults to today)
        run_screener: If True, run screener first before getting results
    
    Returns:
        List of ticker symbols
    """
    screener = DailyScreener()
    
    # Run screener if requested
    if run_screener:
        if console:
            console.print("[cyan]Running screener to get latest results...[/cyan]")
        else:
            print("Running screener to get latest results...")
        
        screener.scan_all(update_prices=True, store_results=True)
    
    # Get top opportunities
    if console:
        console.print(f"[cyan]Getting top {limit} stocks from screener...[/cyan]")
    else:
        print(f"Getting top {limit} stocks from screener...")
    
    opportunities = screener.get_top_opportunities(
        limit=limit,
        scan_date=scan_date,
        filter_buy_only=False
    )
    
    if not opportunities:
        if console:
            console.print("[yellow]No screener results found. Run screener first.[/yellow]")
        else:
            print("No screener results found. Run screener first.")
        return []
    
    # Extract ticker symbols
    tickers = [opp['symbol'] for opp in opportunities if 'symbol' in opp]
    
    if console:
        console.print(f"[green]Found {len(tickers)} stocks: {', '.join(tickers)}[/green]")
    else:
        print(f"Found {len(tickers)} stocks: {', '.join(tickers)}")
    
    return tickers


def compare_strategies_on_stocks(
    tickers: List[str],
    strategies: List = None,
    analysis_date: str = None,
    output_json: bool = False
) -> Dict[str, Any]:
    """
    Compare strategies across multiple stocks from screener.
    
    Args:
        tickers: List of ticker symbols
        strategies: List of strategy instances (defaults to all)
        analysis_date: Analysis date (defaults to today)
        output_json: If True, return JSON instead of displaying
    
    Returns:
        Dictionary with comparison results
    """
    if strategies is None:
        strategies = get_all_strategies()
    
    if analysis_date is None:
        analysis_date = date.today().strftime("%Y-%m-%d")
    
    collector = StrategyDataCollector()
    comparator = StrategyComparator(strategies)
    
    results_by_ticker = {}
    errors = []
    
    if console:
        console.print(f"\n[cyan]Comparing {len(strategies)} strategies on {len(tickers)} stocks...[/cyan]\n")
    else:
        print(f"\nComparing {len(strategies)} strategies on {len(tickers)} stocks...\n")
    
    # Analyze each ticker
    for i, ticker in enumerate(tickers, 1):
        try:
            if console:
                with console.status(f"[green][{i}/{len(tickers)}] Analyzing {ticker}..."):
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
                        }
                    )
            else:
                print(f"[{i}/{len(tickers)}] Analyzing {ticker}...")
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
    display_screener_strategy_summary(results_by_ticker, strategies)
    
    return {
        "results": results_by_ticker,
        "errors": errors
    }


def display_screener_strategy_summary(results_by_ticker: Dict[str, Dict], strategies: List):
    """Display summary table comparing strategies across screener stocks."""
    
    strategy_names = [s.get_strategy_name() for s in strategies]
    
    if console:
        # Create summary table
        summary_table = Table(
            title=f"Strategy Comparison: Screener Top {len(results_by_ticker)} Stocks",
            box=box.ROUNDED
        )
        summary_table.add_column("Stock", style="cyan", width=10)
        summary_table.add_column("Screener\nScore", style="yellow", width=12)
        
        # Add columns for each strategy
        for name in strategy_names:
            summary_table.add_column(name[:15], style="green", width=12)
        
        summary_table.add_column("Consensus", style="yellow", width=12)
        summary_table.add_column("Agreement", style="magenta", width=10)
        
        # Add rows
        for ticker, comparison in results_by_ticker.items():
            row = [ticker]
            
            # Get screener score if available (would need to pass this in)
            row.append("N/A")  # Screener score placeholder
            
            strategies_results = comparison.get('strategies', {})
            
            for strategy_name in strategy_names:
                rec = strategies_results.get(strategy_name, {}).get('recommendation', 'N/A')
                # Color code recommendations
                if rec == 'BUY':
                    rec = f"[green]{rec}[/green]"
                elif rec == 'SELL':
                    rec = f"[red]{rec}[/red]"
                elif rec == 'WAIT':
                    rec = f"[yellow]{rec}[/yellow]"
                row.append(rec)
            
            consensus = comparison.get('consensus', {})
            consensus_rec = consensus.get('recommendation', 'N/A')
            agreement = f"{consensus.get('agreement_level', 0):.0f}%"
            
            if consensus_rec == 'BUY':
                consensus_rec = f"[green]{consensus_rec}[/green]"
            elif consensus_rec == 'SELL':
                consensus_rec = f"[red]{consensus_rec}[/red]"
            
            row.append(consensus_rec)
            row.append(agreement)
            
            summary_table.add_row(*row)
        
        console.print(summary_table)
        
        # Count BUY recommendations by strategy
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
            
            console.print("\n")
            console.print(count_table)
        
        # Show stocks with strong BUY consensus
        strong_buy_stocks = []
        for ticker, comparison in results_by_ticker.items():
            consensus = comparison.get('consensus', {})
            if (consensus.get('recommendation') == 'BUY' and 
                consensus.get('agreement_level', 0) >= 70):
                strong_buy_stocks.append(ticker)
        
        if strong_buy_stocks:
            console.print(f"\n[green]Stocks with strong BUY consensus (≥70% agreement):[/green]")
            console.print(f"  {', '.join(strong_buy_stocks)}")
    
    else:
        # Basic formatting
        print(f"\n{'='*100}")
        print(f"Strategy Comparison: Screener Top {len(results_by_ticker)} Stocks")
        print(f"{'='*100}\n")
        
        # Header
        header = f"{'Stock':<10} {'Screener':<12}"
        for name in strategy_names:
            header += f" {name[:15]:<15}"
        header += f" {'Consensus':<12} {'Agreement':<10}"
        print(header)
        print("-" * 100)
        
        # Rows
        for ticker, comparison in results_by_ticker.items():
            row = f"{ticker:<10} {'N/A':<12}"
            strategies_results = comparison.get('strategies', {})
            
            for strategy_name in strategy_names:
                rec = strategies_results.get(strategy_name, {}).get('recommendation', 'N/A')
                row += f" {rec:<15}"
            
            consensus = comparison.get('consensus', {})
            consensus_rec = consensus.get('recommendation', 'N/A')
            agreement = f"{consensus.get('agreement_level', 0):.0f}%"
            row += f" {consensus_rec:<12} {agreement:<10}"
            print(row)
        
        # BUY counts
        buy_counts = {}
        for ticker, comparison in results_by_ticker.items():
            for strategy_name, result in comparison.get('strategies', {}).items():
                rec = result.get('recommendation', 'WAIT')
                if rec == 'BUY':
                    buy_counts[strategy_name] = buy_counts.get(strategy_name, 0) + 1
        
        if buy_counts:
            print(f"\n{'='*100}")
            print("BUY Recommendation Counts:")
            print(f"{'='*100}")
            for strategy_name, count in sorted(buy_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {strategy_name}: {count} BUY recommendations out of {len(results_by_ticker)} stocks")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare strategies on screener top stocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare strategies on top 20 screener stocks (use existing results)
  python compare_screener_strategies.py
  
  # Run screener first, then compare strategies
  python compare_screener_strategies.py --run-screener
  
  # Compare on top 10 stocks
  python compare_screener_strategies.py --limit 10
  
  # Output JSON
  python compare_screener_strategies.py --json
        """
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of top stocks from screener (default: 20)"
    )
    parser.add_argument(
        "--run-screener",
        action="store_true",
        help="Run screener first before comparing strategies"
    )
    parser.add_argument(
        "--date",
        help="Analysis date (YYYY-MM-DD, default: today)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format"
    )
    
    args = parser.parse_args()
    
    # Get top stocks from screener
    scan_date = None
    if args.date:
        scan_date = date.fromisoformat(args.date)
    
    tickers = get_top_stocks_from_screener(
        limit=args.limit,
        scan_date=scan_date,
        run_screener=args.run_screener
    )
    
    if not tickers:
        if console:
            console.print("[red]No stocks found. Try running screener first.[/red]")
        else:
            print("No stocks found. Try running screener first.")
        return 1
    
    # Compare strategies
    analysis_date = args.date or date.today().strftime("%Y-%m-%d")
    result = compare_strategies_on_stocks(
        tickers=tickers,
        analysis_date=analysis_date,
        output_json=args.json
    )
    
    if args.json:
        import json
        print(json.dumps(result, indent=2, default=str))
    
    return 0


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

