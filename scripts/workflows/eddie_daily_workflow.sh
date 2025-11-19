#!/bin/bash

# Eddie Daily Trading Workflow Script
# Automates common daily trading tasks with Eddie
#
# Usage:
#   ./scripts/eddie_daily_workflow.sh [morning|pre-trade|portfolio|full]
#
# Examples:
#   ./scripts/eddie_daily_workflow.sh morning
#   ./scripts/eddie_daily_workflow.sh full

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PORTFOLIO_VALUE="${EDDIE_PORTFOLIO_VALUE:-100000}"
EDDIE_URL="${EDDIE_URL:-http://localhost:8000}"

# Check if Eddie is running
check_eddie_running() {
    if ! curl -s "$EDDIE_URL" > /dev/null 2>&1; then
        echo -e "${RED}❌ Eddie is not running at $EDDIE_URL${NC}"
        echo -e "${YELLOW}Start Eddie with: ./trading_bot.sh${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Eddie is running${NC}"
}

# Morning routine: Market scan and opportunities
morning_routine() {
    echo -e "\n${BLUE}🌅 Morning Routine${NC}"
    echo "=================="
    
    echo -e "\n${YELLOW}1. Checking data freshness...${NC}"
    # This would call Eddie's API - placeholder for now
    echo "   Run in Eddie: 'What data do you have?'"
    
    echo -e "\n${YELLOW}2. Running market screener...${NC}"
    echo "   Run in Eddie: 'What are the best stocks right now?'"
    
    echo -e "\n${YELLOW}3. Checking sector strength...${NC}"
    echo "   Run in Eddie: 'How are sectors doing?'"
    
    echo -e "\n${GREEN}✅ Morning routine complete${NC}"
    echo -e "${BLUE}Next: Review opportunities and run quick checks${NC}"
}

# Pre-trade validation workflow
pre_trade_workflow() {
    local TICKER="${1:-}"
    
    if [ -z "$TICKER" ]; then
        echo -e "${RED}❌ Please provide a ticker symbol${NC}"
        echo "Usage: $0 pre-trade AAPL"
        exit 1
    fi
    
    echo -e "\n${BLUE}🔍 Pre-Trade Validation for $TICKER${NC}"
    echo "======================================"
    
    echo -e "\n${YELLOW}1. Full Analysis...${NC}"
    echo "   Run in Eddie: 'Should I buy $TICKER? Portfolio \$$PORTFOLIO_VALUE'"
    
    echo -e "\n${YELLOW}2. Earnings Risk Check...${NC}"
    echo "   Run in Eddie: 'Check earnings risk for $TICKER'"
    
    echo -e "\n${YELLOW}3. Price Validation...${NC}"
    echo "   Run in Eddie: 'Validate price sources for $TICKER'"
    
    echo -e "\n${YELLOW}4. Data Quality Check...${NC}"
    echo "   Run in Eddie: 'Check data quality for $TICKER'"
    
    echo -e "\n${YELLOW}5. Track Record Review...${NC}"
    echo "   Run in Eddie: 'What did you learn about $TICKER?'"
    
    echo -e "\n${GREEN}✅ Pre-trade validation complete${NC}"
    echo -e "${BLUE}Review all checks before executing trade${NC}"
}

# Portfolio review workflow
portfolio_workflow() {
    echo -e "\n${BLUE}💼 Portfolio Review${NC}"
    echo "==================="
    
    echo -e "\n${YELLOW}1. Portfolio Status...${NC}"
    echo "   Run in Eddie: 'Show my portfolio status'"
    
    echo -e "\n${YELLOW}2. Rebalancing Recommendations...${NC}"
    echo "   Run in Eddie: 'What should I rebalance?'"
    
    echo -e "\n${YELLOW}3. Underperformer Review...${NC}"
    echo "   Check each losing position:"
    echo "   'Should I sell [LOSING_TICKER]?'"
    
    echo -e "\n${YELLOW}4. Winner Review...${NC}"
    echo "   Check each winning position:"
    echo "   'Should I add more to [WINNING_TICKER]?'"
    
    echo -e "\n${GREEN}✅ Portfolio review complete${NC}"
}

# Full daily workflow
full_workflow() {
    echo -e "\n${BLUE}📅 Full Daily Workflow${NC}"
    echo "======================"
    
    morning_routine
    
    echo -e "\n${BLUE}--- After reviewing opportunities ---${NC}"
    echo "For each stock you're interested in:"
    echo "  $0 pre-trade [TICKER]"
    
    portfolio_workflow
    
    echo -e "\n${GREEN}✅ Full workflow complete${NC}"
}

# Generate Eddie conversation template
generate_template() {
    local TICKER="${1:-}"
    local WORKFLOW_TYPE="${2:-full}"
    
    TEMPLATE_FILE="$PROJECT_DIR/docs/eddie_conversation_template.txt"
    
    cat > "$TEMPLATE_FILE" << EOF
# Eddie Conversation Template
# Generated: $(date)

## Morning Routine
1. "What data do you have?"
2. "What are the best stocks right now?"
3. "How are sectors doing?"

## For Each Stock of Interest
1. "What's the news on [TICKER]?"
2. "Show me [TICKER]'s technicals"
3. "Should I buy [TICKER]? Portfolio \$$PORTFOLIO_VALUE"
4. "Check earnings risk for [TICKER]"
5. "Validate price sources for [TICKER]"
6. "Check data quality for [TICKER]"
7. "What did you learn about [TICKER]?"

## Portfolio Review
1. "Show my portfolio status"
2. "What should I rebalance?"
3. "Should I sell [LOSING_TICKER]?"
4. "Should I add more to [WINNING_TICKER]?"

## Notes
- Always validate before trading
- Use position sizing (3-5% typical)
- Set stop losses
- Review track record
EOF
    
    echo -e "${GREEN}✅ Template generated: $TEMPLATE_FILE${NC}"
}

# Main script
main() {
    local COMMAND="${1:-help}"
    
    case "$COMMAND" in
        morning)
            check_eddie_running
            morning_routine
            ;;
        pre-trade)
            check_eddie_running
            pre_trade_workflow "$2"
            ;;
        portfolio)
            check_eddie_running
            portfolio_workflow
            ;;
        full)
            check_eddie_running
            full_workflow
            ;;
        template)
            generate_template "$2" "$3"
            ;;
        help|--help|-h)
            cat << EOF
Eddie Daily Trading Workflow Script

Usage:
    $0 [command] [options]

Commands:
    morning              Run morning routine (market scan)
    pre-trade [TICKER]   Pre-trade validation workflow
    portfolio            Portfolio review workflow
    full                 Full daily workflow (all steps)
    template             Generate conversation template
    help                 Show this help message

Examples:
    $0 morning
    $0 pre-trade AAPL
    $0 portfolio
    $0 full
    $0 template

Environment Variables:
    EDDIE_PORTFOLIO_VALUE    Portfolio value (default: 100000)
    EDDIE_URL                Eddie URL (default: http://localhost:8000)

Note: This script provides workflow guidance. You still need to
      interact with Eddie through the web interface at $EDDIE_URL
EOF
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
            echo "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"

