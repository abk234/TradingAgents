#!/bin/bash
#
# Script Runner - Run any script from organized structure
#
# Usage:
#   ./scripts/bin/run.sh [category] [script_name]
#   ./scripts/bin/run.sh list                    # List all scripts
#   ./scripts/bin/run.sh main quick_run          # Run quick_run.sh from main
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script categories
CATEGORIES=("main" "workflows" "maintenance" "development" "utilities")

list_scripts() {
    echo -e "${BLUE}Available Scripts:${NC}\n"
    
    for category in "${CATEGORIES[@]}"; do
        category_dir="$SCRIPT_DIR/../$category"
        if [ -d "$category_dir" ]; then
            scripts=$(find "$category_dir" -name "*.sh" -type f | sort)
            if [ -n "$scripts" ]; then
                echo -e "${GREEN}$category:${NC}"
                for script in $scripts; do
                    script_name=$(basename "$script")
                    echo "  - $script_name"
                done
                echo ""
            fi
        fi
    done
}

run_script() {
    local category=$1
    local script_name=$2
    
    # Add .sh if not present
    if [[ ! "$script_name" == *.sh ]]; then
        script_name="${script_name}.sh"
    fi
    
    script_path="$SCRIPT_DIR/../$category/$script_name"
    
    if [ ! -f "$script_path" ]; then
        echo -e "${YELLOW}Error: Script not found: $script_path${NC}"
        echo "Use 'list' to see available scripts"
        return 1
    fi
    
    # Make executable
    chmod +x "$script_path"
    
    # Run script
    echo -e "${GREEN}Running: $category/$script_name${NC}"
    cd "$PROJECT_ROOT"
    exec "$script_path" "${@:3}"
}

# Main logic
if [ $# -eq 0 ] || [ "$1" == "list" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Script Runner - Run scripts from organized structure"
    echo ""
    echo "Usage:"
    echo "  $0 list                              # List all scripts"
    echo "  $0 [category] [script_name] [args]  # Run script"
    echo ""
    list_scripts
    exit 0
fi

if [ $# -lt 2 ]; then
    echo "Error: Category and script name required"
    echo "Usage: $0 [category] [script_name] [args]"
    echo "Use '$0 list' to see available scripts"
    exit 1
fi

run_script "$@"

