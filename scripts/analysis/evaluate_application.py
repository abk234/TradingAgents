#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
TradingAgents Application Evaluation
Tests functionality, efficiency, and accuracy
"""

import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

# Set chromadb environment variables
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich import box

console = Console()

def check_prerequisites():
    """Check if all prerequisites are met."""
    console.print("\n[cyan]Checking Prerequisites...[/cyan]\n")
    
    checks = {
        "PostgreSQL": False,
        "ChromaDB": False,
        "Ollama": False,
        "Python Packages": False
    }
    
    # Check PostgreSQL
    try:
        from tradingagents.database import get_db_connection
        db = get_db_connection()
        result = db.execute_query("SELECT 1", fetch_one=True)
        if result:
            checks["PostgreSQL"] = True
            console.print("[green]✓ PostgreSQL connected[/green]")
            
            # Get table counts
            ticker_count = db.get_table_count("tickers")
            analysis_count = db.get_table_count("analyses")
            console.print(f"   Tickers: {ticker_count}, Analyses: {analysis_count}")
    except Exception as e:
        console.print(f"[red]✗ PostgreSQL: {e}[/red]")
    
    # Check ChromaDB
    try:
        import chromadb
        from chromadb.config import Settings
        client = chromadb.Client(Settings(anonymized_telemetry=False))
        collections = client.list_collections()
        checks["ChromaDB"] = True
        console.print(f"[green]✓ ChromaDB connected ({len(collections)} collections)[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ ChromaDB: {e}[/yellow]")
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            checks["Ollama"] = True
            console.print(f"[green]✓ Ollama running ({len(models)} models available)[/green]")
        else:
            console.print("[red]✗ Ollama not responding[/red]")
    except Exception as e:
        console.print(f"[red]✗ Ollama: {e}[/red]")
        console.print("[yellow]   Start with: ollama serve[/yellow]")
    
    # Check Python packages
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        checks["Python Packages"] = True
        console.print("[green]✓ Python packages installed[/green]")
    except Exception as e:
        console.print(f"[red]✗ Python packages: {e}[/red]")
    
    return checks

def run_analysis_evaluation(ticker="SPY", use_fast=True):
    """Run analysis and evaluate performance."""
    console.print(f"\n[cyan]Running Analysis: {ticker}[/cyan]\n")
    
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "ollama"
    config["backend_url"] = "http://localhost:11434/v1"
    config["deep_think_llm"] = "llama3.3"
    config["quick_think_llm"] = "llama3.1"
    
    # Use fewer analysts for faster test
    analysts = ["market", "news", "fundamentals"] if use_fast else ["market", "social", "news", "fundamentals"]
    
    start_time = time.time()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Initializing...", total=100)
            
            # Initialize
            progress.update(task, description="Creating TradingAgentsGraph...")
            graph = TradingAgentsGraph(
                selected_analysts=analysts,
                debug=False,
                config=config,
                enable_rag=True
            )
            progress.update(task, advance=20, description="Graph initialized")
            
            # Run analysis
            progress.update(task, advance=20, description="Running analysis...")
            final_state, decision = graph.propagate(
                ticker,
                date.today().strftime("%Y-%m-%d"),
                store_analysis=True
            )
            
            progress.update(task, completed=100, description="Complete!")
        
        elapsed = time.time() - start_time
        
        # Evaluate results
        return {
            "success": True,
            "elapsed_time": elapsed,
            "decision": decision,
            "final_state": final_state,
            "ticker": ticker
        }
        
    except Exception as e:
        console.print(f"\n[red]✗ Analysis failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return {"success": False, "error": str(e)}

def evaluate_results(results):
    """Evaluate analysis results."""
    if not results.get("success"):
        return None
    
    console.print("\n[cyan]Evaluation Results:[/cyan]\n")
    
    final_state = results["final_state"]
    elapsed = results["elapsed_time"]
    
    # Create evaluation table
    eval_table = Table(title="Performance Metrics", box=box.ROUNDED, show_header=True)
    eval_table.add_column("Metric", style="cyan", width=25)
    eval_table.add_column("Value", style="green", width=20)
    eval_table.add_column("Status", style="yellow", width=15)
    
    # Time evaluation
    if elapsed < 60:
        time_status = "✓ Excellent"
    elif elapsed < 180:
        time_status = "✓ Good"
    elif elapsed < 300:
        time_status = "⚠ Acceptable"
    else:
        time_status = "⚠ Slow"
    eval_table.add_row("Execution Time", f"{elapsed:.1f} seconds", time_status)
    
    # Decision evaluation
    decision = results["decision"]
    eval_table.add_row("Decision Generated", decision[:50] + "..." if len(decision) > 50 else decision, "✓")
    
    # Report completeness
    reports = {
        "Market Report": final_state.get("market_report"),
        "News Report": final_state.get("news_report"),
        "Fundamentals Report": final_state.get("fundamentals_report"),
        "Investment Plan": final_state.get("investment_plan"),
        "Trader Plan": final_state.get("trader_investment_plan"),
        "Final Decision": final_state.get("final_trade_decision")
    }
    
    complete = sum(1 for v in reports.values() if v and len(str(v)) > 50)
    total = len(reports)
    completeness = (complete / total) * 100
    
    if completeness >= 80:
        comp_status = "✓ Excellent"
    elif completeness >= 60:
        comp_status = "✓ Good"
    else:
        comp_status = "⚠ Incomplete"
    
    eval_table.add_row("Report Completeness", f"{completeness:.0f}% ({complete}/{total})", comp_status)
    
    # RAG status
    has_rag = final_state.get("historical_context") is not None
    eval_table.add_row("RAG Enhancement", "Enabled" if has_rag else "Disabled", "✓" if has_rag else "⚠")
    
    # Report lengths
    total_chars = sum(len(str(v)) for v in reports.values() if v)
    eval_table.add_row("Total Content", f"{total_chars:,} characters", "✓" if total_chars > 1000 else "⚠")
    
    console.print(eval_table)
    
    # Detailed report status
    console.print("\n[cyan]Report Details:[/cyan]\n")
    detail_table = Table(box=box.SIMPLE, show_header=True)
    detail_table.add_column("Report", style="cyan")
    detail_table.add_column("Length", style="green")
    detail_table.add_column("Status", style="yellow")
    
    for name, content in reports.items():
        if content:
            length = len(str(content))
            status = "✓" if length > 100 else "⚠"
            detail_table.add_row(name, f"{length:,} chars", status)
        else:
            detail_table.add_row(name, "0 chars", "✗")
    
    console.print(detail_table)
    
    return {
        "elapsed_time": elapsed,
        "completeness": completeness,
        "total_content": total_chars,
        "rag_enabled": has_rag
    }

def main():
    """Main evaluation function."""
    console.print(Panel.fit(
        "[bold green]TradingAgents Application Evaluation[/bold green]\n"
        "Testing Functionality, Efficiency, and Accuracy",
        border_style="green"
    ))
    
    # Check prerequisites
    checks = check_prerequisites()
    
    if not checks.get("Ollama"):
        console.print("\n[red]Cannot proceed without Ollama. Please start it first.[/red]")
        console.print("[yellow]Command: ollama serve[/yellow]")
        return
    
    # Run analysis
    results = run_analysis_evaluation("SPY", use_fast=True)
    
    if results.get("success"):
        evaluation = evaluate_results(results)
        
        # Summary
        console.print("\n[cyan]Summary:[/cyan]")
        summary_table = Table(box=box.SIMPLE, show_header=False)
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Status", style="green")
        
        summary_table.add_row("PostgreSQL", "✓ Connected" if checks.get("PostgreSQL") else "✗ Failed")
        summary_table.add_row("ChromaDB", "✓ Connected" if checks.get("ChromaDB") else "⚠ Failed")
        summary_table.add_row("Ollama", "✓ Running" if checks.get("Ollama") else "✗ Failed")
        summary_table.add_row("Analysis", "✓ Completed" if results.get("success") else "✗ Failed")
        
        if evaluation:
            summary_table.add_row("Execution Time", f"{evaluation['elapsed_time']:.1f}s")
            summary_table.add_row("Completeness", f"{evaluation['completeness']:.0f}%")
            summary_table.add_row("RAG", "✓ Enabled" if evaluation['rag_enabled'] else "⚠ Disabled")
        
        console.print(summary_table)
        
        console.print("\n[green]✓ Evaluation completed successfully![/green]")
    else:
        console.print("\n[red]✗ Evaluation failed. Check errors above.[/red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Evaluation interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

