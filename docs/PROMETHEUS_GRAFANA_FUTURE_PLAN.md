# Prometheus + Grafana Integration Plan (Phase 2)

**Status:** Future Enhancement  
**Timeline:** After 2-4 weeks of Langfuse usage  
**Purpose:** Add general-purpose monitoring alongside Langfuse

---

## 🎯 Why Add Prometheus + Grafana?

While Langfuse is excellent for **LLM-specific monitoring**, Prometheus + Grafana adds:

1. **System Metrics** - CPU, memory, disk, network
2. **Application Metrics** - Analysis counts, error rates, queue lengths
3. **Database Metrics** - Query performance, connection pools
4. **Infrastructure Monitoring** - Docker containers, services health
5. **Custom Dashboards** - Business metrics, KPIs
6. **Advanced Alerting** - Complex alert rules, multiple channels

**Langfuse + Prometheus/Grafana = Complete Monitoring Solution**

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    TradingAgents App                      │
│  ┌──────────────┐              ┌──────────────┐         │
│  │  Langfuse    │              │  Prometheus  │         │
│  │  (LLM Traces)│              │  (Metrics)   │         │
│  └──────┬───────┘              └──────┬───────┘         │
│         │                              │                  │
│         └──────────┬───────────────────┘                 │
│                    │                                      │
│                    ▼                                      │
│         ┌──────────────────────┐                         │
│         │      Grafana         │                         │
│         │  (Unified Dashboards) │                         │
│         └──────────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Components

### 1. Prometheus
- **Role:** Metrics collection and storage
- **Port:** 9090
- **Data:** Time-series metrics
- **Retention:** Configurable (default: 15 days)

### 2. Grafana
- **Role:** Visualization and dashboards
- **Port:** 3001 (to avoid conflict with Langfuse)
- **Data Sources:** Prometheus, Langfuse API (via JSON)
- **Dashboards:** Pre-built + custom

### 3. Exporters (Metrics Sources)
- **Node Exporter** - System metrics (CPU, memory, disk)
- **PostgreSQL Exporter** - Database metrics
- **Custom Python Exporter** - Application metrics

---

## 📋 Implementation Plan

### Phase 2.1: Setup Infrastructure (Week 1)

#### Step 1: Docker Compose Setup

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-clock-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    restart: unless-stopped
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres-exporter
    ports:
      - "9187:9187"
    environment:
      DATA_SOURCE_NAME: "postgresql://langfuse:langfuse@langfuse-db:5432/langfuse?sslmode=disable"
    restart: unless-stopped
    depends_on:
      - langfuse-db

volumes:
  prometheus-data:
  grafana-data:
```

#### Step 2: Prometheus Configuration

Create `monitoring/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # TradingAgents App (custom metrics)
  - job_name: 'tradingagents'
    static_configs:
      - targets: ['host.docker.internal:8000']  # Your app metrics endpoint
    metrics_path: '/metrics'
```

#### Step 3: Start Services

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Verify
docker-compose -f docker-compose.monitoring.yml ps
```

---

### Phase 2.2: Add Metrics to Application (Week 2)

#### Step 1: Install Prometheus Client

```bash
pip install prometheus-client
```

#### Step 2: Create Metrics Module

Create `tradingagents/monitoring/prometheus_metrics.py`:

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Analysis metrics
analyses_total = Counter(
    'tradingagents_analyses_total',
    'Total number of analyses',
    ['ticker', 'status']
)

analysis_duration = Histogram(
    'tradingagents_analysis_duration_seconds',
    'Analysis duration in seconds',
    ['ticker']
)

# Agent metrics
agent_executions_total = Counter(
    'tradingagents_agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status']
)

agent_duration = Histogram(
    'tradingagents_agent_duration_seconds',
    'Agent execution duration',
    ['agent_name']
)

# System metrics
active_analyses = Gauge(
    'tradingagents_active_analyses',
    'Number of analyses currently running'
)

# Cost metrics (from Langfuse API)
llm_cost_total = Counter(
    'tradingagents_llm_cost_usd',
    'Total LLM cost in USD',
    ['model', 'agent']
)

def start_metrics_server(port=8000):
    """Start Prometheus metrics HTTP server."""
    start_http_server(port)
    print(f"✓ Prometheus metrics server started on port {port}")
```

#### Step 3: Integrate Metrics

Add to `TradingAgentsGraph.propagate()`:

```python
from tradingagents.monitoring.prometheus_metrics import (
    analyses_total,
    analysis_duration,
    active_analyses
)

