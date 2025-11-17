#!/usr/bin/env python3
"""
Quick Test - Run a simple analysis to evaluate functionality
"""

import os
import sys
import time
from datetime import date

# Set chromadb environment variables
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

console = Console()

def main():
    console.print(Panel.fit(
        "[bold green]TradingAgents Quick Test[/bold green]\n"
        "Testing functionality, efficiency, and accuracy",
        border_style="green"
    ))
    
    # Create config
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "ollama"
    config["backend_url"] = "http://localhost:11434/v1"
    config["deep_think_llm"] = "llama3.3"
    config["quick_think_llm"] = "llama3.1"
    
    console.print("\n[cyan]Initializing TradingAgentsGraph...[/cyan]")
    start_init = time.time()
    
    try:
        graph = TradingAgentsGraph(
            selected_analysts=["market", "news", "fundamentals"],  # Skip social for speed
            debug=False,
            config=config,
            enable_rag=True
        )
        init_time = time.time() - start_init
        console.print(f"[green]✓ Initialized in {init_time:.1f} seconds[/green]")
        
        console.print("\n[cyan]Running analysis on SPY...[/cyan]")
        start_analysis = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing...", total=None)
            
            final_state, decision = graph.propagate(
                "SPY",
                date.today().strftime("%Y-%m-%d"),
                store_analysis=True
            )
            
            progress.update(task, completed=True)
        
        analysis_time = time.time() - start_analysis
        total_time = time.time() - start_init
        
        # Evaluate
        console.print("\n[cyan]Results:[/cyan]")
        console.print(f"  Decision: [green]{decision}[/green]")
        console.print(f"  Analysis Time: [cyan]{analysis_time:.1f} seconds[/cyan]")
        console.print(f"  Total Time: [cyan]{total_time:.1f} seconds[/cyan]")
        
        # Check completeness
        reports = {
            "Market": final_state.get("market_report"),
            "News": final_state.get("news_report"),
            "Fundamentals": final_state.get("fundamentals_report"),
            "Investment Plan": final_state.get("investment_plan"),
            "Trader Plan": final_state.get("trader_investment_plan"),
            "Final Decision": final_state.get("final_trade_decision")
        }
        
        complete = sum(1 for v in reports.values() if v)
        console.print(f"  Reports Generated: [green]{complete}/{len(reports)}[/green]")
        
        # Show decision
        console.print(f"\n[bold]Final Decision:[/bold]")
        console.print(Panel(final_state.get("final_trade_decision", "N/A"), border_style="green"))
        
        console.print("\n[green]✓ Test completed successfully![/green]")
        
    except Exception as e:
        console.print(f"\n[red]✗ Test failed: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

if __name__ == "__main__":
    main()

