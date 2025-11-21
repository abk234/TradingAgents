"use client"

import { useState } from "react"
import { Search, Calendar, FileText, ArrowRight } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface HistoricalItem {
    id: string
    ticker: string
    date: string
    type: "analysis" | "chat"
    summary: string
    sentiment: "bullish" | "bearish" | "neutral"
}

export function HistoricalView() {
    const [searchQuery, setSearchQuery] = useState("")

    // Mock data
    const history: HistoricalItem[] = [
        {
            id: "1",
            ticker: "NVDA",
            date: "2024-03-15",
            type: "analysis",
            summary: "Strong buy signal based on new AI chip architecture announcement and increased data center demand.",
            sentiment: "bullish"
        },
        {
            id: "2",
            ticker: "TSLA",
            date: "2024-03-14",
            type: "chat",
            summary: "Discussion about Q1 delivery numbers and impact on margins. Cautious outlook.",
            sentiment: "bearish"
        },
        {
            id: "3",
            ticker: "AAPL",
            date: "2024-03-12",
            type: "analysis",
            summary: "Neutral stance pending WWDC announcements. Services revenue growth remains strong.",
            sentiment: "neutral"
        }
    ]

    const filteredHistory = history.filter(item =>
        item.ticker.includes(searchQuery.toUpperCase()) ||
        item.summary.toLowerCase().includes(searchQuery.toLowerCase())
    )

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">History</h2>
                    <p className="text-muted-foreground">Review past analyses and conversations</p>
                </div>
                <div className="relative w-64">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                        placeholder="Search history..."
                        className="pl-10"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
            </div>

            <div className="space-y-4">
                {filteredHistory.map((item) => (
                    <div
                        key={item.id}
                        className="bg-card border border-border rounded-xl p-4 hover:border-primary/50 transition-colors cursor-pointer group"
                    >
                        <div className="flex justify-between items-start">
                            <div className="flex items-start gap-4">
                                <div className={cn(
                                    "w-10 h-10 rounded-lg flex items-center justify-center shrink-0",
                                    item.sentiment === "bullish" ? "bg-bullish/10 text-bullish" :
                                        item.sentiment === "bearish" ? "bg-bearish/10 text-bearish" :
                                            "bg-secondary text-muted-foreground"
                                )}>
                                    <FileText className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-bold text-lg">{item.ticker}</span>
                                        <span className="text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded-full flex items-center gap-1">
                                            <Calendar className="w-3 h-3" />
                                            {item.date}
                                        </span>
                                        <span className={cn(
                                            "text-xs px-2 py-0.5 rounded-full font-medium uppercase",
                                            item.sentiment === "bullish" ? "bg-bullish/10 text-bullish" :
                                                item.sentiment === "bearish" ? "bg-bearish/10 text-bearish" :
                                                    "bg-secondary text-muted-foreground"
                                        )}>
                                            {item.sentiment}
                                        </span>
                                    </div>
                                    <p className="text-muted-foreground line-clamp-2">{item.summary}</p>
                                </div>
                            </div>
                            <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
