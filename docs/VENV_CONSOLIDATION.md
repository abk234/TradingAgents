# Virtual Environment Consolidation

## Issue
The application had two virtual environments:
- `venv` (1.4GB)
- `.venv` (1.4GB)

This was wasting **2.8GB of disk space** and causing confusion in scripts.

## Solution
Consolidated to a single virtual environment: **`venv`**

### Changes Made

1. **Removed duplicate `.venv` directory** (saved 1.4GB)

2. **Updated all scripts to use `venv` consistently:**
   - `run.py` - Fixed venv paths
   - `run_with_defaults.py` - Fixed venv paths
   - `run_screener.sh` - Updated to prefer `venv`
   - `browse_chromadb.sh` - Updated to use `venv`
   - `trading_agents.sh` - Already supported both, now only needs `venv`

3. **Fixed ChromaDB config path** in `run.py` to use `venv` instead of `.venv`

## Current Status

✅ **Single virtual environment**: `venv`  
✅ **All scripts updated** to use `venv`  
✅ **1.4GB disk space saved**  
✅ **No functionality lost**

## Usage

All scripts now consistently use `venv`:

```bash
# Activate venv
source venv/bin/activate

# Or use the run scripts
python run.py
python run_with_defaults.py
./trading_agents.sh
```

---

*Fixed: 2025-01-16*

