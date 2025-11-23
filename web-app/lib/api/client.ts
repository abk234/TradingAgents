/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

import {
    ChatRequest,
    ChatResponse,
    AnalysisRequest,
    AnalysisResponse,
    FeedbackRequest,
    AgentState,
    PromptAnalytics,
    HistoricalResponse,
    PortfolioPerformance,
    RiskAnalysisRequest,
    RiskAnalysisResponse
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8005"

class ApiClient {
    private baseUrl: string

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl
    }

    private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`

        // Get API key from localStorage if available (client-side only)
        let apiKey = "";
        if (typeof window !== "undefined") {
            apiKey = localStorage.getItem("api_key") || "";
        }

        const headers: Record<string, string> = {
            "Content-Type": "application/json",
            ...options.headers as Record<string, string>,
        }

        if (apiKey) {
            headers["X-API-Key"] = apiKey;
        }

        try {
            const response = await fetch(url, { ...options, headers })

            if (!response.ok) {
                const errorText = await response.text()
                throw new Error(`API Error ${response.status}: ${errorText}`)
            }

            return response.json()
        } catch (error) {
            console.error(`API Request failed for ${endpoint}:`, error)
            throw error
        }
    }

    // Chat Endpoints
    async chat(request: ChatRequest): Promise<ChatResponse> {
        return this.request<ChatResponse>("/chat", {
            method: "POST",
            body: JSON.stringify(request),
        })
    }

    // Analysis Endpoints
    async analyze(request: AnalysisRequest): Promise<AnalysisResponse> {
        return this.request<AnalysisResponse>("/analyze", {
            method: "POST",
            body: JSON.stringify(request),
        })
    }

    // Feedback Endpoints
    async sendFeedback(request: FeedbackRequest): Promise<{ status: string; message: string }> {
        return this.request("/feedback", {
            method: "POST",
            body: JSON.stringify(request),
        })
    }

    // State & Analytics
    async getState(): Promise<AgentState> {
        return this.request<AgentState>("/state")
    }

    async getPromptAnalytics(days: number = 30): Promise<PromptAnalytics> {
        return this.request<PromptAnalytics>(`/analytics/prompts?days=${days}`)
    }

    // Historical Endpoints
    async getHistoricalAnalyses(limit: number = 100, offset: number = 0): Promise<HistoricalResponse> {
        return this.request<HistoricalResponse>(`/analytics/history?limit=${limit}&offset=${offset}`)
    }

    // Portfolio Performance
    async getPortfolioPerformance(): Promise<PortfolioPerformance> {
        return this.request<PortfolioPerformance>("/analytics/portfolio/performance")
    }

    // Risk Analysis
    async analyzeRisk(request: RiskAnalysisRequest): Promise<RiskAnalysisResponse> {
        return this.request<RiskAnalysisResponse>("/analytics/risk", {
            method: "POST",
            body: JSON.stringify(request),
        })
    }

    // Voice Endpoints
    async synthesizeVoice(text: string, tone: string = "professional"): Promise<Blob> {
        // Use query parameters like DevToolsView does (proven to work)
        const apiKey = typeof window !== "undefined" ? localStorage.getItem("api_key") || "" : ""
        const url = `${this.baseUrl}/voice/synthesize?text=${encodeURIComponent(text)}&tone=${encodeURIComponent(tone)}&return_base64=true`
        
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(apiKey ? { "X-API-Key": apiKey } : {})
            }
        })

        if (!response.ok) {
            const errorText = await response.text()
            throw new Error(`Failed to synthesize voice: ${errorText}`)
        }

        // Parse JSON response with base64 audio
        const data = await response.json()
        if (data.audio_base64) {
            // Convert base64 to blob
            try {
                const binaryString = atob(data.audio_base64)
                const bytes = new Uint8Array(binaryString.length)
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i)
                }
                
                // Verify RIFF header before creating blob
                if (bytes.length >= 4) {
                    const header = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3])
                    if (header !== "RIFF") {
                        console.error("Invalid audio header:", header, "Expected: RIFF")
                        throw new Error("Invalid audio format: file does not start with RIFF header")
                    }
                }
                
                return new Blob([bytes], { type: "audio/wav" })
            } catch (error) {
                console.error("Error converting base64 to blob:", error)
                throw new Error(`Failed to process audio data: ${error instanceof Error ? error.message : String(error)}`)
            }
        } else {
            throw new Error("No audio data in response")
        }
    }

    // Helper for streaming chat
    getStreamUrl(): string {
        return `${this.baseUrl}/chat/stream`
    }

    // =============================================================================
    // MCP Endpoints
    // =============================================================================
    
    async getMCPCapabilities() {
        return this.request("/mcp/capabilities")
    }

    async listMCPTools() {
        return this.request<{ tools: any[], count: number }>("/mcp/tools")
    }

    async getMCPCapabilities() {
        return this.request("/mcp/capabilities")
    }

    async callMCPTool(toolName: string, toolArguments: Record<string, any>) {
        return this.request(`/mcp/tools/${toolName}`, {
            method: "POST",
            body: JSON.stringify({ arguments: toolArguments }),
        })
    }

    // =============================================================================
    // Document Endpoints
    // =============================================================================
    
    async uploadDocument(file: File, ticker?: string, workspaceId?: number) {
        const formData = new FormData()
        formData.append("file", file)
        if (ticker) formData.append("ticker", ticker)
        if (workspaceId) formData.append("workspace_id", workspaceId.toString())

        const apiKey = typeof window !== "undefined" ? localStorage.getItem("api_key") || "" : ""
        const headers: Record<string, string> = {}
        if (apiKey) {
            headers["X-API-Key"] = apiKey
        }

        const response = await fetch(`${this.baseUrl}/documents/upload`, {
            method: "POST",
            headers,
            body: formData,
        })

        if (!response.ok) {
            const errorText = await response.text()
            throw new Error(`API Error ${response.status}: ${errorText}`)
        }

        return response.json()
    }

    async listDocuments(ticker?: string, workspaceId?: number, documentType?: string, status?: string) {
        const params = new URLSearchParams()
        if (ticker) params.append("ticker", ticker)
        if (workspaceId) params.append("workspace_id", workspaceId.toString())
        if (documentType) params.append("document_type", documentType)
        if (status) params.append("status", status)

        return this.request<{ documents: any[], count: number }>(`/documents?${params.toString()}`)
    }

    async getDocument(documentId: number) {
        return this.request(`/documents/${documentId}`)
    }

    async getDocumentInsights(documentId: number, analysisId?: number, tickerId?: number) {
        const params = new URLSearchParams()
        if (analysisId) params.append("analysis_id", analysisId.toString())
        if (tickerId) params.append("ticker_id", tickerId.toString())

        return this.request<{ insights: any[], count: number }>(`/documents/${documentId}/insights?${params.toString()}`)
    }

    async deleteDocument(documentId: number) {
        return this.request(`/documents/${documentId}`, {
            method: "DELETE",
        })
    }

    // =============================================================================
    // Workspace Endpoints
    // =============================================================================
    
    async createWorkspace(data: { name: string; description?: string; is_default?: boolean }) {
        return this.request("/workspaces", {
            method: "POST",
            body: JSON.stringify(data),
        })
    }

    async listWorkspaces(activeOnly: boolean = true) {
        return this.request<{ workspaces: any[], count: number }>(`/workspaces?active_only=${activeOnly}`)
    }

    async getDefaultWorkspace() {
        return this.request("/workspaces/default")
    }

    async getWorkspace(workspaceId: number) {
        return this.request(`/workspaces/${workspaceId}`)
    }

    async updateWorkspace(workspaceId: number, data: Partial<{ name: string; description: string; is_default: boolean; is_active: boolean }>) {
        return this.request(`/workspaces/${workspaceId}`, {
            method: "PUT",
            body: JSON.stringify(data),
        })
    }

    async deleteWorkspace(workspaceId: number, softDelete: boolean = true) {
        return this.request(`/workspaces/${workspaceId}?soft_delete=${softDelete}`, {
            method: "DELETE",
        })
    }

    async getWorkspaceTickers(workspaceId: number) {
        return this.request<{ tickers: any[], count: number }>(`/workspaces/${workspaceId}/tickers`)
    }

    async getWorkspaceAnalyses(workspaceId: number, limit: number = 50, offset: number = 0) {
        return this.request<{ analyses: any[], count: number }>(`/workspaces/${workspaceId}/analyses?limit=${limit}&offset=${offset}`)
    }
}

export const api = new ApiClient(API_BASE_URL)
