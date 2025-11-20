# Monitoring Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install prometheus-client prometheus-fastapi-instrumentator psutil
```

### Step 2: Configure Environment
Create/update `.env` file:
```bash
POSTGRES_PASSWORD=your_actual_password
POSTGRES_HOST=localhost
POSTGRES_DB=investment_intelligence
```

### Step 3: Start Everything
```bash
# Start monitoring stack
./scripts/start-monitoring.sh

# Start your API (in another terminal)
uvicorn tradingagents.api.main:app --host 0.0.0.0 --port 8005
```

## 📊 Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin/admin |
| **Prometheus** | http://localhost:9090 | None |
| **AlertManager** | http://localhost:9093 | None |
| **API Metrics** | http://localhost:8005/metrics | None |

## 🎯 What to Monitor

### Key Metrics Dashboard
Open Grafana → **Trading Agents - Overview** to see:

✅ **API Health** - Is the API up?
📈 **Request Rate** - How many requests per second?
⏱️ **Response Time** - p50, p95, p99 latencies
😊 **User Satisfaction** - Average feedback score
🤖 **LLM Usage** - Token consumption and costs
💻 **System Resources** - CPU, Memory, Disk

### Business Metrics
- Trading signals generated
- Tickers analyzed
- User interactions
- Analysis requests

## 🚨 Built-in Alerts

You'll be automatically alerted for:
- API downtime (>1 min)
- High error rates (>10%)
- Slow responses (>30s)
- Database issues
- High resource usage
- Low user satisfaction

Configure notifications in `monitoring/alertmanager/alertmanager.yml`

## 🔍 Quick Queries

### Find Errors in Logs
Grafana → Explore → Loki:
```logql
{job="tradingagents"} |= "error" | json
```

### Check Error Rate
Prometheus → Graph:
```promql
rate(tradingagents_chat_failures_total[5m])
```

### Top Analyzed Tickers
```promql
topk(10, sum by (ticker) (tradingagents_analysis_requests_total))
```

## 🛑 Stop Monitoring
```bash
./scripts/stop-monitoring.sh
```

## 📖 Full Documentation
See [MONITORING.md](./MONITORING.md) for complete details.
