export type Role = "user" | "assistant" | "system"

export interface Message {
    role: Role
    content: string
    timestamp?: string
    id?: string
}

export interface ChatRequest {
    message: string
    conversation_history: Message[]
    conversation_id?: string
    prompt_type?: string
    prompt_id?: string
}

export interface ChatResponse {
    response: string
    conversation_id: string
    timestamp: string
    metadata?: Record<string, any>
}

export interface AnalysisRequest {
    ticker: string
    risk_level?: string
    investment_style?: string
    analysts?: string[]
}

export interface AnalysisResponse {
    ticker: string
    decision: string
    confidence: number
    summary: string
    details: Record<string, any>
    timestamp: string
}

export interface FeedbackRequest {
    conversation_id: string
    message_id?: string
    rating: number
    comment?: string
    correction?: string
}

export interface UserPreference {
    risk_tolerance: string
    investment_horizon: string
    favorite_sectors: string[]
    excluded_sectors: string[]
}

// State Types for UI Visualization
export interface AgentState {
    state: "idle" | "listening" | "processing" | "speaking" | "error" | "validating"
    confidence: {
        data_freshness: number
        math_verification: number
        ai_confidence: number
        overall: number
    }
    current_ticker?: string
    active_tools: string[]
    system_health: "HEALTHY" | "WARNING" | "CRITICAL"
    timestamp?: string
    message?: string
}

export interface PromptAnalytics {
    total_prompts: number
    popular_categories: Record<string, number>
    avg_rating: number
    daily_usage: Record<string, number>
}
