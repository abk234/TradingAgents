#!/bin/bash
# TradingAgents Interactive Shell
# Comprehensive interface to all TradingAgents features

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo "Please run: python run.py (this will create the venv and install dependencies)"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to display main menu
show_main_menu() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}     ${GREEN}TradingAgents - Multi-Agent LLM Financial Trading${NC}     ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                    ${YELLOW}Interactive Shell${NC}                      ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${MAGENTA}Main Menu:${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC}  ${BLUE}Interactive Analysis${NC}          - Run full multi-agent analysis"
    echo -e "  ${GREEN}2)${NC}  ${BLUE}Daily Screener${NC}               - Scan stocks for opportunities"
    echo -e "  ${GREEN}3)${NC}  ${BLUE}Deep Analysis${NC}                - Analyze specific ticker(s)"
    echo -e "  ${GREEN}4)${NC}  ${BLUE}Batch Analysis${NC}              - Analyze top N from screener"
    echo -e "  ${GREEN}5)${NC}  ${BLUE}Portfolio Management${NC}         - View/manage portfolio"
    echo -e "  ${GREEN}6)${NC}  ${BLUE}Performance Evaluation${NC}      - Track recommendation outcomes"
    echo -e "  ${GREEN}7)${NC}  ${BLUE}Insights & Alerts${NC}            - Daily digest and alerts"
    echo -e "  ${GREEN}8)${NC}  ${BLUE}Dividend Tracking${NC}            - View upcoming dividends"
    echo -e "  ${GREEN}9)${NC}  ${BLUE}Browse ChromaDB${NC}              - Explore agent memory"
    echo -e "  ${GREEN}10)${NC} ${BLUE}Configuration${NC}               - View/edit settings"
    echo -e "  ${GREEN}11)${NC} ${BLUE}Documentation${NC}               - View feature docs"
    echo -e "  ${GREEN}0)${NC}  ${RED}Exit${NC}"
    echo ""
    echo -ne "${YELLOW}Select option [0-11]: ${NC}"
}

