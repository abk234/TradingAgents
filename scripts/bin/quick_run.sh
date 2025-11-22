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
    echo "  dividend-income   - Find best stocks for living off dividends (top 20)"
    echo "                     Use --details for detailed breakdown"
    echo "                     Use --top N to show N results"
    echo "  analyze TICKER    - Analyze specific stock (AI-powered)"
    echo "                     Use --refresh-data to fetch fresh data first"
    echo "  morning           - Full morning briefing"
    echo ""
    echo -e "${GREEN}Portfolio & Performance:${NC}"
    echo "  portfolio         - View portfolio summary"
    echo "                     Use --refresh to refresh portfolio prices"
    echo "  performance       - View portfolio performance"
    echo "                     Use --refresh to refresh portfolio prices"
    echo "  dividends         - View upcoming dividends"
    echo "                     Use --refresh-data to fetch fresh dividend data"
    echo "  evaluate          - Performance evaluation report"
    echo ""
    echo -e "${GREEN}Quick Checks:${NC}"
    echo "  digest            - Quick market digest"
    echo "                     Use --refresh to refresh underlying data"
    echo "  alerts            - Check price alerts"
    echo "                     Use --refresh to refresh price data"
    echo "  top [N]           - Show top N opportunities (default: 5)"
    echo "                     Use --refresh to run fresh screener scan"
    echo "                     Use --min-rr X to filter by R/R ratio (e.g., --min-rr 2.0)"
    echo "  stats             - Quick performance statistics"
    echo ""
    echo -e "${GREEN}Trading Metrics:${NC}"
    echo "  professional      - Show professional-grade trades (R/R >= 2.0)"
    echo "                     Use --min-rr X to change minimum R/R"
    echo "  excellent         - Show excellent trades (R/R >= 3.0)"
    echo "  setups [N]        - Detailed trade setups with position sizing (default: 10)"
    echo "                     Use --account X --risk Y for custom sizing"
    echo "  position TICKER   - Calculate position size for specific stock"
    echo "                     Use --account X --risk Y for custom sizing"
    echo "  trade-summary     - Today's actionable trades summary"
    echo "  indicators [TICK...] - Show all indicators (or for specific ticker(s))"
    echo "                         Can specify multiple tickers: indicators AAPL MSFT GOOGL"
    echo "                         Multiple tickers show comparison table (easier to scan)"
    echo "                         Use --detailed to show full breakdown for each ticker"
    echo "                         Use --refresh to recalculate indicators"
    echo "                         Use --refresh-data to fetch fresh data first"
    echo "  indexes           - Show market indexes and regime analysis"
    echo "                     Use --refresh to force refresh index data"
    echo ""
    echo -e "${GREEN}Configuration:${NC}"
    echo "  setup             - Configure notifications"
    echo "  test              - Test notifications"
    echo "  logs              - View recent logs"
    echo ""
    echo -e "${GREEN}Strategy Testing:${NC}"
    echo "  strategies TICKER        - Compare all strategies on a stock"
    echo "  strategy-compare TICKER  - Compare all strategies (detailed)"
    echo "  strategy-multi TICKERS   - Compare strategies across multiple stocks"
    echo "  strategy-run NAME TICKER - Run single strategy (value/growth/etc)"
    echo "  strategy-list            - List all available strategies"
    echo "  strategy-screener [N]   - Compare strategies on top N screener stocks (default: 20)"
    echo "  strategy-screener-full [N] - Run screener + compare strategies on top N stocks (default: 20)"
    echo ""
    echo -e "${GREEN}Workflows:${NC}"
    echo "  full-analysis     - Comprehensive analysis (9 steps: indexes, screener, setups,"
    echo "                     dividends, indicators, briefing, portfolio, performance)"
    echo "  quick-check       - Fast check (digest + top stocks)"
    echo "  portfolio-review  - Complete portfolio review"
    echo "  strategy-test TICKER - Comprehensive strategy comparison"
    echo ""
    echo -e "${BLUE}Interactive Mode:${NC}"
    echo "  interactive       - Launch full interactive shell"
    echo ""
}

