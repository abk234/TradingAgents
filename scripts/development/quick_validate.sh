#!/bin/bash
# Quick Validation Script for TradingAgents

cd "$(dirname "$0")"
source venv/bin/activate

echo "🔍 Running TradingAgents Validation Suite..."
echo ""

scripts=(
    "validate_eddie_prerequisites.py:Database Prerequisites"
    "validate_system_data_flow.py:System Data Flow"
    "validate_data_accuracy.py:Data Accuracy"
    "validate_screener.py:Screener"
    "validate_agents.py:Agents"
    "test_caching_implementation.py:Caching"
)

for script_info in "${scripts[@]}"; do
    IFS=':' read -r script name <<< "$script_info"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python "$script"
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ $name: PASSED"
    else
        echo "❌ $name: FAILED (exit code: $exit_code)"
    fi
    echo ""
done

echo "✅ Validation suite complete!"
