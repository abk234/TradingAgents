#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Test and Evaluate TradingAgents Application
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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.database import get_db_connection

console = Console()

def test_database_connection():
    """Test database connectivity."""
    console.print("\n[cyan]Testing Database Connection...[/cyan]")
    try:
        db = get_db_connection()
        # Test query
        result = db.execute_query("SELECT 1", fetch_one=True)
        if result:
            console.print("[green]✓ PostgreSQL database connected[/green]")
            return True
    except Exception as e:
        console.print(f"[red]✗ Database connection failed: {e}[/red]")
        return False

def test_chromadb():
    """Test ChromaDB connectivity."""
    console.print("\n[cyan]Testing ChromaDB...[/cyan]")
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.Client(Settings(anonymized_telemetry=False))
        collections = client.list_collections()
        console.print(f"[green]✓ ChromaDB connected (found {len(collections)} collections)[/green]")
        return True
    except Exception as e:
        console.print(f"[yellow]⚠ ChromaDB test failed: {e}[/yellow]")
        return False

def test_ollama():
    """Test Ollama connection."""
    console.print("\n[cyan]Testing Ollama...[/cyan]")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            console.print(f"[green]✓ Ollama connected (found {len(models)} models)[/green]")
            if model_names:
                console.print(f"   Models: {', '.join(model_names[:5])}")
            return True
    except Exception as e:
        console.print(f"[red]✗ Ollama connection failed: {e}[/red]")
        console.print("[yellow]   Make sure Ollama is running: ollama serve[/yellow]")
        return False

def run_analysis_test(ticker="SPY", analysis_date=None):
    """Run a test analysis and measure performance."""
    if analysis_date is None:
        analysis_date = date.today().strftime("%Y-%m-%d")
    
    console.print(f"\n[cyan]Running Analysis Test: {ticker} on {analysis_date}[/cyan]")
    
    # Create config
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "ollama"
    config["backend_url"] = "http://localhost:11434/v1"
    config["deep_think_llm"] = "llama3.3"
    config["quick_think_llm"] = "llama3.1"
    
    start_time = time.time()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Initializing TradingAgentsGraph...", total=None)
            
            # Initialize graph
            graph = TradingAgentsGraph(
                selected_analysts=["market", "news", "fundamentals"],  # Skip social for speed
                debug=False,
                config=config,
                enable_rag=True
            )
            
            progress.update(task, description="Running analysis...")
            
            # Run analysis
            final_state, decision = graph.propagate(
                ticker,
                analysis_date,
                store_analysis=True
            )
            
            elapsed_time = time.time() - start_time
            
            progress.update(task, completed=True, description="Analysis complete!")
            
            # Extract results
            results = {
                "ticker": ticker,
                "date": analysis_date,
                "decision": decision,
                "elapsed_time": elapsed_time,
                "final_state": final_state
            }
            
            return results
            
    except Exception as e:
        console.print(f"[red]✗ Analysis failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return None

def evaluate_results(results):
    """Evaluate analysis results."""
    if not results:
        return None
    
    console.print("\n[cyan]Evaluation Results:[/cyan]\n")
    
    # Create evaluation table
    eval_table = Table(title="Analysis Evaluation", box=box.ROUNDED)
    eval_table.add_column("Metric", style="cyan")
    eval_table.add_column("Value", style="green")
    eval_table.add_column("Status", style="yellow")
    
    # Time evaluation
    elapsed = results["elapsed_time"]
    if elapsed < 60:
        time_status = "✓ Fast"
    elif elapsed < 180:
        time_status = "✓ Acceptable"
    else:
        time_status = "⚠ Slow"
    eval_table.add_row("Execution Time", f"{elapsed:.1f} seconds", time_status)
    
    # Decision evaluation
    decision = results["decision"]
    eval_table.add_row("Decision", decision, "✓ Generated")
    
    # State completeness
    final_state = results["final_state"]
    reports = {
        "Market Report": final_state.get("market_report"),
        "News Report": final_state.get("news_report"),
        "Fundamentals Report": final_state.get("fundamentals_report"),
        "Investment Plan": final_state.get("investment_plan"),
        "Trader Plan": final_state.get("trader_investment_plan"),
        "Final Decision": final_state.get("final_trade_decision")
    }
    
    complete_reports = sum(1 for v in reports.values() if v)
    total_reports = len(reports)
    completeness = (complete_reports / total_reports) * 100
    
    if completeness >= 80:
        completeness_status = "✓ Excellent"
    elif completeness >= 60:
        completeness_status = "✓ Good"
    else:
        completeness_status = "⚠ Incomplete"
    
    eval_table.add_row("Report Completeness", f"{completeness:.0f}% ({complete_reports}/{total_reports})", completeness_status)
    
    # RAG evaluation
    has_rag = final_state.get("historical_context") is not None
    rag_status = "✓ Enabled" if has_rag else "⚠ Disabled"
    eval_table.add_row("RAG Enhancement", "Yes" if has_rag else "No", rag_status)
    
    console.print(eval_table)
    
    # Detailed reports
    console.print("\n[cyan]Generated Reports:[/cyan]\n")
    for name, content in reports.items():
        if content:
            length = len(content)
            status = "✓" if length > 100 else "⚠"
            console.print(f"  {status} {name}: {length} characters")
        else:
            console.print(f"  ✗ {name}: Missing")
    
    return {
        "elapsed_time": elapsed,
        "decision": decision,
        "completeness": completeness,
        "rag_enabled": has_rag
    }

def main():
    """Main test function."""
    console.print(Panel.fit(
        "[bold green]TradingAgents Application Test & Evaluation[/bold green]",
        border_style="green"
    ))
    
    # Test 1: Database Connection
    db_ok = test_database_connection()
    
    # Test 2: ChromaDB
    chroma_ok = test_chromadb()
    
    # Test 3: Ollama
    ollama_ok = test_ollama()
    
    if not ollama_ok:
        console.print("\n[red]Cannot proceed without Ollama. Please start it with: ollama serve[/red]")
        return
    
    # Test 4: Run Analysis
    console.print("\n[cyan]Starting Analysis Test...[/cyan]")
    results = run_analysis_test("SPY", date.today().strftime("%Y-%m-%d"))
    
    if results:
        evaluation = evaluate_results(results)
        
        # Summary
        console.print("\n[cyan]Summary:[/cyan]")
        summary_table = Table(box=box.SIMPLE)
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Status", style="green")
        
        summary_table.add_row("PostgreSQL Database", "✓ Connected" if db_ok else "✗ Failed")
        summary_table.add_row("ChromaDB", "✓ Connected" if chroma_ok else "⚠ Failed")
        summary_table.add_row("Ollama", "✓ Connected" if ollama_ok else "✗ Failed")
        summary_table.add_row("Analysis Execution", "✓ Completed" if results else "✗ Failed")
        
        if evaluation:
            summary_table.add_row("Report Completeness", f"{evaluation['completeness']:.0f}%")
            summary_table.add_row("Execution Time", f"{evaluation['elapsed_time']:.1f}s")
        
        console.print(summary_table)
    else:
        console.print("\n[red]Analysis test failed. Check errors above.[/red]")

if __name__ == "__main__":
    main()

