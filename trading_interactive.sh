#!/bin/bash

################################################################################
# TradingAgents Interactive Shell
#
# This script provides an interactive menu-driven interface for running
# TradingAgents features with progress tracking and notifications.
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
SESSION_LOG="$LOG_DIR/session_$(date +%Y%m%d_%H%M%S).log"
PROGRESS_FILE="$LOG_DIR/progress.txt"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Initialize progress tracking
TOTAL_TASKS=0
COMPLETED_TASKS=0

################################################################################
# Utility Functions
################################################################################

# Print header
print_header() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║                  TradingAgents Interactive Shell                   ║"
    echo "║                     Investment Intelligence Hub                    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Log function
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$SESSION_LOG"
}

# Progress bar function
progress_bar() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))

    printf "\r${CYAN}Progress: [${GREEN}"
    printf "%${filled}s" | tr ' ' '█'
    printf "${NC}%${empty}s${CYAN}] ${WHITE}%3d%%${NC} (${current}/${total})" ' ' $percentage
}

# Update progress
update_progress() {
    COMPLETED_TASKS=$((COMPLETED_TASKS + 1))
    progress_bar $COMPLETED_TASKS $TOTAL_TASKS
    echo ""
    log "INFO" "Task completed: $COMPLETED_TASKS/$TOTAL_TASKS"
}

# Check if virtual environment is activated
check_venv() {
    # Check for both .venv and venv
    if [ -d "$SCRIPT_DIR/.venv" ]; then
        VENV_PATH="$SCRIPT_DIR/.venv"
    elif [ -d "$SCRIPT_DIR/venv" ]; then
        VENV_PATH="$SCRIPT_DIR/venv"
    else
        echo -e "${RED}Error: Virtual environment not found${NC}"
        echo "Please create a virtual environment (.venv or venv) first."
        exit 1
    fi
    export PYTHONPATH="$SCRIPT_DIR"
}

# Check if .env file exists
check_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo -e "Would you like to configure notifications now? (y/n): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            configure_notifications
        fi
    fi
}

################################################################################
# Notification Configuration
################################################################################

