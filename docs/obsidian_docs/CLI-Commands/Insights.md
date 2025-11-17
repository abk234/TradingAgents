# Insights CLI - Alerts & Notifications

## Overview

Get daily market insights, price alerts, and notifications across multiple channels.

## Commands

### Morning Briefing
```bash
python -m tradingagents.insights morning
```

Complete morning routine:
- Daily market digest
- Price alerts
- RSI alerts
- Summary of opportunities

### Daily Digest
```bash
python -m tradingagents.insights digest
```

**Includes:**
- Market summary
- Top opportunities from screener
- Recent analyses
- Portfolio updates

**Options:**
- `--date`: Specific date (YYYY-MM-DD)
- `--output`: Save to file

### Check Alerts
```bash
python -m tradingagents.insights alerts
```

**Alert Types:**
- Price alerts (entry/exit/stop-loss)
- RSI alerts (oversold/overbought)
- Volume alerts
- Technical indicator alerts

**Options:**
- `--output`: Save to file

### Quick Summary
```bash
python -m tradingagents.insights summary
```

Quick overview of:
- Today's opportunities
- Active alerts
- Portfolio status

### Send Test Notification
```bash
python -m tradingagents.insights notify --message "Test alert" --title "Test"
```

**Options:**
- `--message`: Notification message (required)
- `--title`: Notification title
- `--priority`: URGENT, HIGH, MEDIUM, LOW
- `--channels`: Comma-separated (terminal,log,email,webhook)

## Notification Channels

### Terminal
Outputs directly to terminal (default).

### Log File
Writes to log file in `logs/` directory.

### Email
Sends via SMTP (requires configuration).

### Webhook
POSTs to configured webhook URL.

## Alert Configuration

Alerts are configured in the database:
- Price alerts: Set entry/exit/stop-loss levels
- RSI alerts: Configure oversold/overbought thresholds
- Volume alerts: Set volume spike thresholds

---

**Next**: [[Dividends|Dividends CLI]] | [[Main-CLI|Main CLI]]

