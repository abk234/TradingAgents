# Shell Scripts Organization

**Date:** November 17, 2025  
**Status:** ✅ **All Scripts Organized & Verified**

---

## 📁 Organization Structure

All shell scripts have been organized into a logical directory structure:

```
scripts/
├── bin/                    # Main entry point scripts
│   ├── quick_run.sh        # Quick access to common operations
│   ├── make_profit.sh      # Profit-making workflow
│   ├── start_eddie.sh      # Start Eddie interface
│   ├── trading_agents.sh   # Main trading agents script
│   ├── trading_bot.sh      # Trading bot script
│   ├── trading_interactive.sh # Interactive trading
│   └── run.sh              # Script runner utility
│
├── workflows/              # Daily/weekly workflows
│   ├── phase1_screening.sh
│   ├── phase2_agents.sh
│   ├── phase3_reports.sh
│   ├── phase4_full_workflow.sh
│   ├── run_daily_analysis.sh
│   ├── eddie_daily_workflow.sh
│   ├── eddie_quick_analysis.sh
│   ├── morning_briefing.sh
│   ├── daily_evaluation.sh
│   └── weekly_report.sh
│
├── maintenance/            # Maintenance & setup scripts
│   ├── backup_database.sh
│   ├── show_database_state.sh
│   ├── check_alerts.sh
│   ├── dividend_alerts.sh
│   ├── update_dividends.sh
│   ├── cleanup_price_cache.sh
│   ├── setup_cron.sh
│   ├── setup_redis.sh
│   ├── fix_redis.sh
│   └── check_run_status.sh
│
├── development/            # Development & testing scripts
│   ├── quick_validate.sh
│   ├── test_all_features.sh
│   ├── run_tests.sh
│   ├── ensure_eddie_prerequisites.sh
│   └── evaluate.sh
│
└── utilities/              # Utility scripts
    ├── browse_chromadb.sh
    ├── run_screener.sh
    └── sync_to_obsidian.sh
```

---

## 🔗 Backward Compatibility

### Symlinks Created

For backward compatibility, symlinks have been created in the root directory for commonly used scripts:

- `quick_run.sh` → `scripts/bin/quick_run.sh`
- `make_profit.sh` → `scripts/bin/make_profit.sh`
- `start_eddie.sh` → `scripts/bin/start_eddie.sh`
- `trading_agents.sh` → `scripts/bin/trading_agents.sh`
- `trading_bot.sh` → `scripts/bin/trading_bot.sh`
- `trading_interactive.sh` → `scripts/bin/trading_interactive.sh`
- `setup_redis.sh` → `scripts/maintenance/setup_redis.sh`
- `fix_redis.sh` → `scripts/maintenance/fix_redis.sh`
- `check_run_status.sh` → `scripts/maintenance/check_run_status.sh`
- `sync_to_obsidian.sh` → `scripts/utilities/sync_to_obsidian.sh`
- `browse_chromadb.sh` → `scripts/utilities/browse_chromadb.sh`
- `run_screener.sh` → `scripts/utilities/run_screener.sh`
- `quick_validate.sh` → `scripts/development/quick_validate.sh`
- `test_all_features.sh` → `scripts/development/test_all_features.sh`

**All existing commands continue to work!**

---

## 🚀 Usage

### Option 1: Use Symlinks (Backward Compatible)

```bash
# These still work from root directory
./quick_run.sh
./make_profit.sh
./start_eddie.sh
```

### Option 2: Use Direct Paths

```bash
# Use full paths
./scripts/bin/quick_run.sh
./scripts/workflows/phase1_screening.sh
./scripts/maintenance/backup_database.sh
```

### Option 3: Use Script Runner

```bash
# List all scripts
./scripts/bin/run.sh list

# Run a script
./scripts/bin/run.sh main quick_run
./scripts/bin/run.sh workflows phase1_screening
./scripts/bin/run.sh maintenance backup_database
```

---

## ✅ Verification

### All Scripts Verified ✅

**Total Scripts:** 36  
**Valid:** 36  
**Invalid:** 0  
**Status:** ✅ **All scripts are valid and executable**

### Verification Command

```bash
./scripts/verify_scripts.sh
```

