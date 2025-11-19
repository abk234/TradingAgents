# Privacy Audit: External Logging & Data Transmission

**Date:** 2025-01-17  
**Purpose:** Audit application for any data transmission to Google or 3rd party services

---

## 🔍 Audit Results

### ✅ **No Active External Logging Services Found**

The application does **NOT** send logging data to Google or other 3rd party analytics services by default.

---

## 📊 Services Identified

### 1. **Langfuse** (Optional Observability Tool) ⚠️

**Status:** Optional, only enabled if explicitly configured  
**Type:** 3rd party observability/monitoring service  
**Data Sent:** LLM traces, agent execution data, performance metrics

**Location:**
- `tradingagents/monitoring/langfuse_integration.py`
- `tradingagents/api/main.py` (lines 32-35, 48-51)

**How It Works:**
- Only enabled if environment variables are set:
  - `LANGFUSE_ENABLED=true`
  - `LANGFUSE_PUBLIC_KEY` (required)
  - `LANGFUSE_SECRET_KEY` (required)
  - `LANGFUSE_HOST` (default: `http://localhost:3000`)

**Default Behavior:**
- ✅ **DISABLED by default** - Only activates if credentials are provided
- ✅ Can be self-hosted (default host is `localhost:3000`)
- ✅ Can be completely disabled by not setting environment variables

**What Data Is Sent (if enabled):**
- LLM request/response traces
- Agent execution metadata
- Performance metrics
- User feedback scores (if provided)

**Privacy Impact:**
- ✅ **Low/None** - Self-hosted Langfuse (localhost) = **100% Private** ✅
- ⚠️ **Medium** - Only if using cloud-hosted Langfuse (external transmission)
- ✅ **None** - Disabled by default

**Recommendation:**
- ✅ **Self-hosted Langfuse is PRIVATE** - If `LANGFUSE_HOST` is `localhost` or `127.0.0.1`, all data stays local
- ✅ Safe to enable Langfuse when self-hosted - No external data transmission
- ⚠️ Only avoid if using cloud-hosted Langfuse (external service)

---

### 2. **Google Fonts** (Frontend) 📝

**Status:** Active (frontend only)  
**Type:** Google CDN for fonts  
**Data Sent:** Font requests (standard browser behavior)

**Location:**
- `web-app/app/layout.tsx` (line 2)
- Uses Next.js `next/font/google` which optimizes font loading

**How It Works:**
- Next.js fetches Inter font from Google Fonts CDN
- Standard browser request (no user data sent)
- Font files are cached by browser

**Privacy Impact:**
- ✅ **Minimal** - Only font file requests (standard HTTP requests)
- ✅ **No user data** - Google only sees IP address (standard web behavior)
- ✅ **Can be self-hosted** - Fonts can be downloaded and served locally

**Recommendation:**
- Low privacy concern (standard web practice)
- Can be replaced with self-hosted fonts if desired

---

### 3. **Google Gemini API** (LLM Provider) 🤖

**Status:** Optional (one of multiple LLM options)  
**Type:** AI/LLM service  
**Data Sent:** User queries and conversation context (if Google is selected as LLM provider)

**Location:**
- `tradingagents/graph/trading_graph.py` (lines 200-202)
- `tradingagents/default_config.py` (line 12)

**How It Works:**
- Only used if `llm_provider = "google"` in config
- Sends user messages and conversation context to Google Gemini API
- Returns AI-generated responses

**Privacy Impact:**
- ⚠️ **High** - If enabled, sends all user queries and conversation data to Google
- ✅ **Optional** - Can use other providers (OpenAI, Anthropic, Ollama/local)
- ✅ **Not default** - Default is Ollama (local)

**Recommendation:**
- If privacy is critical, use Ollama (local) or self-hosted models
- Google Gemini is only one option among many

---

### 4. **Google News** (Data Source) 📰

**Status:** Active (data retrieval only)  
**Type:** News data source  
**Data Sent:** News search queries (no user data)

**Location:**
- `tradingagents/dataflows/google.py`
- Used for fetching stock news

**How It Works:**
- Fetches news articles from Google News
- Only sends search queries (e.g., "AAPL stock news")
- No user identification or tracking

**Privacy Impact:**
- ✅ **Low** - Only search queries, no user data
- ✅ **Standard** - Similar to using Google Search

---

## 🚫 Services NOT Found

The following common tracking/analytics services are **NOT** present:

