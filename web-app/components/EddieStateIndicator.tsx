"use client"

import { Activity, Mic, Volume2, BrainCircuit, AlertCircle, CheckCircle2 } from "lucide-react"
import { cn } from "@/lib/utils"

export type AgentState = "idle" | "listening" | "processing" | "speaking" | "error" | "validating"

interface EddieStateIndicatorProps {
    state: AgentState
    message?: string
    className?: string
}

export function EddieStateIndicator({ state, message, className }: EddieStateIndicatorProps) {
    const getStateConfig = (s: AgentState) => {
        switch (s) {
            case "listening":
                return {
                    icon: Mic,
                    color: "text-blue-500",
                    bg: "bg-blue-500/10",
                    border: "border-blue-500/20",
                    animate: "animate-pulse"
                }
            case "processing":
                return {
                    icon: BrainCircuit,
                    color: "text-purple-500",
                    bg: "bg-purple-500/10",
                    border: "border-purple-500/20",
                    animate: "animate-pulse"
                }
            case "speaking":
                return {
                    icon: Volume2,
                    color: "text-green-500",
                    bg: "bg-green-500/10",
                    border: "border-green-500/20",
                    animate: "animate-bounce" // Subtle bounce
                }
            case "error":
                return {
                    icon: AlertCircle,
                    color: "text-red-500",
                    bg: "bg-red-500/10",
                    border: "border-red-500/20",
                    animate: ""
                }
            case "validating":
                return {
                    icon: Activity,
                    color: "text-orange-500",
                    bg: "bg-orange-500/10",
                    border: "border-orange-500/20",
                    animate: "animate-spin"
                }
            case "idle":
            default:
                return {
                    icon: CheckCircle2,
                    color: "text-muted-foreground",
                    bg: "bg-secondary",
                    border: "border-border",
                    animate: ""
                }
        }
    }

    const config = getStateConfig(state)
    const Icon = config.icon

    return (
        <div className={cn(
            "flex items-center gap-3 px-3 py-2 rounded-full border transition-all duration-300",
            config.bg,
            config.border,
            className
        )}>
            <div className={cn("relative flex items-center justify-center", config.color)}>
                <Icon className={cn("w-4 h-4", config.animate)} />
                {state === "processing" && (
                    <span className="absolute inset-0 rounded-full animate-ping opacity-20 bg-current" />
                )}
            </div>

            {message && (
                <span className={cn("text-xs font-medium", config.color)}>
                    {message}
                </span>
            )}
        </div>
    )
}
