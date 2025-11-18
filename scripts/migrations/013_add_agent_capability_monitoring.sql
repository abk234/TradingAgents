-- Migration 013: Agent Capability Monitoring
-- Tracks individual agent performance and capabilities
-- Date: 2025-11-17

-- ============================================================================
-- AGENT_EXECUTIONS TABLE - Track individual agent runs
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_executions (
    execution_id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    agent_name VARCHAR(50) NOT NULL, -- e.g., 'market_analyst', 'bull_researcher'
    agent_team VARCHAR(30) NOT NULL, -- 'analyst', 'research', 'trading', 'risk_mgmt', 'manager'
    
    -- Execution metrics
    execution_start_time TIMESTAMP NOT NULL,
    execution_end_time TIMESTAMP,
    duration_seconds DECIMAL(8,3), -- Execution time
    
    -- Agent output quality metrics
    output_length INTEGER, -- Character count of output
    output_quality_score INTEGER, -- 0-100, calculated based on completeness
    has_errors BOOLEAN DEFAULT false,
    error_message TEXT,
    
    -- LLM-specific metrics (if applicable)
    llm_model VARCHAR(50),
    llm_tokens_used INTEGER,
    llm_cost_usd DECIMAL(10,6),
    llm_temperature DECIMAL(3,2),
    
    -- Agent-specific metrics (JSONB for flexibility)
    agent_metrics JSONB, -- e.g., {"indicators_analyzed": 5, "data_sources": ["yfinance", "alpha_vantage"]}
    
    -- Contribution to final decision
    contribution_score INTEGER, -- 0-100, how much this agent influenced final decision
    was_cited_in_final_report BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_executions_analysis ON agent_executions(analysis_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent ON agent_executions(agent_name, execution_start_time DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_team ON agent_executions(agent_team);
CREATE INDEX IF NOT EXISTS idx_agent_executions_date ON agent_executions(execution_start_time DESC);

-- ============================================================================
-- AGENT_CAPABILITY_METRICS TABLE - Aggregated agent performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_capability_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    
    -- Performance metrics
    total_executions INTEGER DEFAULT 0,
    successful_executions INTEGER DEFAULT 0,
    failed_executions INTEGER DEFAULT 0,
    avg_duration_seconds DECIMAL(8,3),
    avg_quality_score DECIMAL(5,2),
    
    -- Success rate
    success_rate DECIMAL(5,2), -- Percentage
    
    -- Contribution metrics
    avg_contribution_score DECIMAL(5,2),
    citation_rate DECIMAL(5,2), -- % of times cited in final report
    
    -- Cost metrics (if applicable)
    total_tokens_used BIGINT,
    total_cost_usd DECIMAL(10,2),
    avg_cost_per_execution DECIMAL(10,6),
    
    -- Capability trends
    quality_trend VARCHAR(10), -- 'IMPROVING', 'STABLE', 'DECLINING'
    performance_trend VARCHAR(10), -- 'IMPROVING', 'STABLE', 'DECLINING'
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(agent_name, metric_date)
);

CREATE INDEX IF NOT EXISTS idx_agent_metrics_agent ON agent_capability_metrics(agent_name, metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_date ON agent_capability_metrics(metric_date DESC);

-- ============================================================================
-- AGENT_COMPARISON_VIEW - Compare agents side-by-side
-- ============================================================================
CREATE OR REPLACE VIEW v_agent_comparison AS
SELECT 
    agent_name,
    agent_team,
    COUNT(*) as total_executions,
    SUM(CASE WHEN has_errors = false THEN 1 ELSE 0 END) as successful_executions,
    ROUND(AVG(duration_seconds), 2) as avg_duration_seconds,
    ROUND(AVG(output_quality_score), 2) as avg_quality_score,
    ROUND(AVG(contribution_score), 2) as avg_contribution_score,
    ROUND(SUM(CASE WHEN was_cited_in_final_report THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) as citation_rate_pct,
    ROUND(SUM(llm_cost_usd), 2) as total_cost_usd,
    ROUND(AVG(llm_cost_usd), 6) as avg_cost_per_execution
FROM agent_executions
WHERE execution_start_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY agent_name, agent_team
ORDER BY avg_quality_score DESC;

-- ============================================================================
-- AGENT_HEALTH_VIEW - Agent health and availability
-- ============================================================================
CREATE OR REPLACE VIEW v_agent_health AS
SELECT 
    agent_name,
    agent_team,
    COUNT(*) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '7 days') as executions_last_7_days,
    COUNT(*) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '30 days') as executions_last_30_days,
    ROUND(AVG(duration_seconds) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '7 days'), 2) as avg_duration_last_7_days,
    ROUND(AVG(output_quality_score) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '7 days'), 2) as avg_quality_last_7_days,
    SUM(CASE WHEN has_errors = true AND execution_start_time >= CURRENT_DATE - INTERVAL '7 days' THEN 1 ELSE 0 END) as errors_last_7_days,
    CASE 
        WHEN COUNT(*) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '7 days') = 0 THEN 'INACTIVE'
        WHEN SUM(CASE WHEN has_errors = true AND execution_start_time >= CURRENT_DATE - INTERVAL '7 days' THEN 1 ELSE 0 END)::NUMERIC / 
             NULLIF(COUNT(*) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '7 days'), 0) > 0.1 THEN 'UNHEALTHY'
        WHEN AVG(output_quality_score) FILTER (WHERE execution_start_time >= CURRENT_DATE - INTERVAL '7 days') < 50 THEN 'POOR_QUALITY'
        ELSE 'HEALTHY'
    END as health_status
