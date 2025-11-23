-- Workspaces Table Migration
-- Adds support for workspace/organization management

CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Workspace settings
    default_ticker_list INTEGER[], -- Array of ticker_ids for default watchlist
    analysis_preferences JSONB, -- User preferences for analysis
    
    -- Metadata
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_workspaces_active ON workspaces(is_active);
CREATE INDEX IF NOT EXISTS idx_workspaces_default ON workspaces(is_default);

-- Add workspace_id to existing tables
ALTER TABLE tickers ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE SET NULL;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE SET NULL;
ALTER TABLE daily_scans ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE SET NULL;
ALTER TABLE portfolio_actions ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(workspace_id) ON DELETE SET NULL;

-- Create indexes for workspace filtering
CREATE INDEX IF NOT EXISTS idx_tickers_workspace ON tickers(workspace_id);
CREATE INDEX IF NOT EXISTS idx_analyses_workspace ON analyses(workspace_id);
CREATE INDEX IF NOT EXISTS idx_scans_workspace ON daily_scans(workspace_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_workspace ON portfolio_actions(workspace_id);

-- Create default workspace
INSERT INTO workspaces (name, description, is_default, is_active)
VALUES ('Default Workspace', 'Default workspace for all analyses', true, true)
ON CONFLICT DO NOTHING;

