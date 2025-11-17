#!/bin/bash
# Quick script to check run.py status

PID=$(pgrep -f "run.py" | head -1)

if [ -z "$PID" ]; then
    echo "❌ run.py is not running"
    exit 1
fi

echo "📊 run.py Process Status:"
echo "PID: $PID"
ps -p $PID -o etime,state,command

echo ""
echo "📁 Open Files:"
lsof -p $PID 2>/dev/null | grep -E "REG|FIFO|PIPE" | head -10

echo ""
echo "💡 If it's stuck, you can:"
echo "   1. Check the terminal where you ran it for output"
echo "   2. Press Ctrl+C to stop it"
echo "   3. Or kill it: kill $PID"

