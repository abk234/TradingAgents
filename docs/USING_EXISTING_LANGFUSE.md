# Using Your Existing Langfuse Instance

## ✅ Setup Complete!

You're using your existing Langfuse installation at `/Users/lxupkzwjs/Developer/langfuse/`

---

## 🔍 Check Status

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose ps
```

You should see:
- ✅ `langfuse-postgres-1` - Database
- ✅ `langfuse-redis-1` - Cache
- ✅ `langfuse-clickhouse-1` - Analytics
- ✅ `langfuse-minio-1` - Object storage
- ✅ `langfuse-langfuse-worker-1` - Worker
- ✅ `langfuse-langfuse-web-1` - Web UI (should be running)

---

## 🌐 Access Langfuse

**Web UI:** `http://localhost:3000`

If you see an error:
1. Wait 30-60 seconds for startup
2. Check logs: `docker compose logs langfuse-web --tail 50`
3. Restart: `docker compose restart langfuse-web`

---

## 🔑 Get Your API Keys

1. **Open:** `http://localhost:3000`
2. **Login** with your existing account
3. **Go to:** Settings → API Keys (or Projects → [Your Project] → Settings → API Keys)
4. **Create or copy** your keys:
   - **Public Key** (starts with `pk_...`)
   - **Secret Key** (starts with `sk_...`) ⚠️ Save this!

---

## ⚙️ Configure TradingAgents

### 1. Add to `.env` File

Add these to your TradingAgents `.env` file:

```bash
# Langfuse Configuration (using existing instance)
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk_your_existing_key_here
LANGFUSE_SECRET_KEY=sk_your_existing_key_here
LANGFUSE_HOST=http://localhost:3000
```

### 2. Install Langfuse Python Package

```bash
pip install langfuse>=2.0.0
```

### 3. Test Connection

```python
from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer

tracer = get_langfuse_tracer()
if tracer and tracer.enabled:
    print("✅ Langfuse connected!")
else:
    print("❌ Check your API keys in .env")
```

---

## ✅ Test Integration

Run a test analysis:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import date

# Create graph with Langfuse enabled
graph = TradingAgentsGraph(enable_langfuse=True)

# Run an analysis
result, signal = graph.propagate("AAPL", date.today())

print("✅ Analysis complete! Check Langfuse dashboard.")
```

---

## 📊 View Traces

1. Open `http://localhost:3000`
2. Go to **Traces** in sidebar
3. You should see: `"Stock Analysis: AAPL"`
4. Click to see:
   - All 13 agent executions
   - LLM calls with tokens/costs
   - Tool usage
   - Full execution flow

---

## 🛠️ Managing Your Langfuse

### Start Services

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose up -d
```

### Stop Services

```bash
docker compose stop
```

### View Logs

```bash
# All services
docker compose logs -f

# Just web UI
docker compose logs -f langfuse-web

# Just worker
docker compose logs -f langfuse-worker
```

### Restart Services

```bash
docker compose restart
```

---

## 🐛 Troubleshooting

### Web UI Not Accessible

```bash
# Check status
docker compose ps

# Check logs
docker compose logs langfuse-web --tail 50

# Restart web container
docker compose restart langfuse-web

# If still failing, check database connection
docker compose logs postgres --tail 20
```

### Can't Connect from TradingAgents

1. Verify API keys are correct in `.env`
2. Check `LANGFUSE_HOST=http://localhost:3000`
3. Test connection:
   ```python
   from langfuse import Langfuse
   langfuse = Langfuse(
       public_key="pk_your_key",
       secret_key="sk_your_key",
       host="http://localhost:3000"
   )
   print(langfuse.health())
   ```

### Port Conflicts

If port 3000 is in use:
```bash
# Find what's using it
lsof -i :3000

# Stop conflicting service or change Langfuse port in docker-compose.yml
```

---

## ✅ Success Checklist

- [ ] Existing Langfuse running (`docker compose ps`)
- [ ] Web UI accessible (`http://localhost:3000`)
- [ ] Logged into Langfuse
- [ ] API keys obtained
- [ ] Keys added to TradingAgents `.env`
- [ ] Langfuse Python package installed
- [ ] Test analysis run successfully
- [ ] Traces visible in dashboard

---

## 🎉 You're All Set!

Your TradingAgents will now automatically trace all agent executions to your existing Langfuse instance!

**Next:** Start monitoring your 13 agents! 🚀

---

## 📝 Notes

- **No new infrastructure** - Using your existing setup
- **All data** - Stored in your existing Langfuse database
- **Same instance** - All your other projects can use it too
- **Clean setup** - Removed the new Langfuse containers we created