def propagate(self, company_name, trade_date, store_analysis=False):
    # Track active analysis
    active_analyses.inc()
    
    start_time = time.time()
    try:
        # ... existing code ...
        
        # Track success
        analyses_total.labels(
            ticker=company_name,
            status='success'
        ).inc()
        
    except Exception as e:
        # Track failure
        analyses_total.labels(
            ticker=company_name,
            status='error'
        ).inc()
        raise
    finally:
        # Track duration
        duration = time.time() - start_time
        analysis_duration.labels(ticker=company_name).observe(duration)
        active_analyses.dec()
```

---

### Phase 2.3: Grafana Dashboards (Week 3)

#### Step 1: Access Grafana

```
http://localhost:3001
Login: admin / admin
```

#### Step 2: Add Prometheus Data Source

1. Go to **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. URL: `http://prometheus:9090`
5. Click **Save & Test**

#### Step 3: Create Dashboards

**Dashboard 1: System Overview**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

**Dashboard 2: Application Metrics**
- Analysis count (total, success, errors)
- Analysis duration
- Active analyses
- Error rate

**Dashboard 3: Agent Performance**
- Executions per agent
- Duration per agent
- Success rate per agent
- Cost per agent

**Dashboard 4: Database Metrics**
- Query performance
- Connection pool
- Cache hit rate

---

### Phase 2.4: Alerting (Week 4)

#### Step 1: Configure Alert Rules

Create `monitoring/prometheus/alerts.yml`:

```yaml
groups:
  - name: tradingagents_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(tradingagents_analyses_total{status="error"}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
          
      - alert: SlowAnalysis
        expr: histogram_quantile(0.95, tradingagents_analysis_duration_seconds) > 300
        for: 10m
        annotations:
          summary: "Analysis taking too long"
          
      - alert: HighLLMCost
        expr: rate(tradingagents_llm_cost_usd[1h]) > 10
        for: 1h
        annotations:
          summary: "High LLM costs detected"
```

#### Step 2: Configure Alertmanager

Set up Alertmanager for notifications (Slack, Email, etc.)

---

## 📊 Metrics to Track

### Application Metrics
- Analysis count (total, success, error)
- Analysis duration (p50, p95, p99)
- Active analyses
- Queue length (if async)

### Agent Metrics
- Executions per agent
- Duration per agent
- Success rate per agent
- Token usage per agent
- Cost per agent

### System Metrics
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

### Database Metrics
- Query duration
- Connection pool size
- Cache hit rate
- Slow queries

### Business Metrics
- Analyses per day
- Average cost per analysis
- Win rate (if tracking outcomes)
- User satisfaction scores

---

## 🔄 Integration with Langfuse

### Option 1: Langfuse API Integration

Query Langfuse API from Grafana:

```python
# Create custom exporter
from prometheus_client import Gauge
import requests

langfuse_cost = Gauge(
    'langfuse_total_cost_usd',
    'Total cost from Langfuse'
)

def update_langfuse_metrics():
    # Query Langfuse API
    response = requests.get('http://localhost:3000/api/public/metrics')
    data = response.json()
    langfuse_cost.set(data['total_cost'])
```

### Option 2: Combined Dashboard

- **Langfuse:** LLM traces, debugging
- **Prometheus:** System metrics, application metrics
- **Grafana:** Unified view of both

---

## 📅 Timeline

### Week 1: Infrastructure Setup
- [ ] Docker Compose setup
- [ ] Prometheus configuration
- [ ] Grafana setup
- [ ] Basic dashboards

### Week 2: Application Integration
- [ ] Add Prometheus client
- [ ] Instrument code with metrics
- [ ] Test metrics collection

### Week 3: Dashboards
- [ ] Create system dashboard
- [ ] Create application dashboard
- [ ] Create agent performance dashboard
- [ ] Create business metrics dashboard

### Week 4: Alerting
- [ ] Configure alert rules
- [ ] Set up Alertmanager
- [ ] Configure notification channels
- [ ] Test alerts

---

## 🎯 Success Criteria

- ✅ Prometheus collecting metrics
- ✅ Grafana dashboards showing data
- ✅ Alerts configured and working
- ✅ Team using dashboards regularly
- ✅ Langfuse + Prometheus working together

---

## 📚 Resources

- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **Prometheus Python Client:** https://github.com/prometheus/client_python
- **Grafana Dashboards:** https://grafana.com/grafana/dashboards/

---

## ⚠️ When to Implement

**Start Phase 2 when:**
- ✅ Langfuse is running smoothly (2-4 weeks)
- ✅ You need system-level metrics
- ✅ You need advanced alerting
- ✅ Team wants unified dashboards
- ✅ You're ready for more complexity

**Don't start if:**
- ❌ Langfuse isn't set up yet
- ❌ You're still learning Langfuse
- ❌ Basic monitoring is sufficient
- ❌ Team is overwhelmed

---

**Remember:** Langfuse handles LLM monitoring excellently. Prometheus + Grafana adds general monitoring. Start with Langfuse, add Prometheus/Grafana when needed!

