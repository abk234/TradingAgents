#!/usr/bin/env python3
"""
Database Status Verification Script

Tests all databases used by TradingAgents:
1. PostgreSQL (main relational database)
2. PostgreSQL Vector Extension (for RAG embeddings)
3. Redis (optional caching layer)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from tradingagents.database import get_db_connection
from tradingagents.rag import EmbeddingGenerator

console = Console()


def test_postgresql():
    """Test PostgreSQL main database connection and tables."""
    console.print("\n[bold cyan]Testing PostgreSQL Database...[/bold cyan]")

    try:
        db = get_db_connection()

        # Test connection
        result = db.execute_query("SELECT version();", fetch_one=True)
        if result:
            console.print(f"✓ [green]PostgreSQL connected[/green]")
            console.print(f"  Version: {result[0].split(',')[0]}")

        # Check key tables
        tables_to_check = [
            'tickers', 'daily_scans', 'analyses', 'daily_prices',
            'portfolio_holdings', 'portfolio_snapshots', 'price_cache'
        ]

        table = Table(title="PostgreSQL Tables", box=box.ROUNDED)
        table.add_column("Table", style="cyan")
        table.add_column("Row Count", style="green", justify="right")
        table.add_column("Status", style="yellow")

        for table_name in tables_to_check:
            if db.table_exists(table_name):
                count = db.get_table_count(table_name)
                status = "✓ Active" if count > 0 else "⚠ Empty"
                table.add_row(table_name, str(count), status)
            else:
                table.add_row(table_name, "N/A", "✗ Missing")

        console.print(table)

        # Check connection pool stats
        stats = db.get_pool_stats()
        if stats:
            console.print(f"\n[bold]Connection Pool Stats:[/bold]")
            console.print(f"  Active connections: {stats.get('active_connections', 0)}")
            console.print(f"  Available connections: {stats.get('available_connections', 0)}")
            console.print(f"  Utilization: {stats.get('utilization_pct', 0):.1f}%")

        return True

    except Exception as e:
        console.print(f"✗ [red]PostgreSQL connection failed: {e}[/red]")
        return False


def test_vector_extension():
    """Test PostgreSQL vector extension (pgvector) for RAG."""
    console.print("\n[bold cyan]Testing Vector Extension (RAG)...[/bold cyan]")

    try:
        db = get_db_connection()

        # Check if pgvector extension is installed
        result = db.execute_query(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');",
            fetch_one=True
        )

        if result and result[0]:
            console.print("✓ [green]pgvector extension installed[/green]")

            # Check if analyses table has embedding column
            result = db.execute_query(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'analyses' AND column_name = 'embedding';
                """,
                fetch_one=True
            )

            if result:
                console.print(f"✓ [green]Embedding column exists[/green]")
                console.print(f"  Type: {result[1]}")

                # Count analyses with embeddings
                result = db.execute_query(
                    "SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL;",
                    fetch_one=True
                )

                if result:
                    count = result[0]
                    console.print(f"  Analyses with embeddings: {count}")

                    if count > 0:
                        console.print("✓ [green]RAG system operational[/green]")
                        return True
                    else:
                        console.print("⚠ [yellow]RAG ready but no embeddings yet[/yellow]")
                        return True
            else:
                console.print("✗ [red]Embedding column not found[/red]")
                return False
        else:
            console.print("✗ [red]pgvector extension not installed[/red]")
            console.print("  To install: CREATE EXTENSION IF NOT EXISTS vector;")
            return False

    except Exception as e:
        console.print(f"✗ [red]Vector extension check failed: {e}[/red]")
        return False


def test_embedding_service():
    """Test Ollama embedding service."""
    console.print("\n[bold cyan]Testing Embedding Service (Ollama)...[/bold cyan]")

    try:
        generator = EmbeddingGenerator()

        # Test connection
        if generator.test_connection():
            console.print("✓ [green]Ollama embedding service operational[/green]")
            console.print(f"  Model: {generator.model}")
            console.print(f"  Base URL: {generator.base_url}")

            # Test embedding generation
            embedding = generator.generate("Test query")
            if embedding and len(embedding) == 768:
                console.print(f"  Embedding dimensions: {len(embedding)}")
                console.print("✓ [green]Embedding generation working[/green]")
                return True
            else:
                console.print("✗ [red]Invalid embedding dimensions[/red]")
                return False
        else:
            console.print("✗ [red]Ollama service not responding[/red]")
            console.print("  Make sure Ollama is running and has nomic-embed-text model")
            console.print("  Run: ollama pull nomic-embed-text")
            return False

    except Exception as e:
        console.print(f"✗ [red]Embedding service test failed: {e}[/red]")
        return False


