/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState, useEffect } from "react"
import { Calculator, DollarSign, Percent, AlertCircle } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { usePortfolio } from "@/lib/hooks/usePortfolio"

export function PositionSizingCalculator() {
    const { getTotalValue } = usePortfolio()
    const totalValue = getTotalValue()

    const [accountBalance, setAccountBalance] = useState(totalValue || 100000)
    const [riskPercentage, setRiskPercentage] = useState(1.0)
    const [entryPrice, setEntryPrice] = useState(0)
    const [stopLoss, setStopLoss] = useState(0)

    const [result, setResult] = useState({
        shares: 0,
        positionValue: 0,
        riskAmount: 0,
        riskPerShare: 0
    })

    useEffect(() => {
        if (totalValue > 0 && accountBalance === 100000) {
            setAccountBalance(totalValue)
        }
    }, [totalValue])

    const calculate = () => {
        if (entryPrice <= 0 || stopLoss <= 0 || entryPrice === stopLoss) return

        const riskAmount = accountBalance * (riskPercentage / 100)
        const riskPerShare = Math.abs(entryPrice - stopLoss)
        const shares = Math.floor(riskAmount / riskPerShare)
        const positionValue = shares * entryPrice

        setResult({
            shares,
            positionValue,
            riskAmount,
            riskPerShare
        })
    }

    useEffect(() => {
        calculate()
    }, [accountBalance, riskPercentage, entryPrice, stopLoss])

    return (
        <div className="bg-card border border-border rounded-xl p-6 space-y-6">
            <div className="flex items-center gap-2 border-b border-border pb-4">
                <Calculator className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Position Sizing Calculator</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="balance">Account Balance</Label>
                        <div className="relative">
                            <DollarSign className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                id="balance"
                                type="number"
                                className="pl-8"
                                value={accountBalance}
                                onChange={(e) => setAccountBalance(parseFloat(e.target.value) || 0)}
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="risk">Risk Percentage</Label>
                        <div className="relative">
                            <Percent className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                id="risk"
                                type="number"
                                className="pl-8"
                                step="0.1"
                                value={riskPercentage}
                                onChange={(e) => setRiskPercentage(parseFloat(e.target.value) || 0)}
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="entry">Entry Price</Label>
                            <div className="relative">
                                <DollarSign className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="entry"
                                    type="number"
                                    className="pl-8"
                                    value={entryPrice}
                                    onChange={(e) => setEntryPrice(parseFloat(e.target.value) || 0)}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="stop">Stop Loss</Label>
                            <div className="relative">
                                <DollarSign className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    id="stop"
                                    type="number"
                                    className="pl-8"
                                    value={stopLoss}
                                    onChange={(e) => setStopLoss(parseFloat(e.target.value) || 0)}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-secondary/20 rounded-lg p-6 space-y-6">
                    <div>
                        <div className="text-sm text-muted-foreground mb-1">Recommended Position Size</div>
                        <div className="text-3xl font-bold font-mono text-primary">
                            {result.shares.toLocaleString()} <span className="text-base font-normal text-muted-foreground">shares</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border/50">
                        <div>
                            <div className="text-xs text-muted-foreground mb-1">Total Value</div>
                            <div className="font-mono font-semibold">
                                ${result.positionValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs text-muted-foreground mb-1">Risk Amount</div>
                            <div className="font-mono font-semibold text-bearish">
                                ${result.riskAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                    </div>

                    {result.shares > 0 && (
                        <div className="flex items-start gap-2 text-xs text-muted-foreground bg-secondary/50 p-3 rounded">
                            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                            <p>
                                This position size ensures you only risk <strong>{riskPercentage}%</strong> of your capital if the stop loss is hit.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
