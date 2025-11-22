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
        const response = await fetch(`${this.baseUrl}/voice/synthesize`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(typeof window !== "undefined" && localStorage.getItem("api_key")
                    ? { "X-API-Key": localStorage.getItem("api_key") || "" }
                    : {})
            },
            body: JSON.stringify({ text, tone, return_base64: false }),
        })

        if (!response.ok) {
            throw new Error("Failed to synthesize voice")
        }

        return response.blob()
    }

    // Helper for streaming chat
    getStreamUrl(): string {
        return `${this.baseUrl}/chat/stream`
    }
}

export const api = new ApiClient(API_BASE_URL)
