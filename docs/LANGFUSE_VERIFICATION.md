# Verifying Langfuse Monitoring Capture

## 🔍 Current Status

Based on the Langfuse dashboard showing "Instrument Your Application" as pending, we need to verify that traces are actually being captured.

---

## ✅ What We've Configured

1. **Environment Variables** ✅
   - `LANGFUSE_ENABLED=true`
   - `LANGFUSE_PUBLIC_KEY` set
   - `LANGFUSE_SECRET_KEY` set
   - `LANGFUSE_HOST=http://localhost:3000`

2. **Langfuse Client** ✅
   - Initialized with credentials
   - OpenTelemetry tracing enabled
   - Custom callback handler created

3. **Integration** ✅
   - Integrated into `TradingAgentsGraph`
   - Callbacks passed to LangGraph execution

---

## 🧪 How to Verify Traces Are Being Captured

### Step 1: Run a Test Analysis

```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
python3 test_langfuse_monitoring.py
```

This will:
- Create a test trace manually
- Run a minimal analysis
- Show you where to check for traces

### Step 2: Check Langfuse Dashboard

1. **Open:** `http://localhost:3000`
2. **Go to:** Traces (sidebar)
3. **Look for:**
   - `"Test Trace - Langfuse Monitoring Verification"`
   - `"Stock Analysis: AAPL"`

### Step 3: Check Langfuse Logs

```bash
cd /Users/lxupkzwjs/Developer/langfuse
docker compose logs langfuse-web --tail 50 | grep -i "trace\|span\|otel"
```

Look for:
- Incoming trace requests
- OpenTelemetry spans
- API calls from your application

---

## 🔧 If Traces Don't Appear

### Issue 1: OpenTelemetry Not Properly Configured

Langfuse v3 uses OpenTelemetry. We may need to:

1. **Ensure OpenTelemetry is initialized:**
   ```python
   from langfuse import Langfuse
   
   # This should automatically set up OpenTelemetry
   langfuse = Langfuse(
       public_key="...",
       secret_key="...",
       host="http://localhost:3000",
       tracing_enabled=True
   )
   ```

2. **Check if spans are being created:**
   ```python
   from opentelemetry import trace
   
   tracer = trace.get_tracer(__name__)
   with tracer.start_as_current_span("test_span"):
       # Your code here
       pass
   ```

### Issue 2: Callback Handler Not Working

Our custom callback handler may not be capturing LangGraph executions properly. We can:

1. **Add manual trace creation:**
   ```python
   from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer
   
   tracer = get_langfuse_tracer()
   if tracer and tracer.enabled:
       trace = tracer.langfuse_client.trace(
           name="Manual Trace",
           input={"ticker": "AAPL"}
       )
       # Run analysis
       result = graph.propagate("AAPL", date.today())
       trace.update(output={"decision": result.get("final_decision")})
   ```

### Issue 3: Environment Variables Not Loaded

Make sure `.env` is being loaded:

```python
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing Langfuse
```

---

## 📊 Expected Behavior

When working correctly, you should see:

1. **In Langfuse Dashboard:**
   - Traces appear within seconds
   - Each trace shows execution details
   - Spans show individual agent runs

2. **In Logs:**
   - Langfuse web container receives POST requests
   - Traces are being ingested
   - No errors about missing credentials

3. **In Your Code:**
   - No errors when creating traces
   - Callback handler is called
   - Traces are flushed to Langfuse

---

## 🎯 Next Steps

1. **Run the verification script:**
   ```bash
   python3 test_langfuse_monitoring.py
   ```

2. **Check the dashboard** - Do traces appear?

3. **If yes:** ✅ Monitoring is working!
4. **If no:** Check logs and verify OpenTelemetry setup

---

## 🔍 Debugging Commands

```bash
# Check Langfuse is running
cd /Users/lxupkzwjs/Developer/langfuse
docker compose ps

# Check logs for incoming traces
docker compose logs langfuse-web --tail 100 | grep -i "trace\|api"

# Test connection
curl http://localhost:3000/api/public/health

# Check environment variables
cd /Users/lxupkzwjs/Developer/eval/TradingAgents
python3 test_langfuse_connection.py
```

---

**Status:** Integration code is ready, but we need to verify traces are actually being captured by Langfuse.

