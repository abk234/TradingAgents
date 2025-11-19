# Langfuse Quick Start - TradingAgents

## ✅ Status: Langfuse is Starting!

Your new Langfuse instance is being set up. Here's what to do next:

---

## 🔍 Step 1: Wait for Langfuse to Start

Langfuse needs about 30-60 seconds to fully start. Check status:

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
docker compose -f docker-compose.langfuse-v2.yml ps
```

You should see:
- `langfuse-db` - Healthy
- `langfuse-server` - Running

---

## 🌐 Step 2: Access Langfuse Web UI

Once started, open in your browser:

```
http://localhost:3000
```

**First time setup:**
1. You'll see the Langfuse setup page
2. Create your admin account (first user becomes admin)
3. You'll be redirected to the dashboard

---

## 🔑 Step 3: Get Your API Keys

1. **Login** to Langfuse (`http://localhost:3000`)
2. Go to **Settings** → **API Keys** (or **Projects** → Select Project → **Settings** → **API Keys**)
3. Click **"Create API Key"**
4. Name it (e.g., "TradingAgents Production")
5. **Copy both keys:**
   - **Public Key** (starts with `pk_...`)
   - **Secret Key** (starts with `sk_...`) ⚠️ **Save this - won't be shown again!**

---

## ⚙️ Step 4: Configure TradingAgents

### Add to `.env` File

Add these to your TradingAgents `.env` file:

```bash
# Langfuse Configuration
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk_your_public_key_here
LANGFUSE_SECRET_KEY=sk_your_secret_key_here
LANGFUSE_HOST=http://localhost:3000
```

### Install Langfuse Python Package

```bash
pip install langfuse>=2.0.0
```

---

## ✅ Step 5: Test Integration

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

## 📊 Step 6: View Traces

1. Open `http://localhost:3000`
2. Go to **Traces** in the sidebar
3. You should see: `"Stock Analysis: AAPL"`
4. Click on it to see:
   - All 13 agent executions
   - LLM calls with tokens and costs
   - Tool usage
   - Full execution flow

---

## 🛠️ Managing Langfuse

### Start Services

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
docker compose -f docker-compose.langfuse-v2.yml up -d
```

### Stop Services

```bash
docker compose -f docker-compose.langfuse-v2.yml stop
```

### View Logs

```bash
# All services
docker compose -f docker-compose.langfuse-v2.yml logs -f

# Just Langfuse server
docker compose -f docker-compose.langfuse-v2.yml logs -f langfuse
```

### Restart Services

```bash
docker compose -f docker-compose.langfuse-v2.yml restart
```

---

## 🐛 Troubleshooting

### Web UI Not Loading

```bash
# Check if containers are running
docker compose -f docker-compose.langfuse-v2.yml ps

# Check logs
docker compose -f docker-compose.langfuse-v2.yml logs langfuse --tail 50

# Restart
docker compose -f docker-compose.langfuse-v2.yml restart langfuse
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

If port 3000 is already in use:
- Edit `docker-compose.langfuse-v2.yml`
- Change `"3001:3000"` to `"3002:3000"` (already uses 3001 to avoid conflicts)
- Update `LANGFUSE_HOST=http://localhost:3002` in `.env`

---

## ✅ Success Checklist

- [ ] Langfuse containers running (`docker compose ps`)
- [ ] Web UI accessible (`http://localhost:3000`)
- [ ] Admin account created
- [ ] API keys obtained and saved
- [ ] Keys added to `.env` file
- [ ] Langfuse Python package installed
- [ ] Test analysis run successfully
- [ ] Traces visible in dashboard

---

## 🎉 You're All Set!

Once you see traces in Langfuse, you have full visibility into:
- ✅ All 13 agent executions
- ✅ Token usage and costs per agent
- ✅ Execution times and performance
- ✅ Full trace debugging

**Next:** Start using Langfuse to monitor your TradingAgents! 🚀

