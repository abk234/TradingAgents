#!/bin/bash
#
# TradingAgents AI Assistant Launcher
#
# Launches the conversational trading bot with Chainlit UI
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}          🤖 ${GREEN}Eddie - AI Trading Expert${NC}                            ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}          Your Evolving Intelligent Trading Assistant              ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    VENV_PATH="$SCRIPT_DIR/venv"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    VENV_PATH="$SCRIPT_DIR/venv"
else
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please create one with: python -m venv venv"
    exit 1
fi

# Check if Ollama is running
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${RED}⚠️  Ollama is not running!${NC}"
    echo ""
    echo "Please start Ollama first:"
    echo "  • macOS/Linux: ollama serve"
    echo "  • Or start Ollama app"
    echo ""
    exit 1
fi

# Check if llama3.3 model is available
if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.3"; then
    echo -e "${YELLOW}⚠️  llama3.3 model not found${NC}"
    echo ""
    echo "Downloading llama3.3... (this may take a few minutes)"
    ollama pull llama3.3
fi

echo -e "${GREEN}✓${NC} Ollama is running"
echo -e "${GREEN}✓${NC} llama3.3 model available"
echo ""

# Set up environment
export PYTHONPATH="$SCRIPT_DIR"

# Launch the bot
echo -e "${BLUE}Starting Eddie...${NC}"
echo ""
echo "The bot will open in your browser at: ${GREEN}http://localhost:8000${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "  • Natural language queries"
echo "  • Market screening and analysis"
echo "  • AI-powered recommendations"
echo "  • Real-time data from your database"
echo ""
echo -e "${YELLOW}Example queries:${NC}"
echo "  • 'What stocks should I look at?'"
echo "  • 'Analyze AAPL for me'"
echo "  • 'How is the tech sector doing?'"
echo ""
echo "Press Ctrl+C to stop the bot"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Run the bot
$VENV_PATH/bin/python -m tradingagents.bot
