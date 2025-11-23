-- Documents Table Migration
-- Adds support for document storage and processing

CREATE TABLE IF NOT EXISTS documents (
    document_id BIGSERIAL PRIMARY KEY,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE SET NULL,
    workspace_id INTEGER, -- Will reference workspaces table (to be created)
    
    -- Document metadata
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    document_type VARCHAR(20) NOT NULL, -- 'pdf', 'html', 'txt', 'docx'
    mime_type VARCHAR(100),
    file_size_bytes BIGINT,
    
    -- Processing results
    processed_at TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    processing_error TEXT,
    
    -- Extracted content
    text_content TEXT, -- Full extracted text
    financial_data JSONB, -- Extracted financial metrics, tickers, etc.
    summary JSONB, -- Document summary
    
    -- Vector embedding for RAG
    embedding vector(768), -- nomic-embed-text dimension
    
    -- Metadata
    uploaded_by VARCHAR(100), -- User identifier
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- File storage (path or reference)
    storage_path TEXT, -- Path to stored file
    storage_type VARCHAR(20) DEFAULT 'local' -- 'local', 's3', etc.
);

CREATE INDEX IF NOT EXISTS idx_documents_ticker ON documents(ticker_id);
CREATE INDEX IF NOT EXISTS idx_documents_workspace ON documents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded ON documents(uploaded_at DESC);

-- Vector index for similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Document insights table (links documents to analyses)
CREATE TABLE IF NOT EXISTS document_insights (
    insight_id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(document_id) ON DELETE CASCADE,
    analysis_id BIGINT REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    ticker_id INTEGER REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    
    -- Insight details
    insight_type VARCHAR(50), -- 'metric', 'ticker_mention', 'filing_type', 'key_insight'
    insight_value TEXT,
    confidence_score DECIMAL(3,2), -- 0-1
    
    -- Context
    extracted_from_section TEXT, -- Which part of document
    relevance_score DECIMAL(3,2), -- How relevant to the analysis
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insights_document ON document_insights(document_id);
CREATE INDEX IF NOT EXISTS idx_insights_analysis ON document_insights(analysis_id);
CREATE INDEX IF NOT EXISTS idx_insights_ticker ON document_insights(ticker_id);

