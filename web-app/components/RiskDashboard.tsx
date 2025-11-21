"use client"

import { useState, useMemo } from "react"
import { ShieldAlert, Activity, TrendingDown, AlertTriangle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { usePortfolio } from "@/lib/hooks/usePortfolio"
import { RiskDebateViewer } from "./RiskDebateViewer"
import { PositionSizingCalculator } from "./PositionSizingCalculator"
import { calculateRiskMetrics } from "@/lib/risk"
import { cn } from "@/lib/utils"

export function RiskDashboard() {
    const { positions, getTotalValue } = usePortfolio()
    const [isAnalyzing, setIsAnalyzing] = useState(false)

    const totalValue = getTotalValue()

    const riskMetrics = useMemo(() => {
        return calculateRiskMetrics(positions, totalValue)
    }, [positions, totalValue])

    const handleRunAnalysis = () => {
        setIsAnalyzing(true)
        // Simulate API call
        setTimeout(() => setIsAnalyzing(false), 2000)
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold flex items-center gap-2">
                        <ShieldAlert className="w-6 h-6 text-primary" />
                        Risk Assessment
                    </h2>
                    <p className="text-muted-foreground">
                        Portfolio exposure and risk analysis
                    </p>
                </div>
                <Button onClick={handleRunAnalysis} disabled={isAnalyzing} className="gap-2">
                    <RefreshCw className={cn("w-4 h-4", isAnalyzing && "animate-spin")} />
                    {isAnalyzing ? "Analyzing..." : "Run Risk Analysis"}
                </Button>
            </div>

            {/* Key Risk Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <TrendingDown className="w-4 h-4" />
                        <span className="text-sm font-medium">Value at Risk (95%)</span>
                    </div>
                    <div className="text-2xl font-bold font-mono text-bearish">
                        ${riskMetrics.var.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">Potential daily loss</p>
                </div>

                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <Activity className="w-4 h-4" />
                        <span className="text-sm font-medium">Sharpe Ratio</span>
                    </div>
                    <div className="text-2xl font-bold font-mono text-bullish">
                        {riskMetrics.sharpeRatio}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">Risk-adjusted return</p>
                </div>

                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-sm font-medium">Portfolio Beta</span>
                    </div>
                    <div className="text-2xl font-bold font-mono">
                        {riskMetrics.beta}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">Market sensitivity</p>
                </div>

                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <Activity className="w-4 h-4" />
                        <span className="text-sm font-medium">Volatility</span>
                    </div>
                    <div className="text-2xl font-bold font-mono text-orange-500">
                        {riskMetrics.volatility}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">Price fluctuation risk</p>
                </div>
            </div>

            {/* Risk Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-card border border-border rounded-xl p-6">
                    <h3 className="font-semibold mb-4">Sector Exposure</h3>
                    <div className="space-y-4">
                        {positions.length > 0 ? (
                            positions.map((pos) => (
                                <div key={pos.id} className="space-y-1">
                                    <div className="flex justify-between text-sm">
                                        <span>{pos.ticker}</span>
                                        <span className="font-mono">
                                            {((pos.shares * pos.entryPrice) / totalValue * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-primary rounded-full"
                                            style={{ width: `${(pos.shares * pos.entryPrice) / totalValue * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ))
                        ) : (
                            <p className="text-muted-foreground text-sm">No positions to analyze.</p>
                        )}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="bg-card border border-border rounded-xl p-6">
                        <h3 className="font-semibold mb-4">Risk Alerts</h3>
                        <div className="space-y-3">
                            <div className="flex items-start gap-3 p-3 bg-bearish/10 border border-bearish/20 rounded-lg">
                                <AlertTriangle className="w-5 h-5 text-bearish shrink-0 mt-0.5" />
                                <div>
                                    <h4 className="text-sm font-semibold text-bearish">High Concentration Risk</h4>
                                    <p className="text-xs text-muted-foreground">
                                        Portfolio is heavily weighted in technology sector. Consider diversifying into defensive assets.
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                                <Activity className="w-5 h-5 text-orange-500 shrink-0 mt-0.5" />
                                <div>
                                    <h4 className="text-sm font-semibold text-orange-500">Volatility Warning</h4>
                                    <p className="text-xs text-muted-foreground">
                                        Recent market conditions suggest increased volatility in your held positions.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Risk Debate Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <RiskDebateViewer />
                <PositionSizingCalculator />
            </div>
        </div>
    )
}
