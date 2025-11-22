/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState } from "react"
import { Calendar, Search, SlidersHorizontal, Play, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { useAnalysis } from "@/lib/hooks/useAnalysis"
import { AnalysisResults } from "./AnalysisResults"
import { cn } from "@/lib/utils"

export function DirectAnalysis() {
    const {
        messages,
        isLoading,
        isThinking,
        activeTools,
        thinkingMessage,
        sendMessage
    } = useAnalysis()

    const [ticker, setTicker] = useState("")
    const [analysts, setAnalysts] = useState({
        market: true,
        social: true,
        news: true,
        fundamentals: true
    })
    const [showResults, setShowResults] = useState(false)

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!ticker.trim()) return

        setShowResults(true)

        const selectedAnalysts = Object.entries(analysts)
            .filter(([_, selected]) => selected)
            .map(([name]) => name)
            .join(", ")

        const prompt = `Perform a comprehensive analysis of ${ticker}. 
    Enable the following analyst agents: ${selectedAnalysts}.
    Provide a detailed report including executive summary, analyst breakdowns, investment debate, and a final buy/sell/hold recommendation.`

        await sendMessage(prompt, { promptType: "direct_analysis", promptId: "custom" })
    }

    // Extract the last assistant message as the result
    const lastMessage = messages[messages.length - 1]
    const analysisData = lastMessage?.role === "assistant" && !isThinking && lastMessage.content
        ? {
            summary: lastMessage.content.split("## Analyst Reports")[0], // Naive parsing for demo
            analysts: {
                "Full Report": lastMessage.content // Just show full content for now
            },
            decision: lastMessage.content.includes("BUY") ? "BUY" : lastMessage.content.includes("SELL") ? "SELL" : "HOLD",
            recommendation: "Based on the analysis above."
        }
        : null

    return (
        <div className="h-full flex flex-col gap-6">
            {/* Input Section */}
            <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <form onSubmit={handleAnalyze} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <Label htmlFor="ticker">Stock Ticker</Label>
                            <div className="relative">
                                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="ticker"
                                    placeholder="e.g. NVDA, AAPL, TSLA"
                                    className="pl-10 h-12 text-lg font-mono uppercase"
                                    value={ticker}
                                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Analysis Date</Label>
                            <div className="relative">
                                <Calendar className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                <Input
                                    type="date"
                                    className="pl-10 h-12"
                                    defaultValue={new Date().toISOString().split('T')[0]}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <Label className="flex items-center gap-2">
                            <SlidersHorizontal className="w-4 h-4" />
                            Active Analysts
                        </Label>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {Object.entries(analysts).map(([id, checked]) => (
                                <div key={id} className="flex items-center space-x-2 border border-border rounded-lg p-3 hover:bg-secondary/50 transition-colors">
                                    <Checkbox
                                        id={id}
                                        checked={checked}
                                        onCheckedChange={(c) => setAnalysts(prev => ({ ...prev, [id]: !!c }))}
                                        disabled={isLoading}
                                    />
                                    <Label htmlFor={id} className="capitalize cursor-pointer flex-1">{id} Analyst</Label>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex justify-end pt-2">
                        <Button
                            type="submit"
                            size="lg"
                            className="w-full md:w-auto gap-2 font-semibold"
                            disabled={isLoading || !ticker.trim()}
                        >
                            {isLoading ? (
                                <>Running Analysis...</>
                            ) : (
                                <>
                                    <Play className="w-4 h-4" /> Run Analysis
                                </>
                            )}
                        </Button>
                    </div>
                </form>
            </div>

            {/* Results Section */}
            {(showResults || isLoading) && (
                <div className="flex-1 min-h-0">
                    {isLoading ? (
                        <div className="h-full flex flex-col items-center justify-center bg-card border border-border rounded-xl p-8 space-y-6">
                            <div className="relative w-20 h-20">
                                <div className="absolute inset-0 border-4 border-secondary rounded-full"></div>
                                <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin"></div>
                            </div>
                            <div className="text-center space-y-2">
                                <h3 className="text-xl font-semibold animate-pulse">{thinkingMessage || "Initializing agents..."}</h3>
                                <p className="text-muted-foreground max-w-md mx-auto">
                                    Eddie is coordinating the multi-agent system to analyze {ticker}. This usually takes 1-2 minutes.
                                </p>
                            </div>

                            {activeTools.length > 0 && (
                                <div className="w-full max-w-md bg-secondary/30 rounded-lg p-4 space-y-2">
                                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Active Operations</div>
                                    {activeTools.map((tool, i) => (
                                        <div key={i} className="flex items-center gap-3 text-sm">
                                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                            <span className="font-mono text-foreground">{tool}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : analysisData ? (
                        <AnalysisResults
                            ticker={ticker}
                            data={analysisData}
                        />
                    ) : null}
                </div>
            )}
        </div>
    )
}