# Change to script directory
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ -d "venv" ]; then
    VENV_PATH="venv"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
else
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please create a virtual environment (venv or venv) first."
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR"

# Parse command
COMMAND=${1:-""}

case "$COMMAND" in
    # Market Analysis
    "screener")
        echo -e "${CYAN}Running screener with sector analysis...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener run --sector-analysis --top 20
        ;;

    "screener-fast")
        echo -e "${CYAN}Running fast screener...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener run --fast --top 10
        ;;

    "dividend-income")
        # Parse arguments for dividend income screener
        TOP_N=20
        DETAILS_FLAG=""
        shift  # Remove 'dividend-income' command

        for arg in "$@"; do
            case "$arg" in
                --details)
                    DETAILS_FLAG="--details"
                    ;;
                --top)
                    shift
                    TOP_N="$1"
                    ;;
                --top=*)
                    TOP_N="${arg#*=}"
                    ;;
            esac
        done

        echo -e "${CYAN}${BOLD}Finding Best Dividend Income Stocks...${NC}\n"
        echo -e "${YELLOW}Scanning for stocks suitable for living off dividends${NC}"
        echo -e "${YELLOW}Minimum criteria: 2.5%+ yield, 3+ years dividend history${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener.dividend_income_main --top "$TOP_N" $DETAILS_FLAG
        ;;

    "analyze")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide a ticker symbol${NC}"
            echo "Usage: ./quick_run.sh analyze AAPL [--refresh-data]"
            exit 1
        fi
        TICKER="$2"
        REFRESH_FLAG=""
        shift 2
        for arg in "$@"; do
            case "$arg" in
                --refresh-data)
                    REFRESH_FLAG="--refresh-data"
                    ;;
            esac
        done
        
        echo -e "${CYAN}Analyzing $TICKER...${NC}\n"
        # Use Ollama config if it exists, otherwise use default
        if [ -f "config/config_ollama.json" ]; then
            $VENV_PATH/bin/python -m tradingagents.analyze "$TICKER" --plain-english --portfolio-value 100000 --config config/config_ollama.json $REFRESH_FLAG
        else
            $VENV_PATH/bin/python -m tradingagents.analyze "$TICKER" --plain-english --portfolio-value 100000 $REFRESH_FLAG
        fi
        ;;

    "morning")
        echo -e "${CYAN}Running morning briefing...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights morning
        ;;

    # Portfolio & Performance
    "portfolio")
        REFRESH_FLAG=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
            esac
        done
        echo -e "${CYAN}Portfolio Summary:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.portfolio view $REFRESH_FLAG
        ;;

    "performance")
        REFRESH_FLAG=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
            esac
        done
        echo -e "${CYAN}Portfolio Performance:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.portfolio performance $REFRESH_FLAG
        ;;

    "dividends")
        REFRESH_FLAG=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh-data)
                    REFRESH_FLAG="--refresh-data"
                    ;;
            esac
        done
        echo -e "${CYAN}Upcoming Dividends:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.dividends upcoming $REFRESH_FLAG
        ;;

    "evaluate")
        echo -e "${CYAN}Performance Evaluation:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.evaluate report
        ;;

    # Quick Checks
    "digest")
        REFRESH_FLAG=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
            esac
        done
        echo -e "${CYAN}Market Digest:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights digest $REFRESH_FLAG
        ;;

    "alerts")
        REFRESH_FLAG=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
            esac
        done
        echo -e "${CYAN}Price Alerts:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.insights alerts $REFRESH_FLAG
        ;;

    "top")
        REFRESH_FLAG=""
        LIMIT=5
        MIN_RR=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
                --min-rr)
                    shift
                    MIN_RR="--min-rr $1"
                    ;;
                --min-rr=*)
                    MIN_RR="--min-rr ${arg#*=}"
                    ;;
                [0-9]*)
                    LIMIT="$arg"
                    ;;
            esac
        done
        echo -e "${CYAN}Top $LIMIT Opportunities:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener top $LIMIT $REFRESH_FLAG $MIN_RR
        ;;

    "stats")
        echo -e "${CYAN}Performance Statistics:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.evaluate stats
        ;;

    # Trading Metrics Commands
    "professional")
        MIN_RR=2.0
        LIMIT=20
        shift
        for arg in "$@"; do
            case "$arg" in
                --min-rr)
                    shift
                    MIN_RR="$1"
                    ;;
                --min-rr=*)
                    MIN_RR="${arg#*=}"
                    ;;
                [0-9]*)
                    LIMIT="$arg"
                    ;;
            esac
        done
        echo -e "${CYAN}Professional-Grade Trades (R/R >= $MIN_RR):${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener.trading_commands professional --min-rr $MIN_RR --limit $LIMIT
        ;;

    "excellent")
        LIMIT=20
        shift
        for arg in "$@"; do
            case "$arg" in
                [0-9]*)
                    LIMIT="$arg"
                    ;;
            esac
        done
        echo -e "${CYAN}Excellent Trades (R/R >= 3.0):${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener.trading_commands professional --min-rr 3.0 --limit $LIMIT
        ;;

    "setups")
        LIMIT=10
        ACCOUNT=10000
        RISK=1.0
        MIN_RR=2.0
        shift
        for arg in "$@"; do
            case "$arg" in
                --account)
                    shift
                    ACCOUNT="$1"
                    ;;
                --account=*)
                    ACCOUNT="${arg#*=}"
                    ;;
                --risk)
                    shift
                    RISK="$1"
                    ;;
                --risk=*)
                    RISK="${arg#*=}"
                    ;;
                --min-rr)
                    shift
                    MIN_RR="$1"
                    ;;
                --min-rr=*)
                    MIN_RR="${arg#*=}"
                    ;;
                [0-9]*)
                    LIMIT="$arg"
                    ;;
            esac
        done
        echo -e "${CYAN}Detailed Trade Setups:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener.trading_commands setups --min-rr $MIN_RR --limit $LIMIT --account $ACCOUNT --risk $RISK
        ;;

    "position")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide a ticker symbol${NC}"
            echo "Usage: ./quick_run.sh position AAPL [--account 10000] [--risk 1.0]"
            exit 1
        fi
        TICKER="$2"
        ACCOUNT=10000
        RISK=1.0
        shift 2
        for arg in "$@"; do
            case "$arg" in
                --account)
                    shift
                    ACCOUNT="$1"
                    ;;
                --account=*)
                    ACCOUNT="${arg#*=}"
                    ;;
                --risk)
                    shift
                    RISK="$1"
                    ;;
                --risk=*)
                    RISK="${arg#*=}"
                    ;;
            esac
        done
        echo -e "${CYAN}Position Size Calculator for $TICKER:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener.trading_commands position $TICKER --account $ACCOUNT --risk $RISK
        ;;

    "trade-summary")
        echo -e "${CYAN}Today's Trade Summary:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.screener.trading_commands summary
        ;;

    "indicators")
        REFRESH_FLAG=""
        REFRESH_DATA_FLAG=""
        DETAILED_FLAG=""
        TICKERS=()
        
        # Parse arguments - collect tickers and flags
        shift  # Remove 'indicators' command
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
                --refresh-data)
                    REFRESH_DATA_FLAG="--refresh-data"
                    ;;
                --detailed)
                    DETAILED_FLAG="--detailed"
                    ;;
                *)
                    # Assume it's a ticker symbol
                    TICKERS+=("$arg")
                    ;;
            esac
        done
        
        # Build command arguments
        CMD_ARGS=()
        if [ ${#TICKERS[@]} -gt 0 ]; then
            # Add all tickers
            CMD_ARGS+=("${TICKERS[@]}")
        fi
        
        if [ -n "$REFRESH_DATA_FLAG" ]; then
            CMD_ARGS+=("--refresh-data")
            if [ ${#TICKERS[@]} -gt 0 ]; then
                echo -e "${CYAN}Technical Indicators for ${TICKERS[*]}:${NC}\n"
                echo -e "${YELLOW}Note: Refreshing price data and recalculating indicators...${NC}\n"
            fi
        elif [ -n "$REFRESH_FLAG" ]; then
            CMD_ARGS+=("--refresh")
            if [ ${#TICKERS[@]} -gt 0 ]; then
                echo -e "${CYAN}Technical Indicators for ${TICKERS[*]}:${NC}\n"
                echo -e "${YELLOW}Note: Recalculating indicators from existing data...${NC}\n"
            fi
        else
            if [ ${#TICKERS[@]} -gt 0 ]; then
                echo -e "${CYAN}Technical Indicators for ${TICKERS[*]}:${NC}\n"
            else
                echo -e "${CYAN}Technical Indicators Reference Guide:${NC}\n"
            fi
        fi
        
        # Add --detailed flag if specified
        if [ -n "$DETAILED_FLAG" ]; then
            CMD_ARGS+=("--detailed")
        fi
        
        $VENV_PATH/bin/python -m tradingagents.screener.show_indicators "${CMD_ARGS[@]}"
        ;;

    "indexes")
        REFRESH_FLAG=""
        shift
        for arg in "$@"; do
            case "$arg" in
                --refresh)
                    REFRESH_FLAG="--refresh"
                    ;;
            esac
        done
        echo -e "${CYAN}Market Indexes & Analysis:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.market.show_indexes $REFRESH_FLAG
        ;;

    # Strategy Testing
    "strategies"|"strategy-compare")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide a ticker symbol${NC}"
            echo "Usage: ./quick_run.sh strategies AAPL"
            exit 1
        fi
        TICKER=$(echo "$2" | tr '[:lower:]' '[:upper:]')
        echo -e "${CYAN}Comparing all strategies for $TICKER...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.strategies compare "$TICKER"
        ;;

    "strategy-multi")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide ticker symbols${NC}"
            echo "Usage: ./quick_run.sh strategy-multi AAPL MSFT GOOGL"
            exit 1
        fi
        shift  # Remove first argument (command)
        TICKERS=""
        for ticker in "$@"; do
            TICKERS="$TICKERS $(echo "$ticker" | tr '[:lower:]' '[:upper:]')"
        done
        TICKERS=$(echo $TICKERS | xargs)  # Trim whitespace
        echo -e "${CYAN}Comparing strategies across: $TICKERS${NC}\n"
        $VENV_PATH/bin/python test_and_compare_strategies.py compare-multi $TICKERS
        ;;

    "strategy-run")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: Please provide strategy name and ticker${NC}"
            echo "Usage: ./quick_run.sh strategy-run value AAPL"
            echo "Available strategies: value, growth, dividend, momentum, contrarian, quantitative, sector_rotation, market_structure"
            exit 1
        fi
        STRATEGY_NAME="$2"
        TICKER=$(echo "$3" | tr '[:lower:]' '[:upper:]')
        echo -e "${CYAN}Running $STRATEGY_NAME strategy for $TICKER...${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.strategies run "$STRATEGY_NAME" "$TICKER"
        ;;

    "strategy-list")
        echo -e "${CYAN}Available Strategies:${NC}\n"
        $VENV_PATH/bin/python -m tradingagents.strategies list
        ;;

    "strategy-screener")
        LIMIT=${2:-20}
        echo -e "${CYAN}${BOLD}Comparing strategies on top $LIMIT screener stocks...${NC}\n"
        echo -e "${YELLOW}Using existing screener results. Use 'strategy-screener-full' to run screener first.${NC}\n"
        $VENV_PATH/bin/python compare_screener_strategies.py --limit "$LIMIT"
        ;;

    "strategy-screener-full")
        LIMIT=${2:-20}
        echo -e "${CYAN}${BOLD}Running screener + comparing strategies on top $LIMIT stocks...${NC}\n"
        echo -e "${YELLOW}Step 1/2: Running screener...${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener run --top "$LIMIT" --quiet
        echo ""
        echo -e "${YELLOW}Step 2/2: Comparing strategies on top stocks...${NC}\n"
        # Don't use --run-screener since we just ran it above
        $VENV_PATH/bin/python compare_screener_strategies.py --limit "$LIMIT"
        echo ""
        echo -e "${GREEN}${BOLD}✓ Strategy comparison complete!${NC}"
        ;;

    "strategy-test")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide a ticker symbol${NC}"
            echo "Usage: ./quick_run.sh strategy-test AAPL"
            exit 1
        fi
        TICKER=$(echo "$2" | tr '[:lower:]' '[:upper:]')
        echo -e "${CYAN}${BOLD}Comprehensive Strategy Test: $TICKER${NC}\n"
        echo -e "${YELLOW}Running comprehensive strategy comparison...${NC}\n"
        $VENV_PATH/bin/python test_and_compare_strategies.py compare "$TICKER"
        echo ""
        echo -e "${GREEN}${BOLD}✓ Strategy test complete!${NC}"
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
        echo -e "${CYAN}${BOLD}Running Comprehensive Full Analysis${NC}\n"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo ""
        
        echo -e "${YELLOW}Step 1/9: Market Regime Analysis${NC}"
        echo -e "${BLUE}Analyzing market indexes and current regime...${NC}"
        $VENV_PATH/bin/python -m tradingagents.market.show_indexes
        echo ""
        
        echo -e "${YELLOW}Step 2/9: Market Screener${NC}"
        echo -e "${BLUE}Scanning all stocks for opportunities...${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener run --sector-analysis --top 10
        echo ""
        
        echo -e "${YELLOW}Step 3/9: Top Opportunities${NC}"
        echo -e "${BLUE}Identifying best trade opportunities...${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener top 10
        echo ""
        
        echo -e "${YELLOW}Step 4/9: Trade Setups${NC}"
        echo -e "${BLUE}Generating detailed trade setups with position sizing...${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener.trading_commands setups --limit 10
        echo ""
        
        echo -e "${YELLOW}Step 5/9: Dividend Income Opportunities${NC}"
        echo -e "${BLUE}Finding best dividend stocks...${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener.dividend_income_main --top 10
        echo ""
        
        echo -e "${YELLOW}Step 6/9: Market Indicators Overview${NC}"
        echo -e "${BLUE}Analyzing key market indicators...${NC}"
        $VENV_PATH/bin/python -m tradingagents.screener.show_indicators
        echo ""
        
        echo -e "${YELLOW}Step 7/9: Morning Briefing${NC}"
        echo -e "${BLUE}Generating comprehensive market briefing...${NC}"
        $VENV_PATH/bin/python -m tradingagents.insights morning
        echo ""
        
        echo -e "${YELLOW}Step 8/9: Portfolio Status${NC}"
        echo -e "${BLUE}Reviewing portfolio performance...${NC}"
        $VENV_PATH/bin/python -m tradingagents.portfolio view
        echo ""
        
        echo -e "${YELLOW}Step 9/9: Performance Evaluation${NC}"
        echo -e "${BLUE}Evaluating trading performance...${NC}"
        $VENV_PATH/bin/python -m tradingagents.evaluate update
        $VENV_PATH/bin/python -m tradingagents.evaluate report
        echo ""
        
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}${BOLD}✓ Comprehensive full analysis complete!${NC}"
        echo -e "${CYAN}All major functionalities have been analyzed.${NC}"
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
