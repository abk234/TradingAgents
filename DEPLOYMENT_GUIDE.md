# TradingAgents - Production Deployment Guide

**Date:** 2025-11-16
**Version:** 1.0 (Phases 1-8 Complete)
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [Database Setup](#database-setup)
4. [Environment Configuration](#environment-configuration)
5. [Data Initialization](#data-initialization)
6. [Automated Jobs Setup](#automated-jobs-setup)
7. [Daily Workflow](#daily-workflow)
8. [Troubleshooting](#troubleshooting)
9. [Backup & Maintenance](#backup--maintenance)

---

## 🖥️ System Requirements

### Minimum Requirements:
- **OS:** macOS, Linux, or Windows (WSL recommended)
- **Python:** 3.10 or higher
- **PostgreSQL:** 14 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 10GB free space
- **Internet:** Stable connection for API calls

### Required Services:
- PostgreSQL database
- Ollama (for embeddings) - optional but recommended
- API Keys (see Environment Configuration)

---

## 🚀 Initial Setup

### 1. Clone or Navigate to Repository

```bash
cd /path/to/TradingAgents
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Verify key packages
python -c "import psycopg2; import yfinance; import langchain; print('✓ All packages imported successfully')"
```

---

## 🗄️ Database Setup

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Verify Installation:**
```bash
psql --version  # Should show PostgreSQL 14+
```

### 2. Create Database

```bash
# Create database
createdb investment_intelligence

# Or using psql
psql -U $USER -d postgres -c "CREATE DATABASE investment_intelligence;"
```

### 3. Run Migrations

```bash
# Run all migrations in order
psql -U $USER -d investment_intelligence -f scripts/migrations/001_initial_schema.sql
psql -U $USER -d investment_intelligence -f scripts/migrations/002_add_analyses.sql
psql -U $USER -d investment_intelligence -f scripts/migrations/003_add_embeddings.sql
# ... continue for all migrations

# Or run them all at once
for file in scripts/migrations/*.sql; do
    echo "Running $file..."
    psql -U $USER -d investment_intelligence -f "$file"
done
```

### 4. Verify Database Schema

```bash
# Check tables
psql -U $USER -d investment_intelligence -c "\dt"

# Should see tables like:
# - tickers
# - daily_prices
# - analyses
# - scan_results
# - dividend_payments
# - portfolio_holdings
# - etc.
```

---

## 🔧 Environment Configuration

### 1. Create .env File

```bash
cp .env.example .env  # If example exists, or create new
```

### 2. Edit .env File

```bash
# .env
# Database Configuration
DATABASE_NAME=investment_intelligence
DATABASE_USER=your_username
DATABASE_PASSWORD=  # Leave empty for local development
DATABASE_HOST=localhost
DATABASE_PORT=5432

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional

# Ollama Configuration (for embeddings)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# Portfolio Configuration
DEFAULT_PORTFOLIO_VALUE=100000
RISK_TOLERANCE=moderate  # conservative, moderate, aggressive
```

### 3. Install Ollama (Optional but Recommended)

**For local embeddings (faster and free):**

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Verify
ollama list  # Should show nomic-embed-text
```

**Without Ollama:**
- System will use API-based embeddings (slower, costs money)
- Or run with `--no-rag` flag to skip RAG features

---

## 📊 Data Initialization

### 1. Add Your Watchlist

```bash
# Add tickers you want to track
python -m tradingagents.database.ticker_ops add AAPL "Apple Inc." Technology
python -m tradingagents.database.ticker_ops add MSFT "Microsoft Corp." Technology
python -m tradingagents.database.ticker_ops add GOOGL "Alphabet Inc." Technology
python -m tradingagents.database.ticker_ops add NVDA "NVIDIA Corp." Technology
python -m tradingagents.database.ticker_ops add V "Visa Inc." Financial Services
python -m tradingagents.database.ticker_ops add JPM "JPMorgan Chase" Financial Services
python -m tradingagents.database.ticker_ops add JNJ "Johnson & Johnson" Healthcare
python -m tradingagents.database.ticker_ops add UNH "UnitedHealth Group" Healthcare
python -m tradingagents.database.ticker_ops add XOM "Exxon Mobil" Energy
python -m tradingagents.database.ticker_ops add PG "Procter & Gamble" Consumer Defensive

# Verify
python -m tradingagents.database.ticker_ops list
```

### 2. Initial Data Fetch

```bash
# Fetch historical price data (last 2 years)
python -m tradingagents.dataflows.y_finance backfill --days 730

# This will take a few minutes depending on number of tickers
```

### 3. Backfill Dividend Data (if applicable)

```bash
# Fetch dividend history for all tickers
python -m tradingagents.dividends backfill --years 5

# Update dividend yield cache
python -m tradingagents.dividends update-cache

# Update dividend calendar
python -m tradingagents.dividends update-calendar
```

### 4. Initialize Performance Tracking

```bash
# Backfill recommendation outcomes (if you have historical analyses)
python -m tradingagents.evaluate backfill --days 90

# Update with latest prices
python -m tradingagents.evaluate update --days 90
```

---

## ⏰ Automated Jobs Setup

### 1. Make Scripts Executable

```bash
chmod +x scripts/*.sh
```

### 2. Set Up Cron Jobs

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths to your installation):

# Daily screener - Every weekday at 6:30 AM
30 6 * * 1-5 cd /path/to/TradingAgents && ./scripts/run_daily_analysis.sh >> logs/daily.log 2>&1

# Daily evaluation update - Every day at 6:00 PM
0 18 * * * cd /path/to/TradingAgents && ./scripts/daily_evaluation.sh >> logs/evaluation.log 2>&1

# Dividend data update - Every day at 6:15 PM
15 18 * * * cd /path/to/TradingAgents && ./scripts/update_dividends.sh >> logs/dividends.log 2>&1

# Morning briefing - Every weekday at 7:00 AM
0 7 * * 1-5 cd /path/to/TradingAgents && ./scripts/morning_briefing.sh >> logs/briefing.log 2>&1

# Weekly report - Every Sunday at 9:00 AM
0 9 * * 0 cd /path/to/TradingAgents && ./scripts/weekly_report.sh >> logs/weekly.log 2>&1

# Price alerts - Every hour during market hours (9 AM - 4 PM ET)
0 9-16 * * 1-5 cd /path/to/TradingAgents && ./scripts/check_alerts.sh >> logs/alerts.log 2>&1

# Database backup - Every day at 2:00 AM
0 2 * * * cd /path/to/TradingAgents && ./scripts/backup_database.sh >> logs/backup.log 2>&1
```

### 3. Create Log Directory

```bash
mkdir -p logs
```

### 4. Test Cron Jobs

```bash
# Test each script manually first
./scripts/morning_briefing.sh
./scripts/run_daily_analysis.sh
./scripts/check_alerts.sh
```

---

## 📅 Daily Workflow

### Morning Routine (7:00-7:15 AM)

**Automated:**
```bash
# Cron runs morning briefing automatically
# Check logs/briefing.log for output
```

**Manual:**
```bash
# Run morning briefing
./scripts/morning_briefing.sh

# Or run screener with analysis
python -m tradingagents.screener run --with-analysis --fast --no-rag \
  --analysis-limit 3 --portfolio-value 100000
```

**Review:**
- Top opportunities from screener
- Price alerts from overnight
- Upcoming dividend payments
- Recent performance metrics

### During Market Hours

**Check alerts periodically:**
```bash
# Manual check
./scripts/check_alerts.sh

# Or automated via cron (every hour)
```

**Deep dive on specific stocks:**
```bash
# Full analysis with RAG
python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000

# Fast analysis
python -m tradingagents.analyze AAPL --plain-english --fast --no-rag
```

### Evening Routine (6:00-6:30 PM)

**Automated:**
```bash
# Cron updates:
# - Daily evaluation (6:00 PM)
# - Dividend data (6:15 PM)
# - Performance metrics (background)
```

**Manual Review:**
```bash
# View performance report
python -m tradingagents.evaluate report --period 30

# Check dividend income
python -m tradingagents.dividends income

# Review alerts generated during the day
tail -50 logs/alerts.log
```

### Weekly Review (Sunday Morning)

```bash
# Automated weekly report
# Check logs/weekly.log

# Or run manually
./scripts/weekly_report.sh

# View comprehensive performance
python -m tradingagents.evaluate report --period 90

# Check dividend opportunities
python -m tradingagents.dividends high-yield --min-yield 3.0
```

---

## 🔍 Troubleshooting

### Database Connection Issues

**Problem:** Cannot connect to database

```bash
# Check if PostgreSQL is running
pg_isready

# Check database exists
psql -U $USER -d postgres -c "\l" | grep investment_intelligence

# Test connection
psql -U $USER -d investment_intelligence -c "SELECT COUNT(*) FROM tickers;"
```

**Fix:**
```bash
# Start PostgreSQL
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Recreate database if needed
dropdb investment_intelligence
createdb investment_intelligence
# Re-run migrations
```

### Ollama Issues

**Problem:** Embeddings not working

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve &

# Pull model if missing
ollama pull nomic-embed-text
```

**Workaround:**
```bash
# Run without RAG
python -m tradingagents.analyze AAPL --no-rag --plain-english
```

### API Key Issues

**Problem:** API calls failing

```bash
# Check .env file exists
cat .env | grep API_KEY

# Verify keys are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:10])"
```

**Fix:**
- Verify API keys in .env
- Check key permissions/quotas
- Ensure .env is in project root

### Missing Data

**Problem:** No price data or analyses

```bash
# Backfill price data
python -m tradingagents.dataflows.y_finance backfill --days 90

# Check data exists
psql -U $USER -d investment_intelligence -c "SELECT COUNT(*) FROM daily_prices;"

# Run screener to generate analyses
python -m tradingagents.screener run
```

### Performance Issues

**Problem:** Analyses taking too long

```bash
# Use fast mode (60-80% faster)
python -m tradingagents.screener run --fast --no-rag

# Reduce analysis limit
python -m tradingagents.screener run --with-analysis --analysis-limit 1

# Check database indexes
psql -U $USER -d investment_intelligence -c "\di"
```

---

## 💾 Backup & Maintenance

### Daily Backups

**Automated (via cron):**
```bash
# Already set up in cron (2:00 AM daily)
# Backups stored in backups/ directory
```

**Manual Backup:**
```bash
# Run backup script
./scripts/backup_database.sh

# Or manual pg_dump
pg_dump -U $USER investment_intelligence > backups/backup_$(date +%Y%m%d).sql
```

### Restore from Backup

```bash
# List backups
ls -lh backups/

# Restore specific backup
psql -U $USER -d investment_intelligence < backups/backup_20251116.sql
```

### Database Maintenance

**Weekly:**
```bash
# Vacuum and analyze (run on Sunday night)
psql -U $USER -d investment_intelligence -c "VACUUM ANALYZE;"

# Check database size
psql -U $USER -d investment_intelligence -c "SELECT pg_size_pretty(pg_database_size('investment_intelligence'));"
```

**Monthly:**
```bash
# Clean up old scan results (keep last 90 days)
psql -U $USER -d investment_intelligence -c "
DELETE FROM scan_results
WHERE scan_date < CURRENT_DATE - INTERVAL '90 days';
"

# Clean up old price data (if needed)
# Keep at least 2 years of history
```

### Log Rotation

**Set up logrotate (Linux):**
```bash
# Create /etc/logrotate.d/tradingagents
/path/to/TradingAgents/logs/*.log {
    weekly
    rotate 4
    compress
    missingok
    notifempty
}
```

**Manual cleanup:**
```bash
# Clean logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 🎯 Quick Reference Commands

### Most Used Commands

```bash
# Morning briefing
./scripts/morning_briefing.sh

# Run daily screener
python -m tradingagents.screener run

# Analyze specific stock
python -m tradingagents.analyze AAPL --plain-english --portfolio-value 100000

# View performance
python -m tradingagents.evaluate report --period 30

# Upcoming dividends
python -m tradingagents.dividends upcoming --days 30

# High-yield stocks
python -m tradingagents.dividends high-yield --min-yield 3.0

# Check alerts
./scripts/check_alerts.sh
```

### System Health Checks

```bash
# Database connection
psql -U $USER -d investment_intelligence -c "SELECT 1;"

# Ticker count
psql -U $USER -d investment_intelligence -c "SELECT COUNT(*) FROM tickers WHERE active = TRUE;"

# Recent analyses
psql -U $USER -d investment_intelligence -c "SELECT COUNT(*) FROM analyses WHERE analysis_date >= CURRENT_DATE - 7;"

# Ollama status
curl http://localhost:11434/api/tags

# Disk usage
du -sh .
df -h .
```

---

## 📞 Support & Resources

### Documentation

- **Phase Completion Reports:** See `PHASE*_COMPLETION_REPORT.md` files
- **User Guide:** `USER_GUIDE.md`
- **Troubleshooting:** `TROUBLESHOOTING_CONNECTION_ERRORS.md`
- **Portfolio Guide:** `PORTFOLIO_GUIDE.md`

### Logs

All logs are stored in `logs/` directory:
- `daily.log` - Daily screener runs
- `briefing.log` - Morning briefings
- `alerts.log` - Price alerts
- `evaluation.log` - Performance updates
- `dividends.log` - Dividend updates
- `weekly.log` - Weekly reports
- `backup.log` - Database backups

### Getting Help

```bash
# Command help
python -m tradingagents.screener --help
python -m tradingagents.analyze --help
python -m tradingagents.dividends --help
python -m tradingagents.evaluate --help

# Check system status
python scripts/check_setup.py
```

---

## ✅ Post-Deployment Checklist

- [ ] Python 3.10+ installed
- [ ] PostgreSQL 14+ installed and running
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Database created (`investment_intelligence`)
- [ ] All migrations run successfully
- [ ] `.env` file configured with API keys
- [ ] Ollama installed and running (optional)
- [ ] Watchlist tickers added
- [ ] Historical price data fetched
- [ ] Dividend data backfilled (if applicable)
- [ ] Cron jobs configured
- [ ] All scripts executable (`chmod +x scripts/*.sh`)
- [ ] Logs directory created
- [ ] Test run of morning briefing successful
- [ ] Backup system tested

---

## 🎉 You're Ready!

Your TradingAgents system is now deployed and ready for production use!

**Next Steps:**
1. Run your first morning briefing
2. Let automated jobs run for a week
3. Review performance metrics
4. Adjust watchlist and settings as needed
5. Enjoy AI-powered trading intelligence! 🚀

---

**Version:** 1.0
**Last Updated:** 2025-11-16
**Phases Complete:** 1-8 (Foundation through Dividend Tracking)
**Status:** ✅ Production Ready
