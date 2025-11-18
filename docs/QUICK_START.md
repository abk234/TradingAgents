# TradingAgents Interactive Shell - Quick Start

## 🚀 Launch in 3 Steps

### 1. Run the Interactive Shell
```bash
cd /path/to/TradingAgents
./trading_interactive.sh
```

### 2. Configure Notifications (First Time)
When prompted or select option `7`:
- **Email**: Gmail address + app password from https://myaccount.google.com/apppasswords
- **Slack/Discord**: Webhook URL from https://api.slack.com/messaging/webhooks
- Test with option `8`

### 3. Choose Your Feature
```
1  → 📊 Market Screener       - Find top stocks
2  → 🔍 Stock Analysis        - AI deep dive
3  → 🌅 Morning Briefing      - Daily digest
4  → 💼 Portfolio             - Track investments
5  → 💰 Dividends             - Income tracking
6  → 📈 Performance           - How good are recommendations?
10 → 🎯 Run Multiple          - Batch execution
```

---

## 📋 Common Workflows

### Daily Morning Routine
```
Option 3 → Option 2 (Full briefing)
```
Gets you: Market digest + alerts + top opportunities

### Research a Stock
```
Option 2 → Enter ticker (e.g., AAPL) → Use defaults
```
Gets you: BUY/HOLD/SELL + confidence score + position size

### Find Investment Opportunities
```
Option 1 → Option 2 (Sector analysis) → Top 10
```
Gets you: Best stocks ranked by technical indicators

### Check Portfolio Performance
```
Option 4 → Option 2 (Performance history)
```
Gets you: Your P&L, returns, holdings

### Complete Analysis
```
Option 10 → Enter: 1,3,6
```
Runs: Screener → Morning Briefing → Evaluation

---

## 🔔 Notification Setup

### Gmail (5 minutes)
1. Go to https://myaccount.google.com/apppasswords
2. Create app password for "TradingAgents"
3. In shell: Option 7 → Enter email + app password
4. Test: Option 8

### Slack (3 minutes)
1. Go to https://api.slack.com/messaging/webhooks
2. Create webhook for your channel
3. In shell: Option 7 → Enter webhook URL
4. Test: Option 8

### Discord (2 minutes)
1. Server Settings → Integrations → Webhooks → New
2. Copy webhook URL
3. In shell: Option 7 → Enter webhook URL (same as Slack)
4. Test: Option 8

---

## 🎯 Feature Quick Reference

| Feature | What It Does | When to Use |
|---------|-------------|-------------|
| **Screener** | Scans all stocks for signals | Daily before market open |
| **Analysis** | Deep AI dive on specific stocks | Before buying/selling |
| **Briefing** | Market summary + alerts | Every morning |
| **Portfolio** | Track holdings & performance | After trades, weekly review |
| **Dividends** | Income tracking & forecasts | Monthly, before ex-dates |
| **Evaluation** | Recommendation performance | Weekly, monthly reports |

---

## ⚡ Speed Modes

### Fast Screener
```
Option 1 → Option 5 (Fast mode)
```
3-5x faster, skips news

### Quick Analysis
```
Option 2 → Use fast mode: y
```
No RAG lookups, faster results

### Sector-First (Most Efficient)
```
Option 1 → Option 3 (Sector-first)
```
Analyze sectors → top stocks only

---

## 📊 Progress Tracking

### View Real-Time Progress
```bash
# In another terminal
./scripts/progress_tracker.py watch
```

### View Session Logs
```
Option 9 (from main menu)
```

### Check Summary Stats
```bash
./scripts/progress_tracker.py summary
```

---

## 🔧 Troubleshooting

### Email Not Working
- Use Gmail **app password**, not regular password
- App passwords: https://myaccount.google.com/apppasswords
- Port should be `587`

### Slack Not Working
- Verify webhook URL is complete
- Check webhook hasn't been revoked
- Test in browser: `curl -X POST <webhook-url> -d '{"text":"test"}'`

### Script Won't Run
```bash
chmod +x trading_interactive.sh
```

### Commands Fail
```bash
# Check virtual environment
ls .venv/bin/python

# Activate if needed
source .venv/bin/activate
```

---

## 🤖 Automation

### One-Time Setup
```bash
./scripts/setup_cron.sh
```

### Manual Cron Examples
```cron
# Morning briefing (7 AM weekdays)
0 7 * * 1-5 cd ~/TradingAgents && ./scripts/morning_briefing.sh

# Evening evaluation (6 PM daily)
0 18 * * * cd ~/TradingAgents && .venv/bin/python -m tradingagents.evaluate update
```

---

## 📖 Full Documentation

For detailed information, see:
- **INTERACTIVE_SHELL_GUIDE.md** - Complete feature guide
- **README.md** - Project overview
- **.env.example** - All configuration options

---

## 💡 Pro Tips

1. **Use Defaults** - Press Enter to accept defaults, saves time
2. **Batch Operations** - Option 10 for multiple tasks
3. **Fast Mode** - For quick checks during market hours
4. **Sector-First** - Most efficient daily screening method
5. **Automate** - Set up cron for hands-free daily updates
6. **Notifications** - Slack for real-time, email for summaries
7. **Progress Tracker** - Run in separate terminal for live updates

---

## 🆘 Need Help?

```bash
# Module help
.venv/bin/python -m tradingagents.screener --help

# Script help
./scripts/morning_briefing.sh --help

# View logs
tail -f logs/session_*.log
```

---

**Get Started Now:**
```bash
./trading_interactive.sh
```

**Happy Trading! 📈**
