"use client"

import { ArrowUpRight, ArrowDownRight, MoreVertical, Trash2, BarChart2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Position } from "@/lib/hooks/usePortfolio"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface PositionCardProps {
    position: Position
    onRemove: (id: string) => void
    onAnalyze: (ticker: string) => void
}

export function PositionCard({ position, onRemove, onAnalyze }: PositionCardProps) {
    const currentPrice = position.currentPrice || position.entryPrice
    const marketValue = position.shares * currentPrice
    const costBasis = position.shares * position.entryPrice
    const pl = marketValue - costBasis
    const plPercent = (pl / costBasis) * 100
    const isPositive = pl >= 0

    return (
        <div className="bg-card border border-border rounded-xl p-4 hover:border-primary/50 transition-colors group">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg">{position.ticker}</h3>
                        <span className={cn(
                            "text-xs px-2 py-0.5 rounded-full font-medium",
                            isPositive ? "bg-bullish/10 text-bullish" : "bg-bearish/10 text-bearish"
                        )}>
                            {isPositive ? "+" : ""}{plPercent.toFixed(2)}%
                        </span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                        {position.shares} shares @ ${position.entryPrice.toFixed(2)}
                    </p>
                </div>

                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreVertical className="w-4 h-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onAnalyze(position.ticker)}>
                            <BarChart2 className="w-4 h-4 mr-2" /> Analyze
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => onRemove(position.id)} className="text-destructive focus:text-destructive">
                            <Trash2 className="w-4 h-4 mr-2" /> Remove
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <p className="text-xs text-muted-foreground">Market Value</p>
                    <p className="font-mono font-semibold">${marketValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                </div>
                <div className="text-right">
                    <p className="text-xs text-muted-foreground">Total P&L</p>
                    <p className={cn(
                        "font-mono font-semibold flex items-center justify-end gap-1",
                        isPositive ? "text-bullish" : "text-bearish"
                    )}>
                        {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        ${Math.abs(pl).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                </div>
            </div>
        </div>
    )
}