def test_redis_cache():
    """Test Redis cache (optional)."""
    console.print("\n[bold cyan]Testing Redis Cache (Optional)...[/bold cyan]")

    try:
        from tradingagents.utils.cache_manager import CacheManager, REDIS_AVAILABLE
        from dotenv import load_dotenv

        # Load .env to get Redis configuration
        load_dotenv()

        if not REDIS_AVAILABLE:
            console.print("⚠ [yellow]Redis Python module not installed (optional)[/yellow]")
            console.print("  Install with: pip install redis")
            return None

        cache = CacheManager()

        if cache.redis:
            # Test set/get
            test_key = "test:status"
            test_value = {"status": "operational"}

            cache.set(test_key, test_value, ttl=60)
            retrieved = cache.get(test_key)

            if retrieved == test_value:
                console.print("✓ [green]Redis cache operational (Docker)[/green]")

                # Get connection info
                try:
                    connection_info = cache.redis.connection_pool.connection_kwargs
                    host = connection_info.get('host', 'unknown')
                    port = connection_info.get('port', 'unknown')
                    db = connection_info.get('db', 0)
                    console.print(f"  Connection: {host}:{port} (database {db})")
                except:
                    console.print("  Connection: Docker Redis")

                # Clean up test key
                cache.delete(test_key)
                return True
            else:
                console.print("✗ [red]Redis get/set test failed[/red]")
                return False
        else:
            console.print("⚠ [yellow]Redis connection failed (optional)[/yellow]")
            console.print("  Using Docker Redis? Check .env has REDIS_URL configured")
            console.print("  Run: python connect_docker_redis.py")
            return None

    except ImportError:
        console.print("⚠ [yellow]Redis module not installed (optional)[/yellow]")
        console.print("  Install with: pip install redis")
        return None
    except Exception as e:
        console.print(f"⚠ [yellow]Redis not available: {e}[/yellow]")
        return None


def main():
    """Run all database tests."""
    console.print(Panel.fit(
        "[bold white]TradingAgents Database Status Check[/bold white]",
        border_style="blue"
    ))

    results = {}

    # Test each database/service
    results['postgresql'] = test_postgresql()
    results['vector_extension'] = test_vector_extension()
    results['embedding_service'] = test_embedding_service()
    results['redis_cache'] = test_redis_cache()

    # Summary
    console.print("\n" + "=" * 60)
    console.print("[bold white]Summary[/bold white]")
    console.print("=" * 60)

    summary_table = Table(box=box.SIMPLE)
    summary_table.add_column("Component", style="cyan")
    summary_table.add_column("Status", style="white")
    summary_table.add_column("Required", style="yellow")

    def status_icon(status):
        if status is True:
            return "[green]✓ Operational[/green]"
        elif status is False:
            return "[red]✗ Failed[/red]"
        else:
            return "[yellow]⚠ Optional/Not Available[/yellow]"

    summary_table.add_row(
        "PostgreSQL Database",
        status_icon(results['postgresql']),
        "✓ Required"
    )
    summary_table.add_row(
        "Vector Extension (RAG)",
        status_icon(results['vector_extension']),
        "✓ Required for RAG"
    )
    summary_table.add_row(
        "Embedding Service (Ollama)",
        status_icon(results['embedding_service']),
        "✓ Required for RAG"
    )
    summary_table.add_row(
        "Redis Cache",
        status_icon(results['redis_cache']),
        "○ Optional"
    )

    console.print(summary_table)

    # Overall status
    required_ok = results['postgresql'] and results['vector_extension']

    if required_ok:
        console.print("\n[bold green]✓ All required databases operational![/bold green]")
        if results['embedding_service']:
            console.print("[bold green]✓ RAG system fully operational![/bold green]")
        else:
            console.print("[yellow]⚠ RAG embeddings service needs attention[/yellow]")
    else:
        console.print("\n[bold red]✗ Some required databases need attention[/bold red]")
        console.print("\nFix issues above before running TradingAgents.")

    return 0 if required_ok else 1


if __name__ == "__main__":
    sys.exit(main())