configure_notifications() {
    print_header
    echo -e "${MAGENTA}${BOLD}=== Notification Configuration ===${NC}\n"

    # Check if .env exists
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${YELLOW}Existing .env file found. This will update your configuration.${NC}\n"
    else
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        echo -e "${GREEN}Created new .env file from template${NC}\n"
    fi

    # Email Configuration
    echo -e "${CYAN}${BOLD}Email Configuration${NC}"
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━${NC}\n"

    echo -n "Enable email notifications? (y/n) [n]: "
    read -r email_enabled
    email_enabled=${email_enabled:-n}

    if [[ "$email_enabled" =~ ^[Yy]$ ]]; then
        echo -n "From email address: "
        read -r email_from

        echo -n "To email address: "
        read -r email_to

        echo -n "Email password (Gmail app password): "
        read -rs email_password
        echo ""

        echo -n "SMTP server [smtp.gmail.com]: "
        read -r smtp_server
        smtp_server=${smtp_server:-smtp.gmail.com}

        echo -n "SMTP port [587]: "
        read -r smtp_port
        smtp_port=${smtp_port:-587}

        # Update .env
        sed -i.bak "s/^EMAIL_ENABLED=.*/EMAIL_ENABLED=true/" "$SCRIPT_DIR/.env"
        sed -i.bak "s/^EMAIL_FROM=.*/EMAIL_FROM=$email_from/" "$SCRIPT_DIR/.env"
        sed -i.bak "s/^EMAIL_TO=.*/EMAIL_TO=$email_to/" "$SCRIPT_DIR/.env"
        sed -i.bak "s/^EMAIL_PASSWORD=.*/EMAIL_PASSWORD=$email_password/" "$SCRIPT_DIR/.env"
        sed -i.bak "s/^SMTP_SERVER=.*/SMTP_SERVER=$smtp_server/" "$SCRIPT_DIR/.env"
        sed -i.bak "s/^SMTP_PORT=.*/SMTP_PORT=$smtp_port/" "$SCRIPT_DIR/.env"

        echo -e "\n${GREEN}✓ Email configuration saved${NC}\n"
    else
        sed -i.bak "s/^EMAIL_ENABLED=.*/EMAIL_ENABLED=false/" "$SCRIPT_DIR/.env"
    fi

    # Slack Configuration
    echo -e "${CYAN}${BOLD}Slack/Discord Configuration${NC}"
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    echo -n "Enable Slack/Discord notifications? (y/n) [n]: "
    read -r slack_enabled
    slack_enabled=${slack_enabled:-n}

    if [[ "$slack_enabled" =~ ^[Yy]$ ]]; then
        echo -n "Webhook URL: "
        read -r webhook_url

        echo -n "Channel name [#trading]: "
        read -r channel
        channel=${channel:-#trading}

        echo -n "Bot username [TradingAgents]: "
        read -r username
        username=${username:-TradingAgents}

        echo -n "Icon emoji [:chart_with_upwards_trend:]: "
        read -r icon
        icon=${icon:-:chart_with_upwards_trend:}

        # Update .env
        sed -i.bak "s|^SLACK_ENABLED=.*|SLACK_ENABLED=true|" "$SCRIPT_DIR/.env"
        sed -i.bak "s|^SLACK_WEBHOOK_URL=.*|SLACK_WEBHOOK_URL=$webhook_url|" "$SCRIPT_DIR/.env"
        sed -i.bak "s|^SLACK_CHANNEL=.*|SLACK_CHANNEL=$channel|" "$SCRIPT_DIR/.env"
        sed -i.bak "s|^SLACK_USERNAME=.*|SLACK_USERNAME=$username|" "$SCRIPT_DIR/.env"
        sed -i.bak "s|^SLACK_ICON_EMOJI=.*|SLACK_ICON_EMOJI=$icon|" "$SCRIPT_DIR/.env"

        echo -e "\n${GREEN}✓ Slack/Discord configuration saved${NC}\n"
    else
        sed -i.bak "s/^SLACK_ENABLED=.*/SLACK_ENABLED=false/" "$SCRIPT_DIR/.env"
    fi

    # Notification preferences
    echo -e "${CYAN}${BOLD}Notification Preferences${NC}"
    echo -e "${WHITE}━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

    echo -n "Notify on successful task completion? (y/n) [y]: "
    read -r notify_success
    notify_success=${notify_success:-y}
    if [[ "$notify_success" =~ ^[Yy]$ ]]; then
        sed -i.bak "s/^NOTIFY_ON_SUCCESS=.*/NOTIFY_ON_SUCCESS=true/" "$SCRIPT_DIR/.env"
    else
        sed -i.bak "s/^NOTIFY_ON_SUCCESS=.*/NOTIFY_ON_SUCCESS=false/" "$SCRIPT_DIR/.env"
    fi

    echo -n "Notify on errors? (y/n) [y]: "
    read -r notify_error
    notify_error=${notify_error:-y}
    if [[ "$notify_error" =~ ^[Yy]$ ]]; then
        sed -i.bak "s/^NOTIFY_ON_ERROR=.*/NOTIFY_ON_ERROR=true/" "$SCRIPT_DIR/.env"
    else
        sed -i.bak "s/^NOTIFY_ON_ERROR=.*/NOTIFY_ON_ERROR=false/" "$SCRIPT_DIR/.env"
    fi

    # Clean up backup files
    rm -f "$SCRIPT_DIR/.env.bak"

    echo -e "\n${GREEN}${BOLD}✓ Notification configuration complete!${NC}\n"
    echo "Press Enter to continue..."
    read -r
}

# Test notifications
test_notifications() {
    print_header
    echo -e "${MAGENTA}${BOLD}=== Testing Notifications ===${NC}\n"

    log "INFO" "Testing notification system"

    cd "$SCRIPT_DIR"
    $VENV_PATH/bin/python -m tradingagents.insights notify \
        --message "Test notification from TradingAgents Interactive Shell! 🚀 If you're seeing this, your notifications are working perfectly." \
        --title "TradingAgents Test" \
        --priority MEDIUM \
        --channels terminal,log,email,webhook

    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✓ Test notification sent successfully!${NC}"
        echo -e "Check your email and Slack/Discord channels.\n"
    else
        echo -e "\n${RED}✗ Failed to send test notification${NC}"
        echo -e "${YELLOW}Please check your notification configuration in .env${NC}\n"
    fi

    echo "Press Enter to continue..."
    read -r
}

################################################################################
# Feature Execution Functions
################################################################################

# Market Screener
run_screener() {
    echo -e "\n${CYAN}${BOLD}=== Market Screener Options ===${NC}\n"

    echo "1) Basic screener (technical indicators only)"
    echo "2) Screener with sector analysis"
    echo "3) Sector-first workflow (sectors → top stocks)"
    echo "4) Full analysis with AI recommendations"
    echo "5) Fast mode (optimized for speed)"
    echo ""
    echo -n "Select option [2]: "
    read -r screener_option
    screener_option=${screener_option:-2}

    echo -n "Number of top opportunities to show [10]: "
    read -r top_count
    top_count=${top_count:-10}

    local cmd="$VENV_PATH/bin/python -m tradingagents.screener run --top $top_count"

    case $screener_option in
        1)
            log "INFO" "Running basic screener"
            ;;
        2)
            cmd="$cmd --sector-analysis"
            log "INFO" "Running screener with sector analysis"
            ;;
        3)
            cmd="$cmd --sector-first --sector-analysis"
            log "INFO" "Running sector-first workflow"
            ;;
        4)
            cmd="$cmd --sector-analysis --with-analysis"
            log "INFO" "Running full analysis with AI recommendations"
            ;;
        5)
            cmd="$cmd --fast"
            log "INFO" "Running screener in fast mode"
            ;;
    esac

    echo -e "\n${YELLOW}Executing: $cmd${NC}\n"
    cd "$SCRIPT_DIR"
    eval "$cmd"

    update_progress
}

