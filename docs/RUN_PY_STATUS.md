# run.py Status Check Guide

## What run.py Does

The `run.py` script performs several setup steps that can take time:

1. **Check Python Version** - Quick (< 1 second)
2. **Create Virtual Environment** - Quick if exists, ~30 seconds if creating new
3. **Install Dependencies** - **This is the slow step** (5-15 minutes)
   - Installs all packages from `requirements.txt`
   - Can take a long time depending on:
     - Number of packages
     - Internet speed
     - System performance
4. **Install Additional Dependencies** - 1-2 minutes
5. **Check Environment Variables** - Quick
6. **Fix ChromaDB Config** - Quick
7. **Run Application** - Interactive (waits for user input)

## Why It Might Seem Stuck

### During Dependency Installation (Most Common)
- Installing packages can take **5-15 minutes**
- No visible output (output is captured)
- Process appears "stuck" but is actually working

### During Application Run
- Waiting for user input (interactive prompts)
- Running analysis (can take 2-5 minutes per ticker)

## How to Check Status

### Check if Process is Running
```bash
ps aux | grep run.py
```

### Check Process Age
```bash
ps -p <PID> -o etime
```

### Check What It's Doing
```bash
lsof -p <PID> | grep -E "pip|requirements|REG"
```

## Expected Behavior

### Normal Flow
1. Shows setup steps with colored output
2. Takes 5-15 minutes for dependency installation
3. Then launches interactive CLI
4. Waits for user input

### If Stuck
- **> 20 minutes**: Likely stuck, should check
- **During pip install**: Normal, wait longer
- **During analysis**: Normal, can take 2-5 minutes

## Troubleshooting

### If It's Taking Too Long (> 20 minutes)

1. **Check the terminal** where you ran it - look for error messages
2. **Check if pip is working**:
   ```bash
   source venv/bin/activate
   pip list | head -10
   ```
3. **Check network connection** - pip needs internet
4. **Kill and restart** if truly stuck:
   ```bash
   pkill -f run.py
   python run.py
   ```

### If Dependencies Are Already Installed

You can skip `run.py` and use the application directly:
```bash
source venv/bin/activate
python -m cli.main analyze
```

## Quick Status Check Script

Use the provided `check_run_status.sh`:
```bash
./check_run_status.sh
```

---

*Last Updated: 2025-01-16*

