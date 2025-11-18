#!/usr/bin/env python3
"""
Generate Embeddings for Existing Analyses

This script backfills embeddings for analyses that don't have them yet.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from tradingagents.database import get_db_connection
from tradingagents.rag import EmbeddingGenerator
import logging

console = Console()
logging.basicConfig(level=logging.WARNING)  # Suppress info logs for cleaner output


def generate_embeddings_for_analyses():
    """Generate embeddings for all analyses that don't have them."""
    console.print("[bold cyan]Generating Embeddings for Existing Analyses[/bold cyan]\n")

    try:
        # Connect to database and embedding service
        db = get_db_connection()
        generator = EmbeddingGenerator()

        # Test embedding service
        if not generator.test_connection():
            console.print("[red]✗ Ollama embedding service not available[/red]")
            console.print("  Make sure Ollama is running: ollama serve")
            console.print("  And has the model: ollama pull nomic-embed-text")
            return False

        # Get analyses without embeddings
        query = """
            SELECT
                a.analysis_id,
                t.symbol,
                a.analysis_date,
                a.executive_summary,
                a.bull_case,
                a.bear_case,
                a.key_catalysts,
                a.risk_factors,
                a.final_decision
            FROM analyses a
            JOIN tickers t ON a.ticker_id = t.ticker_id
            WHERE a.embedding IS NULL
            ORDER BY a.analysis_date DESC
        """

        analyses = db.execute_dict_query(query) or []

        if not analyses:
            console.print("[green]✓ All analyses already have embeddings![/green]")
            return True

        console.print(f"Found {len(analyses)} analyses without embeddings\n")

        # Generate embeddings with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:

            task = progress.add_task("Generating embeddings...", total=len(analyses))

            success_count = 0
            error_count = 0

            for analysis in analyses:
                # Prepare analysis data for embedding
                analysis_data = {
                    'executive_summary': analysis.get('executive_summary', ''),
                    'bull_case': analysis.get('bull_case', ''),
                    'bear_case': analysis.get('bear_case', ''),
                    'key_catalysts': analysis.get('key_catalysts', []),
                    'risk_factors': analysis.get('risk_factors', []),
                    'final_decision': analysis.get('final_decision', '')
                }

                # Generate embedding
                embedding = generator.embed_analysis(analysis_data)

                if embedding and len(embedding) == 768:
                    # Store embedding in database
                    embedding_str = '[' + ','.join(map(str, embedding)) + ']'

                    update_query = """
                        UPDATE analyses
                        SET embedding = %s::vector
                        WHERE analysis_id = %s
                    """

                    try:
                        db.execute_query(update_query, (embedding_str, analysis['analysis_id']), fetch=False)
                        success_count += 1

                        progress.console.print(
                            f"  ✓ {analysis['symbol']} ({analysis['analysis_date']})",
                            style="green"
                        )
                    except Exception as e:
                        error_count += 1
                        progress.console.print(
                            f"  ✗ {analysis['symbol']}: Database error - {e}",
                            style="red"
                        )
                else:
                    error_count += 1
                    progress.console.print(
                        f"  ✗ {analysis['symbol']}: Failed to generate embedding",
                        style="red"
                    )

                progress.advance(task)

        # Summary
        console.print(f"\n[bold]Results:[/bold]")
        console.print(f"  ✓ Successfully generated: {success_count}")
        if error_count > 0:
            console.print(f"  ✗ Failed: {error_count}")

        return success_count > 0

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def verify_embeddings():
    """Verify that embeddings were created successfully."""
    console.print("\n[bold cyan]Verifying Embeddings...[/bold cyan]\n")

    try:
        db = get_db_connection()

        # Count analyses with embeddings
        result = db.execute_query(
            "SELECT COUNT(*) FROM analyses WHERE embedding IS NOT NULL;",
            fetch_one=True
        )

        if result:
            count = result[0]
            total = db.get_table_count('analyses')

            console.print(f"  Analyses with embeddings: {count}/{total}")

            if count == total:
                console.print("[green]✓ All analyses have embeddings![/green]")
                return True
            elif count > 0:
                console.print(f"[yellow]⚠ {total - count} analyses still missing embeddings[/yellow]")
                return False
            else:
                console.print("[red]✗ No embeddings were generated[/red]")
                return False

        return False

    except Exception as e:
        console.print(f"[red]✗ Verification failed: {e}[/red]")
        return False


def main():
    """Main function."""
    console.print("\n" + "="*60)
    console.print("[bold white]TradingAgents Embedding Generator[/bold white]")
    console.print("="*60 + "\n")

    # Generate embeddings
    success = generate_embeddings_for_analyses()

    if success:
        # Verify embeddings
        verify_embeddings()

        console.print("\n[green]✓ Embedding generation complete![/green]")
        console.print("\n[bold]RAG system is now fully operational.[/bold]")
        console.print("Future analyses will automatically retrieve similar past analyses.")
        return 0
    else:
        console.print("\n[red]✗ Embedding generation failed[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