# Stock Analysis
run_analysis() {
    echo -e "\n${CYAN}${BOLD}=== Stock Analysis ===${NC}\n"

    echo -n "Enter ticker symbols (space-separated): "
    read -r tickers

    if [ -z "$tickers" ]; then
        echo -e "${RED}No tickers provided${NC}"
        return
    fi

    echo -n "Portfolio value for position sizing [100000]: "
    read -r portfolio_value
    portfolio_value=${portfolio_value:-100000}

    echo -n "Plain English recommendations? (y/n) [y]: "
    read -r plain_english
    plain_english=${plain_english:-y}

    echo -n "Use fast mode? (y/n) [n]: "
    read -r fast_mode
    fast_mode=${fast_mode:-n}

    local cmd="$VENV_PATH/bin/python -m tradingagents.analyze $tickers --portfolio-value $portfolio_value"

    if [[ "$plain_english" =~ ^[Yy]$ ]]; then
        cmd="$cmd --plain-english"
    fi

    if [[ "$fast_mode" =~ ^[Yy]$ ]]; then
        cmd="$cmd --fast --no-rag"
    fi

    log "INFO" "Analyzing tickers: $tickers"
    echo -e "\n${YELLOW}Executing: $cmd${NC}\n"
    cd "$SCRIPT_DIR"
    eval "$cmd"

    update_progress
}

# Morning Briefing
run_morning_briefing() {
    echo -e "\n${CYAN}${BOLD}=== Morning Briefing ===${NC}\n"

    echo "1) Quick digest (market summary only)"
    echo "2) Full briefing (digest + alerts)"
    echo "3) Comprehensive (briefing + screener + analysis)"
    echo ""
    echo -n "Select option [2]: "
    read -r briefing_option
    briefing_option=${briefing_option:-2}

    log "INFO" "Running morning briefing (option $briefing_option)"
    cd "$SCRIPT_DIR"

    case $briefing_option in
        1)
            $VENV_PATH/bin/python -m tradingagents.insights digest
            ;;
        2)
            $VENV_PATH/bin/python -m tradingagents.insights morning
            ;;
        3)
            ./scripts/morning_briefing.sh --with-analysis
            ;;
    esac

    update_progress
}

