"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { CheckCircle2, AlertCircle, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface ConfidenceMetrics {
    data_freshness: number  // 0-10
    math_verification: number  // 0-10
    ai_confidence: number  // 0-100
    overall: number  // 0-100
}

interface ConfidenceMeterProps {
    confidence: ConfidenceMetrics
    className?: string
    showDetails?: boolean
}

export function ConfidenceMeter({ confidence, className, showDetails = true }: ConfidenceMeterProps) {
    const getColor = (value: number, max: number = 100) => {
        const percentage = (value / max) * 100
        if (percentage >= 80) return "bg-green-500"
        if (percentage >= 60) return "bg-yellow-500"
        if (percentage >= 40) return "bg-orange-500"
        return "bg-red-500"
    }

    const getIcon = (value: number, max: number = 100) => {
        const percentage = (value / max) * 100
        if (percentage >= 80) return <CheckCircle2 className="w-4 h-4 text-green-500" />
        if (percentage >= 60) return <AlertCircle className="w-4 h-4 text-yellow-500" />
        return <XCircle className="w-4 h-4 text-red-500" />
    }

    const getStatus = (value: number, max: number = 100) => {
        const percentage = (value / max) * 100
        if (percentage >= 80) return "Excellent"
        if (percentage >= 60) return "Good"
        if (percentage >= 40) return "Fair"
        return "Poor"
    }

    return (
        <div className={cn("space-y-3", className)}>
            {/* Overall Confidence */}
            <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">Overall Confidence</span>
                    <div className="flex items-center gap-2">
                        {getIcon(confidence.overall)}
                        <span className="font-semibold">{confidence.overall.toFixed(0)}%</span>
                        <span className="text-xs text-muted-foreground">
                            ({getStatus(confidence.overall)})
                        </span>
                    </div>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                        className={cn("h-full", getColor(confidence.overall))}
                        initial={{ width: 0 }}
                        animate={{ width: `${confidence.overall}%` }}
                        transition={{ duration: 0.5, ease: "easeOut" }}
                    />
                </div>
            </div>

            {showDetails && (
                <div className="space-y-2 text-xs">
                    {/* Data Freshness */}
                    <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Data Freshness</span>
                        <div className="flex items-center gap-2">
                            {getIcon(confidence.data_freshness, 10)}
                            <span>{confidence.data_freshness.toFixed(1)}/10</span>
                        </div>
                    </div>
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div
                            className={cn("h-full", getColor(confidence.data_freshness, 10))}
                            initial={{ width: 0 }}
                            animate={{ width: `${(confidence.data_freshness / 10) * 100}%` }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                        />
                    </div>

                    {/* Math Verification */}
                    <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Math Verification</span>
                        <div className="flex items-center gap-2">
                            {getIcon(confidence.math_verification, 10)}
                            <span>{confidence.math_verification.toFixed(1)}/10</span>
                        </div>
                    </div>
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div
                            className={cn("h-full", getColor(confidence.math_verification, 10))}
                            initial={{ width: 0 }}
                            animate={{ width: `${(confidence.math_verification / 10) * 100}%` }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                        />
                    </div>

                    {/* AI Confidence */}
                    <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">AI Confidence</span>
                        <div className="flex items-center gap-2">
                            {getIcon(confidence.ai_confidence)}
                            <span>{confidence.ai_confidence.toFixed(0)}%</span>
                        </div>
                    </div>
                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <motion.div
                            className={cn("h-full", getColor(confidence.ai_confidence))}
                            initial={{ width: 0 }}
                            animate={{ width: `${confidence.ai_confidence}%` }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                        />
                    </div>
                </div>
            )}
        </div>
    )
}

