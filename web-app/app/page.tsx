"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/DashboardLayout"
import { ChatInterface } from "@/components/ChatInterface"
import { DirectAnalysis } from "@/components/DirectAnalysis"
import { PortfolioView } from "@/components/PortfolioView"
import { RiskDashboard } from "@/components/RiskDashboard"
import { HistoricalView } from "@/components/HistoricalView"
import { AnalyticsView } from "@/components/AnalyticsView"
import { SettingsView } from "@/components/SettingsView"
import { SystemView } from "@/components/SystemView"
import { ViewPlaceholder } from "@/components/ViewPlaceholder"
import { Toaster } from "react-hot-toast"

export default function Home() {
  const [activeView, setActiveView] = useState("analysis")

  const renderView = () => {
    switch (activeView) {
      case "analysis":
        return <ChatInterface />
      case "direct":
        return <DirectAnalysis />
      case "portfolio":
        return <PortfolioView onNavigateToAnalysis={(ticker) => setActiveView("direct")} />
      case "risk":
        return <RiskDashboard />
      case "history":
        return <HistoricalView />
      case "analytics":
        return <AnalyticsView />
      case "settings":
        return <SettingsView />
      case "system":
        return <SystemView />
      default:
        return <ChatInterface />
    }
  }

  return (
    <DashboardLayout activeView={activeView} onViewChange={setActiveView}>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'hsl(var(--card))',
            color: 'hsl(var(--foreground))',
            border: '1px solid hsl(var(--border))',
          },
          success: {
            iconTheme: {
              primary: 'hsl(var(--bullish))',
              secondary: 'hsl(var(--card))',
            },
          },
          error: {
            iconTheme: {
              primary: 'hsl(var(--bearish))',
              secondary: 'hsl(var(--card))',
            },
          },
        }}
      />
      {renderView()}
    </DashboardLayout>
  )
}
