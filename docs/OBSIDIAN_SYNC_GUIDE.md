# Obsidian Sync Guide

## Overview

This guide explains how to sync all TradingAgents documentation to your Obsidian vault in a single organized folder under `projects/TradingAgents/`.

## Quick Sync

### Option 1: Python Script (Recommended)
```bash
python sync_to_obsidian.py
```

### Option 2: Bash Script
```bash
./sync_to_obsidian.sh
```

## What It Does

1. **Finds Your Obsidian Vault**
   - Automatically searches common locations
   - Lets you select if multiple vaults found
   - Allows manual path entry if needed

2. **Creates Projects Folder**
   - Creates `projects/` folder in your vault (if it doesn't exist)
   - Creates `projects/TradingAgents/` folder

3. **Syncs All Documentation**
   - Copies all markdown files from `obsidian_docs/`
   - Preserves folder structure
   - Creates main README.md index

4. **Organizes Everything**
   - All documentation in one place: `projects/TradingAgents/`
   - Maintains wiki-link structure
   - Ready to use in Obsidian

## Folder Structure in Obsidian

After syncing, your Obsidian vault will have:

```
your-vault/
└── projects/
    └── TradingAgents/
        ├── README.md              # Main index
        ├── Features/
        │   ├── Overview.md
        │   └── Core-Features.md
        ├── CLI-Commands/
        │   ├── Main-CLI.md
        │   ├── Screener.md
        │   ├── Analyzer.md
        │   ├── Portfolio.md
        │   ├── Evaluation.md
        │   ├── Insights.md
        │   └── Dividends.md
        ├── Agents/
        │   └── Analyst-Team.md
        ├── Configuration/
        │   └── LLM-Providers.md
        └── Examples/
            └── Basic-Usage.md
```

## Using in Obsidian

1. **Open Obsidian**
2. **Open your vault** (the one you selected during sync)
3. **Navigate to**: `projects/TradingAgents/`
4. **Start with**: `README.md` for the main index
5. **Use wiki links**: Click any `[[Link]]` to navigate

## Features

### Automatic Vault Detection
The script searches:
- `~/Documents`
- `~/Desktop`
- `~/Dropbox`
- `~/OneDrive`
- iCloud Obsidian folder
- `$OBSIDIAN_VAULT_PATH` environment variable

### Safe Sync
- **Backup**: Creates backup if folder exists
- **Overwrite option**: Choose to overwrite or backup
- **Preserves structure**: Maintains folder hierarchy

### Wiki Links
All documentation uses Obsidian wiki-link format:
- `[[Features/Overview]]` - Links to other notes
- `[[CLI-Commands/Main-CLI]]` - Cross-references
- Easy navigation in Obsidian

## Manual Sync (Alternative)

If you prefer to sync manually:

1. **Locate your Obsidian vault**
2. **Create folder**: `projects/TradingAgents/`
3. **Copy contents**: Copy everything from `obsidian_docs/` to the new folder
4. **Open in Obsidian**: Navigate to the folder

## Troubleshooting

### Vault Not Found
- Run script and enter path manually
- Or set `OBSIDIAN_VAULT_PATH` environment variable:
  ```bash
  export OBSIDIAN_VAULT_PATH="/path/to/your/vault"
  ```

### Permission Errors
- Make sure you have write access to the vault
- Check vault location permissions

### Files Not Showing
- Refresh Obsidian (Cmd+R / Ctrl+R)
- Check if files are in correct location
- Verify `.obsidian/config.json` exists in vault root

## Re-syncing

To update documentation:
1. Run sync script again
2. Choose to overwrite or backup existing folder
3. All files will be updated

## Benefits

✅ **Single Location**: All docs in one folder  
✅ **Easy Navigation**: Wiki links for quick access  
✅ **Organized**: Clear folder structure  
✅ **Searchable**: Full-text search in Obsidian  
✅ **Graph View**: Visualize connections  
✅ **Version Control**: Can use Git with Obsidian  

---

**Created**: 2025-01-16  
**Scripts**: `sync_to_obsidian.py`, `sync_to_obsidian.sh`

