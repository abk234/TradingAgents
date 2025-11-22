/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { cn } from "@/lib/utils"

interface ConfidenceMeterProps {
    score: number // 0 to 1
    label?: string
    className?: string
    showLabel?: boolean
}

export function ConfidenceMeter({
    score,
    label = "Confidence",
    className,
    showLabel = true
}: ConfidenceMeterProps) {
    // Clamp score between 0 and 1
    const validScore = Math.max(0, Math.min(1, score))
    const percentage = Math.round(validScore * 100)

    let colorClass = "bg-red-500"
    let textClass = "text-red-500"

    if (validScore >= 0.7) {
        colorClass = "bg-green-500"
        textClass = "text-green-500"
    } else if (validScore >= 0.4) {
        colorClass = "bg-yellow-500"
        textClass = "text-yellow-500"
    }

    return (
        <div className={cn("w-full", className)}>
            {showLabel && (
                <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted-foreground">{label}</span>
                    <span className={cn("font-mono font-medium", textClass)}>
                        {percentage}%
                    </span>
                </div>
            )}
            <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div
                    className={cn("h-full transition-all duration-500 ease-out", colorClass)}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    )
}
