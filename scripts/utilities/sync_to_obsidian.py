#!/usr/bin/env python3
# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
TradingAgents → Obsidian Sync Script
Organizes and syncs all documentation to Obsidian vault's projects folder
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime

def find_obsidian_vaults():
    """Find all Obsidian vaults on the system."""
    vaults = []
    
    # Common locations
    locations = [
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path.home() / "Dropbox",
        Path.home() / "OneDrive",
        Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents",
    ]
    
    # Check environment variable
    if os.getenv("OBSIDIAN_VAULT_PATH"):
        locations.insert(0, Path(os.getenv("OBSIDIAN_VAULT_PATH")))
    
    for location in locations:
        if location.exists():
            # Find .obsidian folders (indicates a vault)
            for obsidian_config in location.rglob(".obsidian/config.json"):
                vault_path = obsidian_config.parent.parent
                if vault_path not in vaults:
                    vaults.append(vault_path)
    
    return vaults

def select_vault(vaults):
    """Let user select a vault."""
    if not vaults:
        print("No Obsidian vaults found automatically.")
        vault_path = input("Enter path to your Obsidian vault: ").strip()
        vault_path = Path(vault_path).expanduser()
        
        if not vault_path.exists():
            print(f"Error: Directory does not exist: {vault_path}")
            return None
        
        if not (vault_path / ".obsidian" / "config.json").exists():
            confirm = input("Warning: .obsidian/config.json not found. Continue? (y/n): ")
            if confirm.lower() != 'y':
                return None
        
        return vault_path
    
    if len(vaults) == 1:
        print(f"Found vault: {vaults[0]}")
        return vaults[0]
    
    print(f"Found {len(vaults)} vaults:")
    for i, vault in enumerate(vaults, 1):
        print(f"  {i}) {vault}")
    
    while True:
        try:
            choice = int(input(f"Select vault [1-{len(vaults)}]: "))
            if 1 <= choice <= len(vaults):
                return vaults[choice - 1]
            print("Invalid selection")
        except ValueError:
            print("Please enter a number")

def sync_documentation(source_dir, target_dir):
    """Sync all documentation files to target directory."""
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory not found: {source_path}")
        return False
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Copy all files, preserving structure
    files_copied = 0
    for file_path in source_path.rglob("*"):
        if file_path.is_file() and file_path.name != ".DS_Store":
            relative_path = file_path.relative_to(source_path)
            target_file = target_path / relative_path
            
            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, target_file)
            files_copied += 1
    
    return files_copied

def create_main_index(target_dir):
    """Create a main README.md in the target directory."""
    readme_content = f"""# TradingAgents - Complete Documentation

Welcome to the TradingAgents documentation in Obsidian!

## 📚 Quick Navigation

### Core Documentation
- [[Features/Overview|Features Overview]]
- [[Features/Core-Features|Core Features]]

### CLI Commands
- [[CLI-Commands/Main-CLI|Main CLI]]
- [[CLI-Commands/Screener|Screener]]
- [[CLI-Commands/Analyzer|Analyzer]]
- [[CLI-Commands/Portfolio|Portfolio]]
- [[CLI-Commands/Evaluation|Evaluation]]
- [[CLI-Commands/Insights|Insights]]
- [[CLI-Commands/Dividends|Dividends]]

### Agents
- [[Agents/Analyst-Team|Analyst Team]]

### Configuration
- [[Configuration/LLM-Providers|LLM Providers]]

### Examples
- [[Examples/Basic-Usage|Basic Usage]]

## 🚀 Quick Start

Use the interactive shell:
```bash
./trading_agents.sh
```

## 📝 Project Location

This documentation is located in: `projects/TradingAgents/`

---

*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    readme_path = Path(target_dir) / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)

def main():
    """Main sync function."""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     TradingAgents → Obsidian Sync Script                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Find vaults
    print("Searching for Obsidian vaults...")
    vaults = find_obsidian_vaults()
    
    # Select vault
    vault_path = select_vault(vaults)
    if not vault_path:
        print("No vault selected. Exiting.")
        return
    
    print(f"\nSelected vault: {vault_path}")
    print()
    
    # Create projects folder if it doesn't exist
    projects_folder = vault_path / "projects"
    projects_folder.mkdir(exist_ok=True)
    
    # Target folder
    target_folder = projects_folder / "TradingAgents"
    
    # Check if folder exists
    if target_folder.exists():
        overwrite = input("Folder 'TradingAgents' already exists. Overwrite? (y/n): ")
        if overwrite.lower() == 'y':
            print("Removing existing folder...")
            shutil.rmtree(target_folder)
        else:
            # Create backup
            backup_folder = target_folder.parent / f"TradingAgents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Creating backup: {backup_folder}")
            shutil.move(str(target_folder), str(backup_folder))
    
    # Source directory
    script_dir = Path(__file__).parent
    source_dir = script_dir / "obsidian_docs"
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return
    
    # Sync files
    print("Copying documentation files...")
    files_copied = sync_documentation(source_dir, target_folder)
    
    if files_copied:
        # Create main index
        create_main_index(target_folder)
        
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    Sync Complete!                           ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        print(f"✓ Copied {files_copied} files")
        print(f"✓ Location: {target_folder}")
        print()
        print("Next steps:")
        print(f"  1. Open Obsidian")
        print(f"  2. Open vault: {vault_path}")
        print(f"  3. Navigate to: projects/TradingAgents/")
        print(f"  4. Start with: README.md")
        print()
        print("All documentation is now organized in a single folder!")
    else:
        print("Error: No files were copied")

if __name__ == "__main__":
    main()