This checks:
- ✅ Script exists
- ✅ Script is executable
- ✅ Script has shebang (#!)
- ✅ Script has valid bash syntax

---

## 📊 Script Categories

### Main Scripts (`scripts/bin/`)
**Purpose:** Primary entry points for users

- `quick_run.sh` - Quick access to common operations
- `make_profit.sh` - Profit-making workflow
- `start_eddie.sh` - Start Eddie interface
- `trading_agents.sh` - Main trading agents script
- `trading_bot.sh` - Trading bot script
- `trading_interactive.sh` - Interactive trading

### Workflows (`scripts/workflows/`)
**Purpose:** Daily/weekly automated workflows

- `phase1_screening.sh` - Phase 1: Screening
- `phase2_agents.sh` - Phase 2: Agent analysis
- `phase3_reports.sh` - Phase 3: Reports
- `phase4_full_workflow.sh` - Phase 4: Full workflow
- `run_daily_analysis.sh` - Daily analysis
- `eddie_daily_workflow.sh` - Eddie daily workflow
- `eddie_quick_analysis.sh` - Eddie quick analysis
- `morning_briefing.sh` - Morning briefing
- `daily_evaluation.sh` - Daily evaluation
- `weekly_report.sh` - Weekly report

### Maintenance (`scripts/maintenance/`)
**Purpose:** System maintenance and setup

- `backup_database.sh` - Backup database
- `show_database_state.sh` - Show database state
- `check_alerts.sh` - Check alerts
- `dividend_alerts.sh` - Dividend alerts
- `update_dividends.sh` - Update dividends
- `cleanup_price_cache.sh` - Cleanup price cache
- `setup_cron.sh` - Setup cron jobs
- `setup_redis.sh` - Setup Redis
- `fix_redis.sh` - Fix Redis issues
- `check_run_status.sh` - Check run status

### Development (`scripts/development/`)
**Purpose:** Development and testing

- `quick_validate.sh` - Quick validation
- `test_all_features.sh` - Test all features
- `run_tests.sh` - Run test suite
- `ensure_eddie_prerequisites.sh` - Ensure Eddie prerequisites
- `evaluate.sh` - Evaluation script

### Utilities (`scripts/utilities/`)
**Purpose:** Utility scripts

- `browse_chromadb.sh` - Browse ChromaDB
- `run_screener.sh` - Run screener
- `sync_to_obsidian.sh` - Sync to Obsidian

---

## 🔧 Script Runner

### Usage

```bash
# List all scripts
./scripts/bin/run.sh list

# Run a script by category and name
./scripts/bin/run.sh main quick_run
./scripts/bin/run.sh workflows phase1_screening
./scripts/bin/run.sh maintenance backup_database
./scripts/bin/run.sh development run_tests
./scripts/bin/run.sh utilities browse_chromadb
```

### Examples

```bash
# Run quick_run.sh
./scripts/bin/run.sh main quick_run

# Run phase 1 screening
./scripts/bin/run.sh workflows phase1_screening AAPL

# Run database backup
./scripts/bin/run.sh maintenance backup_database

# Run tests
./scripts/bin/run.sh development run_tests
```

---

## ✅ Verification Results

All 36 scripts have been verified:

- ✅ **Syntax valid** - All scripts have valid bash syntax
- ✅ **Executable** - All scripts are executable
- ✅ **Shebang present** - All scripts have proper shebang
- ✅ **No errors** - No syntax or structural errors

---

## 📝 Migration Notes

### For Existing Users

**No changes required!** All existing commands continue to work:

```bash
# These still work (via symlinks)
./quick_run.sh
./make_profit.sh
./start_eddie.sh
```

### For New Users

Use the organized structure:

```bash
# Use organized paths
./scripts/bin/quick_run.sh
./scripts/workflows/phase1_screening.sh

# Or use script runner
./scripts/bin/run.sh list
./scripts/bin/run.sh main quick_run
```

---

## 🛠️ Maintenance

### Adding New Scripts

1. **Determine category:**
   - Main entry point → `scripts/bin/`
   - Workflow → `scripts/workflows/`
   - Maintenance → `scripts/maintenance/`
   - Development → `scripts/development/`
   - Utility → `scripts/utilities/`

2. **Place script in appropriate directory**

3. **Make executable:**
   ```bash
   chmod +x scripts/[category]/your_script.sh
   ```

4. **Verify:**
   ```bash
   ./scripts/verify_scripts.sh
   ```

### Updating Scripts

Scripts can be updated in their organized locations. Symlinks will automatically point to the updated versions.

---

## 📚 Related Documentation

- `CLAUDE.md` - Project overview and commands
- `QUICK_START_GUIDE.md` - Quick start guide
- `USAGE_GUIDE.md` - Usage guide

---

## ✅ Summary

**Status:** ✅ **All Scripts Organized & Verified**

- ✅ **36 scripts** organized into 5 categories
- ✅ **14 symlinks** created for backward compatibility
- ✅ **All scripts verified** - syntax valid, executable
- ✅ **Script runner** created for easy access
- ✅ **Verification script** created for maintenance

**All existing commands continue to work!**

---

**Last Updated:** November 17, 2025

