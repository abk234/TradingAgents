#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Configure TradingAgents to use Docker Redis

This script configures TradingAgents to connect to the Redis instance
running in Docker (for Langfuse) instead of installing a separate local Redis.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def update_env_file():
    """Add Redis configuration to .env file."""

    env_file = ".env"
    env_example = ".env.example"

    # Redis configuration
    redis_config = """
# ========================================
# Redis Cache Configuration
# ========================================
# Redis URL for caching (using Docker Redis from Langfuse)
REDIS_URL=redis://:myredissecret@localhost:6379/1
# Note: Using database 1 to avoid conflicts with Langfuse (database 0)

# Redis connection settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=myredissecret
REDIS_DB=1
"""

    # Check if .env exists
    if not os.path.exists(env_file):
        # Copy from example
        if os.path.exists(env_example):
            with open(env_example, 'r') as f:
                content = f.read()

            with open(env_file, 'w') as f:
                f.write(content)

            console.print(f"[green]✓ Created .env from .env.example[/green]")
        else:
            # Create new .env
            with open(env_file, 'w') as f:
                f.write(redis_config)

            console.print(f"[green]✓ Created new .env file[/green]")
            return True

    # Check if Redis config already exists
    with open(env_file, 'r') as f:
        content = f.read()

    if 'REDIS_URL' in content or 'REDIS_PASSWORD' in content:
        console.print(f"[yellow]⚠ Redis configuration already exists in .env[/yellow]")

        # Update password if needed
        if 'myredissecret' not in content:
            console.print("[yellow]  Updating Redis password...[/yellow]")

            # Replace or add Redis config
            lines = content.split('\n')
            new_lines = []
            in_redis_section = False
            redis_section_added = False

            for line in lines:
                if '# Redis' in line or 'REDIS_' in line:
                    if not redis_section_added:
                        new_lines.append(redis_config)
                        redis_section_added = True
                    continue
                new_lines.append(line)

            if not redis_section_added:
                new_lines.append(redis_config)

            with open(env_file, 'w') as f:
                f.write('\n'.join(new_lines))

            console.print("[green]✓ Updated Redis configuration[/green]")
        return True

    # Append Redis config
    with open(env_file, 'a') as f:
        f.write('\n' + redis_config)

    console.print(f"[green]✓ Added Redis configuration to .env[/green]")
    return True


def test_docker_redis():
    """Test connection to Docker Redis."""

    console.print("\n[bold cyan]Testing Docker Redis Connection...[/bold cyan]\n")

    try:
        import redis

        # Connect with password
        r = redis.Redis(
            host='localhost',
            port=6379,
            password='myredissecret',
            db=1,  # Use database 1 to avoid conflicts
            decode_responses=True
        )

        # Test ping
        pong = r.ping()

        if pong:
            console.print("[green]✓ Redis ping successful[/green]")

            # Test set/get
            r.set('test:tradingagents', 'connected')
            value = r.get('test:tradingagents')

            if value == 'connected':
                console.print("[green]✓ Redis read/write working[/green]")
                r.delete('test:tradingagents')

                # Get server info
                info = r.info('server')
                console.print(f"\n[bold]Redis Server Info:[/bold]")
                console.print(f"  Version: {info.get('redis_version')}")
                console.print(f"  Mode: {info.get('redis_mode')}")
                console.print(f"  Process ID: {info.get('process_id')}")

                return True
            else:
                console.print("[red]✗ Redis read/write failed[/red]")
                return False
        else:
            console.print("[red]✗ Redis ping failed[/red]")
            return False

    except ImportError:
        console.print("[red]✗ Redis Python module not installed[/red]")
        console.print("  Install with: pip install redis")
        return False
    except redis.exceptions.AuthenticationError as e:
        console.print(f"[red]✗ Authentication failed: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        return False


def update_cache_manager():
    """Update cache_manager.py to use environment variables."""

    cache_file = "tradingagents/utils/cache_manager.py"

    console.print(f"\n[bold cyan]Updating Cache Manager...[/bold cyan]\n")

    try:
        with open(cache_file, 'r') as f:
            content = f.read()

        # Check if already uses env vars
        if 'os.getenv' in content and 'REDIS_' in content:
            console.print("[green]✓ Cache manager already configured for env vars[/green]")
            return True

        # Update the __init__ method to use environment variables
        old_init = 'def __init__(\n        self,\n        redis_url: str = "redis://localhost:6379/0",'

        new_init = '''def __init__(
        self,
        redis_url: str = None,'''

        if old_init in content:
            content = content.replace(old_init, new_init)

            # Add env var reading
            old_redis_line = '        self.redis = None'
            new_redis_block = '''        self.redis = None

        # Get Redis URL from environment if not provided
        if redis_url is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')'''

            if old_redis_line in content and new_redis_block not in content:
                content = content.replace(old_redis_line, new_redis_block)

                # Make sure os is imported
                if 'import os' not in content:
                    content = 'import os\n' + content

                with open(cache_file, 'w') as f:
                    f.write(content)

                console.print("[green]✓ Updated cache_manager.py[/green]")
                return True

        console.print("[yellow]⚠ Cache manager doesn't need updating[/yellow]")
        return True

    except Exception as e:
        console.print(f"[red]✗ Error updating cache manager: {e}[/red]")
        return False


def main():
    """Main configuration function."""

    console.print(Panel.fit(
        "[bold white]Configure TradingAgents for Docker Redis[/bold white]",
        border_style="blue"
    ))

    console.print("\n[bold]Strategy:[/bold]")
    console.print("  • Use existing Redis in Docker (langfuse-redis-1)")
    console.print("  • Password: myredissecret")
    console.print("  • Database: 1 (to avoid conflicts with Langfuse)")
    console.print("  • No local Redis installation needed")

    # Update .env
    console.print("\n" + "="*60)
    console.print("[bold]Step 1: Update Environment Configuration[/bold]")
    console.print("="*60)

    if update_env_file():
        console.print("[green]✓ Environment configured[/green]")
    else:
        console.print("[red]✗ Failed to update environment[/red]")
        return 1

    # Test connection
    console.print("\n" + "="*60)
    console.print("[bold]Step 2: Test Docker Redis Connection[/bold]")
    console.print("="*60)

    if test_docker_redis():
        console.print("[green]✓ Docker Redis connection working[/green]")
    else:
        console.print("[red]✗ Docker Redis connection failed[/red]")
        console.print("\nMake sure the Docker Redis container is running:")
        console.print("  docker ps | grep redis")
        return 1

    # Update cache manager
    console.print("\n" + "="*60)
    console.print("[bold]Step 3: Update Cache Manager[/bold]")
    console.print("="*60)

    if update_cache_manager():
        console.print("[green]✓ Cache manager configured[/green]")
    else:
        console.print("[yellow]⚠ Cache manager update skipped[/yellow]")

    # Success summary
    console.print("\n" + "="*60)
    console.print("[bold green]✓ Configuration Complete![/bold green]")
    console.print("="*60)

    console.print("\n[bold]TradingAgents is now configured to use Docker Redis.[/bold]")
    console.print("\nBenefits:")
    console.print("  ✓ No local Redis installation needed")
    console.print("  ✓ Shared infrastructure with Langfuse")
    console.print("  ✓ API responses will be cached for faster queries")
    console.print("  ✓ Reduced API rate limit usage")

    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  1. Restart any running TradingAgents processes")
    console.print("  2. Redis caching will work automatically")
    console.print("  3. Monitor cache: redis-cli -a myredissecret MONITOR")

    return 0


if __name__ == "__main__":
    sys.exit(main())
