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
}

export const api = new ApiClient(API_BASE_URL)
