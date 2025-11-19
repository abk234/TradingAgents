# Using Existing Langfuse Installation

## ✅ Status: Langfuse Already Running

You already have Langfuse running on your machine!

**Location:** `/Users/lxupkzwjs/Developer/langfuse/`

**Components Running:**
- ✅ PostgreSQL database (`langfuse-postgres-1`)
- ✅ Redis (`langfuse-redis-1`)
- ✅ ClickHouse (`langfuse-clickhouse-1`)
- ✅ MinIO (`langfuse-minio-1`)
- ✅ Langfuse Worker (`langfuse-langfuse-worker-1`)
- ⚠️ Langfuse Web (`langfuse-langfuse-web-1`) - May need attention

---

## 🔍 Check Current Status

### 1. Check if Web UI is Accessible

```bash
# Try accessing the web UI
curl http://localhost:3000

# Or open in browser
open http://localhost:3000
```

### 2. Check Container Status

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose ps
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose ps
```

### 3. Check Web Container Logs

```bash
docker logs langfuse-langfuse-web-1 --tail 50
```

---

## 🔧 Fix Web Container (If Needed)

If the web container is restarting, it's likely a database connection issue:

### Option 1: Restart All Services

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose restart
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose restart
```

### Option 2: Recreate Web Container

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose up -d --force-recreate langfuse-web
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose up -d --force-recreate langfuse-web
```

### Option 3: Check Database Connection

```bash
# Test database connection
docker exec langfuse-postgres-1 psql -U postgres -d postgres -c "SELECT 1;"
```

---

## 🔑 Get Your API Keys

Once the web UI is accessible:

1. **Open Langfuse:** `http://localhost:3000`
2. **Login** with your existing account
3. **Go to Settings** → **API Keys**
4. **Create or copy** your Public Key and Secret Key

---

## ⚙️ Configure TradingAgents

### 1. Add to `.env` File

Add these variables to your TradingAgents `.env` file:

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
    print("❌ Langfuse not connected. Check your API keys.")
```

---

## 🚀 Use Existing Setup

**No need to create a new Docker Compose file!** 

Your existing Langfuse installation at `/Users/lxupkzwjs/Developer/langfuse/` is perfect. Just:

1. ✅ Make sure web UI is running (`http://localhost:3000`)
2. ✅ Get your API keys from the web UI
3. ✅ Add keys to your `.env` file
4. ✅ Install `langfuse` Python package
5. ✅ Start using it!

---

## 📊 Verify Everything Works

### Run a Test Analysis

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from datetime import date

graph = TradingAgentsGraph(enable_langfuse=True)
result, signal = graph.propagate("AAPL", date.today())
```

### Check Traces in Langfuse

1. Open `http://localhost:3000`
2. Go to **Traces**
3. You should see: `"Stock Analysis: AAPL"`

---

## 🔄 Managing Your Existing Langfuse

### Start Services

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose up -d
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose up -d
```

### Stop Services

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose stop
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose stop
```

### View Logs

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose logs -f langfuse-web
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose logs -f langfuse-web
```

### Restart Services

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose restart
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose restart
```

---

## ⚠️ Important Notes

1. **Don't create a new Langfuse instance** - Use your existing one!
2. **Port 3000** - Make sure nothing else is using this port
3. **Database** - Your existing PostgreSQL is already set up
4. **API Keys** - Use the keys from your existing Langfuse instance

---

## 🆘 Troubleshooting

### Web UI Not Accessible

```bash
# Check if port 3000 is in use
lsof -i :3000

# Check web container logs
docker logs langfuse-langfuse-web-1 --tail 50

# Restart web container
cd /Users/lxupkzwjs/Developer/langfuse
docker compose restart langfuse-web
# Note: If your existing setup uses older Docker Compose V1, use: docker-compose restart langfuse-web
```

### Can't Connect from TradingAgents

1. Verify API keys are correct
2. Check `LANGFUSE_HOST=http://localhost:3000`
3. Test connection:
   ```python
   from langfuse import Langfuse
   langfuse = Langfuse(
       public_key="pk_your_key",
       secret_key="sk_your_key",
       host="http://localhost:3000"
   )
   langfuse.health()
   ```

### Database Connection Issues

```bash
# Check database is running
docker ps | grep langfuse-postgres

# Test connection
docker exec langfuse-postgres-1 psql -U postgres -c "SELECT version();"
```

---

## ✅ Next Steps

1. **Verify web UI** - Open `http://localhost:3000`
2. **Get API keys** - From Settings → API Keys
3. **Configure TradingAgents** - Add keys to `.env`
4. **Test integration** - Run a test analysis
5. **View traces** - Check Langfuse dashboard

---

**You're all set!** Use your existing Langfuse installation - no need to create a new one.

