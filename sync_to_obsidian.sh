#!/bin/bash
# Script to sync TradingAgents documentation to Obsidian vault

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${GREEN}TradingAgents → Obsidian Sync Script${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to find Obsidian vaults
find_obsidian_vaults() {
    local vaults=()
    
    # Common locations
    local locations=(
        "$HOME/Documents"
        "$HOME/Desktop"
        "$HOME/Dropbox"
        "$HOME/OneDrive"
        "$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents"
    )
    
    for location in "${locations[@]}"; do
        if [ -d "$location" ]; then
            while IFS= read -r -d '' vault; do
                if [ -f "$vault/.obsidian/config.json" ]; then
                    vaults+=("$vault")
                fi
            done < <(find "$location" -maxdepth 2 -name ".obsidian" -type d -print0 2>/dev/null)
        fi
    done
    
    # Also check if user has a specific vault path
    if [ -n "$OBSIDIAN_VAULT_PATH" ]; then
        if [ -d "$OBSIDIAN_VAULT_PATH" ] && [ -f "$OBSIDIAN_VAULT_PATH/.obsidian/config.json" ]; then
            vaults+=("$OBSIDIAN_VAULT_PATH")
        fi
    fi
    
    printf '%s\n' "${vaults[@]}"
}

# Find available vaults
echo -e "${YELLOW}Searching for Obsidian vaults...${NC}"
vaults=($(find_obsidian_vaults))

if [ ${#vaults[@]} -eq 0 ]; then
    echo -e "${RED}No Obsidian vaults found automatically.${NC}"
    echo -e "${YELLOW}Please enter the path to your Obsidian vault:${NC}"
    read -r vault_path
    
    if [ ! -d "$vault_path" ]; then
        echo -e "${RED}Error: Directory does not exist: $vault_path${NC}"
        exit 1
    fi
    
    if [ ! -f "$vault_path/.obsidian/config.json" ]; then
        echo -e "${YELLOW}Warning: .obsidian/config.json not found. This might not be an Obsidian vault.${NC}"
        echo -e "${YELLOW}Continue anyway? (y/n):${NC} "
        read -r confirm
        if [ "$confirm" != "y" ]; then
            exit 1
        fi
    fi
    
    selected_vault="$vault_path"
elif [ ${#vaults[@]} -eq 1 ]; then
    selected_vault="${vaults[0]}"
    echo -e "${GREEN}Found vault: $selected_vault${NC}"
else
    echo -e "${GREEN}Found ${#vaults[@]} vaults:${NC}"
    for i in "${!vaults[@]}"; do
        echo -e "  ${BLUE}$((i+1)))${NC} ${vaults[$i]}"
    done
    echo ""
    echo -ne "${YELLOW}Select vault [1-${#vaults[@]}]: ${NC}"
    read -r choice
    
    if [ "$choice" -ge 1 ] && [ "$choice" -le ${#vaults[@]} ]; then
        selected_vault="${vaults[$((choice-1))]}"
    else
        echo -e "${RED}Invalid selection${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}Selected vault: $selected_vault${NC}"
echo ""

# Check if projects folder exists, create if not
projects_folder="$selected_vault/projects"
if [ ! -d "$projects_folder" ]; then
    echo -e "${YELLOW}Creating 'projects' folder in vault...${NC}"
    mkdir -p "$projects_folder"
fi

# Target folder for TradingAgents
target_folder="$projects_folder/TradingAgents"

# Ask user if they want to overwrite existing folder
if [ -d "$target_folder" ]; then
    echo -e "${YELLOW}Folder 'TradingAgents' already exists in projects.${NC}"
    echo -ne "${YELLOW}Overwrite? (y/n): ${NC}"
    read -r overwrite
    
    if [ "$overwrite" = "y" ]; then
        echo -e "${YELLOW}Removing existing folder...${NC}"
        rm -rf "$target_folder"
    else
        echo -e "${YELLOW}Creating backup...${NC}"
        backup_folder="${target_folder}_backup_$(date +%Y%m%d_%H%M%S)"
        mv "$target_folder" "$backup_folder"
        echo -e "${GREEN}Backup created: $backup_folder${NC}"
    fi
fi

# Create target folder
mkdir -p "$target_folder"

echo ""
echo -e "${YELLOW}Copying documentation files...${NC}"

# Copy all markdown files from obsidian_docs
if [ -d "obsidian_docs" ]; then
    # Use rsync to preserve structure
    rsync -av --exclude='.DS_Store' obsidian_docs/ "$target_folder/"
    echo -e "${GREEN}✓ Documentation files copied${NC}"
else
    echo -e "${RED}Error: obsidian_docs folder not found${NC}"
    exit 1
fi

# Create a main index file at the root
cat > "$target_folder/README.md" << 'EOF'
# TradingAgents - Complete Documentation

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

*Last synced: $(date)*
EOF

# Replace the date placeholder
sed -i '' "s/\$(date)/$(date)/" "$target_folder/README.md" 2>/dev/null || \
sed -i "s/\$(date)/$(date)/" "$target_folder/README.md"

# Count files
file_count=$(find "$target_folder" -type f -name "*.md" | wc -l | tr -d ' ')

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                    ${BLUE}Sync Complete!${NC}                        ${GREEN}║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Copied $file_count markdown files${NC}"
echo -e "${GREEN}✓ Location: $target_folder${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Open Obsidian"
echo -e "  2. Open vault: $selected_vault"
echo -e "  3. Navigate to: ${BLUE}projects/TradingAgents/${NC}"
echo -e "  4. Start with: ${BLUE}README.md${NC}"
echo ""
echo -e "${GREEN}All documentation is now organized in a single folder!${NC}"

