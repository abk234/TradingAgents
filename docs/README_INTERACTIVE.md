# 🎯 TradingAgents Interactive Shell - README

## ✅ Installation Complete!

Your TradingAgents interactive shell system is now ready to use. All virtual environment paths have been configured automatically (works with both `venv` and `.venv`).

---

## 🚀 Quick Start (3 Ways to Run)

### 1. Interactive Menu (Recommended for New Users)
```bash
./trading_interactive.sh
```
- Full menu-driven interface
- Guided configuration wizards
- Progress tracking with visual feedback
- Session logging
- Perfect for exploring all features

### 2. Quick Commands (For Power Users)
```bash
# View all available commands
./quick_run.sh

# Examples:
./quick_run.sh screener          # Run market screener
./quick_run.sh analyze AAPL      # Analyze a specific stock
./quick_run.sh morning           # Morning briefing
./quick_run.sh full-analysis     # Complete workflow
```

### 3. Direct Python Modules (Advanced)
```bash
venv/bin/python -m tradingagents.screener run --sector-analysis
venv/bin/python -m tradingagents.analyze AAPL --plain-english
venv/bin/python -m tradingagents.insights morning
```

---

## 🔔 Setting Up Notifications (5 Minutes)

### Email Notifications (Gmail)

**Step 1:** Get App Password
1. Visit: https://myaccount.google.com/apppasswords
2. Sign in → Create app password → Name it "TradingAgents"
3. Copy the 16-character password

**Step 2:** Configure
```bash
./trading_interactive.sh
# Select option 7 (Configure Notifications)
# Follow the wizard for email setup
```

**Step 3:** Test
```bash
./quick_run.sh test
# OR from interactive menu: option 8
```

### Slack Notifications

**Step 1:** Create Webhook
1. Visit: https://api.slack.com/messaging/webhooks
2. Create app → Enable webhooks → Add to workspace
3. Copy webhook URL

**Step 2:** Configure
```bash
./trading_interactive.sh
# Select option 7
# Enter webhook URL when prompted
```

### Discord Notifications
Same as Slack! Discord webhooks are compatible.

---

## 📊 Available Features

| Feature | Interactive Menu | Quick Command | Description |
|---------|-----------------|---------------|-------------|
| **Market Screener** | Option 1 | `./quick_run.sh screener` | Screen stocks with technical indicators across all sectors |
| **Stock Analysis** | Option 2 | `./quick_run.sh analyze AAPL` | Deep AI analysis with BUY/HOLD/SELL recommendations |
| **Morning Briefing** | Option 3 | `./quick_run.sh morning` | Daily market digest + alerts + opportunities |
| **Portfolio** | Option 4 | `./quick_run.sh portfolio` | Track holdings, performance, P&L |
| **Dividends** | Option 5 | `./quick_run.sh dividends` | Income tracking and forecasts |
| **Evaluation** | Option 6 | `./quick_run.sh evaluate` | AI recommendation performance metrics |
| **Multi-Feature** | Option 10 | `./quick_run.sh full-analysis` | Run multiple features in sequence |

---

## 🎯 Common Workflows

### Daily Morning Routine
```bash
# Interactive way:
./trading_interactive.sh
# Select: 3 → 2 (Full morning briefing)

# Quick way:
./quick_run.sh morning
```

### Find Investment Opportunities
```bash
# Interactive way:
./trading_interactive.sh
# Select: 1 → 2 (Sector analysis) → Enter 10

# Quick way:
./quick_run.sh screener
```

### Research Before Buying
```bash
# Interactive way:
./trading_interactive.sh
# Select: 2 → Enter AAPL → Use defaults

# Quick way:
./quick_run.sh analyze AAPL
```

### Complete Daily Analysis
```bash
# Interactive way:
./trading_interactive.sh
# Select: 10 → Enter: 1,3,6

# Quick way:
./quick_run.sh full-analysis
```