# Portfolio Management
run_portfolio() {
    echo -e "\n${CYAN}${BOLD}=== Portfolio Management ===${NC}\n"

    echo "1) View portfolio summary"
    echo "2) View performance history"
    echo "3) Buy stock"
    echo "4) Sell stock"
    echo "5) View upcoming dividends"
    echo "6) Create daily snapshot"
    echo ""
    echo -n "Select option [1]: "
    read -r portfolio_option
    portfolio_option=${portfolio_option:-1}

    cd "$SCRIPT_DIR"

    case $portfolio_option in
        1)
            log "INFO" "Viewing portfolio summary"
            $VENV_PATH/bin/python -m tradingagents.portfolio view
            ;;
        2)
            log "INFO" "Viewing performance history"
            $VENV_PATH/bin/python -m tradingagents.portfolio performance
            ;;
        3)
            echo -n "Ticker symbol: "
            read -r symbol
            echo -n "Number of shares: "
            read -r shares
            echo -n "Price per share: "
            read -r price
            log "INFO" "Buying $shares shares of $symbol at \$$price"
            $VENV_PATH/bin/python -m tradingagents.portfolio buy "$symbol" "$shares" "$price"
            ;;
        4)
            echo -n "Ticker symbol: "
            read -r symbol
            echo -n "Number of shares: "
            read -r shares
            echo -n "Price per share: "
            read -r price
            log "INFO" "Selling $shares shares of $symbol at \$$price"
            $VENV_PATH/bin/python -m tradingagents.portfolio sell "$symbol" "$shares" "$price"
            ;;
        5)
            log "INFO" "Viewing upcoming dividends"
            $VENV_PATH/bin/python -m tradingagents.portfolio dividends
            ;;
        6)
            log "INFO" "Creating daily snapshot"
            $VENV_PATH/bin/python -m tradingagents.portfolio snapshot
            ;;
    esac

    update_progress
}

# Dividend Analysis
run_dividends() {
    echo -e "\n${CYAN}${BOLD}=== Dividend Analysis ===${NC}\n"

    echo "1) View upcoming dividends"
    echo "2) View dividend income report"
    echo "3) Find high-yield dividend stocks"
    echo "4) Analyze dividend safety"
    echo "5) Get reinvestment suggestions"
    echo "6) Update dividend data"
    echo ""
    echo -n "Select option [1]: "
    read -r dividend_option
    dividend_option=${dividend_option:-1}

    cd "$SCRIPT_DIR"

    case $dividend_option in
        1)
            log "INFO" "Viewing upcoming dividends"
            $VENV_PATH/bin/python -m tradingagents.dividends upcoming
            ;;
        2)
            log "INFO" "Generating dividend income report"
            $VENV_PATH/bin/python -m tradingagents.dividends income
            ;;
        3)
            log "INFO" "Finding high-yield dividend stocks"
            $VENV_PATH/bin/python -m tradingagents.dividends high-yield
            ;;
        4)
            log "INFO" "Analyzing dividend safety"
            $VENV_PATH/bin/python -m tradingagents.dividends safety
            ;;
        5)
            log "INFO" "Getting reinvestment suggestions"
            $VENV_PATH/bin/python -m tradingagents.dividends reinvest
            ;;
        6)
            log "INFO" "Updating dividend data"
            $VENV_PATH/bin/python -m tradingagents.dividends backfill
            $VENV_PATH/bin/python -m tradingagents.dividends update-calendar
            ;;
    esac

    update_progress
}

# Performance Evaluation
run_evaluation() {
    echo -e "\n${CYAN}${BOLD}=== Performance Evaluation ===${NC}\n"

    echo "1) View recent recommendations"
    echo "2) Full performance report"
    echo "3) Quick statistics"
    echo "4) Update outcomes with latest prices"
    echo ""
    echo -n "Select option [2]: "
    read -r eval_option
    eval_option=${eval_option:-2}

    cd "$SCRIPT_DIR"

    case $eval_option in
        1)
            log "INFO" "Viewing recent recommendations"
            $VENV_PATH/bin/python -m tradingagents.evaluate recent
            ;;
        2)
            log "INFO" "Generating performance report"
            $VENV_PATH/bin/python -m tradingagents.evaluate report
            ;;
        3)
            log "INFO" "Showing quick statistics"
            $VENV_PATH/bin/python -m tradingagents.evaluate stats
            ;;
        4)
            log "INFO" "Updating outcomes"
            $VENV_PATH/bin/python -m tradingagents.evaluate update
            ;;
    esac

    update_progress
}

################################################################################
# Main Menu
################################################################################

