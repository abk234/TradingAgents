# TradingAgents Startup Guide

## Quick Start

The easiest way to start the application is using the comprehensive startup script:

```bash
./start.sh
```

This script will automatically:
- ✅ Check all system requirements
- ✅ Verify dependencies are installed
- ✅ Validate configuration files
- ✅ Start backend and frontend services
- ✅ Provide health checks and status updates

## What the Startup Script Checks

### 1. **System Requirements**
- Python 3.10 or higher
- Node.js 18 or higher
- npm package manager

### 2. **Python Environment**
- Virtual environment (`.venv` or `venv`)
- Python dependencies from `pyproject.toml`
- `tradingagents` package installation

### 3. **Node.js Environment**
- `web-app/node_modules` directory
- Frontend dependencies from `package.json`

### 4. **Configuration Files**
- `.env` file existence
- Environment variable validation
- API key configuration

### 5. **Optional Services**
- PostgreSQL database (for persistence)
- Redis server (for caching)

### 6. **Port Availability**
- Backend port 8005
- Frontend port 3005
- Automatic cleanup of existing processes

## Manual Setup (If Script Fails)

If the startup script encounters issues, you can start services manually:

### Backend (FastAPI)

```bash
# 1. Activate virtual environment
source .venv/bin/activate  # or source venv/bin/activate

# 2. Install dependencies (if needed)
pip install -e .

# 3. Start backend
python -m tradingagents.api.main
```

The backend will be available at:
- API: http://localhost:8005
- Documentation: http://localhost:8005/docs

### Frontend (Next.js)

```bash
# 1. Navigate to web-app directory
cd web-app

# 2. Install dependencies (if needed)
npm install

# 3. Start development server
npm run dev -- -p 3005
```

The frontend will be available at:
- UI: http://localhost:3005

## First-Time Setup

### 1. Install System Dependencies

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.13

# Install Node.js
brew install node

# Install PostgreSQL (optional)
brew install postgresql@14
brew services start postgresql@14

# Install Redis (optional)
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
# Update package list
sudo apt update

# Install Python
sudo apt install python3.13 python3.13-venv python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs

# Install PostgreSQL (optional)
sudo apt install postgresql postgresql-contrib

# Install Redis (optional)
sudo apt install redis-server
sudo systemctl start redis-server
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

**Required API Keys:**
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys
- `ALPHA_VANTAGE_API_KEY`: Get from https://www.alphavantage.co/support/#api-key

**Optional API Keys:**
- `ANTHROPIC_API_KEY`: For Claude models
- `GOOGLE_API_KEY`: For Gemini models

### 3. Initialize Database (if using PostgreSQL)

```bash
# Create database
createdb investment_intelligence

# Run initialization script (if exists)
python scripts/init_database.py
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Kill process on port 8005 (backend)
lsof -ti:8005 | xargs kill -9

# Kill process on port 3005 (frontend)
lsof -ti:3005 | xargs kill -9
```

### Virtual Environment Issues

```bash
# Remove existing virtual environment
rm -rf .venv

# Create new virtual environment
python3 -m venv .venv

# Activate and install dependencies
source .venv/bin/activate
pip install -e .
```

### Node Modules Issues

```bash
# Remove existing node_modules
cd web-app
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

### Python Import Errors

```bash
# Reinstall in development mode
pip install -e . --force-reinstall
```

### Redis Connection Errors

```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis-server
```

## Alternative Startup Scripts

The project includes several startup scripts for different use cases:

| Script | Purpose | Usage |
|--------|---------|-------|
| `start.sh` | **Comprehensive startup** with all checks | `./start.sh` |
| `start_assistant.sh` | Quick start (less validation) | `./start_assistant.sh` |
| `scripts/bin/start_eddie.sh` | Backend API only | `./scripts/bin/start_eddie.sh` |
| `scripts/start-monitoring.sh` | Start with monitoring stack | `./scripts/start-monitoring.sh` |

## Stopping the Application

To stop all services:

1. **If using startup script:** Press `Ctrl+C` in the terminal
2. **Manual cleanup:**
   ```bash
   # Kill backend
   pkill -f "tradingagents.api.main"

   # Kill frontend
   pkill -f "next dev"
   ```

## Health Checks

### Backend Health

```bash
# Check if backend is responding
curl http://localhost:8005/health

# Or visit in browser
open http://localhost:8005/docs
```

### Frontend Health

```bash
# Check if frontend is responding
curl http://localhost:3005

# Or visit in browser
open http://localhost:3005
```

## Environment Variables Reference

See `.env.example` for all available configuration options:

### Core Settings
- `OPENAI_API_KEY`: Required for AI features
- `ALPHA_VANTAGE_API_KEY`: Required for stock data

### Optional Features
- `EMAIL_ENABLED`: Enable email notifications
- `SLACK_ENABLED`: Enable Slack notifications
- `SECTOR_ANALYSIS_ENABLED`: Enable sector-based analysis

### Portfolio Settings
- `DEFAULT_PORTFOLIO_VALUE`: Default portfolio size
- `RISK_TOLERANCE`: conservative/moderate/aggressive
- `MAX_POSITION_SIZE`: Maximum position as % of portfolio

## Performance Tips

1. **Use SSD:** The application works best on SSD storage
2. **Memory:** Recommended 8GB+ RAM
3. **Network:** Stable internet connection for API calls
4. **Redis:** Enable Redis for better caching performance
5. **PostgreSQL:** Use PostgreSQL for better data persistence

## Getting Help

If you encounter issues:

1. Check the logs in the terminal output
2. Review the troubleshooting section above
3. Check API documentation at http://localhost:8005/docs
4. Ensure all API keys are properly configured in `.env`

## Next Steps

Once the application is running:

1. **Access the UI:** Open http://localhost:3005 in your browser
2. **Explore API Docs:** Visit http://localhost:8005/docs
3. **Try Voice Features:** Click the microphone button in the UI
4. **Analyze Stocks:** Enter a stock ticker in the Direct Analysis view
5. **Build Portfolio:** Add positions in the Portfolio view
6. **Check Risk:** Review your portfolio risk in the Risk Dashboard

---

**Note:** The startup script is the recommended way to start the application as it performs comprehensive checks and ensures all prerequisites are met.