# Function to run interactive analysis
run_interactive_analysis() {
    echo -e "\n${CYAN}Starting Interactive Analysis...${NC}\n"
    python -m cli.main analyze
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to run screener
run_screener() {
    echo -e "\n${CYAN}Daily Screener Menu:${NC}\n"
    echo -e "  ${GREEN}1)${NC} Run full screener"
    echo -e "  ${GREEN}2)${NC} Show top N opportunities"
    echo -e "  ${GREEN}3)${NC} Show latest report"
    echo -e "  ${GREEN}4)${NC} Update price data only"
    echo -e "  ${GREEN}5)${NC} Run with sector analysis"
    echo -e "  ${GREEN}6)${NC} Run with deep analysis on top N"
    echo -e "  ${GREEN}0)${NC} Back to main menu"
    echo ""
    echo -ne "${YELLOW}Select option [0-6]: ${NC}"
    read screener_choice
    
    case $screener_choice in
        1)
            echo -e "\n${CYAN}Running full screener...${NC}\n"
            python -m tradingagents.screener run
            ;;
        2)
            echo -ne "${YELLOW}Enter N (default 5): ${NC}"
            read n
            n=${n:-5}
            echo -e "\n${CYAN}Showing top $n opportunities...${NC}\n"
            python -m tradingagents.screener top $n
            ;;
        3)
            echo -e "\n${CYAN}Showing latest report...${NC}\n"
            python -m tradingagents.screener report
            ;;
        4)
            echo -e "\n${CYAN}Updating price data...${NC}\n"
            python -m tradingagents.screener update
            ;;
        5)
            echo -e "\n${CYAN}Running screener with sector analysis...${NC}\n"
            python -m tradingagents.screener run --sector-analysis
            ;;
        6)
            echo -ne "${YELLOW}Enter N for top opportunities (default 3): ${NC}"
            read n
            n=${n:-3}
            echo -e "\n${CYAN}Running screener with deep analysis on top $n...${NC}\n"
            python -m tradingagents.screener run --with-analysis --top $n
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to run deep analysis
run_deep_analysis() {
    echo -e "\n${CYAN}Deep Analysis${NC}\n"
    echo -ne "${YELLOW}Enter ticker symbol(s) (space-separated, e.g., AAPL GOOGL): ${NC}"
    read tickers
    
    if [ -z "$tickers" ]; then
        echo -e "${RED}No ticker provided${NC}"
        return
    fi
    
    echo -e "\n${CYAN}Analysis Options:${NC}\n"
    echo -e "  ${GREEN}1)${NC} Standard analysis"
    echo -e "  ${GREEN}2)${NC} Plain English mode (with portfolio value)"
    echo -e "  ${GREEN}3)${NC} Without RAG (faster)"
    echo -e "  ${GREEN}4)${NC} Verbose output"
    echo -e "  ${GREEN}5)${NC} With custom date"
    echo ""
    echo -ne "${YELLOW}Select option [1-5]: ${NC}"
    read analysis_option
    
    case $analysis_option in
        1)
            echo -e "\n${CYAN}Running standard analysis...${NC}\n"
            python -m tradingagents.analyze $tickers
            ;;
        2)
            echo -ne "${YELLOW}Enter portfolio value (default 100000): ${NC}"
            read portfolio_value
            portfolio_value=${portfolio_value:-100000}
            echo -e "\n${CYAN}Running plain English analysis...${NC}\n"
            python -m tradingagents.analyze $tickers --plain-english --portfolio-value $portfolio_value
            ;;
        3)
            echo -e "\n${CYAN}Running analysis without RAG...${NC}\n"
            python -m tradingagents.analyze $tickers --no-rag
            ;;
        4)
            echo -e "\n${CYAN}Running verbose analysis...${NC}\n"
            python -m tradingagents.analyze $tickers --verbose
            ;;
        5)
            echo -ne "${YELLOW}Enter date (YYYY-MM-DD): ${NC}"
            read analysis_date
            echo -e "\n${CYAN}Running analysis for date $analysis_date...${NC}\n"
            python -m tradingagents.analyze $tickers --date $analysis_date
            ;;
        *)
            echo -e "${RED}Invalid option, running standard analysis...${NC}\n"
            python -m tradingagents.analyze $tickers
            ;;
    esac
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to run batch analysis
run_batch_analysis() {
    echo -e "\n${CYAN}Batch Analysis${NC}\n"
    echo -ne "${YELLOW}Enter number of top tickers to analyze (default 5): ${NC}"
    read n
    n=${n:-5}
    echo -e "\n${CYAN}Running batch analysis on top $n tickers...${NC}\n"
    python -m tradingagents.analyze.batch_analyze --top $n
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to manage portfolio
manage_portfolio() {
    echo -e "\n${CYAN}Portfolio Management Menu:${NC}\n"
    echo -e "  ${GREEN}1)${NC} View portfolio"
    echo -e "  ${GREEN}2)${NC} Buy stock"
    echo -e "  ${GREEN}3)${NC} Sell stock"
    echo -e "  ${GREEN}4)${NC} View performance"
    echo -e "  ${GREEN}5)${NC} View dividends"
    echo -e "  ${GREEN}6)${NC} Create snapshot"
    echo -e "  ${GREEN}0)${NC} Back to main menu"
    echo ""
    echo -ne "${YELLOW}Select option [0-6]: ${NC}"
    read portfolio_choice
    
    case $portfolio_choice in
        1)
            echo -e "\n${CYAN}Viewing portfolio...${NC}\n"
            python -m tradingagents.portfolio view
            ;;
        2)
            echo -ne "${YELLOW}Enter symbol: ${NC}"
            read symbol
            echo -ne "${YELLOW}Enter shares: ${NC}"
            read shares
            echo -ne "${YELLOW}Enter price per share: ${NC}"
            read price
            echo -e "\n${CYAN}Buying $shares shares of $symbol at \$$price...${NC}\n"
            python -m tradingagents.portfolio buy $symbol $shares $price
            ;;
        3)
            echo -ne "${YELLOW}Enter symbol: ${NC}"
            read symbol
            echo -ne "${YELLOW}Enter shares: ${NC}"
            read shares
            echo -ne "${YELLOW}Enter price per share: ${NC}"
            read price
            echo -e "\n${CYAN}Selling $shares shares of $symbol at \$$price...${NC}\n"
            python -m tradingagents.portfolio sell $symbol $shares $price
            ;;
        4)
            echo -ne "${YELLOW}Enter days of history (default 30): ${NC}"
            read days
            days=${days:-30}
            echo -e "\n${CYAN}Viewing performance for last $days days...${NC}\n"
            python -m tradingagents.portfolio performance --days $days
            ;;
        5)
            echo -ne "${YELLOW}Enter days ahead (default 90): ${NC}"
            read days
            days=${days:-90}
            echo -e "\n${CYAN}Viewing dividends for next $days days...${NC}\n"
            python -m tradingagents.portfolio dividends --days $days
            ;;
        6)
            echo -e "\n${CYAN}Creating portfolio snapshot...${NC}\n"
            python -m tradingagents.portfolio snapshot
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to view performance evaluation
view_performance() {
    echo -e "\n${CYAN}Performance Evaluation Menu:${NC}\n"
    echo -e "  ${GREEN}1)${NC} View performance report"
    echo -e "  ${GREEN}2)${NC} View statistics"
    echo -e "  ${GREEN}3)${NC} Update outcomes"
    echo -e "  ${GREEN}4)${NC} Backfill historical recommendations"
    echo -e "  ${GREEN}0)${NC} Back to main menu"
    echo ""
    echo -ne "${YELLOW}Select option [0-4]: ${NC}"
    read perf_choice
    
    case $perf_choice in
        1)
            echo -ne "${YELLOW}Enter period in days (default 30): ${NC}"
            read period
            period=${period:-30}
            echo -e "\n${CYAN}Generating performance report...${NC}\n"
            python -m tradingagents.evaluate report --period $period
            ;;
        2)
            echo -e "\n${CYAN}Viewing statistics...${NC}\n"
            python -m tradingagents.evaluate stats
            ;;
        3)
            echo -ne "${YELLOW}Enter days to look back (default 30): ${NC}"
            read days
            days=${days:-30}
            echo -e "\n${CYAN}Updating outcomes...${NC}\n"
            python -m tradingagents.evaluate update --days $days
            ;;
        4)
            echo -ne "${YELLOW}Enter days to backfill (default 30): ${NC}"
            read days
            days=${days:-30}
            echo -e "\n${CYAN}Backfilling historical recommendations...${NC}\n"
            python -m tradingagents.evaluate backfill --days $days
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to view insights and alerts
view_insights() {
    echo -e "\n${CYAN}Insights & Alerts Menu:${NC}\n"
    echo -e "  ${GREEN}1)${NC} Morning briefing (digest + alerts)"
    echo -e "  ${GREEN}2)${NC} Daily digest"
    echo -e "  ${GREEN}3)${NC} Check alerts"
    echo -e "  ${GREEN}4)${NC} Quick summary"
    echo -e "  ${GREEN}0)${NC} Back to main menu"
    echo ""
    echo -ne "${YELLOW}Select option [0-4]: ${NC}"
    read insights_choice
    
    case $insights_choice in
        1)
            echo -e "\n${CYAN}Generating morning briefing...${NC}\n"
            python -m tradingagents.insights morning
            ;;
        2)
            echo -e "\n${CYAN}Generating daily digest...${NC}\n"
            python -m tradingagents.insights digest
            ;;
        3)
            echo -e "\n${CYAN}Checking alerts...${NC}\n"
            python -m tradingagents.insights alerts
            ;;
        4)
            echo -e "\n${CYAN}Generating quick summary...${NC}\n"
            python -m tradingagents.insights summary
            ;;
        0)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to view dividends
