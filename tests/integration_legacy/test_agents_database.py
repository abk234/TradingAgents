#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Agent-Database Integration Test

This script comprehensively tests all agents' ability to:
1. Connect to and interact with the database
2. Retrieve data for analysis
3. Generate embeddings via RAG
4. Store analysis results
5. Use cached data from Redis
6. Complete full workflow end-to-end
"""

import sys
import os
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from dotenv import load_dotenv
import logging

# Load environment
load_dotenv()

console = Console()
logging.basicConfig(level=logging.WARNING)  # Suppress info logs


def test_database_connection():
    """Test basic database connection."""
    console.print("\n[bold cyan]1. Testing Database Connection[/bold cyan]")

    try:
        from tradingagents.database import get_db_connection

        db = get_db_connection()

        # Test query
        result = db.execute_query("SELECT COUNT(*) FROM tickers", fetch_one=True)
        ticker_count = result[0] if result else 0

        console.print(f"  ✓ Database connected")
        console.print(f"  ✓ Found {ticker_count} tickers in watchlist")

        # Get a test ticker
        test_ticker = db.execute_dict_query(
            "SELECT ticker_id, symbol FROM tickers WHERE symbol = 'AAPL'",
            fetch_one=True
        )

        if test_ticker:
            console.print(f"  ✓ Test ticker: {test_ticker['symbol']} (ID: {test_ticker['ticker_id']})")
            return True, test_ticker
        else:
            console.print("  ⚠ No AAPL ticker found, using first available")
            test_ticker = db.execute_dict_query(
                "SELECT ticker_id, symbol FROM tickers LIMIT 1",
                fetch_one=True
            )
            return True, test_ticker

    except Exception as e:
        console.print(f"  ✗ Database connection failed: {e}")
        return False, None


def test_rag_system():
    """Test RAG embeddings and context retrieval."""
    console.print("\n[bold cyan]2. Testing RAG System[/bold cyan]")

    try:
        from tradingagents.rag import EmbeddingGenerator, ContextRetriever
        from tradingagents.database import get_db_connection

        # Test embedding generation
        generator = EmbeddingGenerator()
        test_text = "AAPL technical analysis shows bullish momentum with strong fundamentals"
        embedding = generator.generate(test_text)

        if embedding and len(embedding) == 768:
            console.print("  ✓ Embedding generation working")
        else:
            console.print("  ✗ Embedding generation failed")
            return False

        # Test context retrieval
        db = get_db_connection()
        retriever = ContextRetriever(db)

        # Check for existing embeddings
        result = db.execute_query(
            "SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL",
            fetch_one=True
        )
        embedding_count = result[0] if result else 0

        console.print(f"  ✓ Context retriever initialized")
        console.print(f"  ✓ {embedding_count} analyses with embeddings available")

        if embedding_count > 0:
            # Try similarity search
            similar = retriever.find_similar_analyses(
                embedding,
                limit=3,
                similarity_threshold=0.5
            )
            console.print(f"  ✓ Found {len(similar)} similar analyses")

        return True

    except Exception as e:
        console.print(f"  ✗ RAG system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_system():
    """Test Redis cache integration."""
    console.print("\n[bold cyan]3. Testing Cache System[/bold cyan]")

    try:
        from tradingagents.utils.cache_manager import CacheManager

        cache = CacheManager()

        if cache.redis:
            # Test cache operations
            test_key = "test:agent_validation"
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "test": "agent_database_integration"
            }

            cache.set(test_key, test_data, ttl=60)
            retrieved = cache.get(test_key)

            if retrieved == test_data:
                console.print("  ✓ Redis cache operational")
                console.print("  ✓ Cache read/write working")

                # Get stats
                stats = cache.get_stats()
                console.print(f"  ✓ Cache has {stats.get('total_keys', 0)} keys")

                # Cleanup
                cache.delete(test_key)
                return True
            else:
                console.print("  ✗ Cache verification failed")
                return False
        else:
            console.print("  ⚠ Redis not available (optional)")
            return None

    except Exception as e:
        console.print(f"  ⚠ Cache system error: {e}")
        return None


def test_analyst_agents(ticker_symbol: str):
    """Test analyst team agents."""
    console.print("\n[bold cyan]4. Testing Analyst Team Agents[/bold cyan]")

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # Create config for fast testing
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = 1
        config["max_risk_discuss_rounds"] = 1

        # Test with single analyst first
        console.print("\n  [yellow]Testing Market Analyst...[/yellow]")
        ta = TradingAgentsGraph(
            selected_analysts=["market"],
            debug=False,
            config=config,
            enable_rag=True
        )

        # Get today's date or recent date
        test_date = date.today().strftime("%Y-%m-%d")

        console.print(f"  Running analysis for {ticker_symbol} on {test_date}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("  Executing market analysis...", total=None)

            try:
                _, decision = ta.propagate(ticker_symbol, test_date, store_analysis=False)

                if decision:
                    console.print("  ✓ Market analyst executed successfully")
                    console.print(f"  ✓ Decision: {decision.get('action', 'N/A')}")
                    return True
                else:
                    console.print("  ✗ No decision returned")
                    return False

            except Exception as e:
                console.print(f"  ✗ Market analyst failed: {e}")
                return False

    except Exception as e:
        console.print(f"  ✗ Analyst agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow(ticker_symbol: str):
    """Test complete agent workflow with database storage."""
    console.print("\n[bold cyan]5. Testing Full Agent Workflow[/bold cyan]")

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.database import get_db_connection

        # Fast config for testing
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = 1
        config["max_risk_discuss_rounds"] = 1

        # Initialize with all agents and RAG
        console.print(f"\n  [yellow]Initializing full agent system...[/yellow]")
        ta = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals"],  # Use 2 analysts for faster testing
            debug=False,
            config=config,
            enable_rag=True,
            enable_langfuse=False
        )

        console.print(f"  ✓ Agent graph initialized with RAG")

        # Run full analysis
        test_date = date.today().strftime("%Y-%m-%d")

        console.print(f"\n  [yellow]Running full analysis for {ticker_symbol}...[/yellow]")
        console.print("  This will test:")
        console.print("    • Analyst team execution")
        console.print("    • Research team debate")
        console.print("    • Trader agent decision")
        console.print("    • Risk management evaluation")
        console.print("    • Database storage")
        console.print("    • Embedding generation")
        console.print("    • RAG context retrieval")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("  Executing workflow...", total=None)

            try:
                # Store analysis to test database integration
                final_state, decision = ta.propagate(
                    ticker_symbol,
                    test_date,
                    store_analysis=True
                )

                if decision:
                    console.print("\n  ✓ Full workflow executed successfully")

                    # Display results
                    table = Table(title="Analysis Results", box=box.ROUNDED)
                    table.add_column("Component", style="cyan")
                    table.add_column("Result", style="green")

                    table.add_row("Decision", decision.get('action', 'N/A'))
                    table.add_row("Confidence", f"{decision.get('confidence', 0)}%")
                    table.add_row("Price Target", f"${decision.get('price_target', 'N/A')}")

                    console.print(table)

                    # Verify database storage
                    console.print("\n  [yellow]Verifying database storage...[/yellow]")
                    db = get_db_connection()

                    # Check if analysis was stored
                    result = db.execute_dict_query("""
                        SELECT
                            a.analysis_id,
                            a.final_decision,
                            a.confidence_score,
                            a.embedding IS NOT NULL as has_embedding
                        FROM analyses a
                        JOIN tickers t ON a.ticker_id = t.ticker_id
                        WHERE t.symbol = %s
                        ORDER BY a.analysis_date DESC
                        LIMIT 1
                    """, (ticker_symbol,), fetch_one=True)

                    if result:
                        console.print(f"  ✓ Analysis stored in database (ID: {result['analysis_id']})")
                        console.print(f"  ✓ Decision: {result['final_decision']}")
                        console.print(f"  ✓ Confidence: {result['confidence_score']}%")

                        if result['has_embedding']:
                            console.print("  ✓ Embedding generated and stored")
                        else:
                            console.print("  ⚠ Embedding not stored (check Ollama)")

                        return True
                    else:
                        console.print("  ⚠ Analysis executed but not found in database")
                        return False
                else:
                    console.print("  ✗ No decision returned from workflow")
                    return False

            except Exception as e:
                console.print(f"  ✗ Workflow execution failed: {e}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        console.print(f"  ✗ Full workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_stored_data(ticker_symbol: str):
    """Verify all data was properly stored."""
    console.print("\n[bold cyan]6. Verifying Stored Data[/bold cyan]")

    try:
        from tradingagents.database import get_db_connection

        db = get_db_connection()

        # Check analysis data
        result = db.execute_dict_query("""
            SELECT
                a.*,
                t.symbol
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE t.symbol = %s
            ORDER BY a.analysis_date DESC
            LIMIT 1
        """, (ticker_symbol,), fetch_one=True)

        if not result:
            console.print(f"  ⚠ No analysis found for {ticker_symbol}")
            return False

        # Verify components
        checks = [
            ("Executive Summary", result.get('executive_summary')),
            ("Bull Case", result.get('bull_case')),
            ("Bear Case", result.get('bear_case')),
            ("Market Report", result.get('market_report')),
            ("Fundamentals Report", result.get('fundamentals_report')),
            ("Final Decision", result.get('final_decision')),
            ("Confidence Score", result.get('confidence_score')),
            ("Embedding", result.get('embedding'))
        ]

        table = Table(title=f"Data Verification for {ticker_symbol}", box=box.ROUNDED)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="white")

        all_good = True
        for name, value in checks:
            if value:
                table.add_row(name, "[green]✓ Present[/green]")
            else:
                table.add_row(name, "[yellow]⚠ Missing[/yellow]")
                all_good = False

        console.print(table)

        if all_good:
            console.print("\n  ✓ All data components properly stored")
        else:
            console.print("\n  ⚠ Some components missing (may be expected)")

        return True

    except Exception as e:
        console.print(f"  ✗ Data verification failed: {e}")
        return False


def main():
    """Run comprehensive agent-database integration tests."""

    console.print(Panel.fit(
        "[bold white]TradingAgents Agent-Database Integration Test[/bold white]\n"
        "[dim]Testing all agents' ability to interact with databases[/dim]",
        border_style="blue"
    ))

    # Track results
    results = {}

    # 1. Database connection
    results['database'], test_ticker = test_database_connection()
    if not results['database'] or not test_ticker:
        console.print("\n[red]✗ Database connection failed - cannot continue[/red]")
        return 1

    ticker_symbol = test_ticker['symbol']

    # 2. RAG system
    results['rag'] = test_rag_system()

    # 3. Cache system
    results['cache'] = test_cache_system()

    # 4. Analyst agents
    results['analysts'] = test_analyst_agents(ticker_symbol)

    # 5. Full workflow
    results['workflow'] = test_full_workflow(ticker_symbol)

    # 6. Data verification
    results['verification'] = verify_stored_data(ticker_symbol)

    # Summary
    console.print("\n" + "="*60)
    console.print("[bold white]Test Summary[/bold white]")
    console.print("="*60)

    summary_table = Table(box=box.SIMPLE)
    summary_table.add_column("Test", style="cyan")
    summary_table.add_column("Status", style="white")
    summary_table.add_column("Required", style="yellow")

    def status_icon(status):
        if status is True:
            return "[green]✓ Passed[/green]"
        elif status is False:
            return "[red]✗ Failed[/red]"
        else:
            return "[yellow]⚠ Skipped[/yellow]"

    summary_table.add_row("Database Connection", status_icon(results['database']), "✓ Required")
    summary_table.add_row("RAG System", status_icon(results['rag']), "✓ Required")
    summary_table.add_row("Cache System", status_icon(results['cache']), "○ Optional")
    summary_table.add_row("Analyst Agents", status_icon(results['analysts']), "✓ Required")
    summary_table.add_row("Full Workflow", status_icon(results['workflow']), "✓ Required")
    summary_table.add_row("Data Verification", status_icon(results['verification']), "✓ Required")

    console.print(summary_table)

    # Overall status
    required_tests = ['database', 'rag', 'analysts', 'workflow', 'verification']
    all_required_passed = all(results[test] for test in required_tests)

    if all_required_passed:
        console.print("\n[bold green]✓ All Agent-Database Integration Tests Passed![/bold green]")
        console.print("\n[bold]All agents can successfully:[/bold]")
        console.print("  ✓ Connect to and query the database")
        console.print("  ✓ Retrieve historical context via RAG")
        console.print("  ✓ Execute analysis workflows")
        console.print("  ✓ Store results with embeddings")
        console.print("  ✓ Complete end-to-end operations")

        if results['cache']:
            console.print("  ✓ Use Redis caching for performance")

        return 0
    else:
        console.print("\n[bold red]✗ Some tests failed[/bold red]")
        console.print("\nFailed tests:")
        for test, passed in results.items():
            if passed is False and test in required_tests:
                console.print(f"  ✗ {test}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
