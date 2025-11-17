# Environment Variables Setup Guide

## 📁 Location

**File:** `/Users/lxupkzwjs/Developer/eval/TradingAgents/.env`

The `.env` file is already configured in your project root directory.

---

## 🔑 API Keys Configuration

### **Current Configuration** (from your `.env` file)

```bash
# Alpha Vantage API Key (✅ Already configured)
ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF

# Google Gemini API Key (✅ Already configured)
GOOGLE_API_KEY=AIzaSyD01ucslecwkn9kOSt4ElqxogiNiHpRgw8

# OpenAI API Key (⚠️ Placeholder - not needed if using Ollama)
OPENAI_API_KEY=your-openai-api-key-here
```

---

## ✅ **What You Need for Different Modes**

### **Fast Mode (Recommended)** ⚡

```bash
# ✅ NO API KEYS NEEDED!
# Fast mode skips news and uses only yfinance
```

**Command:**
```bash
python -m tradingagents.screener run --with-analysis --fast --no-rag --analysis-limit 3
```

**What it uses:**
- ✅ yfinance (FREE - no API key needed)
- ✅ Ollama (FREE - local LLM)
- ✅ No news vendors (skipped)
- ✅ No fundamentals from paid APIs

**Speed:** ~2-3 minutes for 3 stocks

---

### **Default Mode (With News)** 📰

```bash
# ✅ ALREADY CONFIGURED!
ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF  # Free tier: 25 requests/day
```

**Command:**
```bash
python -m tradingagents.screener run --with-analysis --analysis-limit 3
```

**What it uses:**
- ✅ yfinance (price data, fundamentals)
- ✅ Alpha Vantage (news, if yfinance unavailable)
- ✅ Ollama (local LLM)

**Speed:** ~5-7 minutes for 3 stocks (tries news vendors)

**Note:** Alpha Vantage free tier = 25 API calls/day

---

### **Using Google Gemini** (Optional)

If you want to use Google Gemini instead of Ollama:

**1. Modify config:**
```python
# tradingagents/default_config.py
"llm_provider": "google",  # Change from "ollama"
"deep_think_llm": "gemini-2.0-flash",
"quick_think_llm": "gemini-2.0-flash-lite",
```

**2. Your .env already has:**
```bash
GOOGLE_API_KEY=AIzaSyD01ucslecwkn9kOSt4ElqxogiNiHpRgw8  # ✅ Set
```

---

### **Using OpenAI** (Not Recommended - Costs Money)

Only if you want to use GPT models:

**1. Get API key:** https://platform.openai.com/api-keys

**2. Update .env:**
```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**3. Modify config:**
```python
# tradingagents/default_config.py
"llm_provider": "openai",
"deep_think_llm": "gpt-4o-mini",
"quick_think_llm": "gpt-4o-mini",
```

**Cost:** ~$0.01-0.05 per stock analysis

---

## 🛠️ How to Modify `.env`

### **Option 1: Direct Edit**
```bash
nano /Users/lxupkzwjs/Developer/eval/TradingAgents/.env
```

### **Option 2: VS Code**
```bash
code /Users/lxupkzwjs/Developer/eval/TradingAgents/.env
```

---

## 📋 API Key Sources

| Service | Free Tier | Get Key From | Usage |
|---------|-----------|--------------|-------|
| **Alpha Vantage** | ✅ 25 calls/day | https://www.alphavantage.co/support/#api-key | News, fundamentals |
| **Google Gemini** | ✅ Generous | https://aistudio.google.com/app/apikey | LLM (alternative to Ollama) |
| **OpenAI** | ❌ Paid only | https://platform.openai.com/api-keys | LLM (GPT models) |
| **yfinance** | ✅ Unlimited | No key needed! | Price, fundamentals, news |

---

## ⚠️ Important Notes

### **1. `.env` is Automatically Loaded**

The system uses `python-dotenv` to load variables from `.env` automatically.

**Files that load `.env`:**
- `main_ollama.py` (line 22)
- `main.py` (line 7)
- `run.py` (line 155)
- All CLI scripts

**You don't need to do anything special - just edit `.env` and run!**

---

### **2. `.env` Should Be in `.gitignore`**

**Check:**
```bash
cat /Users/lxupkzwjs/Developer/eval/TradingAgents/.gitignore | grep .env
```

If `.env` is NOT in `.gitignore`, add it:
```bash
echo ".env" >> .gitignore
```

**Why?** Prevents accidentally committing your API keys to GitHub!

---

### **3. Environment Variables Override `.env`**

If you set variables in your shell, they take precedence:

```bash
# This overrides .env
export ALPHA_VANTAGE_API_KEY=different-key
python -m tradingagents.screener run
```

To check what's loaded:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Alpha Vantage:', os.getenv('ALPHA_VANTAGE_API_KEY'))"
```

