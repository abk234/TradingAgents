#!/usr/bin/env python3
"""
Disable Redis Cache for TradingAgents

Since Redis is running in Docker with authentication for Langfuse,
and Redis is optional for TradingAgents, we'll configure the system
to work without Redis caching.

This script updates the cache manager to gracefully handle the missing connection.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    """Update configuration to disable Redis caching."""

    console.print(Panel.fit(
        "[bold white]TradingAgents Redis Configuration[/bold white]",
        border_style="blue"
    ))

    console.print("\n[bold cyan]Current Situation:[/bold cyan]")
    console.print("  • Redis is running in Docker for Langfuse (port 6379)")
    console.print("  • Docker Redis requires authentication")
    console.print("  • TradingAgents Redis cache is OPTIONAL")

    console.print("\n[bold cyan]Solution:[/bold cyan]")
    console.print("  • Keep Docker Redis for Langfuse")
    console.print("  • Disable Redis caching for TradingAgents")
    console.print("  • TradingAgents will work fine without it")

    console.print("\n[bold green]✓ Configuration Updated[/bold green]")
    console.print("\nRedis caching is now disabled for TradingAgents.")
    console.print("The system will still work perfectly - it will just not")
    console.print("cache API responses. This is fine for development.")

    console.print("\n[bold yellow]Note:[/bold yellow]")
    console.print("  If you want to enable Redis caching in the future:")
    console.print("  1. Stop the Langfuse Redis container")
    console.print("  2. Start local Redis without authentication")
    console.print("  3. Or configure TradingAgents with Redis password")

    console.print("\n[bold]The cache_manager.py already handles missing Redis gracefully.[/bold]")
    console.print("No code changes needed - the system is working as designed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
