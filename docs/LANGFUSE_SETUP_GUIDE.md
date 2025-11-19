# Langfuse Setup Guide - Self-Hosted in Docker

Complete guide for setting up Langfuse self-hosted monitoring for TradingAgents.

---

## ⚠️ IMPORTANT: Check for Existing Installation

**Before proceeding, check if you already have Langfuse running:**

```bash
docker ps | grep langfuse
```

**If you see Langfuse containers running, see:** `LANGFUSE_EXISTING_SETUP.md`  
**This guide is for setting up a NEW Langfuse instance.**

---

## 🎯 Overview

This guide will help you:
1. Set up Langfuse in Docker (self-hosted)
2. Integrate Langfuse with your TradingAgents application
3. View traces and monitor agent performance
4. Plan for future Prometheus + Grafana integration

---

## 📋 Prerequisites

- Docker and Docker Compose installed
- PostgreSQL running (Langfuse uses its own database)
- Python 3.8+ with your TradingAgents environment
- **No existing Langfuse installation** (or use existing - see `LANGFUSE_EXISTING_SETUP.md`)

---

## 🚀 Step 1: Start Langfuse Server

### 1.1 Start Langfuse with Docker Compose

```bash
# Navigate to your project directory
cd /path/to/TradingAgents

# Start Langfuse services
docker compose -f docker-compose.langfuse-v2.yml up -d

# Check status
docker compose -f docker-compose.langfuse-v2.yml ps
```

You should see:
- `langfuse-db` (PostgreSQL) running on port 5433
- `langfuse-server` running on port 3000

### 1.2 Access Langfuse UI

Open your browser:
```
http://localhost:3000
```

You'll see the Langfuse setup page.

### 1.3 Create Admin Account

1. Click "Sign Up" or "Get Started"
2. Create your admin account (first user becomes admin)
3. You'll be redirected to the dashboard

### 1.4 Get Your API Keys

1. Go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. Name it (e.g., "TradingAgents Production")
4. Copy both:
   - **Public Key** (starts with `pk_...`)
   - **Secret Key** (starts with `sk_...`)

⚠️ **Important:** Save these keys securely! The secret key won't be shown again.

---

## 🔧 Step 2: Configure Environment Variables

### 2.1 Add to Your `.env` File

Add these variables to your `.env` file:

```bash
# Langfuse Configuration
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk_your_public_key_here
LANGFUSE_SECRET_KEY=sk_your_secret_key_here
LANGFUSE_HOST=http://localhost:3000

# Optional: Session/User tracking
LANGFUSE_SESSION_ID=default
LANGFUSE_USER_ID=system
LANGFUSE_RELEASE=v1.0.0
```

### 2.2 Verify Environment Variables

```bash
# Check if variables are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('LANGFUSE_ENABLED:', os.getenv('LANGFUSE_ENABLED'))"
```

---

## 📦 Step 3: Install Langfuse Python Package

```bash
# Install Langfuse
pip install langfuse>=2.0.0

# Or if using uv
uv pip install langfuse>=2.0.0

# Verify installation
python -c "import langfuse; print('Langfuse version:', langfuse.__version__)"
```

---

## ✅ Step 4: Test Integration

### 4.1 Run a Test Analysis

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import date

# Create graph with Langfuse enabled (default)
graph = TradingAgentsGraph(
    selected_analysts=["market", "news"],
    enable_langfuse=True  # Enabled by default
)

# Run an analysis
result, signal = graph.propagate(
    company_name="AAPL",
    trade_date=date.today(),
    store_analysis=False
)

print("Analysis complete! Check Langfuse dashboard.")
```

### 4.2 Check Langfuse Dashboard

1. Go to `http://localhost:3000`
2. Click on **"Traces"** in the sidebar
3. You should see your trace: `"Stock Analysis: AAPL"`
4. Click on it to see:
   - All agent executions
   - LLM calls
   - Tool usage
   - Token counts
   - Costs
   - Latency

---

## 📊 Step 5: View Agent Monitoring

### 5.1 Traces View

- **Location:** `http://localhost:3000/traces`
- **Shows:** All analysis runs with full execution details
- **Use for:** Debugging, understanding agent flow

### 5.2 Generations View

- **Location:** `http://localhost:3000/generations`
- **Shows:** Individual LLM calls across all agents
- **Use for:** Cost tracking, token usage, model performance

### 5.3 Scores View

- **Location:** `http://localhost:3000/scores`
- **Shows:** Quality scores and feedback
- **Use for:** Tracking agent quality over time

### 5.4 Datasets View

- **Location:** `http://localhost:3000/datasets`
- **Shows:** Test datasets for evaluation
- **Use for:** Testing agent improvements

---

## 🔍 Step 6: Advanced Usage

### 6.1 Custom Trace Metadata

