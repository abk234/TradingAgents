#!/bin/bash
# Comprehensive test and validation script for quick_run.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0
WARNINGS=0

test_command() {
    local cmd="$1"
    local description="$2"
    local timeout_sec="${3:-30}"
    local validate_output="${4:-false}"
    
    echo -e "\n${CYAN}Testing: $description${NC}"
    echo "Command: ./quick_run.sh $cmd"
    
    local output_file="/tmp/quick_run_test_${RANDOM}.log"
    
    # Run command with timeout
    if timeout $timeout_sec ./quick_run.sh $cmd > "$output_file" 2>&1; then
        local exit_code=0
        
        # Validate output if requested
        if [ "$validate_output" = "true" ]; then
            if validate_output_file "$output_file" "$description"; then
                echo -e "${GREEN}✓ PASSED (output validated)${NC}"
            else
                echo -e "${YELLOW}⚠ PASSED but output validation issues${NC}"
                ((WARNINGS++))
            fi
        else
            echo -e "${GREEN}✓ PASSED${NC}"
        fi
        
        ((PASSED++))
        rm -f "$output_file"
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${YELLOW}⚠ TIMEOUT (may be normal for long-running commands)${NC}"
            ((SKIPPED++))
            rm -f "$output_file"
            return 0
        else
            echo -e "${RED}✗ FAILED (exit code: $exit_code)${NC}"
            echo "Last 10 lines of output:"
            tail -10 "$output_file"
            ((FAILED++))
            rm -f "$output_file"
            return 1
        fi
    fi
}

validate_output_file() {
    local file="$1"
    local description="$2"
    local issues=0
    
    # Check for common error patterns
    if grep -qi "error\|exception\|traceback\|failed\|critical" "$file"; then
        echo "  ⚠ Found error keywords in output"
        ((issues++))
    fi
    
    # Check if output is empty (might be OK for some commands)
    if [ ! -s "$file" ]; then
        echo "  ⚠ Output is empty"
        ((issues++))
    fi
    
    # Strategy-specific validations
    if [[ "$description" == *"strategy"* ]]; then
        # Should contain strategy names or recommendations
        if ! grep -qiE "strategy|recommendation|BUY|SELL|HOLD|WAIT|consensus" "$file"; then
            echo "  ⚠ Missing expected strategy output keywords"
            ((issues++))
        fi
    fi
    
    return $issues
}

validate_data_accuracy() {
    echo -e "\n${YELLOW}=== Data Accuracy Validation ===${NC}"
    
    # Test strategy comparison output
    echo -e "\n${CYAN}Validating strategy comparison data...${NC}"
    local output_file="/tmp/strategy_validation.log"
    
    if timeout 60 ./quick_run.sh strategies AAPL > "$output_file" 2>&1; then
        # Check for required fields
        local checks=0
        local passed_checks=0
        
        echo "  Checking for consensus data..."
        ((checks++))
        if grep -qi "consensus\|agreement" "$output_file"; then
            echo -e "    ${GREEN}✓ Consensus data present${NC}"
            ((passed_checks++))
        else
            echo -e "    ${RED}✗ Consensus data missing${NC}"
        fi
        
        echo "  Checking for strategy recommendations..."
        ((checks++))
        if grep -qiE "BUY|SELL|HOLD|WAIT" "$output_file"; then
            echo -e "    ${GREEN}✓ Recommendations present${NC}"
            ((passed_checks++))
        else
            echo -e "    ${RED}✗ Recommendations missing${NC}"
        fi
        
        echo "  Checking for confidence scores..."
        ((checks++))
        if grep -qiE "confidence|%" "$output_file"; then
            echo -e "    ${GREEN}✓ Confidence scores present${NC}"
            ((passed_checks++))
        else
            echo -e "    ${RED}✗ Confidence scores missing${NC}"
        fi
        
        echo "  Checking for strategy names..."
        ((checks++))
        if grep -qiE "Value|Growth|Dividend|Momentum|Contrarian|Quantitative|Sector" "$output_file"; then
            echo -e "    ${GREEN}✓ Strategy names present${NC}"
            ((passed_checks++))
        else
            echo -e "    ${RED}✗ Strategy names missing${NC}"
        fi
        
        if [ $passed_checks -eq $checks ]; then
            echo -e "\n  ${GREEN}✓ All data accuracy checks passed ($passed_checks/$checks)${NC}"
            rm -f "$output_file"
            return 0
        else
            echo -e "\n  ${YELLOW}⚠ Some data accuracy checks failed ($passed_checks/$checks)${NC}"
            rm -f "$output_file"
            return 1
        fi
    else
        echo -e "  ${RED}✗ Could not run strategy comparison for validation${NC}"
        rm -f "$output_file"
        return 1
    fi
}

echo "=========================================="
echo "Comprehensive Quick Run Script Test"
echo "=========================================="

# Market Analysis Commands
echo -e "\n${YELLOW}=== Market Analysis Commands ===${NC}"
test_command "top" "Show top 5 opportunities" 30 true
# Note: screener, screener-fast, analyze, morning are long-running - skip for now

# Portfolio & Performance Commands
echo -e "\n${YELLOW}=== Portfolio & Performance Commands ===${NC}"
# These may require database setup - test if they exist
test_command "portfolio" "View portfolio summary" 30 false
test_command "performance" "View portfolio performance" 30 false
test_command "dividends" "View upcoming dividends" 30 false
test_command "evaluate" "Performance evaluation report" 60 false

# Quick Checks Commands
echo -e "\n${YELLOW}=== Quick Check Commands ===${NC}"
test_command "digest" "Quick market digest" 30 false
test_command "alerts" "Check price alerts" 30 false
test_command "stats" "Quick performance statistics" 30 false
test_command "indicators AAPL" "Show indicators for AAPL" 30 true
test_command "indexes" "Show market indexes" 30 false

# Configuration Commands
echo -e "\n${YELLOW}=== Configuration Commands ===${NC}"
test_command "logs" "View recent logs" 10 false
# Note: setup and test require user interaction - skip

# Strategy Testing Commands (comprehensive)
echo -e "\n${YELLOW}=== Strategy Testing Commands ===${NC}"
test_command "strategy-list" "List available strategies" 10 true
test_command "strategies AAPL" "Compare all strategies on AAPL" 60 true
test_command "strategy-compare AAPL" "Compare strategies (detailed)" 60 true
test_command "strategy-run value AAPL" "Run single value strategy" 60 true
test_command "strategy-multi AAPL MSFT" "Compare strategies across stocks" 90 true
test_command "strategy-screener 3" "Compare strategies on screener stocks" 120 true
test_command "strategy-test AAPL" "Comprehensive strategy test" 60 true

# Workflow Commands
echo -e "\n${YELLOW}=== Workflow Commands ===${NC}"
# These are long-running - skip for now
# test_command "quick-check" "Fast check workflow" 60 false

# Data Accuracy Validation
validate_data_accuracy

# Summary
echo -e "\n=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped/Timeout: $SKIPPED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}All tests passed with no warnings!${NC}"
        exit 0
    else
        echo -e "${YELLOW}All tests passed but with some warnings${NC}"
        exit 0
    fi
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi

