# TradingAgents Interactive Shell Guide

## Quick Start

### Running the Interactive Shell

```bash
./trading_interactive.sh
```

This launches an interactive menu-driven interface where you can:
- Choose and run any TradingAgents feature
- Configure email and Slack notifications
- Track progress of operations
- Run multiple features in sequence
- View session logs

---

## Features Overview

### 1. 📊 Market Screener

Screen stocks using technical indicators with multiple modes:

- **Basic Screener** - Technical indicators only (MACD, RSI, Bollinger Bands, Volume)
- **Sector Analysis** - Analyze 11 market sectors + top stocks
- **Sector-First Workflow** - Identify top sectors, then analyze best stocks in those sectors
- **Full Analysis** - Include AI-powered investment recommendations
- **Fast Mode** - Optimized for speed (skip news, no RAG)

**What it does:**
- Scans all tracked stocks for technical signals
- Identifies bullish crosses, oversold conditions, volume spikes
- Ranks sectors by strength
- Provides top N opportunities with scores

### 2. 🔍 Stock Analysis

Deep AI-powered analysis of specific stocks:

- **Multi-Agent Analysis** - 4 specialized analysts (Market, Social, News, Fundamentals)
- **Bull/Bear Debate** - Researchers argue both sides
- **Plain English** - Easy-to-understand recommendations
- **Position Sizing** - Tailored to your portfolio value
- **Confidence Scores** - 0-100 rating for each recommendation
- **RAG Enhancement** - Uses historical intelligence for context

**What it provides:**
- BUY/HOLD/SELL recommendations
- Target price and stop loss
- Position size (shares and dollar amount)
- Bullish and bearish arguments
- Confidence score and reasoning

### 3. 🌅 Morning Briefing

Daily market intelligence delivered to your inbox/Slack:

- **Quick Digest** - Market summary only
- **Full Briefing** - Digest + price alerts
- **Comprehensive** - Briefing + screener + top stock analysis

**Includes:**
- Market overview and sentiment
- Top movers (gainers/losers)
- Sector performance
- Your price alerts
- Top investment opportunities

### 4. 💼 Portfolio Management

Track and manage your investment portfolio:

- View portfolio summary (holdings, positions, P&L)
- Buy and sell stocks
- Performance history with daily snapshots
- Unrealized gains/losses
- Average cost tracking
- Upcoming dividends

**Metrics:**
- Total value and cash balance
- Individual position performance
- Overall portfolio returns
- Dividend income tracking

### 5. 💰 Dividend Analysis

Comprehensive dividend tracking and analysis:

- **Upcoming Dividends** - Calendar of ex-dates and pay dates
- **Income Report** - Historical dividend income
- **High-Yield Finder** - Screen for high-yield stocks
- **Safety Analysis** - Evaluate dividend sustainability
- **Reinvestment Suggestions** - Optimize dividend reinvestment
- **Data Updates** - Backfill and update dividend data

**Insights:**
- Annual dividend income projections
- Yield on cost calculations
- Payout ratio analysis
- Dividend growth rates

### 6. 📈 Performance Evaluation

Track how well your AI recommendations perform:

- **Recent Recommendations** - View latest outcomes
- **Performance Report** - Win rate, average returns, alpha
- **Quick Statistics** - Key metrics at a glance
- **Update Outcomes** - Refresh with latest prices

**Metrics Tracked:**
- 1-day, 7-day, 30-day returns
- Win rate (% of profitable recommendations)
- Average return per recommendation
- Alpha vs S&P 500 benchmark
- Best and worst performers

---

## Notification Setup

### Email Configuration

The interactive shell includes a guided setup for email notifications via Gmail:

#### Step 1: Enable Email
Select option 7 from main menu → Enable email notifications

#### Step 2: Get Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Create a new app password for "TradingAgents"
4. Copy the 16-character password

#### Step 3: Configure in Interactive Shell
- From email: Your Gmail address
- To email: Recipient email (can be same)
- Password: The app password from step 2
- SMTP server: `smtp.gmail.com` (default)
- SMTP port: `587` (default)

#### Email Notifications Include:
- Morning briefings with market digest
- Price alerts
- Portfolio performance reports
- Task completion notifications
- Error alerts

---

### Slack/Discord Configuration

#### Step 1: Create Webhook

**For Slack:**
1. Go to https://api.slack.com/messaging/webhooks
2. Create a new Slack App
3. Enable "Incoming Webhooks"
4. Add webhook to your workspace
5. Copy the webhook URL

**For Discord:**
1. Go to your Discord server
2. Edit Channel → Integrations → Webhooks
3. Create webhook
4. Copy webhook URL

#### Step 2: Configure in Interactive Shell
Select option 7 from main menu → Enable Slack/Discord notifications

- Webhook URL: Paste the URL from step 1
- Channel: `#trading` (or your preferred channel)
- Username: `TradingAgents` (bot display name)
- Icon emoji: `:chart_with_upwards_trend:` (or any emoji)

