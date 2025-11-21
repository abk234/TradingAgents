#!/bin/bash

################################################################################
# Fresh Start Script - Kill all existing instances and start clean
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

BACKEND_PORT=8005
FRONTEND_PORT=3005

print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

cleanup() {
    echo -e "\n${BLUE}🛑 Shutting down services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

################################################################################
# STEP 1: Kill ALL existing instances
################################################################################

print_header "🧹 Cleaning Up Existing Processes"

# Kill all Python backend instances
print_info "Killing all backend instances..."
pkill -9 -f "tradingagents.api.main" 2>/dev/null && print_success "Killed backend processes" || print_info "No backend processes found"

# Kill all Next.js frontend instances
print_info "Killing all frontend instances..."
pkill -9 -f "next dev" 2>/dev/null && print_success "Killed frontend processes" || print_info "No frontend processes found"

# Force kill anything on our ports
print_info "Freeing ports ${BACKEND_PORT} and ${FRONTEND_PORT}..."
lsof -ti:${BACKEND_PORT} | xargs kill -9 2>/dev/null && print_success "Port ${BACKEND_PORT} freed" || print_info "Port ${BACKEND_PORT} already free"
lsof -ti:${FRONTEND_PORT} | xargs kill -9 2>/dev/null && print_success "Port ${FRONTEND_PORT} freed" || print_info "Port ${FRONTEND_PORT} already free"

# Wait for processes to fully terminate
sleep 2

print_success "All existing processes cleaned up"

################################################################################
# STEP 2: Activate Virtual Environment
################################################################################

print_header "🐍 Setting Up Python Environment"

# Find and activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    print_success "Activated .venv virtual environment"
elif [ -d "venv" ]; then
    source venv/bin/activate
    print_success "Activated venv virtual environment"
else
    print_warning "No virtual environment found - using system Python"
fi

################################################################################
# STEP 3: Start Backend
################################################################################

print_header "🚀 Starting Fresh Backend (Port ${BACKEND_PORT})"

python -m tradingagents.api.main > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}   Backend PID: ${BACKEND_PID}${NC}"

# Wait for backend to be ready
print_info "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
        print_success "Backend is ready and responding!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_warning "Backend took longer than expected. Check backend.log for details."
        break
    fi
    sleep 1
done

################################################################################
# STEP 4: Clear Frontend Cache and Start
################################################################################

print_header "🎨 Starting Fresh Frontend (Port ${FRONTEND_PORT})"

cd web-app

# Clear Next.js cache
print_info "Clearing Next.js cache..."
rm -rf .next 2>/dev/null && print_success "Cleared .next cache" || print_info "No cache to clear"

# Start frontend with clean cache
print_info "Starting Next.js dev server..."
npm run dev -- -p ${FRONTEND_PORT} > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}   Frontend PID: ${FRONTEND_PID}${NC}"

# Wait for frontend to be ready
print_info "Waiting for frontend to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:${FRONTEND_PORT} >/dev/null 2>&1; then
        print_success "Frontend is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        print_warning "Frontend took longer than expected. Check frontend.log for details."
        break
    fi
    sleep 1
done

################################################################################
# Success Message
################################################################################

print_header "✨ Fresh Application Started!"

echo -e "${GREEN}Services are now running:${NC}"
echo -e "   ${CYAN}📊 Backend API:${NC}     http://localhost:${BACKEND_PORT}"
echo -e "   ${CYAN}📚 API Docs:${NC}        http://localhost:${BACKEND_PORT}/docs"
echo -e "   ${CYAN}💻 Frontend UI:${NC}     http://localhost:${FRONTEND_PORT}"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo -e "   ${CYAN}Backend:${NC}  tail -f backend.log"
echo -e "   ${CYAN}Frontend:${NC} tail -f frontend.log"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   - Hard refresh browser: ${CYAN}Cmd+Shift+R${NC} (Mac) or ${CYAN}Ctrl+Shift+R${NC} (Windows/Linux)"
echo -e "   - Press ${YELLOW}Ctrl+C${NC} to stop all services"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Wait for both processes
wait