view_dividends() {
    echo -e "\n${CYAN}Dividend Tracking${NC}\n"
    echo -ne "${YELLOW}Enter days ahead (default 90): ${NC}"
    read days
    days=${days:-90}
    echo -e "\n${CYAN}Viewing dividends for next $days days...${NC}\n"
    python -m tradingagents.dividends calendar --days $days
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to browse ChromaDB
browse_chromadb() {
    echo -e "\n${CYAN}Opening ChromaDB browser...${NC}\n"
    if [ -f "browse_chromadb.sh" ]; then
        ./browse_chromadb.sh
    elif [ -f "browse_chromadb.py" ]; then
        python browse_chromadb.py
    else
        echo -e "${RED}ChromaDB browser not found${NC}"
    fi
    echo -e "\n${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to view configuration
view_config() {
    echo -e "\n${CYAN}Configuration${NC}\n"
    echo -e "Current settings from default_config.py:"
    echo ""
    python -c "
from tradingagents.default_config import DEFAULT_CONFIG
import json
print(json.dumps(DEFAULT_CONFIG, indent=2))
"
    echo ""
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo -e "  OPENAI_API_KEY: ${GREEN}${OPENAI_API_KEY:+Set}${NC}${OPENAI_API_KEY:-Not set}"
    echo -e "  GOOGLE_API_KEY: ${GREEN}${GOOGLE_API_KEY:+Set}${NC}${GOOGLE_API_KEY:-Not set}"
    echo -e "  ALPHA_VANTAGE_API_KEY: ${GREEN}${ALPHA_VANTAGE_API_KEY:+Set}${NC}${ALPHA_VANTAGE_API_KEY:-Not set}"
    echo ""
    echo -e "${YELLOW}To edit configuration:${NC}"
    echo -e "  Edit: tradingagents/default_config.py"
    echo -e "  Or set environment variables in .env file"
    echo ""
    echo -e "${GREEN}Press Enter to continue...${NC}"
    read
}

# Function to view documentation
view_docs() {
    echo -e "\n${CYAN}Documentation${NC}\n"
    if [ -d "obsidian_docs" ]; then
        echo -e "Obsidian documentation available in: ${GREEN}obsidian_docs/${NC}"
        echo ""
        echo -e "Available documentation:"
        echo -e "  - Features overview"
        echo -e "  - CLI commands"
        echo -e "  - Agent documentation"
        echo -e "  - Configuration guides"
        echo -e "  - Workflows"
        echo -e "  - Examples"
        echo ""
        echo -e "${YELLOW}To view in Obsidian:${NC}"
        echo -e "  1. Open Obsidian"
        echo -e "  2. Open folder: $(pwd)/obsidian_docs"
        echo ""
    else
        echo -e "${YELLOW}Documentation folder not found${NC}"
    fi
    echo -e "${GREEN}Press Enter to continue...${NC}"
    read
}

# Main loop
while true; do
    show_main_menu
    read choice
    
    case $choice in
        1)
            run_interactive_analysis
            ;;
        2)
            run_screener
            ;;
        3)
            run_deep_analysis
            ;;
        4)
            run_batch_analysis
            ;;
        5)
            manage_portfolio
            ;;
        6)
            view_performance
            ;;
        7)
            view_insights
            ;;
        8)
            view_dividends
            ;;
        9)
            browse_chromadb
            ;;
        10)
            view_config
            ;;
        11)
            view_docs
            ;;
        0)
            echo -e "\n${GREEN}Goodbye!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option. Please try again.${NC}"
            sleep 1
            ;;
    esac
done