#### Slack/Discord Notifications Include:
- Real-time market alerts
- Analysis completions
- Portfolio updates
- Performance reports
- Error notifications

---

### Notification Preferences

Control when you receive notifications:

- **Notify on Success** - Get alerts when tasks complete successfully
- **Notify on Error** - Get alerts when errors occur

**Best Practice:**
- Enable success notifications for scheduled tasks (cron jobs)
- Always enable error notifications
- Use Slack for real-time alerts, email for daily summaries

---

### Testing Notifications

After configuring, test your setup:

1. From main menu, select option 8 (Test Notifications)
2. Check your email inbox
3. Check your Slack/Discord channel
4. Verify formatting and delivery

---

## Progress Tracking

The interactive shell includes built-in progress tracking:

### During Execution
- Real-time progress bars show completion status
- Task counters display "X/Y tasks completed"
- Color-coded output for success/warnings/errors

### Session Logs
All operations are logged with timestamps:

```
[2025-01-16 09:30:15] [INFO] TradingAgents Interactive Shell started
[2025-01-16 09:31:22] [INFO] Running screener with sector analysis
[2025-01-16 09:35:44] [INFO] Task completed: 1/1
```

**View logs:** Select option 9 from main menu

### Advanced Progress Tracking

Use the standalone progress tracker:

```bash
# Watch progress in real-time
./scripts/progress_tracker.py watch

# View summary statistics
./scripts/progress_tracker.py summary

# Clear tracked tasks
./scripts/progress_tracker.py clear
```

---

## Multi-Feature Execution

Run multiple features in sequence with progress tracking:

### Example: Complete Morning Routine

1. Select option 10 (Run Multiple Features)
2. Enter: `1,3,6` (Screener, Morning Briefing, Evaluation)
3. Watch progress as each feature executes
4. Review combined results

### Popular Combinations

**Daily Analysis:**
```
1,3,6  → Screener + Morning Briefing + Evaluation
```

**Portfolio Review:**
```
4,5,6  → Portfolio + Dividends + Evaluation
```

**Deep Research:**
```
1,2,6  → Screener + Stock Analysis + Evaluation
```

**Quick Check:**
```
3,4    → Morning Briefing + Portfolio View
```

---

## Environment Variables

The interactive shell uses `.env` for configuration. All settings can be configured via the notification wizard (option 7), but you can also edit manually:

### API Keys
```bash
OPENAI_API_KEY=sk-...
ALPHA_VANTAGE_API_KEY=...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
```

### Email Settings
```bash
EMAIL_ENABLED=true
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Slack Settings
```bash
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_CHANNEL=#trading
SLACK_USERNAME=TradingAgents
SLACK_ICON_EMOJI=:chart_with_upwards_trend:
```

### Notification Preferences
```bash
NOTIFY_ON_SUCCESS=true
NOTIFY_ON_ERROR=true
```

### Feature Defaults
```bash
# Sector Analysis
SECTOR_ANALYSIS_ENABLED=true
MIN_STOCKS_PER_SECTOR=5
TOP_SECTORS_TO_ANALYZE=3
STOCKS_PER_SECTOR=3

# Portfolio
DEFAULT_PORTFOLIO_VALUE=100000
RISK_TOLERANCE=moderate
MAX_POSITION_SIZE=0.05
CASH_RESERVE=0.10

# CLI
RICH_THEME=monokai
ENABLE_PROGRESS_BARS=true
```

---

## Automation with Cron

Automate daily tasks using cron jobs:

### Quick Setup

```bash
./scripts/setup_cron.sh
```

### Manual Cron Configuration

Edit your crontab:
```bash
crontab -e
```

Add scheduled tasks:
```cron
# Morning briefing at 7 AM (weekdays)
0 7 * * 1-5 cd /path/to/TradingAgents && ./scripts/morning_briefing.sh --with-analysis

# Update dividend data (Sunday 6 AM)
0 6 * * 0 cd /path/to/TradingAgents && .venv/bin/python -m tradingagents.dividends backfill

# Daily evaluation at 6 PM
0 18 * * * cd /path/to/TradingAgents && ./scripts/daily_evaluation.sh

# Weekly performance report (Friday 5 PM)
0 17 * * 5 cd /path/to/TradingAgents && .venv/bin/python -m tradingagents.evaluate report