### Portfolio Review
```bash
./quick_run.sh portfolio-review
# Runs: Portfolio + Performance + Dividends
```

---

## 📈 Progress Tracking

### Real-Time Progress
The interactive shell shows live progress bars:
```
Progress: [██████████████████░░░░] 75% (3/4)
```

### Session Logs
Every action is logged with timestamps:
```
[2025-11-16 09:30:15] [INFO] Running screener with sector analysis
[2025-11-16 09:35:44] [INFO] Task completed: 1/1
```

View logs from interactive menu: **Option 9**

### Standalone Progress Tracker
```bash
# Watch progress in another terminal
./scripts/progress_tracker.py watch

# View summary statistics
./scripts/progress_tracker.py summary

# Clear progress data
./scripts/progress_tracker.py clear
```

---

## 🤖 Automation

### Set Up Daily Automation
```bash
# Edit your crontab
crontab -e

# Add these lines:
# Morning briefing at 7 AM (weekdays)
0 7 * * 1-5 cd /Users/lxupkzwjs/Developer/eval/TradingAgents && ./quick_run.sh morning

# Evening evaluation at 6 PM
0 18 * * * cd /Users/lxupkzwjs/Developer/eval/TradingAgents && venv/bin/python -m tradingagents.evaluate update

# Weekly report (Friday 5 PM)
0 17 * * 5 cd /Users/lxupkzwjs/Developer/eval/TradingAgents && ./quick_run.sh evaluate
```

With notifications configured, you'll get automatic emails/Slack messages!

---

## 📁 What Was Created

| File | Purpose |
|------|---------|
| `trading_interactive.sh` | Main interactive menu (773 lines) |
| `quick_run.sh` | Fast command-line access |
| `scripts/progress_tracker.py` | Standalone progress monitoring |
| `INTERACTIVE_SHELL_GUIDE.md` | Complete user guide (500+ lines) |
| `QUICK_START.md` | 3-step quick start |
| `logs/` | Session logs directory (auto-created) |

---

## 🔧 Troubleshooting

### "Virtual environment not found"
✅ **FIXED!** The scripts now automatically detect both `venv` and `.venv`

### Email not sending
- Use Gmail **app password**, not regular password
- Get app password: https://myaccount.google.com/apppasswords
- Port must be 587 (not 465)

### Slack not working
- Verify webhook URL is complete
- Test: `curl -X POST <webhook-url> -d '{"text":"test"}'`

### Commands fail
```bash
# Verify virtual environment
ls venv/bin/python

# Check Python version
venv/bin/python --version
```

---

## 📖 Full Documentation

- **QUICK_START.md** - Get started in 3 steps
- **INTERACTIVE_SHELL_GUIDE.md** - Complete feature guide with examples
- **.env.example** - All configuration options
- **README.md** - Main project documentation

---

## 💡 Pro Tips

1. **Use Defaults** - Press Enter to accept defaults, saves time
2. **Quick Commands** - Faster than interactive menu for repeat tasks
3. **Multi-Feature** - Option 10 or `full-analysis` for comprehensive updates
4. **Sector-First** - Most efficient screening method
5. **Fast Mode** - For quick checks during market hours
6. **Notifications** - Set up once, get automated updates forever
7. **Cron Jobs** - Hands-free daily intelligence

---

## 🎉 You're All Set!

### Try It Now
```bash
# Launch the interactive shell
./trading_interactive.sh

# Or run a quick command
./quick_run.sh screener
```

### Next Steps
1. ✅ Run the interactive shell
2. ✅ Configure notifications (option 7)
3. ✅ Test notifications (option 8)
4. ✅ Try your first feature (option 1-6)
5. ✅ Read QUICK_START.md for more examples
6. ✅ Set up cron automation

---

**Happy Trading! 📈💰**

*For issues or questions, check INTERACTIVE_SHELL_GUIDE.md or view session logs in `logs/`*
