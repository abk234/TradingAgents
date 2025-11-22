/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState } from "react"
import { Plus, PieChart, TrendingUp, DollarSign, Wallet } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { usePortfolio } from "@/lib/hooks/usePortfolio"
import { PositionCard } from "./PositionCard"
import { cn } from "@/lib/utils"

interface PortfolioViewProps {
    onNavigateToAnalysis?: (ticker: string) => void
}

export function PortfolioView({ onNavigateToAnalysis }: PortfolioViewProps) {
    const { positions, addPosition, removePosition, getTotalValue, getTotalPL } = usePortfolio()
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
    const [newPosition, setNewPosition] = useState({
        ticker: "",
        shares: "",
        entryPrice: ""
    })

    const totalValue = getTotalValue()
    const totalPL = getTotalPL()
    const isPositive = totalPL >= 0

    const handleAddPosition = (e: React.FormEvent) => {
        e.preventDefault()
        if (!newPosition.ticker || !newPosition.shares || !newPosition.entryPrice) return

        addPosition({
            ticker: newPosition.ticker.toUpperCase(),
            shares: Number(newPosition.shares),
            entryPrice: Number(newPosition.entryPrice)
        })

        setNewPosition({ ticker: "", shares: "", entryPrice: "" })
        setIsAddDialogOpen(false)
    }

    const handleAnalyze = (ticker: string) => {
        if (onNavigateToAnalysis) {
            onNavigateToAnalysis(ticker)
        }
    }

    return (
        <div className="space-y-6">
            {/* Header & Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <Wallet className="w-4 h-4" />
                        <span className="text-sm font-medium">Total Value</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">
                        ${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <TrendingUp className="w-4 h-4" />
                        <span className="text-sm font-medium">Total P&L</span>
                    </div>
                    <div className={cn(
                        "text-3xl font-bold font-mono",
                        isPositive ? "text-bullish" : "text-bearish"
                    )}>
                        {isPositive ? "+" : ""}${totalPL.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <PieChart className="w-4 h-4" />
                        <span className="text-sm font-medium">Positions</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">
                        {positions.length}
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">Current Holdings</h2>
                <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                    <DialogTrigger asChild>
                        <Button className="gap-2">
                            <Plus className="w-4 h-4" /> Add Position
                        </Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Add New Position</DialogTitle>
                            <DialogDescription>
                                Enter the details of your stock position.
                            </DialogDescription>
                        </DialogHeader>
                        <form onSubmit={handleAddPosition}>
                            <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="ticker" className="text-right">
                                        Ticker
                                    </Label>
                                    <Input
                                        id="ticker"
                                        value={newPosition.ticker}
                                        onChange={(e) => setNewPosition({ ...newPosition, ticker: e.target.value })}
                                        className="col-span-3 uppercase"
                                        placeholder="AAPL"
                                    />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="shares" className="text-right">
                                        Shares
                                    </Label>
                                    <Input
                                        id="shares"
                                        type="number"
                                        value={newPosition.shares}
                                        onChange={(e) => setNewPosition({ ...newPosition, shares: e.target.value })}
                                        className="col-span-3"
                                        placeholder="10"
                                    />
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="price" className="text-right">
                                        Avg Price
                                    </Label>
                                    <Input
                                        id="price"
                                        type="number"
                                        step="0.01"
                                        value={newPosition.entryPrice}
                                        onChange={(e) => setNewPosition({ ...newPosition, entryPrice: e.target.value })}
                                        className="col-span-3"
                                        placeholder="150.00"
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button type="submit">Add Position</Button>
                            </DialogFooter>
                        </form>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Positions Grid */}
            {positions.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-border rounded-xl bg-card/50">
                    <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                        <DollarSign className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-medium mb-2">No positions yet</h3>
                    <p className="text-muted-foreground mb-6">Add your first stock position to start tracking.</p>
                    <Button variant="outline" onClick={() => setIsAddDialogOpen(true)}>
                        Add Position
                    </Button>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {positions.map((position) => (
                        <PositionCard
                            key={position.id}
                            position={position}
                            onRemove={removePosition}
                            onAnalyze={handleAnalyze}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}
