# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Interactive Menu for Command Selection

Provides an interactive menu interface for selecting and executing generated commands.
"""

from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def show_command_menu(commands: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Display an interactive menu of commands and allow user to select.
    
    Args:
        commands: Dictionary mapping category names to lists of commands
        
    Returns:
        List of selected command strings, or None if cancelled
    """
    if not commands:
        return None
    
    # Flatten commands into a numbered list
    all_commands = []
    command_map = {}  # Map menu number to command string
    
    menu_number = 1
    for category, cmd_list in commands.items():
        for cmd in cmd_list:
            all_commands.append((menu_number, category, cmd))
            command_map[menu_number] = cmd
            menu_number += 1
    
    if not all_commands:
        return None
    
    # Display menu
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🚀 Quick Actions Menu[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    # Create table for better formatting
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Number", style="bold cyan", width=6)
    table.add_column("Category", style="yellow", width=20)
    table.add_column("Command", style="white")
    
    current_category = None
    for num, category, cmd in all_commands:
        # Show category header when it changes
        if category != current_category:
            current_category = category
            # Add spacing row
            if num > 1:
                table.add_row("", "", "")
        
        # Format category name
        category_display = category.replace('_', ' ').title()
        
        # Truncate command if too long
        cmd_display = cmd
        if len(cmd_display) > 70:
            cmd_display = cmd_display[:67] + "..."
        
        table.add_row(f"[{num}]", category_display, cmd_display)
    
    console.print(table)
    console.print()
    
    # Get user input
    try:
        selection = console.input(
            "[bold cyan]Select commands (comma-separated numbers, e.g., 1,3,5) or 'q' to quit: [/bold cyan]"
        ).strip()
        
        if selection.lower() in ['q', 'quit', 'exit', '']:
            return None
        
        # Parse selections
        selected_numbers = []
        for part in selection.split(','):
            part = part.strip()
            try:
                num = int(part)
                if num in command_map:
                    selected_numbers.append(num)
            except ValueError:
                continue
        
        if not selected_numbers:
            console.print("[yellow]No valid selections made.[/yellow]")
            return None
        
        # Return selected commands
        selected_commands = [command_map[num] for num in selected_numbers]
        return selected_commands
        
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Cancelled.[/yellow]")
        return None


def execute_commands(commands: List[str]) -> None:
    """
    Execute a list of commands.
    
    Args:
        commands: List of command strings to execute
    """
    if not commands:
        return
    
    console.print()
    console.print("[bold green]Executing selected commands...[/bold green]")
    console.print()
    
    import subprocess
    import sys
    
    for i, cmd in enumerate(commands, 1):
        console.print(f"[cyan][{i}/{len(commands)}][/cyan] [dim]{cmd}[/dim]")
        console.print()
        
        try:
            # Extract the actual command (remove comments)
            cmd_clean = cmd.split('#')[0].strip()
            
            # Execute command
            result = subprocess.run(
                cmd_clean,
                shell=True,
                check=False,
                capture_output=False
            )
            
            if result.returncode != 0:
                console.print(f"[yellow]Command returned exit code {result.returncode}[/yellow]")
            
            console.print()
            
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
            console.print()
    
    console.print("[bold green]✓ Command execution complete![/bold green]")
    console.print()

