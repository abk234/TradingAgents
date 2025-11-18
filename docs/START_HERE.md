# 🚀 Start Here - High Priority Fixes

**Time to Complete Week 1:** 30-40 hours (4-5 days)  
**Focus:** Fix security issues that prevent portability and expose secrets

---

## 📋 What You'll Fix This Week

1. ✅ **Hardcoded user path** - Makes app work for all users
2. ✅ **Exposed API keys** - Removes keys from documentation  
3. ✅ **Static API keys** - Adds rotation support
4. ✅ **Insecure credentials** - Uses keyring for DB passwords

**Result:** Your app will be secure, portable, and production-ready! 🎉

---

## 🎯 Day 1: Quick Wins (2-3 hours)

### Task 1: Fix Hardcoded Path (1 hour)

**Problem:** App won't work for other users  
**File:** `tradingagents/default_config.py` line 6

**Before:**
```python
"data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",  # ❌ Hardcoded
```

**After:**
```python
"data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", 
                     os.path.join(os.path.dirname(__file__), "..", "data")),  # ✅ Flexible
```

**Test it:**
```bash
# Should work now without that user's directory existing
python -c "from tradingagents.default_config import DEFAULT_CONFIG; print(DEFAULT_CONFIG['data_dir'])"
```

---

### Task 2: Create .env.example (30 minutes)

**Create new file:** `.env.example`

```bash
# TradingAgents Environment Configuration
# Copy this file to .env and fill in your actual values

# === LLM Provider API Keys ===
OPENAI_API_KEY=sk-proj-your_key_here
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# === Data Provider API Keys ===
ALPHA_VANTAGE_API_KEY=your_key_here

# === Directory Configuration ===
TRADINGAGENTS_RESULTS_DIR=./results
TRADINGAGENTS_DATA_DIR=./data

# === Database Configuration ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=investment_intelligence
DB_USER=your_username
DB_PASSWORD=your_password
```

**Test it:**
```bash
# Verify file is gitignored
git status | grep .env.example  # Should show as new file
git status | grep .env          # Should NOT show (already in .gitignore)
```

---

### Task 3: Clean Documentation (1 hour)

**Search for exposed keys:**
```bash
cd /Users/lxupkzwjs/Developer/eval/TradingAgents

# Find exposed keys
grep -r "LOCR3UMJ91AJ1VBF" docs/
grep -r "AIzaSy" docs/
```

**Replace with placeholders in these files:**
- `docs/ENV_SETUP_GUIDE.md`
- Any other files found

**Before:**
```bash
ALPHA_VANTAGE_API_KEY=LOCR3UMJ91AJ1VBF  # ❌ Real key exposed
```

**After:**
```bash
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here  # ✅ Placeholder
```

**Commit changes:**
```bash
git add .env.example docs/
git commit -m "fix: secure API keys and add .env.example template"
```

---

## 🔐 Days 2-3: API Key Rotation (16-20 hours)

### Step 1: Install Dependencies (5 minutes)

```bash
# Install keyring for secure storage
pip install keyring

# Update requirements.txt
echo "keyring>=24.0.0" >> requirements.txt
```

### Step 2: Create Secrets Manager (4-6 hours)

**Create file:** `tradingagents/utils/secrets_manager.py`

