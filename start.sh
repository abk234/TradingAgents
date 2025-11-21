#!/bin/bash

################################################################################
# TradingAgents Application Startup Script
#
# This script performs comprehensive checks before starting the application:
# - Verifies all dependencies (Python, Node.js, databases, etc.)
# - Checks configuration files
# - Ensures services are ready
# - Starts backend and frontend with proper error handling
################################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
BACKEND_PORT=8005
FRONTEND_PORT=3005
PYTHON_MIN_VERSION="3.10"
NODE_MIN_VERSION="18"

# Error tracking
ERRORS=()
WARNINGS=()

################################################################################
# Helper Functions
################################################################################

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
    WARNINGS+=("$1")
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ERRORS+=("$1")
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

version_ge() {
    [ "$1" = "$(echo -e "$1\n$2" | sort -V | tail -n1)" ]
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

kill_port() {
    local port=$1
    local service_name=$2

    if lsof -ti:$port > /dev/null 2>&1; then
        print_warning "Found existing process on port ${port} (${service_name}). Stopping..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1

        if lsof -ti:$port > /dev/null 2>&1; then
            print_error "Could not free port ${port}. Manual intervention required."
            echo -e "   ${YELLOW}Run: lsof -ti:${port} | xargs kill -9${NC}"
            return 1
        else
            print_success "Port ${port} is now free"
        fi
    else
        print_success "Port ${port} is available"
    fi
    return 0
}

cleanup() {
    echo -e "\n${BLUE}🛑 Shutting down services...${NC}"
    jobs -p | xargs -r kill 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

################################################################################
# Pre-flight Checks
################################################################################

print_header "🚀 TradingAgents Startup - Pre-flight Checks"

# 1. Check Python
print_info "Checking Python installation..."
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    if version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        print_success "Python $PYTHON_VERSION (>= $PYTHON_MIN_VERSION required)"
    else
        print_error "Python $PYTHON_VERSION found, but >= $PYTHON_MIN_VERSION required"
    fi
else
    print_error "Python 3 is not installed"
fi

# 2. Check Node.js
print_info "Checking Node.js installation..."
if check_command node; then
    NODE_VERSION=$(node --version | sed 's/v//')
    if version_ge "$NODE_VERSION" "$NODE_MIN_VERSION"; then
        print_success "Node.js $NODE_VERSION (>= $NODE_MIN_VERSION required)"
    else
        print_error "Node.js $NODE_VERSION found, but >= $NODE_MIN_VERSION required"
    fi
else
    print_error "Node.js is not installed"
fi

# 3. Check npm
print_info "Checking npm installation..."
if check_command npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION"
else
    print_error "npm is not installed"
fi

# 4. Check Python Virtual Environment
print_info "Checking Python virtual environment..."
if [ -d ".venv" ]; then
    print_success "Virtual environment found at .venv/"
    VENV_PATH=".venv"
elif [ -d "venv" ]; then
    print_success "Virtual environment found at venv/"
    VENV_PATH="venv"
else
    print_error "No virtual environment found (.venv or venv)"
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created at .venv/"
        VENV_PATH=".venv"
    else
        print_error "Failed to create virtual environment"
    fi
fi

# Activate virtual environment
if [ -n "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
fi

# 5. Check Python Dependencies
print_info "Checking Python dependencies..."
if [ -f "pyproject.toml" ]; then
    print_success "pyproject.toml found"

    # Check if key packages are installed
    if python -c "import tradingagents" 2>/dev/null; then
        print_success "tradingagents package is installed"
    else
        print_warning "tradingagents package not found. Installing dependencies..."
        pip install -e . --quiet
        if [ $? -eq 0 ]; then
            print_success "Dependencies installed successfully"
        else
            print_error "Failed to install Python dependencies"
        fi
    fi
else
    print_error "pyproject.toml not found"
fi

# 6. Check Node.js Dependencies
print_info "Checking Node.js dependencies (web-app)..."
if [ -d "web-app" ]; then
    if [ -d "web-app/node_modules" ]; then
        print_success "Node modules found in web-app/"
    else
        print_warning "Node modules not found. Installing..."
        cd web-app
        npm install --silent
        if [ $? -eq 0 ]; then
            print_success "Node dependencies installed successfully"
        else
            print_error "Failed to install Node dependencies"
        fi
        cd ..
    fi
else
    print_error "web-app directory not found"
fi

# 7. Check Environment Variables
print_info "Checking environment configuration..."
if [ -f ".env" ]; then
    print_success ".env file found"

    # Check for critical environment variables
    if grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env 2>/dev/null; then
        print_warning "OPENAI_API_KEY appears to be a placeholder. Please update .env file."
    elif grep -q "OPENAI_API_KEY=" .env 2>/dev/null; then
        print_success "OPENAI_API_KEY is configured"
    else
        print_warning "OPENAI_API_KEY not found in .env"
    fi
else
    print_error ".env file not found"
    if [ -f ".env.example" ]; then
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_success ".env file created. Please update it with your API keys."
        print_warning "You need to edit .env and add your API keys before the application will work properly."
    fi
fi

# 8. Check PostgreSQL (optional)
print_info "Checking PostgreSQL database..."
if check_command psql; then
    # Try to connect to default database
    if psql -U $USER -d postgres -c '\l' &>/dev/null 2>&1; then
        print_success "PostgreSQL is running and accessible"
    else
        print_warning "PostgreSQL installed but cannot connect. Database features may not work."
    fi
else
    print_warning "PostgreSQL not installed. Database features will be limited."
fi

# 9. Check Redis (optional)
print_info "Checking Redis server..."
if check_command redis-cli; then
    if redis-cli ping &>/dev/null; then
        print_success "Redis is running and accessible"
    else
        print_warning "Redis installed but not running. Caching features will be limited."
        print_info "You can start Redis with: redis-server (or brew services start redis)"
    fi
else
    print_warning "Redis not installed. Caching features will be limited."
fi

# 10. Check for port conflicts
print_info "Checking for port conflicts..."
kill_port $BACKEND_PORT "Backend API" || true
kill_port $FRONTEND_PORT "Frontend" || true

# Also kill any existing processes
if pgrep -f "tradingagents.api.main" > /dev/null 2>&1; then
    print_warning "Found existing tradingagents.api.main process. Stopping..."
    pkill -f "tradingagents.api.main" 2>/dev/null
    sleep 1
fi

if pgrep -f "next dev.*${FRONTEND_PORT}" > /dev/null 2>&1; then
    print_warning "Found existing Next.js dev server. Stopping..."
    pkill -f "next dev.*${FRONTEND_PORT}" 2>/dev/null
    sleep 1
fi

################################################################################
# Summary of Checks
################################################################################

print_header "📋 Pre-flight Check Summary"

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Critical Errors Found:${NC}"
    for error in "${ERRORS[@]}"; do
        echo -e "   - $error"
    done
    echo ""
    echo -e "${YELLOW}Please fix the errors above before starting the application.${NC}"
    exit 1
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings (${#WARNINGS[@]}):${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo -e "   - $warning"
    done
    echo ""
    echo -e "${YELLOW}The application may start with limited functionality.${NC}"
    echo -e "${BLUE}Continue anyway? (y/N) ${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Startup cancelled."
        exit 0
    fi
fi

print_success "All critical checks passed!"

################################################################################
# Start Services
################################################################################

print_header "🚀 Starting Services"

# Start Backend
print_info "Starting Backend API (FastAPI on port $BACKEND_PORT)..."
python -m tradingagents.api.main &
BACKEND_PID=$!
echo -e "${GREEN}   Backend PID: $BACKEND_PID${NC}"

# Wait for backend to be ready
print_info "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health &>/dev/null || \
       curl -s http://localhost:$BACKEND_PORT/docs &>/dev/null || \
       lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start within 30 seconds"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Start Frontend
print_info "Starting Frontend (Next.js on port $FRONTEND_PORT)..."
cd web-app
npm run dev -- -p $FRONTEND_PORT &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}   Frontend PID: $FRONTEND_PID${NC}"

# Wait for frontend to be ready
print_info "Waiting for frontend to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:$FRONTEND_PORT &>/dev/null; then
        print_success "Frontend is ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        print_warning "Frontend is taking longer than expected to start"
        break
    fi
    sleep 1
done

################################################################################
# Success Message
################################################################################

print_header "✨ TradingAgents is Running!"

echo -e "${GREEN}Services are now available:${NC}"
echo -e "   ${CYAN}📊 Backend API:${NC}     http://localhost:$BACKEND_PORT"
echo -e "   ${CYAN}📚 API Docs:${NC}        http://localhost:$BACKEND_PORT/docs"
echo -e "   ${CYAN}💻 Frontend UI:${NC}     http://localhost:$FRONTEND_PORT"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo -e "   - View API documentation at http://localhost:$BACKEND_PORT/docs"
echo -e "   - Access the trading dashboard at http://localhost:$FRONTEND_PORT"
echo -e "   - Press ${YELLOW}Ctrl+C${NC} to stop all services"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Wait for both processes
wait
