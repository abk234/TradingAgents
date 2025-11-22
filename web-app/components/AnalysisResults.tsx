/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState, useRef, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { motion, AnimatePresence } from "framer-motion"
import {
    FileText,
    TrendingUp,
    TrendingDown,
    Activity,
    Scale,
    CheckCircle2,
    Download,
    Share2,
    Volume2,
    VolumeX
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { StockChart } from "./StockChart"
import { api } from "@/lib/api/client"

interface AnalysisData {
    summary?: string
    analysts?: Record<string, string>
    debate?: {
        bullish?: string
        bearish?: string
    }
    decision?: string
    recommendation?: string
}

interface AnalysisResultsProps {
    ticker: string
    data: AnalysisData
    isLoading?: boolean
}

export function AnalysisResults({ ticker, data, isLoading }: AnalysisResultsProps) {
    const [activeTab, setActiveTab] = useState("summary")
    const [isPlayingVoice, setIsPlayingVoice] = useState(false)
    const audioRef = useRef<HTMLAudioElement | null>(null)
    const audioUrlRef = useRef<string | null>(null)

    // Cleanup audio on unmount
    useEffect(() => {
        return () => {
            if (audioRef.current) {
                audioRef.current.pause()
                audioRef.current.src = ""
            }
            if (audioUrlRef.current) {
                URL.revokeObjectURL(audioUrlRef.current)
            }
        }
    }, [])

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-64 space-y-4">
                <div className="relative w-16 h-16">
                    <div className="absolute inset-0 border-4 border-secondary rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin"></div>
                </div>
                <p className="text-muted-foreground animate-pulse">Generating comprehensive analysis...</p>
            </div>
        )
    }

    if (!data) return null

    const tabs = [
        { id: "summary", label: "Executive Summary", icon: FileText },
        { id: "analysts", label: "Analyst Reports", icon: Activity },
        { id: "debate", label: "Investment Debate", icon: Scale },
        { id: "decision", label: "Final Decision", icon: CheckCircle2 },
    ]

    // Mock chart data for visualization (replace with real data later)
    const mockChartData = Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
        price: 150 + Math.random() * 20 - 10
    }))

    const handleExportJSON = () => {
        const dataStr = JSON.stringify(data, null, 2)
        const blob = new Blob([dataStr], { type: "application/json" })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = `${ticker}_analysis_${new Date().toISOString().split('T')[0]}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    }

    const handlePrint = () => {
        window.print()
    }

    const handlePlayVoice = async () => {
        if (isPlayingVoice && audioRef.current) {
            // Stop playback
            audioRef.current.pause()
            audioRef.current.currentTime = 0
            setIsPlayingVoice(false)
            return
        }

        try {
            setIsPlayingVoice(true)

            // Get the text content for the current tab
            let textToSpeak = ""
            switch (activeTab) {
                case "summary":
                    textToSpeak = `Executive Summary for ${ticker}. ${data.summary || "No summary available."}`
                    break
                case "analysts":
                    textToSpeak = `Analyst Reports for ${ticker}. `
                    Object.entries(data.analysts || {}).forEach(([role, content]) => {
                        textToSpeak += `${role.replace("_", " ")} Analyst: ${content}. `
                    })
                    break
                case "debate":
                    textToSpeak = `Investment Debate for ${ticker}. `
                    if (data.debate?.bullish) {
                        textToSpeak += `Bullish Case: ${data.debate.bullish}. `
                    }
                    if (data.debate?.bearish) {
                        textToSpeak += `Bearish Case: ${data.debate.bearish}. `
                    }
                    break
                case "decision":
                    textToSpeak = `Final Decision for ${ticker}. Recommendation: ${data.decision || "HOLD"}. ${data.recommendation || "Based on the analysis above."}`
                    break
                default:
                    textToSpeak = `Analysis for ${ticker}. ${data.summary || "Analysis complete."}`
            }

            // Synthesize speech
            const audioBlob = await api.synthesizeVoice(textToSpeak, "professional")
            
            // Verify blob is valid before creating URL
            if (!audioBlob || audioBlob.size === 0) {
                throw new Error("Invalid audio blob received")
            }
            
            const audioUrl = URL.createObjectURL(audioBlob)
            audioUrlRef.current = audioUrl

            const audio = new Audio(audioUrl)
            audioRef.current = audio

            audio.onended = () => {
                setIsPlayingVoice(false)
                URL.revokeObjectURL(audioUrl)
                audioUrlRef.current = null
            }

            audio.onerror = (e) => {
                console.error("Audio playback error:", e)
                setIsPlayingVoice(false)
                URL.revokeObjectURL(audioUrl)
                audioUrlRef.current = null
            }

            await audio.play()
        } catch (error) {
            console.error("Error playing voice:", error)
            setIsPlayingVoice(false)
            const errorMessage = error instanceof Error ? error.message : String(error)
            if (errorMessage.includes("RIFF")) {
                console.error("Audio format error - this should not happen with the fixed API client")
            }
        }
    }

    return (
        <div className="space-y-6 print:space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between print:hidden">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        {ticker} Analysis Report
                        <span className="text-sm font-normal text-muted-foreground bg-secondary px-2 py-1 rounded-md">
                            {new Date().toLocaleDateString()}
                        </span>
                    </h2>
                </div>
                <div className="flex gap-2">
                    <Button 
                        variant="outline" 
                        size="sm" 
                        className="gap-2" 
                        onClick={handlePlayVoice}
                    >
                        {isPlayingVoice ? (
                            <>
                                <VolumeX className="w-4 h-4" /> Stop Voice
                            </>
                        ) : (
                            <>
                                <Volume2 className="w-4 h-4" /> Play Voice
                            </>
                        )}
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2" onClick={handleExportJSON}>
                        <Download className="w-4 h-4" /> Export JSON
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2" onClick={handlePrint}>
                        <FileText className="w-4 h-4" /> Print PDF
                    </Button>
                </div>
            </div>

            {/* Print Header (Visible only when printing) */}
            <div className="hidden print:block mb-6">
                <h1 className="text-3xl font-bold mb-2">{ticker} Analysis Report</h1>
                <p className="text-gray-500">Generated on {new Date().toLocaleDateString()}</p>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Chart & Key Metrics */}
                <div className="space-y-6">
                    <StockChart
                        data={mockChartData}
                        ticker={ticker}
                        className="h-[350px]"
                    />

                    <div className="bg-card border border-border rounded-xl p-4">
                        <h3 className="font-semibold mb-4">Signal Confidence</h3>
                        <div className="space-y-4">
                            {["Technical", "Fundamental", "Sentiment", "Risk"].map((metric) => (
                                <div key={metric} className="space-y-1">
                                    <div className="flex justify-between text-sm">
                                        <span>{metric}</span>
                                        <span className="font-mono">{(Math.random() * 100).toFixed(0)}%</span>
                                    </div>
                                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary rounded-full"
                                            style={{ width: `${Math.random() * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Right Column: Detailed Analysis */}
                <div className="lg:col-span-2 bg-card border border-border rounded-xl overflow-hidden flex flex-col min-h-[600px]">
                    {/* Tabs */}
                    <div className="flex border-b border-border overflow-x-auto">
                        {tabs.map((tab) => {
                            const Icon = tab.icon
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={cn(
                                        "flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors border-b-2 whitespace-nowrap",
                                        activeTab === tab.id
                                            ? "border-primary text-primary bg-primary/5"
                                            : "border-transparent text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                                    )}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                </button>
                            )
                        })}
                    </div>

                    {/* Tab Content */}
                    <div className="flex-1 p-6 overflow-y-auto custom-scrollbar bg-card/50">
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={activeTab}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="prose prose-invert max-w-none"
                            >
                                {activeTab === "summary" && (
                                    <div>
                                        <h3 className="text-xl font-bold mb-4">Executive Summary</h3>
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {data.summary || "No summary available."}
                                        </ReactMarkdown>
                                    </div>
                                )}

                                {activeTab === "analysts" && (
                                    <div className="space-y-8">
                                        {Object.entries(data.analysts || {}).map(([role, content]) => (
                                            <div key={role} className="border-b border-border/50 pb-6 last:border-0">
                                                <h4 className="text-lg font-semibold capitalize mb-2 text-primary">{role.replace("_", " ")}</h4>
                                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                    {content}
                                                </ReactMarkdown>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {activeTab === "debate" && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-bullish/10 border border-bullish/20 rounded-lg p-4">
                                            <h4 className="text-bullish font-bold flex items-center gap-2 mb-4">
                                                <TrendingUp className="w-4 h-4" /> Bullish Case
                                            </h4>
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {data.debate?.bullish || "No bullish arguments."}
                                            </ReactMarkdown>
                                        </div>
                                        <div className="bg-bearish/10 border border-bearish/20 rounded-lg p-4">
                                            <h4 className="text-bearish font-bold flex items-center gap-2 mb-4">
                                                <TrendingDown className="w-4 h-4" /> Bearish Case
                                            </h4>
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {data.debate?.bearish || "No bearish arguments."}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                )}

                                {activeTab === "decision" && (
                                    <div className="flex flex-col items-center text-center space-y-6 py-8">
                                        <div className={cn(
                                            "w-24 h-24 rounded-full flex items-center justify-center border-4",
                                            data.decision === "BUY" ? "border-bullish bg-bullish/20 text-bullish" :
                                                data.decision === "SELL" ? "border-bearish bg-bearish/20 text-bearish" :
                                                    "border-neutral bg-neutral/20 text-neutral"
                                        )}>
                                            <span className="text-2xl font-bold">{data.decision || "HOLD"}</span>
                                        </div>

                                        <div className="max-w-2xl">
                                            <h3 className="text-xl font-bold mb-2">Final Recommendation</h3>
                                            <p className="text-muted-foreground text-lg">
                                                {data.recommendation || "Wait for further market signals before taking a position."}
                                            </p>
                                        </div>

                                        <div className="grid grid-cols-3 gap-4 w-full max-w-2xl mt-8">
                                            <div className="bg-secondary/50 p-4 rounded-lg">
                                                <div className="text-sm text-muted-foreground">Entry Price</div>
                                                <div className="text-lg font-mono font-bold">$145.20</div>
                                            </div>
                                            <div className="bg-secondary/50 p-4 rounded-lg">
                                                <div className="text-sm text-muted-foreground">Target Price</div>
                                                <div className="text-lg font-mono font-bold text-bullish">$165.00</div>
                                            </div>
                                            <div className="bg-secondary/50 p-4 rounded-lg">
                                                <div className="text-sm text-muted-foreground">Stop Loss</div>
                                                <div className="text-lg font-mono font-bold text-bearish">$138.50</div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    )
}