show_main_menu() {
    print_header

    # Show session info
    echo -e "${WHITE}Session Log: ${CYAN}$SESSION_LOG${NC}"
    echo -e "${WHITE}Started: ${CYAN}$(date)${NC}"
    echo ""

    echo -e "${YELLOW}${BOLD}Available Features:${NC}\n"

    echo -e "${GREEN}1)${NC}  📊 Market Screener       - Screen stocks with technical indicators"
    echo -e "${GREEN}2)${NC}  🔍 Stock Analysis        - Deep AI-powered analysis of stocks"
    echo -e "${GREEN}3)${NC}  🌅 Morning Briefing      - Daily market digest and alerts"
    echo -e "${GREEN}4)${NC}  💼 Portfolio Management  - Track and manage your portfolio"
    echo -e "${GREEN}5)${NC}  💰 Dividend Analysis     - Track and analyze dividends"
    echo -e "${GREEN}6)${NC}  📈 Performance Evaluation - Review recommendation outcomes"
    echo ""
    echo -e "${BLUE}7)${NC}  🔔 Configure Notifications - Setup email and Slack alerts"
    echo -e "${BLUE}8)${NC}  🧪 Test Notifications     - Send test notification"
    echo -e "${BLUE}9)${NC}  📋 View Session Logs      - Review current session activity"
    echo -e "${BLUE}10)${NC} 🎯 Run Multiple Features  - Execute multiple tasks in sequence"
    echo ""
    echo -e "${RED}0)${NC}  Exit"
    echo ""
    echo -n "Select option: "
}

# Run multiple features
run_multiple() {
    echo -e "\n${CYAN}${BOLD}=== Multi-Feature Execution ===${NC}\n"

    echo "Select features to run (comma-separated numbers):"
    echo "1 = Screener, 2 = Analysis, 3 = Morning Briefing,"
    echo "4 = Portfolio, 5 = Dividends, 6 = Evaluation"
    echo ""
    echo -n "Features: "
    read -r features

    # Convert comma-separated to array
    IFS=',' read -ra FEATURE_ARRAY <<< "$features"

    # Set total tasks for progress tracking
    TOTAL_TASKS=${#FEATURE_ARRAY[@]}
    COMPLETED_TASKS=0

    echo -e "\n${YELLOW}Will execute ${TOTAL_TASKS} tasks${NC}\n"
    log "INFO" "Starting multi-feature execution: $features"

    for feature in "${FEATURE_ARRAY[@]}"; do
        feature=$(echo "$feature" | xargs) # Trim whitespace

        case $feature in
            1) run_screener ;;
            2) run_analysis ;;
            3) run_morning_briefing ;;
            4) run_portfolio ;;
            5) run_dividends ;;
            6) run_evaluation ;;
            *)
                echo -e "${RED}Invalid feature: $feature${NC}"
                ;;
        esac

        echo ""
    done

    echo -e "\n${GREEN}${BOLD}✓ All tasks completed!${NC}\n"
    log "INFO" "Multi-feature execution completed"
}

# View session logs
view_logs() {
    print_header
    echo -e "${CYAN}${BOLD}=== Session Logs ===${NC}\n"

    if [ -f "$SESSION_LOG" ]; then
        tail -n 50 "$SESSION_LOG"
    else
        echo -e "${YELLOW}No logs found for this session${NC}"
    fi

    echo -e "\n${WHITE}Full log: ${CYAN}$SESSION_LOG${NC}\n"
    echo "Press Enter to continue..."
    read -r
}

################################################################################
# Main Program Loop
################################################################################

main() {
    # Initial checks
    check_venv
    check_env

    log "INFO" "TradingAgents Interactive Shell started"

    while true; do
        show_main_menu
        read -r choice

        case $choice in
            1)
                TOTAL_TASKS=1
                COMPLETED_TASKS=0
                run_screener
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            2)
                TOTAL_TASKS=1
                COMPLETED_TASKS=0
                run_analysis
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            3)
                TOTAL_TASKS=1
                COMPLETED_TASKS=0
                run_morning_briefing
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            4)
                TOTAL_TASKS=1
                COMPLETED_TASKS=0
                run_portfolio
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            5)
                TOTAL_TASKS=1
                COMPLETED_TASKS=0
                run_dividends
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            6)
                TOTAL_TASKS=1
                COMPLETED_TASKS=0
                run_evaluation
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            7)
                configure_notifications
                ;;
            8)
                test_notifications
                ;;
            9)
                view_logs
                ;;
            10)
                run_multiple
                echo -e "\nPress Enter to continue..."
                read -r
                ;;
            0)
                echo -e "\n${GREEN}Thank you for using TradingAgents!${NC}"
                log "INFO" "Session ended"
                echo -e "Session log saved to: ${CYAN}$SESSION_LOG${NC}\n"
                exit 0
                ;;
            *)
                echo -e "\n${RED}Invalid option${NC}\n"
                sleep 1
                ;;
        esac
    done
}

# Run main program
main
