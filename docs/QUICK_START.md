# Quick Start Guide

## Prerequisites Summary

### 1. System Requirements
- **Python**: 3.10 or higher (3.13 recommended)
- **OS**: macOS, Linux, or Windows
- **Memory**: 4GB+ RAM
- **Internet**: Required for API calls

### 2. Required API Keys

#### LLM API Key (Required - Choose One)

**Option 1: OpenAI API Key (Default)**
- **Get it here**: https://platform.openai.com/api-keys
- **Cost**: Pay-per-use (use `gpt-4o-mini` for testing to save costs)
- **Purpose**: Powers all LLM agents

**Option 2: Google Gemini API Key (Alternative - Often More Cost-Effective)**
- **Get it here**: https://aistudio.google.com/app/apikey
- **Cost**: Free tier available with generous limits
- **Purpose**: Use Gemini models instead of OpenAI
- **Note**: Set `llm_provider` to `"google"` in config

#### Alpha Vantage API Key (Required for default config)
- **Get it here**: https://www.alphavantage.co/support/#api-key
- **Cost**: Free tier available (60 requests/minute)
- **Purpose**: Provides fundamental and news data

## Installation (3 Steps)

### Step 1: Install Dependencies
```bash
# Create virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install packages
pip install -r requirements.txt
```

### Step 2: Set API Keys
```bash
# Option A: Environment variables (OpenAI)
export OPENAI_API_KEY="your-key-here"
export ALPHA_VANTAGE_API_KEY="your-key-here"

# Option A: Environment variables (Gemini)
export GOOGLE_API_KEY="your-key-here"
export ALPHA_VANTAGE_API_KEY="your-key-here"

# Option B: Create .env file (recommended)
cp .env.example .env
# Then edit .env with your actual keys
```

### Step 3: Verify Setup
```bash
python verify_setup.py
```

## Run Your First Analysis

### Interactive CLI (Recommended)
```bash
python -m cli.main analyze
```

### Programmatic Usage
```bash
python main.py
```

## Need Help?

- **Full Setup Guide**: See `SETUP_GUIDE.md`
- **Project README**: See `README.md`
- **Verify Installation**: Run `python verify_setup.py`

