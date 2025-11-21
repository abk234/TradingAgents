"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

export type EddieState = "idle" | "listening" | "processing" | "speaking" | "error" | "validating"

interface EddieStateIndicatorProps {
    state: EddieState
    className?: string
    size?: "sm" | "md" | "lg"
}

const stateConfig = {
    idle: {
        color: "bg-gray-400",
        pulse: false,
        spin: false,
        glow: false,
        label: "Ready"
    },
    listening: {
        color: "bg-blue-500",
        pulse: true,
        spin: false,
        glow: true,
        label: "Listening"
    },
    processing: {
        color: "bg-purple-500",
        pulse: false,
        spin: true,
        glow: true,
        label: "Thinking"
    },
    speaking: {
        color: "bg-green-500",
        pulse: false,
        spin: false,
        glow: false,
        label: "Speaking"
    },
    error: {
        color: "bg-red-500",
        pulse: true,
        spin: false,
        glow: true,
        label: "Error"
    },
    validating: {
        color: "bg-yellow-500",
        pulse: true,
        spin: false,
        glow: false,
        label: "Validating"
    }
}

const sizeConfig = {
    sm: "w-3 h-3",
    md: "w-4 h-4",
    lg: "w-6 h-6"
}

export function EddieStateIndicator({ state, className, size = "md" }: EddieStateIndicatorProps) {
    const config = stateConfig[state]
    const sizeClass = sizeConfig[size]

    return (
        <div className={cn("flex items-center gap-2", className)}>
            <motion.div
                className={cn(
                    "rounded-full",
                    config.color,
                    sizeClass,
                    config.glow && "shadow-lg"
                )}
                animate={{
                    scale: config.pulse ? [1, 1.2, 1] : 1,
                    opacity: config.pulse ? [1, 0.7, 1] : 1,
                    rotate: config.spin ? 360 : 0,
                }}
                transition={{
                    scale: {
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                    },
                    opacity: {
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                    },
                    rotate: {
                        duration: 2,
                        repeat: Infinity,
                        ease: "linear"
                    }
                }}
                style={{
                    boxShadow: config.glow
                        ? `0 0 ${size === "lg" ? "12px" : size === "md" ? "8px" : "4px"} ${config.color.replace("bg-", "")}`
                        : undefined
                }}
            />
            <span className="text-sm text-muted-foreground">{config.label}</span>
        </div>
    )
}

