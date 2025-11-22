# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Progress indicators for TradingAgents initialization and analysis.
"""
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import time
from typing import Callable, Any


def show_initialization_progress(init_func: Callable, *args, **kwargs) -> Any:
    """
    Show a progress indicator while initializing TradingAgentsGraph.
    
    Args:
        init_func: Function to call for initialization (e.g., TradingAgentsGraph.__init__)
        *args: Positional arguments for init_func
        **kwargs: Keyword arguments for init_func
    
    Returns:
        The result of init_func
    """
    console = Console()
    
    # Track initialization steps
    init_steps = [
        "Loading configuration...",
        "Initializing ChromaDB...",
        "Setting up LLM models...",
        "Creating agent graph...",
        "Preparing analysts...",
        "Finalizing setup...",
    ]
    
    start_time = time.time()
    
    # Show progress with steps
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing TradingAgentsGraph...", total=len(init_steps))
        
        # Show each step
        for i, step in enumerate(init_steps):
            progress.update(task, description=step, advance=1)
            time.sleep(0.2)  # Small delay to show progress
        
        # Actually initialize (this is the slow part)
        progress.update(task, description="Creating TradingAgentsGraph...", completed=len(init_steps))
        
        # Call the initialization function
        result = init_func(*args, **kwargs)
    
    elapsed_time = time.time() - start_time
    console.print(f"[green]✅ Graph initialized successfully![/green] [dim](took {elapsed_time:.1f} seconds)[/dim]")
    
    return result


def show_analysis_progress(analysis_func: Callable, *args, **kwargs) -> Any:
    """
    Show a progress indicator while running analysis.
    
    Args:
        analysis_func: Function to call for analysis (e.g., graph.propagate)
        *args: Positional arguments for analysis_func
        **kwargs: Keyword arguments for analysis_func
    
    Returns:
        The result of analysis_func
    """
    console = Console()
    
    analysis_start = time.time()
    
    # Show spinner during analysis
    with Live(
        Spinner("dots", text=Text("Running analysis... This may take several minutes.", style="green")), 
        console=console, 
        refresh_per_second=10
    ) as live:
        result = analysis_func(*args, **kwargs)
    
    analysis_time = time.time() - analysis_start
    console.print(f"[green]⏱️  Analysis completed in {analysis_time:.1f} seconds[/green]")
    
    return result