- ❌ Google Analytics (`gtag`, `ga()`)
- ❌ Google Tag Manager
- ❌ Facebook Pixel (`fbq`)
- ❌ Mixpanel
- ❌ Amplitude
- ❌ Segment
- ❌ Hotjar
- ❌ FullStory
- ❌ Sentry (error tracking)
- ❌ Datadog
- ❌ New Relic
- ❌ Loggly
- ❌ AWS CloudWatch

---

## 📋 Summary

### Data Transmission Status

| Service | Type | Status | Data Sent | Privacy Impact |
|---------|------|--------|-----------|----------------|
| **Langfuse** | Observability | ⚠️ Optional | LLM traces, agent data | Medium (if enabled) |
| **Google Fonts** | Fonts | ✅ Active | Font requests only | Minimal |
| **Google Gemini** | LLM | ⚠️ Optional | User queries, conversations | High (if enabled) |
| **Google News** | Data Source | ✅ Active | News search queries | Low |

### Default Privacy Status

✅ **PRIVACY-FRIENDLY BY DEFAULT**

- No analytics tracking by default
- No user behavior tracking
- No telemetry to 3rd parties
- Langfuse is opt-in only
- LLM provider is local (Ollama) by default

---

## 🔒 Privacy Recommendations

### For Maximum Privacy:

1. **Langfuse (Self-Hosted is Private)** ✅:
   ```bash
   # Self-hosted Langfuse (localhost) = PRIVATE ✅
   # Safe to enable - all data stays local
   export LANGFUSE_ENABLED=true
   export LANGFUSE_HOST=http://localhost:3000  # ✅ Self-hosted = Private
   export LANGFUSE_PUBLIC_KEY=your_key
   export LANGFUSE_SECRET_KEY=your_secret
   
   # Only avoid if using cloud-hosted Langfuse:
   # export LANGFUSE_HOST=https://cloud.langfuse.com  # ⚠️ External
   ```

2. **Use Local LLM** (default):
   ```python
   # Default config already uses Ollama (local)
   config["llm_provider"] = "ollama"  # ✅ Local, no external data
   ```

3. **Self-Host Fonts** (optional):
   - Download Inter font files
   - Serve from your own domain
   - Modify `web-app/app/layout.tsx`

4. **Monitor Environment Variables**:
   ```bash
   # Check for any tracking-related env vars
   env | grep -i "analytics\|tracking\|telemetry\|langfuse"
   ```

---

## 🔍 How to Verify

### Check Langfuse Status:

```python
import os
print("Langfuse Enabled:", os.getenv("LANGFUSE_ENABLED", "false"))
print("Langfuse Public Key:", "SET" if os.getenv("LANGFUSE_PUBLIC_KEY") else "NOT SET")
```

### Check LLM Provider:

```python
from tradingagents.default_config import DEFAULT_CONFIG
print("LLM Provider:", DEFAULT_CONFIG["llm_provider"])
# Should be "ollama" by default (local)
```

### Check Frontend:

```bash
# Search for analytics scripts
cd web-app
grep -r "gtag\|analytics\|tracking" . --exclude-dir=node_modules
# Should return no results
```

---

## ✅ Conclusion

**The application is privacy-friendly by default:**

- ✅ No external logging by default
- ✅ No analytics tracking
- ✅ No telemetry to 3rd parties
- ✅ Langfuse is opt-in only (disabled by default, but **self-hosted = private** ✅)
- ✅ LLM is local by default (Ollama)
- ✅ Only standard web requests (fonts, news)

**Privacy Risk Level:** 🟢 **LOW** (with default configuration)

**To maintain privacy:**
- ✅ **Self-hosted Langfuse is PRIVATE** - Safe to enable if `LANGFUSE_HOST=localhost`
- ⚠️ Only avoid cloud-hosted Langfuse (external service)
- Use Ollama (local) for LLM
- Self-host fonts if desired (optional)

---

## 📝 Notes

- ✅ **Langfuse Self-Hosted = PRIVATE**: If `LANGFUSE_HOST` is `localhost` or `127.0.0.1`, **all data stays local** - safe to enable for observability
- ⚠️ **Langfuse Cloud**: Only avoid if using cloud-hosted Langfuse (external service)
- **Google Fonts** is a standard web practice and can be replaced with self-hosted fonts
- **Google Gemini** is only one option - the default is Ollama (completely local)
- All data storage is local (PostgreSQL database)

**Last Updated:** 2025-01-17

