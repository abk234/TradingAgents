# Agent Capability Monitoring System

## Overview

With **13 specialized agents** across **5 teams** in the TradingAgents system, monitoring individual agent capabilities is critical for:

1. **Performance Optimization** - Identify which agents are most effective
2. **Quality Assurance** - Detect agents with declining performance
3. **Cost Management** - Track LLM usage and costs per agent
4. **System Health** - Monitor agent availability and error rates
5. **Continuous Improvement** - Understand which agents contribute most to successful recommendations

## Why Monitor Agent Capabilities?

### The Challenge

Your TradingAgents system uses a sophisticated multi-agent architecture:

- **Analyst Team** (4 agents): Market, Social Media, News, Fundamentals
- **Research Team** (3 agents): Bull Researcher, Bear Researcher, Research Manager
- **Trading Team** (1 agent): Trader Agent
- **Risk Management** (4 agents): Aggressive, Conservative, Neutral, Portfolio Manager

**Total: 13 specialized agents**

Without monitoring, you can't answer questions like:
- Which agents are most valuable?
- Are any agents underperforming?
- Which agents contribute most to successful trades?
- Are we spending too much on LLM costs for certain agents?
- Is agent quality improving or declining over time?

### The Solution

The **Agent Capability Monitoring System** provides:

1. **Real-time Execution Tracking** - Track every agent run
2. **Performance Metrics** - Quality scores, execution times, success rates
3. **Contribution Analysis** - How much each agent influences final decisions
4. **Health Monitoring** - Detect inactive, unhealthy, or declining agents
5. **Cost Tracking** - LLM token usage and costs per agent
6. **Trend Analysis** - Identify improving or declining capabilities

---

## Architecture

### Database Schema

The monitoring system uses two main tables:

#### `agent_executions`
Tracks individual agent runs with:
- Execution timing (start, end, duration)
- Output quality metrics
- LLM usage (tokens, cost, model)
- Contribution scores
- Error tracking

#### `agent_capability_metrics`
Aggregated daily metrics:
- Success rates
- Average quality scores
- Performance trends
- Cost summaries

### Components

1. **AgentExecutionTracker** - Tracks agent runs in real-time
2. **AgentCapabilityMonitor** - Analyzes and reports on capabilities
3. **CLI Tool** - Command-line interface for monitoring
4. **Database Views** - Pre-computed comparisons and health status

---

## Usage

### 1. Track Agent Executions

Integrate tracking into your agent execution code:

```python
from tradingagents.monitoring import AgentExecutionTracker

# In your analysis code
tracker = AgentExecutionTracker(analysis_id=analysis_id)

with tracker.track_agent(
    agent_name='market_analyst',
    agent_team='analyst',
    llm_model='gpt-4o',
    llm_temperature=0.7
) as execution_id:
    # Your agent code here
    result = market_analyst.analyze(ticker)
    
    # Update with output metrics
    tracker.update_output_metrics(
        execution_id=execution_id,
        output_text=result.report,
        quality_score=85
    )
    
    # Update LLM metrics if applicable
    tracker.update_llm_metrics(
        execution_id=execution_id,
        tokens_used=1500,
        cost_usd=0.015
    )
    
    # Update contribution after final decision
    tracker.update_contribution(
        execution_id=execution_id,
        contribution_score=75,
        was_cited=True
    )
```

### 2. Generate Capability Reports

```bash
# Full capability report
python -m tradingagents.monitoring report --days 30 --output agent_report.txt

# Agent health status
python -m tradingagents.monitoring health

# Compare all agents
python -m tradingagents.monitoring compare --days 30

# Performance trends for specific agent
python -m tradingagents.monitoring trends --agent market_analyst --days 30

# Top performing agents
python -m tradingagents.monitoring top --metric quality_score --limit 5
```

### 3. Programmatic Access

```python
from tradingagents.monitoring import AgentCapabilityMonitor

monitor = AgentCapabilityMonitor()

# Get agent comparison
comparison = monitor.get_agent_comparison(days_back=30)

# Get health status
health = monitor.get_agent_health_status()

# Get performance trends
trends = monitor.get_agent_performance_trends('market_analyst', days_back=30)

# Get top performers
top_agents = monitor.get_top_performers(metric='quality_score', limit=5)

# Comprehensive summary
summary = monitor.get_agent_capabilities_summary()
```

---

## Metrics Tracked

### Execution Metrics
- **Duration** - How long each agent takes to execute
- **Success Rate** - Percentage of successful executions
- **Error Rate** - Frequency of errors or failures
- **Output Quality** - Calculated quality score (0-100)

### Contribution Metrics
- **Contribution Score** - How much agent influenced final decision (0-100)
- **Citation Rate** - Percentage of times agent output was cited in final report
- **Influence** - Whether agent's insights were used

### Cost Metrics
- **LLM Tokens** - Token usage per execution
- **Cost per Execution** - USD cost per agent run
- **Total Cost** - Aggregate cost over time period