FROM agent_executions
GROUP BY agent_name, agent_team
ORDER BY agent_team, agent_name;

-- ============================================================================
-- TRIGGER: Auto-update agent_capability_metrics on insert
-- ============================================================================
CREATE OR REPLACE FUNCTION update_agent_capability_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update daily metrics for this agent
    INSERT INTO agent_capability_metrics (
        agent_name,
        metric_date,
        total_executions,
        successful_executions,
        failed_executions,
        avg_duration_seconds,
        avg_quality_score,
        success_rate,
        avg_contribution_score,
        citation_rate,
        total_tokens_used,
        total_cost_usd,
        avg_cost_per_execution
    )
    SELECT 
        NEW.agent_name,
        DATE(NEW.execution_start_time),
        COUNT(*),
        SUM(CASE WHEN has_errors = false THEN 1 ELSE 0 END),
        SUM(CASE WHEN has_errors = true THEN 1 ELSE 0 END),
        AVG(duration_seconds),
        AVG(output_quality_score),
        ROUND(SUM(CASE WHEN has_errors = false THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2),
        AVG(contribution_score),
        ROUND(SUM(CASE WHEN was_cited_in_final_report THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2),
        SUM(llm_tokens_used),
        SUM(llm_cost_usd),
        AVG(llm_cost_usd)
    FROM agent_executions
    WHERE agent_name = NEW.agent_name
      AND DATE(execution_start_time) = DATE(NEW.execution_start_time)
    GROUP BY agent_name, DATE(execution_start_time)
    ON CONFLICT (agent_name, metric_date) DO UPDATE
    SET 
        total_executions = EXCLUDED.total_executions,
        successful_executions = EXCLUDED.successful_executions,
        failed_executions = EXCLUDED.failed_executions,
        avg_duration_seconds = EXCLUDED.avg_duration_seconds,
        avg_quality_score = EXCLUDED.avg_quality_score,
        success_rate = EXCLUDED.success_rate,
        avg_contribution_score = EXCLUDED.avg_contribution_score,
        citation_rate = EXCLUDED.citation_rate,
        total_tokens_used = EXCLUDED.total_tokens_used,
        total_cost_usd = EXCLUDED.total_cost_usd,
        avg_cost_per_execution = EXCLUDED.avg_cost_per_execution,
        updated_at = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_agent_metrics
AFTER INSERT ON agent_executions
FOR EACH ROW
EXECUTE FUNCTION update_agent_capability_metrics();

COMMENT ON TABLE agent_executions IS 'Tracks individual agent execution metrics for capability monitoring';
COMMENT ON TABLE agent_capability_metrics IS 'Aggregated daily metrics for agent performance tracking';
COMMENT ON VIEW v_agent_comparison IS 'Side-by-side comparison of agent performance over last 30 days';
COMMENT ON VIEW v_agent_health IS 'Current health status of all agents based on recent performance';

