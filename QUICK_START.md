# 🚀 TradingAgents - Quick Start

## Start the Application

```bash
./start.sh
```

That's it! The script will:
- ✅ Check all requirements
- ✅ Install missing dependencies
- ✅ Start backend & frontend
- ✅ Open in your browser

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend UI** | http://localhost:3005 | Main trading dashboard |
| **Backend API** | http://localhost:8005 | REST API |
| **API Docs** | http://localhost:8005/docs | Interactive API documentation |

## Common Commands

### Start Application
```bash
./start.sh                    # Full startup with checks
./start_assistant.sh          # Quick start (legacy)
```

### Stop Application
```bash
# Press Ctrl+C in the terminal running the services
# OR manually kill processes:
pkill -f "tradingagents.api.main"
pkill -f "next dev"
```

### Backend Only
```bash
source .venv/bin/activate
python -m tradingagents.api.main
```

### Frontend Only
```bash
cd web-app
npm run dev -- -p 3005
```

## First Time Setup

1. **Clone & Navigate**
   ```bash
   cd /path/to/TradingAgents
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Add your API keys
   ```

3. **Start**
   ```bash
   ./start.sh
   ```

## Required API Keys

Add these to your `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-...                    # Get from platform.openai.com
ALPHA_VANTAGE_API_KEY=...               # Get from alphavantage.co

# Optional
ANTHROPIC_API_KEY=sk-ant-...            # For Claude models
GOOGLE_API_KEY=...                       # For Gemini models
```

## Troubleshooting

### Port in Use?
```bash
lsof -ti:8005 | xargs kill -9    # Kill backend
lsof -ti:3005 | xargs kill -9    # Kill frontend
```

### Dependencies Issue?
```bash
# Python
source .venv/bin/activate
pip install -e .

# Node.js
cd web-app && npm install
```

### Can't Start?
Check the detailed guide:
```bash
cat STARTUP_GUIDE.md
```

## Key Features

| Feature | Location | Description |
|---------|----------|-------------|
| **Chat Analysis** | Analysis tab | AI-powered stock analysis |
| **Direct Analysis** | Direct tab | Quick ticker analysis |
| **Portfolio** | Portfolio tab | Manage positions |
| **Risk Dashboard** | Risk tab | Portfolio risk analysis |
| **History** | History tab | Past analyses |
| **Analytics** | Analytics tab | Performance metrics |

## Next Steps

1. ✅ Start the application with `./start.sh`
2. 🌐 Open http://localhost:3005
3. 📊 Try analyzing a stock (e.g., AAPL, NVDA, TSLA)
4. 💼 Build your portfolio
5. 📈 Check risk metrics

## Getting Help

- 📚 Full Guide: `STARTUP_GUIDE.md`
- 🔧 API Docs: http://localhost:8005/docs
- ⚠️ Issues: Check terminal output for errors

---

**Pro Tip:** Keep the terminal open to see logs and easily stop services with Ctrl+C
