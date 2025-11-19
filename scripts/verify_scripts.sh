#!/bin/bash
#
# Verify all shell scripts are valid and executable
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

check_script() {
    local script_path=$1
    local script_name=$(basename "$script_path")
    
    # Check if file exists
    if [ ! -f "$script_path" ]; then
        echo -e "${RED}❌ NOT FOUND: $script_path${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Check if executable
    if [ ! -x "$script_path" ]; then
        echo -e "${YELLOW}⚠️  NOT EXECUTABLE: $script_path${NC}"
        chmod +x "$script_path"
        echo -e "${GREEN}   Fixed: Made executable${NC}"
    fi
    
    # Check shebang
    if ! head -n 1 "$script_path" | grep -q "^#!"; then
        echo -e "${RED}❌ NO SHEBANG: $script_path${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
    
    # Check syntax (basic)
    if bash -n "$script_path" 2>/dev/null; then
        echo -e "${GREEN}✅ VALID: $script_path${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ SYNTAX ERROR: $script_path${NC}"
        bash -n "$script_path" 2>&1 | head -3
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "=========================================="
echo "Shell Script Verification"
echo "=========================================="
echo ""

# Find all shell scripts
scripts=$(find "$PROJECT_ROOT" -name "*.sh" -type f | grep -v node_modules | grep -v venv | grep -v ".git" | sort)

total=$(echo "$scripts" | wc -l | tr -d ' ')

echo "Found $total shell scripts"
echo ""

# Check each script
for script in $scripts; do
    check_script "$script"
done

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All scripts are valid!${NC}"
    exit 0
fi

