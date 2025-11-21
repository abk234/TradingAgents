# 🔧 Fix: OpenAI API Connection Error

## The Problem

You're seeing this error:
```
openai.APIConnectionError: Connection error.
```

**Root Cause:** Your OpenAI API key is still set to the placeholder value `your-openai-api-key-here` in the `.env` file.

## Quick Fix (2 minutes)

### Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-`)
5. **Important:** Save it somewhere safe - you can only see it once!

### Step 2: Update .env File

```bash
# Open .env file
nano .env

# Find this line:
OPENAI_API_KEY=your-openai-api-key-here

# Replace with your actual key:
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

Press `Ctrl+O` to save, then `Ctrl+X` to exit.

### Step 3: Verify Configuration

```bash
# Run the API key checker
./scripts/check_api_keys.sh
```

You should see:
```
✅ OPENAI_API_KEY is valid and working
```

### Step 4: Restart the Application

```bash
# Stop current instance (Ctrl+C if running)
# Then start again
./start.sh
```

## Alternative: Quick Command Line Fix

```bash
# Replace YOUR_ACTUAL_KEY_HERE with your OpenAI API key
sed -i '' 's/OPENAI_API_KEY=your-openai-api-key-here/OPENAI_API_KEY=sk-YOUR_ACTUAL_KEY/' .env

# Verify it worked
./scripts/check_api_keys.sh
```

## Optional: Add Other API Keys

While you're at it, you might want to add:

### Alpha Vantage (Free - for stock data)
1. Get free key: https://www.alphavantage.co/support/#api-key
2. Update in `.env`:
   ```bash
   ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
   ```

### Anthropic Claude (Optional)
1. Get key: https://console.anthropic.com/
2. Update in `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
   ```

## Verify Everything Works

After updating your API keys:

```bash
# 1. Check configuration
./scripts/check_api_keys.sh

# 2. Start application
./start.sh

# 3. Test in browser
# Open: http://localhost:3005
# Try asking: "Analyze AAPL stock"
```

## Troubleshooting

### "API key is invalid (401 Unauthorized)"

Your API key is wrong or expired:
1. Double-check you copied the entire key
2. Make sure there are no extra spaces
3. Generate a new key at https://platform.openai.com/api-keys

### "Cannot connect to OpenAI API (network issue)"

Network/firewall problem:
1. Check your internet connection
2. Try: `curl https://api.openai.com/v1/models`
3. Check if a proxy/firewall is blocking OpenAI

### Still Not Working?

1. **View the full .env file:**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

2. **Test API key manually:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY_HERE"
   ```

3. **Check for typos:**
   - Key must start with `sk-`
   - No quotes around the key
   - No spaces before/after the key

## Complete .env Example

Here's what your `.env` should look like:

```bash
# Required
OPENAI_API_KEY=sk-proj-abc123xyz789...
ALPHA_VANTAGE_API_KEY=DEMO

# Optional
ANTHROPIC_API_KEY=sk-ant-abc123...
GOOGLE_API_KEY=AIza...

# Other settings
EMAIL_ENABLED=false
SLACK_ENABLED=false
```

## Next Steps

Once your API key is configured:

1. ✅ Run `./scripts/check_api_keys.sh` to verify
2. ✅ Start application with `./start.sh`
3. ✅ Access UI at http://localhost:3005
4. ✅ Try analyzing a stock to test everything works!

---

**Need more help?** Check the main documentation:
- `README.md` - Full project documentation
- `STARTUP_GUIDE.md` - Complete startup guide
- `QUICK_START.md` - Quick reference
