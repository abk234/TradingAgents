"use client"

import * as React from "react"
import { useState } from "react"
import { Sidebar } from "./Sidebar"
import { EddieStateIndicator } from "./EddieStateIndicator"
import { cn } from "@/lib/utils"

interface DashboardLayoutProps {
    children: React.ReactNode
    activeView: string
    onViewChange: (view: string) => void
}

export function DashboardLayout({ children, activeView, onViewChange }: DashboardLayoutProps) {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

    return (
        <div className="flex h-screen bg-background overflow-hidden">
            <Sidebar
                activeView={activeView}
                onViewChange={onViewChange}
                isCollapsed={isSidebarCollapsed}
                toggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            />

            <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Top Bar (Optional - for breadcrumbs or global actions) */}
                <header className="h-16 border-b border-border flex items-center justify-between px-6 bg-card/50 backdrop-blur-sm">
                    <h2 className="text-lg font-semibold capitalize">
                        {activeView.replace("-", " ")}
                    </h2>

                    <div className="flex items-center gap-4">
                        <EddieStateIndicator state="idle" />
                        {/* User profile or other actions could go here */}
                    </div>
                </header>

                {/* Main Content Area */}
                <div className="flex-1 overflow-auto p-6 custom-scrollbar relative">
                    <div className="max-w-7xl mx-auto h-full">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    )
}
