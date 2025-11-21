#!/bin/bash
#
# TradingAgents AI Assistant Launcher
#
# Launches Eddie with React UI (Next.js frontend + FastAPI backend)
#

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}          🤖 ${GREEN}Eddie - AI Trading Expert${NC}                            ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}          Your Evolving Intelligent Trading Assistant              ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    VENV_PATH="$PROJECT_ROOT/venv"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    VENV_PATH="$PROJECT_ROOT/.venv"
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

# Function to kill processes on a port
kill_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Found existing process on port ${port}. Stopping...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

# Check and kill existing processes
echo -e "${YELLOW}Checking for existing instances...${NC}"
kill_port 8005  # Backend API
kill_port 3005  # Frontend

# Set up environment
export PYTHONPATH="$PROJECT_ROOT"

# Launch the bot
echo -e "${BLUE}Starting Eddie...${NC}"
echo ""
echo "Backend API: ${GREEN}http://localhost:8005${NC}"
echo "Frontend UI: ${GREEN}http://localhost:3005${NC}"
echo ""
echo -e "${YELLOW}Features:${NC}"
echo "  • Natural language queries"
echo "  • Market screening and analysis"
echo "  • AI-powered recommendations"
echo "  • Real-time data from your database"
echo "  • v2.0: System Doctor, Cognitive Modes, Voice, Web Learning"
echo ""
echo -e "${YELLOW}Example queries:${NC}"
echo "  • 'What stocks should I look at?'"
echo "  • 'Analyze AAPL for me'"
echo "  • 'Run a system health check for AAPL'"
echo "  • 'I'm worried about my portfolio'"
echo ""
echo "Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Start Backend API
echo -e "${GREEN}Starting Backend API (FastAPI)...${NC}"
$VENV_PATH/bin/python -m tradingagents.api.main &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend (Next.js)
echo -e "${GREEN}Starting Frontend (Next.js)...${NC}"
cd "$PROJECT_ROOT/web-app"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi
npm run dev -- -p 3005 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

echo ""
echo -e "${BLUE}✨ Services started!${NC}"
echo -e "   Backend: http://localhost:8005"
echo -e "   Frontend: http://localhost:3005"
echo -e "${BLUE}Opening browser...${NC}"
echo ""

# Try to open browser (macOS)
if command -v open &> /dev/null; then
    sleep 2
    open http://localhost:3005
fi

# Wait for both processes
wait