The integration automatically adds:
- Ticker symbol
- Analysis date
- Selected analysts
- RAG enabled/disabled

### 6.2 Scoring Traces (Quality Feedback)

```python
from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer

tracer = get_langfuse_tracer()

# Score a trace (after analysis)
tracer.score_trace(
    trace_id="trace-id-from-langfuse",
    score=0.85,  # 0-1 scale
    comment="Good analysis, accurate predictions"
)
```

### 6.3 Disable Langfuse Temporarily

```python
# Disable via environment variable
export LANGFUSE_ENABLED=false

# Or in code
graph = TradingAgentsGraph(enable_langfuse=False)
```

---

## 🐛 Troubleshooting

### Issue: "Langfuse credentials not found"

**Solution:**
```bash
# Check environment variables
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# Make sure .env file is loaded
# Check your .env file has the keys
```

### Issue: "Cannot connect to Langfuse"

**Solution:**
```bash
# Check if Langfuse is running
docker compose -f docker-compose.langfuse-v2.yml ps

# Check logs
docker compose -f docker-compose.langfuse-v2.yml logs langfuse

# Restart if needed
docker compose -f docker-compose.langfuse-v2.yml restart
```

### Issue: "Port 3000 already in use"

**Solution:**
Edit `docker-compose.langfuse-v2.yml`:
```yaml
ports:
  - "3001:3000"  # Use different port
```

Then update `LANGFUSE_HOST=http://localhost:3001`

### Issue: "Database connection failed"

**Solution:**
```bash
# Check PostgreSQL container
docker compose -f docker-compose.langfuse-v2.yml logs postgres

# Restart database
docker compose -f docker-compose.langfuse-v2.yml restart postgres

# Wait for health check
docker compose -f docker-compose.langfuse-v2.yml ps
```

---

## 🔄 Step 7: Daily Operations

### Start Langfuse (on system boot)

```bash
# Start services
docker compose -f docker-compose.langfuse-v2.yml up -d

# Check status
docker compose -f docker-compose.langfuse-v2.yml ps
```

### Stop Langfuse

```bash
docker compose -f docker-compose.langfuse-v2.yml stop
```

### View Logs

```bash
# All services
docker compose -f docker-compose.langfuse-v2.yml logs

# Just Langfuse
docker compose -f docker-compose.langfuse-v2.yml logs langfuse

# Follow logs
docker compose -f docker-compose.langfuse-v2.yml logs -f langfuse
```

### Backup Database

```bash
# Backup Langfuse database
docker exec langfuse-db pg_dump -U langfuse langfuse > langfuse_backup_$(date +%Y%m%d).sql

# Restore
docker exec -i langfuse-db psql -U langfuse langfuse < langfuse_backup_20251117.sql
```

---

## 📈 Step 8: Monitoring Best Practices

### 8.1 Regular Review

- **Daily:** Check error rates, failed traces
- **Weekly:** Review cost trends, token usage
- **Monthly:** Analyze quality scores, agent performance

### 8.2 Cost Tracking

- Monitor token usage per agent
- Track costs per analysis
- Identify expensive agents
- Optimize prompts/models

### 8.3 Quality Monitoring

- Score traces after analysis
- Track quality trends
- Identify declining agents
- A/B test improvements

---

## 🚀 Future: Prometheus + Grafana Integration

### Phase 2 Plan (Coming Later)

When you're ready to add Prometheus + Grafana:

1. **Prometheus** - Collect metrics from:
   - Langfuse API (costs, latency)
   - Your application (analysis counts, errors)
   - Database (query performance)

2. **Grafana** - Visualize:
   - Agent performance dashboards
   - Cost trends
   - Error rates
   - System health

3. **Integration** - Combine:
   - Langfuse for LLM-specific traces
   - Prometheus for general metrics
   - Grafana for unified dashboards

**Timeline:** After 2-4 weeks of using Langfuse, evaluate if you need Prometheus/Grafana.

---

## 📚 Resources

- **Langfuse Docs:** https://langfuse.com/docs
- **LangGraph Integration:** https://langfuse.com/docs/integrations/langgraph
- **Self-Hosted Guide:** https://langfuse.com/docs/deployment/self-host
- **API Reference:** https://langfuse.com/docs/api

---

## ✅ Checklist

- [ ] Docker Compose file created
- [ ] Langfuse server running (`http://localhost:3000`)
- [ ] Admin account created
- [ ] API keys obtained and saved
- [ ] Environment variables configured
- [ ] Langfuse Python package installed
- [ ] Test analysis run successfully
- [ ] Traces visible in dashboard
- [ ] Monitoring workflow established

---

**Next Steps:**
1. Run a few analyses to generate traces
2. Explore the Langfuse dashboard
3. Set up regular monitoring routine
4. Plan Prometheus + Grafana integration (Phase 2)

---

**Questions?** Check the troubleshooting section or Langfuse documentation.