# Portfolio snapshot (daily at 4:30 PM after market close)
30 16 * * 1-5 cd /path/to/TradingAgents && .venv/bin/python -m tradingagents.portfolio snapshot
```

**Note:** Automated tasks will send notifications if configured!

---

## Tips & Best Practices

### Daily Workflow

**Morning (before market open):**
1. Run morning briefing (option 3 → option 2)
2. Review email/Slack notifications
3. Check top opportunities from screener

**During Market Hours:**
1. Analyze specific stocks (option 2)
2. Execute trades via portfolio (option 4)
3. Monitor alerts

**Evening (after market close):**
1. Update evaluation outcomes (option 6 → option 4)
2. Review portfolio performance (option 4 → option 2)
3. Check dividend calendar (option 5 → option 1)

### Performance Optimization

**Fast Mode:**
- Use for quick checks during market hours
- Skips news aggregation and RAG lookups
- 3-5x faster than full analysis

**Sector-First Workflow:**
- More efficient than analyzing all stocks
- Focuses on strongest sectors
- Best for daily screening

**No-RAG Mode:**
- Faster analysis without historical context
- Good for quick opinions on familiar stocks
- Use full mode for new/unfamiliar tickers

### Notification Strategy

**Email:**
- Morning digest and summaries
- Daily/weekly reports
- Low-urgency updates

**Slack/Discord:**
- Real-time price alerts
- Trade confirmations
- Error notifications
- Quick summaries

### Data Management

**Regular Maintenance:**
```bash
# Update dividend data (weekly)
./scripts/update_dividends.sh

# Backup database (weekly)
./scripts/backup_database.sh

# Update evaluation outcomes (daily)
.venv/bin/python -m tradingagents.evaluate update
```

---

## Troubleshooting

### Email Not Sending

**Check:**
1. Gmail app password (not regular password)
2. "Less secure apps" NOT needed (use app passwords)
3. `.env` file has correct credentials
4. SMTP port is 587 (not 465)

**Test:**
```bash
# Send test notification
.venv/bin/python -m tradingagents.insights notify
```

### Slack/Discord Not Working

**Check:**
1. Webhook URL is complete and correct
2. Channel exists and bot has access
3. Webhook hasn't been revoked
4. `.env` has `SLACK_ENABLED=true`

**Test:**
```bash
# Send test notification
.venv/bin/python -m tradingagents.insights notify
```

### Virtual Environment Issues

**If commands fail:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Verify Python path
which python  # Should show .venv/bin/python

# Reinstall if needed
pip install -r requirements.txt
```

### Database Connection Errors

**Check PostgreSQL:**
```bash
# macOS (Homebrew)
brew services list
brew services start postgresql@14

# Verify connection
psql -d investment_intelligence -c "SELECT 1"
```

### Log Files Growing Large

**Clean up old logs:**
```bash
# Remove logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete

# Keep only recent session logs
find logs/ -name "session_*.log" -mtime +7 -delete
```

---

## Advanced Usage

### Custom Workflows

Create your own bash scripts using the interactive shell components:

```bash
#!/bin/bash
# custom_workflow.sh

cd /path/to/TradingAgents

# Morning routine
.venv/bin/python -m tradingagents.screener run --sector-first --top 5

# Analyze top picks
.venv/bin/python -m tradingagents.analyze AAPL GOOGL --plain-english

# Update portfolio
.venv/bin/python -m tradingagents.portfolio snapshot

# Send summary
.venv/bin/python -m tradingagents.insights digest
```

### API Integration

Use TradingAgents modules in your own Python scripts:

```python
from tradingagents.screener.screener import MarketScreener
from tradingagents.notifications import EmailNotifier, SlackNotifier

# Run screener
screener = MarketScreener()
results = screener.run_screener(sector_analysis=True)

# Send notifications
email = EmailNotifier()
email.send_briefing(results)

slack = SlackNotifier()
slack.send_alert("Top pick: AAPL - Strong technical setup")
```

---

## Support & Resources

**Documentation:**
- Main README: `/README.md`
- Setup Guide: `/SETUP.md`
- This Guide: `/INTERACTIVE_SHELL_GUIDE.md`

**Scripts:**
- Interactive Shell: `/trading_interactive.sh`
- Progress Tracker: `/scripts/progress_tracker.py`
- All Helper Scripts: `/scripts/`

**Logs:**
- Session Logs: `/logs/session_*.log`
- Application Logs: Check during execution

**Get Help:**
```bash
# Python module help
.venv/bin/python -m tradingagents.screener --help
.venv/bin/python -m tradingagents.analyze --help

# Script help
./scripts/morning_briefing.sh --help
```

---

## Quick Reference

### Main Menu Options

```
1  → Market Screener         (5 modes available)
2  → Stock Analysis          (AI-powered deep dive)
3  → Morning Briefing        (3 levels: quick/full/comprehensive)
4  → Portfolio Management    (6 operations)
5  → Dividend Analysis       (6 features)
6  → Performance Evaluation  (4 report types)
7  → Configure Notifications (Email + Slack setup wizard)
8  → Test Notifications      (Verify setup)
9  → View Session Logs       (Last 50 entries)
10 → Run Multiple Features   (Batch execution with progress)
0  → Exit
```

### Keyboard Shortcuts

- `Ctrl+C` - Cancel current operation (returns to menu)
- `Enter` - Use default value in prompts
- `0` - Return to main menu / Exit

### File Locations

```
/trading_interactive.sh          # Main interactive shell
/scripts/progress_tracker.py     # Standalone progress tracker
/logs/session_*.log              # Session logs
/logs/progress.json              # Progress data
/.env                            # Configuration (created on first run)
```

---

**Happy Trading! 📈💰**