Copy the full implementation from `HIGH_PRIORITY_ACTION_PLAN.md` (it's ~200 lines).

Key features:
- Stores keys in system keyring (secure)
- Tracks expiration dates
- Warns when keys need rotation
- Falls back to environment variables

### Step 3: Create Key Management CLI (2-3 hours)

**Create file:** `scripts/manage_keys.py`

Copy the implementation from the action plan.

**Make it executable:**
```bash
chmod +x scripts/manage_keys.py
```

### Step 4: Update Data Vendors (6-8 hours)

**Update:** `tradingagents/dataflows/alpha_vantage_common.py`

**Before:**
```python
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
```

**After:**
```python
from tradingagents.utils.secrets_manager import get_api_key

ALPHA_VANTAGE_API_KEY = get_api_key('alpha_vantage')
```

**Repeat for other files:**
- Any file using `os.environ.get` for API keys
- Update to use `get_api_key()` function

### Step 5: Setup Your Keys (30 minutes)

```bash
# Store keys in secure keyring
python scripts/manage_keys.py set alpha_vantage --rotation-days 90
# (Paste your key when prompted)

python scripts/manage_keys.py set openai --rotation-days 90
# (Paste your key if using OpenAI)

# View all keys
python scripts/manage_keys.py list
```

**Expected output:**
```
╔═══════════════════════════════════════════════╗
║            Managed API Keys                    ║
╠═════════════════╦══════════╦═══════╦══════════╣
║ Service         ║ Expires  ║ Days  ║ Status   ║
╠═════════════════╬══════════╬═══════╬══════════╣
║ alpha_vantage   ║ 2025-02-15 88    ║ ✅ Valid ║
║ openai          ║ 2025-02-15 88    ║ ✅ Valid ║
╚═════════════════╩══════════╩═══════╩══════════╝
```

### Step 6: Test It (1 hour)

```bash
# Test that analysis still works
python -m tradingagents.analyze AAPL

# Should see in logs:
# "✓ Retrieved alpha_vantage API key from keyring"
```

---

## 🗄️ Day 4: Database Security (8-10 hours)

### Step 1: Update Connection Module (4-6 hours)

**Update:** `tradingagents/database/connection.py`

Add the `get_db_credentials()` function from the action plan (it tries keyring first, then env vars).

**Key changes:**
```python
def get_db_credentials() -> Dict[str, str]:
    """Get DB credentials from keyring or env vars"""
    # Try keyring
    import keyring
    user = keyring.get_password('tradingagents', 'db_user')
    password = keyring.get_password('tradingagents', 'db_password')
    
    # Fall back to env
    if not user:
        user = os.getenv('DB_USER', os.getenv('USER'))
    if not password:
        password = os.getenv('DB_PASSWORD', '')
    
    return {
        'dbname': os.getenv('DB_NAME', 'investment_intelligence'),
        'user': user,
        'password': password,
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '5432'))
    }
```

### Step 2: Create Setup Script (2-3 hours)

**Create:** `scripts/setup_db_credentials.py`

```python
#!/usr/bin/env python3
import click
import keyring
from rich.console import Console

console = Console()

@click.command()
@click.option('--user', prompt='Database user')
@click.option('--password', prompt=True, hide_input=True)
def setup(user, password):
    """Store database credentials securely"""
    keyring.set_password('tradingagents', 'db_user', user)
    keyring.set_password('tradingagents', 'db_password', password)
    console.print("✅ Credentials stored in system keyring")

if __name__ == '__main__':
    setup()
```

**Make executable:**
```bash
chmod +x scripts/setup_db_credentials.py
```

### Step 3: Setup Your DB Credentials (15 minutes)

```bash
# Store credentials
python scripts/setup_db_credentials.py
# Enter your PostgreSQL username
# Enter your PostgreSQL password (hidden)

# Output: ✅ Credentials stored in system keyring
```

### Step 4: Test Database Connection (30 minutes)

```bash
# Test connection
python -c "
from tradingagents.database import get_db_connection
db = get_db_connection()
print('✅ Database connected successfully')
print(f'Tables: {db.get_table_count(\"tickers\")} tickers')
"
```

**Expected output:**
```
✓ Database connection pool created for 'investment_intelligence'
✅ Database connected successfully
Tables: 16 tickers
```

---

## ✅ End of Week 1 Checklist

### Test Everything

```bash
# 1. Hardcoded path is fixed
python -c "from tradingagents.default_config import DEFAULT_CONFIG; print(DEFAULT_CONFIG['data_dir'])"
# Should NOT show /Users/yluo/...

# 2. .env.example exists
ls -la .env.example
# Should exist

# 3. No exposed keys in docs
grep -r "LOCR3UMJ91AJ1VBF" docs/
# Should return nothing

# 4. Keys in keyring
python scripts/manage_keys.py list
# Should show your keys with status

# 5. DB credentials secure
python -c "from tradingagents.database import get_db_connection; db = get_db_connection(); print('OK')"
# Should print OK

# 6. Analysis still works
python -m tradingagents.screener run --top 3
# Should complete successfully
```

### Commit Your Changes

```bash
# Add all changes
git add .

# Commit
git commit -m "feat: add secure credential management and API key rotation

- Remove hardcoded user paths
- Add .env.example template
- Implement secrets manager with keyring support
- Add API key rotation tracking
- Secure database credentials
- Create key management CLI tools

Closes #security-week1"

# Push (optional)
# git push origin main
```

---

## 📊 Measure Your Success

### Security Improvements
- ✅ No hardcoded paths in code
- ✅ No exposed API keys in documentation
- ✅ Keys stored in secure keyring
- ✅ Key rotation tracking enabled
- ✅ Database credentials secured

### Time Saved
- **Before:** Had to manually update code for each user
- **After:** Works out of the box for anyone

### Portability
- **Before:** Only worked on one developer's machine
- **After:** Works on any machine with proper setup

---

## 🚀 What's Next?

You've completed **Week 1** - Security Fixes! 

**Next up:** Week 2 - Performance Optimizations
- Redis caching (60-80% faster repeated queries)
- Database query optimization (50-70% faster)
- Connection pool monitoring

**See:** `HIGH_PRIORITY_ACTION_PLAN.md` for Week 2 details

---

## 💡 Pro Tips

### Backup Your Keys
```bash
# Export keys to backup file (encrypted)
python scripts/manage_keys.py export --output keys_backup.json.gpg
```

### Rotate Keys Regularly
```bash
# Check which keys need rotation
python scripts/manage_keys.py list

# Rotate expired keys
python scripts/manage_keys.py rotate alpha_vantage
```

### Test on Fresh Machine
```bash
# Clone to test machine
git clone <your-repo>
cd TradingAgents

# Setup keys
python scripts/manage_keys.py set alpha_vantage
python scripts/setup_db_credentials.py

# Should work without any code changes!
```

---

## ❓ Troubleshooting

### "Module 'keyring' not found"
```bash
pip install keyring
```

### "Permission denied: scripts/manage_keys.py"
```bash
chmod +x scripts/manage_keys.py
chmod +x scripts/setup_db_credentials.py
```

### "Could not access keyring"
```bash
# macOS: Keyring should work out of the box
# Linux: Install a backend
sudo apt-get install python3-keyring gnome-keyring

# Windows: Should work with Windows Credential Manager
```

### Keys not loading
```bash
# Check if stored in keyring
python -c "import keyring; print(keyring.get_password('tradingagents', 'db_user'))"

# If None, keys aren't stored - run setup again
python scripts/setup_db_credentials.py
```

---

## 🎉 Congratulations!

You've completed the most critical security fixes. Your application is now:
- ✅ Portable (works for any user)
- ✅ Secure (keys in keyring, not code)
- ✅ Maintainable (easy key rotation)
- ✅ Production-ready (no secrets in git)

**Time to celebrate!** 🎊

Then move on to **Week 2: Performance Optimizations** 🚀

---

**Questions?** Check the detailed plan in `HIGH_PRIORITY_ACTION_PLAN.md`

