#!/bin/bash

################################################################################
# Quick Run - Fast access to common TradingAgents operations
#
# Usage: ./quick_run.sh [command]
#
# No arguments = show menu
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Show usage
show_usage() {
    echo -e "${CYAN}${BOLD}TradingAgents Quick Run${NC}\n"
    echo "Usage: ./quick_run.sh [command]"
    echo ""
    echo -e "${YELLOW}Available Commands:${NC}"
    echo ""
    echo -e "${GREEN}Market Analysis:${NC}"
    echo "  screener          - Run screener with sector analysis (top 10)"
    echo "  screener-fast     - Fast screener (no news, optimized)"
    echo "  analyze TICKER    - Analyze specific stock (AI-powered)"
    echo "  morning           - Full morning briefing"
    echo ""
    echo -e "${GREEN}Portfolio & Performance:${NC}"
    echo "  portfolio         - View portfolio summary"
    echo "  performance       - View portfolio performance"
    echo "  dividends         - View upcoming dividends"
    echo "  evaluate          - Performance evaluation report"
    echo ""
    echo -e "${GREEN}Quick Checks:${NC}"
    echo "  digest            - Quick market digest"
    echo "  alerts            - Check price alerts"
    echo "  top               - Show top 5 opportunities"
    echo "  stats             - Quick performance statistics"
    echo ""
    echo -e "${GREEN}Configuration:${NC}"
    echo "  setup             - Configure notifications"
    echo "  test              - Test notifications"
    echo "  logs              - View recent logs"
    echo ""
    echo -e "${GREEN}Workflows:${NC}"
    echo "  full-analysis     - Complete analysis (screener + briefing + eval)"
    echo "  quick-check       - Fast check (digest + top stocks)"
    echo "  portfolio-review  - Complete portfolio review"
    echo ""
    echo -e "${BLUE}Interactive Mode:${NC}"
    echo "  interactive       - Launch full interactive shell"
    echo ""
}

# Change to script directory
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ -d ".venv" ]; then
    VENV_PATH=".venv"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
else
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please create a virtual environment (.venv or venv) first."
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR"

# Parse command
COMMAND=${1:-""}

case "$COMMAND" in
    # Market Analysis
    "screener")
        echo -e "${CYAN}Running screener with sector analysis...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener run --sector-analysis --top 10
        ;;

    "screener-fast")
        echo -e "${CYAN}Running fast screener...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener run --fast --top 10
        ;;

    "analyze")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide a ticker symbol${NC}"
            echo "Usage: ./quick_run.sh analyze AAPL"
            exit 1
        fi
        echo -e "${CYAN}Analyzing $2...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.analyze "$2" --plain-english --portfolio-value 100000
        ;;

    "morning")
        echo -e "${CYAN}Running morning briefing...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights morning
        ;;

    # Portfolio & Performance
    "portfolio")
        echo -e "${CYAN}Portfolio Summary:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.portfolio view
        ;;

    "performance")
        echo -e "${CYAN}Portfolio Performance:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.portfolio performance
        ;;

    "dividends")
        echo -e "${CYAN}Upcoming Dividends:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.dividends upcoming
        ;;

    "evaluate")
        echo -e "${CYAN}Performance Evaluation:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.evaluate report
        ;;

    # Quick Checks
    "digest")
        echo -e "${CYAN}Market Digest:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights digest
        ;;

    "alerts")
        echo -e "${CYAN}Price Alerts:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights alerts
        ;;

    "top")
        echo -e "${CYAN}Top 5 Opportunities:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener top 5
        ;;

    "stats")
        echo -e "${CYAN}Performance Statistics:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.evaluate stats
        ;;

    # Configuration
    "setup")
        echo -e "${CYAN}Launching notification setup...${NC}\n"
        ./trading_interactive.sh
        ;;

    "test")
        echo -e "${CYAN}Testing notifications...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights notify \
            --message "Test notification from TradingAgents! 🚀 If you're seeing this, notifications are working." \
            --title "TradingAgents Test" \
            --priority MEDIUM \
            --channels terminal,log,email,webhook

        if [ $? -eq 0 ]; then
            echo -e "\n${GREEN}✓ Test notification sent!${NC}"
            echo "Check your email and Slack/Discord channels."
        else
            echo -e "\n${RED}✗ Failed to send notification${NC}"
            echo "Check your .env configuration."
        fi
        ;;

    "logs")
        echo -e "${CYAN}Recent Session Logs:${NC}\n"
        if [ -d "logs" ] && [ "$(ls -A logs/session_*.log 2>/dev/null)" ]; then
            tail -n 50 "$(ls -t logs/session_*.log | head -1)"
        else
            echo -e "${YELLOW}No session logs found${NC}"
        fi
        ;;

    # Workflows
    "full-analysis")
        echo -e "${CYAN}${BOLD}Running Full Analysis Workflow${NC}\n"
        echo -e "${YELLOW}Step 1/3: Market Screener${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener run --sector-analysis --top 10
        echo ""
        echo -e "${YELLOW}Step 2/3: Morning Briefing${NC}"
        $VENV_PATH/bin/python -m tradingagents.insights morning
        echo ""
        echo -e "${YELLOW}Step 3/3: Performance Evaluation${NC}"
        $VENV_PATH/bin/python -m tradingagents.evaluate update
        $VENV_PATH/bin/python -m tradingagents.evaluate report
        echo ""
        echo -e "${GREEN}${BOLD}✓ Full analysis complete!${NC}"
        ;;

    "quick-check")
        echo -e "${CYAN}${BOLD}Quick Market Check${NC}\n"
        echo -e "${YELLOW}Step 1/2: Market Digest${NC}"
        $VENV_PATH/bin/python -m tradingagents.insights digest
        echo ""
        echo -e "${YELLOW}Step 2/2: Top Opportunities${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener top 5
        echo ""
        echo -e "${GREEN}${BOLD}✓ Quick check complete!${NC}"
        ;;

    "portfolio-review")
        echo -e "${CYAN}${BOLD}Complete Portfolio Review${NC}\n"
        echo -e "${YELLOW}Step 1/3: Portfolio Summary${NC}"
        $VENV_PATH/bin/python -m tradingagents.portfolio view
        echo ""
        echo -e "${YELLOW}Step 2/3: Performance History${NC}"
        $VENV_PATH/bin/python -m tradingagents.portfolio performance
        echo ""
        echo -e "${YELLOW}Step 3/3: Upcoming Dividends${NC}"
        $VENV_PATH/bin/python -m tradingagents.dividends upcoming
        echo ""
        echo -e "${GREEN}${BOLD}✓ Portfolio review complete!${NC}"
        ;;

    # Interactive Mode
    "interactive")
        ./trading_interactive.sh
        ;;

    # Help or no command
    "help"|"--help"|"-h"|"")
        show_usage
        ;;

    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}\n"
        show_usage
        exit 1
        ;;
esac
