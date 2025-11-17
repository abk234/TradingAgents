#!/usr/bin/env python3
"""
TradingAgents Run Script with Default Values (Non-Interactive)

This script runs the TradingAgents application with default values:
- Ticker: SPY
- Date: Today
- Analysts: All 4 (Market, Social, News, Fundamentals)
- Research Depth: Shallow (1 round)
- LLM Provider: Ollama (local)
- Models: llama3.1 (deep), qwen3 (quick)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.RESET):
    """Print colored message."""
    print(f"{color}{message}{Colors.RESET}")

def get_venv_python():
    """Get the path to the virtual environment Python."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def check_ollama():
    """Check if Ollama is running locally."""
    import urllib.request
    try:
        response = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        if response.status == 200:
            print_colored("✅ Ollama is running locally", Colors.GREEN)
            return True
    except Exception:
        pass
    print_colored("⚠️  Ollama is not running on localhost:11434", Colors.YELLOW)
    print_colored("   Please start Ollama: ollama serve", Colors.YELLOW)
    return False

def run_analysis_with_defaults():
    """Run the analysis with default values using Ollama."""
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print_colored("❌ Virtual environment Python not found", Colors.RED)
        print_colored("   Please run: python run.py first", Colors.RED)
        return False
    
    # Check Ollama
    if not check_ollama():
        return False
    
    # Default values
    ticker = "SPY"
    analysis_date = datetime.now().strftime("%Y-%m-%d")
    llm_provider = "Ollama"
    backend_url = "http://localhost:11434/v1"
    # Use models that are actually available and good for trading
    deep_thinker = "llama3.3"  # Most capable for deep thinking
    quick_thinker = "0xroyce/plutus"  # Financial-focused for quick thinking
    research_depth = 1  # Shallow (quick analysis)
    
    print_colored("\n🚀 Starting TradingAgents with Default Values...", Colors.BOLD + Colors.GREEN)
    print_colored("="*60, Colors.CYAN)
    print_colored(f"Ticker: {ticker}", Colors.YELLOW)
    print_colored(f"Date: {analysis_date}", Colors.YELLOW)
    print_colored(f"Analysts: All 4 (Market, Social, News, Fundamentals)", Colors.YELLOW)
    print_colored(f"Research Depth: Shallow ({research_depth} round)", Colors.YELLOW)
    print_colored(f"LLM Provider: {llm_provider}", Colors.YELLOW)
    print_colored(f"Deep Thinker: {deep_thinker}", Colors.YELLOW)
    print_colored(f"Quick Thinker: {quick_thinker}", Colors.YELLOW)
    print_colored("="*60, Colors.CYAN)
    print_colored("", Colors.RESET)
    
    # Create wrapper script that runs with defaults (completely non-interactive)
    wrapper_script = f"""
import os
import sys
from datetime import datetime

# Set chromadb environment variables BEFORE any imports to avoid issues
os.environ.setdefault("CHROMA_SERVER_HOST", "localhost")
os.environ.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
os.environ.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
os.environ.setdefault("CLICKHOUSE_HOST", "localhost")
os.environ.setdefault("CLICKHOUSE_PORT", "8123")

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Import necessary modules (after env vars are set)
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Default values
ticker = "{ticker}"
analysis_date = "{analysis_date}"
llm_provider = "{llm_provider.lower()}"
backend_url = "{backend_url}"
deep_thinker = "{deep_thinker}"
quick_thinker = "{quick_thinker}"
research_depth = {research_depth}

print("\\n" + "="*70)
print("TradingAgents - Non-Interactive Run with Defaults")
print("="*70)
print(f"Ticker: {{ticker}}")
print(f"Date: {{analysis_date}}")
print(f"LLM Provider: {{llm_provider}}")
print(f"Quick Thinker: {{quick_thinker}}")
print(f"Deep Thinker: {{deep_thinker}}")
print(f"Research Depth: {{research_depth}} round(s)")
print("="*70 + "\\n")

# Create config
config = DEFAULT_CONFIG.copy()
config["max_debate_rounds"] = research_depth
config["max_risk_discuss_rounds"] = research_depth
config["quick_think_llm"] = quick_thinker
config["deep_think_llm"] = deep_thinker
config["backend_url"] = backend_url
config["llm_provider"] = llm_provider

print("Initializing TradingAgentsGraph...")
print("(This may take a moment to load models and initialize ChromaDB)\\n")

try:
    # Add progress indicator during initialization
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.spinner import Spinner
    from rich.live import Live
    from rich.text import Text
    import time
    
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
        
        # Call the initialization
        graph = TradingAgentsGraph(
            selected_analysts=["market", "social", "news", "fundamentals"],
            config=config,
            debug=True
        )
    
    elapsed_time = time.time() - start_time
    console.print(f"[green]✅ Graph initialized successfully![/green] [dim](took {{elapsed_time:.1f}} seconds)[/dim]")
    print("")
    print("="*70)
    print("Starting Analysis...")
    print("="*70 + "\\n")
    
    # Run the analysis with progress indicator
    analysis_start = time.time()
    with Live(
        Spinner("dots", text=Text("Running analysis... This may take several minutes.", style="green")), 
        console=console, 
        refresh_per_second=10
    ) as live:
        _, decision = graph.propagate(ticker, analysis_date)
    
    analysis_time = time.time() - analysis_start
    console.print(f"[green]⏱️  Analysis completed in {{analysis_time:.1f}} seconds[/green]")
    print("")
    
    print("\\n" + "="*70)
    print("Analysis Complete!")
    print("="*70)
    print(f"\\nFinal Decision:\\n{{decision}}")
    print("\\n" + "="*70)
    
except Exception as e:
    print(f"\\n❌ Error during analysis: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    wrapper_path = Path("_run_with_defaults.py")
    with open(wrapper_path, "w") as f:
        f.write(wrapper_script)
    
    # Prepare environment
    env = os.environ.copy()
    env.setdefault("CHROMA_SERVER_HOST", "localhost")
    env.setdefault("CHROMA_SERVER_HTTP_PORT", "8000")
    env.setdefault("CHROMA_SERVER_GRPC_PORT", "50051")
    env.setdefault("CLICKHOUSE_HOST", "localhost")
    env.setdefault("CLICKHOUSE_PORT", "8123")
    
    try:
        # Run the analysis
        result = subprocess.run(
            [str(venv_python), str(wrapper_path)],
            env=env,
            cwd=Path(__file__).parent
        )
        
        return result.returncode == 0
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Analysis interrupted by user", Colors.YELLOW)
        return True
    except Exception as e:
        print_colored(f"\n❌ Failed to run analysis: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up wrapper
        if wrapper_path.exists():
            wrapper_path.unlink()

def main():
    """Main function."""
    print_colored("""
    ╔══════════════════════════════════════════════════════════╗
    ║     TradingAgents - Run with Default Values (Ollama)        ║
    ║     Multi-Agents LLM Financial Trading Framework            ║
    ╚══════════════════════════════════════════════════════════╝
    """, Colors.BOLD + Colors.CYAN)
    
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    success = run_analysis_with_defaults()
    
    if success:
        print_colored("\n✅ Analysis completed successfully!", Colors.GREEN)
    else:
        print_colored("\n⚠️  Analysis exited with errors", Colors.YELLOW)
        print_colored("   Check the error messages above for details", Colors.YELLOW)
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Setup interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Unexpected error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)