### Quality Metrics
- **Output Completeness** - Length and structure of output
- **Data Presence** - Whether output contains relevant data
- **Quality Trend** - Improving, stable, or declining

---

## Health Status

Agents are classified into health statuses:

- **HEALTHY** ✅ - Normal operation, good quality scores
- **INACTIVE** ⏸️ - No executions in last 7 days
- **UNHEALTHY** ⚠️ - High error rate (>10%)
- **POOR_QUALITY** 📉 - Low quality scores (<50)

---

## Integration Guide

### Step 1: Run Database Migration

```bash
psql -d tradingagents -f scripts/migrations/013_add_agent_capability_monitoring.sql
```

### Step 2: Integrate Tracking

Add tracking to your agent execution code. The easiest place is in `tradingagents/graph/trading_graph.py` where agents are executed.

### Step 3: Set Up Monitoring

Create a cron job or scheduled task to generate reports:

```bash
# Daily capability report
0 9 * * * cd /path/to/TradingAgents && python -m tradingagents.monitoring report --days 7 --output logs/agent_capability_$(date +\%Y\%m\%d).txt
```

### Step 4: Review and Act

- Review reports weekly
- Investigate agents with declining trends
- Optimize high-cost agents
- Consider disabling or improving underperforming agents

---

## Example Report Output

```
================================================================================
AGENT CAPABILITY MONITORING REPORT
================================================================================
Analysis Period: Last 30 days
Generated: 2025-11-17 10:30:00

📊 OVERALL SUMMARY
--------------------------------------------------------------------------------
Total Agents: 13
Total Executions (30d): 1,247
Total Cost (30d): $45.23
Average Quality Score: 72.3/100

Agents by Team:
  • Analyst: 4 agents
  • Research: 3 agents
  • Trading: 1 agents
  • Risk Management: 4 agents
  • Manager: 1 agents

🏥 AGENT HEALTH STATUS
--------------------------------------------------------------------------------
Healthy: 11/13

⚠️  Issues Detected:
  • social_media_analyst (analyst): POOR_QUALITY - Low quality score: 45.2/100
  • bear_researcher (research): INACTIVE - No executions in last 7 days

🏆 TOP PERFORMERS
--------------------------------------------------------------------------------

By Quality Score:
  1. fundamentals_analyst (analyst): Quality 89.2, 156 executions
  2. market_analyst (analyst): Quality 85.7, 198 executions
  3. risk_manager (risk_mgmt): Quality 82.1, 145 executions

By Contribution Score:
  1. research_manager (research): Contribution 88.5, Citation Rate 92.3%
  2. risk_manager (risk_mgmt): Contribution 85.2, Citation Rate 89.1%
  3. trader_agent (trading): Contribution 81.7, Citation Rate 87.5%

By Speed (Fastest):
  1. news_analyst (analyst): 3.45s avg
  2. social_media_analyst (analyst): 4.12s avg
  3. market_analyst (analyst): 8.23s avg
```

---

## Recommendations

### High Priority

1. **Integrate Tracking** - Add `AgentExecutionTracker` to all agent execution points
2. **Set Up Monitoring** - Create daily/weekly reports
3. **Establish Baselines** - Run for 2-4 weeks to establish baseline metrics
4. **Set Alerts** - Alert on unhealthy agents or declining trends

### Medium Priority

5. **Cost Optimization** - Identify high-cost agents and optimize
6. **Quality Improvement** - Focus on agents with low quality scores
7. **Performance Tuning** - Optimize slow agents
8. **Documentation** - Document agent capabilities and expected performance

### Low Priority

9. **Automated Actions** - Auto-disable agents with persistent issues
10. **A/B Testing** - Test different prompts/models for underperforming agents
11. **Dashboards** - Create visual dashboards (Grafana, etc.)
12. **ML Integration** - Use metrics to train models for agent selection

---

## Benefits

### Immediate Benefits
- **Visibility** - Know which agents are working well
- **Problem Detection** - Quickly identify issues
- **Cost Control** - Track and optimize LLM spending

### Long-term Benefits
- **Continuous Improvement** - Data-driven agent optimization
- **Resource Allocation** - Focus development on high-impact agents
- **Quality Assurance** - Maintain consistent agent performance
- **Strategic Planning** - Make informed decisions about agent architecture

---

## Next Steps

1. ✅ **Database Migration** - Run migration script
2. ✅ **Install Monitoring** - Code is ready to use
3. ⏳ **Integrate Tracking** - Add tracking to agent execution code
4. ⏳ **Generate First Report** - Run initial capability report
5. ⏳ **Establish Baselines** - Collect 2-4 weeks of data
6. ⏳ **Set Up Alerts** - Configure monitoring alerts
7. ⏳ **Optimize** - Use insights to improve agent performance

---

## Questions?

For questions or issues:
- Check the CLI help: `python -m tradingagents.monitoring --help`
- Review the code: `tradingagents/monitoring/`
- See examples in this document

---

**Last Updated:** 2025-11-17

