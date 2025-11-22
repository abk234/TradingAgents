/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState, useEffect } from "react"
import { Shield, Briefcase, Scale, User } from "lucide-react"
import { cn } from "@/lib/utils"
import { motion, AnimatePresence } from "framer-motion"

interface DebateMessage {
    id: string
    role: "risk_manager" | "portfolio_manager" | "compliance_officer"
    content: string
    timestamp: number
}

export function RiskDebateViewer() {
    const [messages, setMessages] = useState<DebateMessage[]>([])
    const [isDebating, setIsDebating] = useState(false)

    const agents = {
        risk_manager: {
            name: "Risk Manager",
            icon: Shield,
            color: "text-red-500",
            bg: "bg-red-500/10",
            border: "border-red-500/20"
        },
        portfolio_manager: {
            name: "Portfolio Manager",
            icon: Briefcase,
            color: "text-blue-500",
            bg: "bg-blue-500/10",
            border: "border-blue-500/20"
        },
        compliance_officer: {
            name: "Compliance",
            icon: Scale,
            color: "text-orange-500",
            bg: "bg-orange-500/10",
            border: "border-orange-500/20"
        }
    }

    const startDebate = () => {
        setIsDebating(true)
        setMessages([])

        const debateFlow: DebateMessage[] = [
            {
                id: "1",
                role: "portfolio_manager",
                content: "I propose increasing our allocation in NVDA by 5%. The AI sector momentum is strong, and technicals suggest a breakout.",
                timestamp: Date.now()
            },
            {
                id: "2",
                role: "risk_manager",
                content: "I have concerns. Our tech exposure is already at 45%, exceeding our 40% sector limit. This trade would push concentration risk to unacceptable levels.",
                timestamp: Date.now() + 1000
            },
            {
                id: "3",
                role: "compliance_officer",
                content: "Additionally, the proposed position size would trigger a Level 2 review requirement under our current risk framework.",
                timestamp: Date.now() + 2000
            },
            {
                id: "4",
                role: "portfolio_manager",
                content: "Understood. What if we trim our MSFT position to fund this? That maintains sector neutrality while capturing the higher beta opportunity.",
                timestamp: Date.now() + 3000
            },
            {
                id: "5",
                role: "risk_manager",
                content: "That's better. Reducing MSFT lowers our correlation risk slightly. If we keep the net sector exposure flat, I can approve a 3% increase instead of 5%.",
                timestamp: Date.now() + 4000
            }
        ]

        let delay = 0
        debateFlow.forEach((msg, index) => {
            delay += 1500 // Stagger messages
            setTimeout(() => {
                setMessages(prev => [...prev, msg])
                if (index === debateFlow.length - 1) {
                    setIsDebating(false)
                }
            }, delay)
        })
    }

    return (
        <div className="bg-card border border-border rounded-xl overflow-hidden flex flex-col h-[500px]">
            <div className="p-4 border-b border-border flex justify-between items-center bg-muted/30">
                <div>
                    <h3 className="font-semibold flex items-center gap-2">
                        <Scale className="w-4 h-4" /> Risk Council Debate
                    </h3>
                    <p className="text-xs text-muted-foreground">Real-time risk assessment dialogue</p>
                </div>
                <button
                    onClick={startDebate}
                    disabled={isDebating}
                    className="text-xs bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                    {isDebating ? "Debate in Progress..." : "Simulate Debate"}
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                <AnimatePresence initial={false}>
                    {messages.length === 0 && !isDebating ? (
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50">
                            <Scale className="w-12 h-12 mb-2" />
                            <p>Start a simulation to view the risk council debate</p>
                        </div>
                    ) : (
                        messages.map((msg) => {
                            const agent = agents[msg.role]
                            const Icon = agent.icon
                            return (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    className={cn(
                                        "flex gap-3 max-w-[90%]",
                                        msg.role === "portfolio_manager" ? "ml-auto flex-row-reverse" : ""
                                    )}
                                >
                                    <div className={cn(
                                        "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                                        agent.bg,
                                        agent.border,
                                        agent.color
                                    )}>
                                        <Icon className="w-4 h-4" />
                                    </div>
                                    <div className={cn(
                                        "p-3 rounded-lg text-sm border",
                                        msg.role === "portfolio_manager"
                                            ? "bg-primary/10 border-primary/20 rounded-tr-none"
                                            : "bg-secondary/50 border-border rounded-tl-none"
                                    )}>
                                        <div className={cn("text-xs font-semibold mb-1", agent.color)}>
                                            {agent.name}
                                        </div>
                                        {msg.content}
                                    </div>
                                </motion.div>
                            )
                        })
                    )}
                </AnimatePresence>
            </div>
        </div>
    )
}
