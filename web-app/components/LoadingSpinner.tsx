/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { cn } from "@/lib/utils"

interface LoadingSpinnerProps {
    size?: "sm" | "md" | "lg" | "xl"
    className?: string
    fullScreen?: boolean
}

export function LoadingSpinner({
    size = "md",
    className,
    fullScreen = false
}: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: "w-4 h-4 border-2",
        md: "w-8 h-8 border-4",
        lg: "w-12 h-12 border-4",
        xl: "w-16 h-16 border-4"
    }

    const spinner = (
        <div className={cn(
            "rounded-full border-secondary border-t-primary animate-spin",
            sizeClasses[size],
            className
        )} />
    )

    if (fullScreen) {
        return (
            <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
                {spinner}
            </div>
        )
    }

    return spinner
}
