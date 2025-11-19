# Langfuse Integration - Fixed! ✓

## Problem

When running Phase 2 agent analysis (parallel agents), Langfuse integration was throwing errors:
```
ERROR:tradingagents.monitoring.langfuse_integration:Failed to create Langfuse trace: 'Langfuse' object has no attribute 'trace'
WARNING:langchain_core.callbacks.manager:Error in LangfuseLangChainHandler.on_chain_start callback: AttributeError("'Langfuse' object has no attribute 'trace'")
```

## Root Cause

The `tradingagents/monitoring/langfuse_integration.py` file had **three major issues**:

1. **Wrong Import**: Tried to import `LangfuseCallbackHandler` but Langfuse v3 exports it as `CallbackHandler`
2. **Wrong Initialization**: Tried to pass `secret_key`, `host`, `session_id`, etc. as parameters, but Langfuse v3 CallbackHandler only accepts credentials via environment variables
3. **Broken Custom Handler**: Created a custom LangChain callback handler that tried to call `langfuse_client.trace()` which doesn't exist in Langfuse v3 SDK

## Solution

### 1. Fixed Import (line 32)
```python
# Before (WRONG):
from langfuse.langchain import LangfuseCallbackHandler

# After (CORRECT):
from langfuse.langchain import CallbackHandler
```

### 2. Fixed Initialization (lines 117-124)
```python
# Langfuse v3 CallbackHandler reads credentials from environment variables
_os.environ["LANGFUSE_PUBLIC_KEY"] = self.public_key
_os.environ["LANGFUSE_SECRET_KEY"] = self.secret_key
_os.environ["LANGFUSE_HOST"] = self.host

# Initialize the callback handler (reads from env)
self.handler = CallbackHandler()
```

### 3. Fixed Trace Creation (line 198)
```python
# Removed broken custom handler that called langfuse_client.trace()
# Langfuse v3 creates traces automatically via the callback handler
logger.debug(f"Auto-tracing enabled for {ticker} on {analysis_date}")
```

### 4. Fixed Score Method (line 220)
```python
# Before (WRONG):
self.langfuse_client.score(trace_id=trace_id, value=score, comment=comment)

# After (CORRECT):
self.langfuse_client.create_score(
    trace_id=trace_id,
    name="quality",
    value=score,
    comment=comment
)
```

### 5. Installed Missing Dependency
```bash
pip install langchain
```

The `langfuse` package requires `langchain` to be installed for the LangChain integration to work.

## Verification

After the fix:
```bash
$ python -m tradingagents.analyze AAPL

INFO:tradingagents.monitoring.langfuse_integration:✓ Langfuse tracing enabled (host: http://localhost:3000, session: default)
INFO:tradingagents.graph.trading_graph:✓ Langfuse tracing enabled
INFO:tradingagents.graph.trading_graph:✓ RAG system initialized
```

**No more errors!** ✅

## Monitoring the Agents

Now when you run any phase scripts, all LLM calls from all 13+ agents are automatically traced to Langfuse:

```bash
# Run Phase 2 with Langfuse monitoring
./scripts/phase2_agents.sh AAPL

# Run full workflow with Langfuse monitoring
./scripts/phase4_full_workflow.sh

# Run profit optimization with Langfuse monitoring
./make_profit.sh --portfolio-value 100000 --top 5
```

Visit **http://localhost:3000** to see:
- All agent traces (Market Analyst, News Analyst, etc.)
- LLM token usage per agent
- Execution time per agent
- Full conversation history
- Cost per analysis

## Configuration

Langfuse is **enabled by default** in your `.env`:
```bash
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-f0337fc6-3a86-4c13-8c3a-b5d0dbc04c99
LANGFUSE_SECRET_KEY=sk-lf-2e6d987a-9e09-40b9-b102-42e7cf5fd110
LANGFUSE_HOST=http://localhost:3000
```

To disable (for faster execution without monitoring):
```bash
export LANGFUSE_ENABLED=false
```

## Files Modified

- `tradingagents/monitoring/langfuse_integration.py` - Fixed Langfuse v3 integration
- `scripts/phase1_screening.sh` - Fixed deprecated `get_active_tickers()` → `get_all_tickers(active_only=True)`
- `scripts/phase3_reports.sh` - Fixed deprecated method call
- `scripts/show_database_state.sh` - Fixed deprecated method call

## Testing

All phase scripts now work correctly with Langfuse enabled:

✅ Phase 1 (Screening): `./scripts/phase1_screening.sh`
✅ Phase 2 (Agent Analysis): `./scripts/phase2_agents.sh AAPL`
✅ Phase 3 (Reports): `./scripts/phase3_reports.sh AAPL`
✅ Phase 4 (Full Workflow): `./scripts/phase4_full_workflow.sh`
✅ Profit Optimization: `./make_profit.sh --portfolio-value 100000 --top 5`

All logs flow cleanly to Langfuse at http://localhost:3000 🎉