---

## 🎯 Recommended Setup

### **For Daily Use (FREE):**

**`.env` file:**
```bash
# No keys needed! (or keep Alpha Vantage for occasional news)
ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF
```

**Command:**
```bash
# Fast mode - no news, no RAG, super fast
python -m tradingagents.screener run --with-analysis --fast --no-rag --analysis-limit 3
```

**Cost:** $0
**Speed:** 2-3 minutes for 3 stocks

---

### **For Weekend Deep Dive (Use Alpha Vantage):**

**`.env` file:**
```bash
ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF  # Already set!
```

**Command:**
```bash
# With news, with RAG, thorough analysis
python -m tradingagents.screener run --with-analysis --analysis-limit 5
```

**Cost:** $0 (free tier)
**Speed:** 8-12 minutes for 5 stocks
**Limit:** 25 API calls/day (don't exceed!)

---

## 🔍 Troubleshooting

### **Issue: "ALPHA_VANTAGE_API_KEY environment variable is not set"**

**Solution 1:** Check `.env` file exists and has the key
```bash
cat /Users/lxupkzwjs/Developer/eval/TradingAgents/.env | grep ALPHA_VANTAGE_API_KEY
```

**Solution 2:** Set it directly in terminal (temporary)
```bash
export ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF
```

**Solution 3:** Use fast mode (doesn't need it)
```bash
python -m tradingagents.screener run --with-analysis --fast
```

---

### **Issue: "Rate limit exceeded"**

Alpha Vantage free tier = 25 calls/day

**Solution:** Use fast mode (skips news)
```bash
python -m tradingagents.screener run --with-analysis --fast --analysis-limit 3
```

---

### **Issue: "Skipping 'get_news' - analysis will continue"**

This is NOT an error! It means:
- Fast mode is enabled, OR
- News vendor failed (no API key)
- Analysis continues without news (which is fine!)

**To enable news:** Use default mode with Alpha Vantage key configured

---

## 📊 API Usage Tracking

### **Check Alpha Vantage Usage:**

Visit: https://www.alphavantage.co/support/#support

Login with your key to see:
- Requests used today
- Requests remaining
- Rate limit resets

---

## 🔐 Security Best Practices

### **✅ DO:**
- Keep `.env` file in `.gitignore`
- Use environment variables for sensitive data
- Rotate API keys periodically
- Use free tiers when possible

### **❌ DON'T:**
- Commit `.env` to Git
- Share API keys publicly
- Hardcode keys in Python files
- Exceed free tier limits

---

## 🚀 Quick Start Commands

### **Morning Routine (No keys needed):**
```bash
python -m tradingagents.screener run --with-analysis --fast --no-rag --analysis-limit 3
```

### **Weekend Analysis (Uses Alpha Vantage):**
```bash
python -m tradingagents.screener run --with-analysis --fast --analysis-limit 5
```

### **Single Stock Deep Dive:**
```bash
python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000
```

---

## 📞 Getting Free API Keys

### **Alpha Vantage (✅ Recommended)**
1. Visit: https://www.alphavantage.co/support/#api-key
2. Enter email
3. Get instant free key (25 calls/day)
4. Add to `.env`:
   ```bash
   ALPHA_VANTAGE_API_KEY=your-key-here
   ```

### **Google Gemini (✅ Optional)**
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Add to `.env`:
   ```bash
   GOOGLE_API_KEY=your-key-here
   ```

---

## ✅ Your Current Status

**✅ Alpha Vantage:** Configured (LOCR3UMJ91AJ1VBF)
**✅ Google Gemini:** Configured
**✅ Ollama:** Running locally (no key needed)
**✅ yfinance:** Works automatically (no key needed)

**You're all set!** 🎉

---

**Questions?**
- Check `PERFORMANCE_OPTIMIZATION_GUIDE.md` for speed tips
- Check `COMPETITIVE_ANALYSIS.md` for system comparison
- Check `README.md` for general usage

---

**Last Updated:** 2025-11-16
