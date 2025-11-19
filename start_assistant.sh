#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Eddie AI - Trading Assistant...${NC}"

# Function to kill background processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Function to check and kill processes on a port
kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Found existing process on port ${port} (${service_name}). Stopping...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
        
        # Verify it's killed
        if lsof -ti:$port > /dev/null 2>&1; then
            echo -e "${RED}❌ Could not free port ${port}. Please manually kill the process.${NC}"
            echo "   Run: lsof -ti:${port} | xargs kill -9"
            return 1
        else
            echo -e "${GREEN}✅ Port ${port} is now free${NC}"
        fi
    else
        echo -e "${GREEN}✅ Port ${port} is available${NC}"
    fi
    return 0
}

# Check and kill existing processes
echo -e "${YELLOW}Checking for existing instances...${NC}"

# Kill processes on backend port (8005)
if ! kill_port 8005 "Backend API"; then
    exit 1
fi

# Kill processes on frontend port (3005)
if ! kill_port 3005 "Frontend"; then
    exit 1
fi

# Also kill any uvicorn processes that might be running the API
if pgrep -f "tradingagents.api.main" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Found existing tradingagents.api.main process. Stopping...${NC}"
    pkill -f "tradingagents.api.main" 2>/dev/null
    sleep 1
fi

# Kill any Next.js dev server processes for this project
if pgrep -f "next dev.*3005" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Found existing Next.js dev server. Stopping...${NC}"
    pkill -f "next dev.*3005" 2>/dev/null
    sleep 1
fi

echo ""

# Check for virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: No virtual environment found (.venv or venv)."
    echo "Attempting to run with system python..."
fi

# Start Backend
echo -e "${GREEN}Starting Backend API (FastAPI)...${NC}"
python -m tradingagents.api.main &
BACKEND_PID=$!

# Wait for backend to start (simple sleep for now, could be a health check)
sleep 2

# Start Frontend
echo -e "${GREEN}Starting Frontend (Next.js)...${NC}"
# Store original directory
ORIGINAL_DIR=$(pwd)
cd web-app
npm run dev -- -p 3005 &
FRONTEND_PID=$!
# Return to original directory (though we'll wait here, this is for good practice)
cd "$ORIGINAL_DIR"

echo -e "${BLUE}✨ Services started!${NC}"
echo -e "   Backend: http://localhost:8005"
echo -e "   Frontend: http://localhost:3005"
echo -e "${BLUE}Press Ctrl+C to stop all services.${NC}"

# Wait for both processes
wait
