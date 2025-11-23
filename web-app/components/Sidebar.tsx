/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import * as React from "react"
import {
    LayoutDashboard,
    LineChart,
    PieChart,
    ShieldAlert,
    History,
    BarChart3,
    Settings,
    ChevronLeft,
    ChevronRight,
    Activity,
    Terminal,
    Bot,
    Database,
    FileText,
    Folder,
    Plug
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface SidebarProps {
    activeView: string
    onViewChange: (view: string) => void
    isCollapsed: boolean
    toggleCollapse: () => void
}

export function Sidebar({ activeView, onViewChange, isCollapsed, toggleCollapse }: SidebarProps) {
    const navItems = [
        { id: "analysis", label: "Stock Analysis", icon: LayoutDashboard },
        { id: "direct", label: "Direct Analysis", icon: LineChart },
        { id: "portfolio", label: "Portfolio", icon: PieChart },
        { id: "risk", label: "Risk Dashboard", icon: ShieldAlert },
        { id: "history", label: "History", icon: History },
        { id: "analytics", label: "Analytics", icon: BarChart3 },
        { id: "documents", label: "Documents", icon: FileText },
        { id: "workspaces", label: "Workspaces", icon: Folder },
        { id: "mcp", label: "MCP Tools", icon: Plug },
        { id: "system", label: "System & Data", icon: Database },
        { id: "devtools", label: "Developer Tools", icon: Terminal },
        { id: "settings", label: "Settings", icon: Settings },
    ]

    return (
        <div
            className={cn(
                "relative flex flex-col h-screen bg-card border-r border-border transition-all duration-300 ease-in-out",
                isCollapsed ? "w-16" : "w-64"
            )}
        >
            {/* Header */}
            <div className="flex items-center h-16 px-4 border-b border-border">
                <div className="flex items-center gap-2 overflow-hidden">
                    <div className="bg-primary/10 p-2 rounded-lg shrink-0">
                        <Bot className="w-6 h-6 text-primary" />
                    </div>
                    {!isCollapsed && (
                        <div className="whitespace-nowrap">
                            <h1 className="text-lg font-bold text-foreground">Eddie AI</h1>
                            <p className="text-xs text-muted-foreground">Trading Assistant</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto custom-scrollbar">
                {navItems.map((item) => {
                    const Icon = item.icon
                    const isActive = activeView === item.id

                    return (
                        <Button
                            key={item.id}
                            variant={isActive ? "secondary" : "ghost"}
                            className={cn(
                                "w-full justify-start",
                                isCollapsed ? "justify-center px-2" : "px-3"
                            )}
                            onClick={() => onViewChange(item.id)}
                            title={isCollapsed ? item.label : undefined}
                        >
                            <Icon className="w-5 h-5 shrink-0" />
                            {!isCollapsed && <span>{item.label}</span>}
                        </Button>
                    )
                })}
            </nav>

            {/* Footer / Collapse Toggle */}
            <div className="p-4 border-t border-border">
                <Button
                    variant="ghost"
                    size="sm"
                    className="w-full flex items-center justify-center"
                    onClick={toggleCollapse}
                >
                    {isCollapsed ? <ChevronRight className="w-4 h-4" /> : (
                        <div className="flex items-center gap-2">
                            <ChevronLeft className="w-4 h-4" />
                            <span className="text-xs">Collapse Sidebar</span>
                        </div>
                    )}
                </Button>
            </div>
        </div>
    )
}
