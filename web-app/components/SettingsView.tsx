/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

import { useState, useEffect } from "react"
import { Save, Bell, Lock, Monitor, Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { toast } from "react-hot-toast"
import { cn } from "@/lib/utils"

export function SettingsView() {
    const [apiKeys, setApiKeys] = useState({
        openai: "",
        alphaVantage: ""
    })

    const [notifications, setNotifications] = useState({
        alerts: true,
        news: true,
        reports: false
    })

    const [theme, setTheme] = useState<"dark" | "light" | "system">("dark")

    useEffect(() => {
        // Load settings from localStorage
        const savedApiKeys = localStorage.getItem("trading_agents_api_keys")
        if (savedApiKeys) {
            setApiKeys(JSON.parse(savedApiKeys))
        }

        const savedNotifications = localStorage.getItem("trading_agents_notifications")
        if (savedNotifications) {
            setNotifications(JSON.parse(savedNotifications))
        }

        const savedTheme = localStorage.getItem("trading_agents_theme") as "dark" | "light" | "system"
        if (savedTheme) {
            setTheme(savedTheme)
        }
    }, [])

    const handleSave = () => {
        localStorage.setItem("trading_agents_api_keys", JSON.stringify(apiKeys))
        localStorage.setItem("trading_agents_notifications", JSON.stringify(notifications))
        localStorage.setItem("trading_agents_theme", theme)
        toast.success("Settings saved successfully")
    }

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <div>
                <h2 className="text-2xl font-bold">Settings</h2>
                <p className="text-muted-foreground">Manage your preferences and API configurations</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-6">
                <div className="flex items-center gap-2 font-semibold text-lg border-b border-border pb-2">
                    <Lock className="w-5 h-5" /> API Configuration
                </div>

                <div className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="openai">OpenAI API Key</Label>
                        <Input
                            id="openai"
                            type="password"
                            value={apiKeys.openai}
                            onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
                            placeholder="sk-..."
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="av">Alpha Vantage API Key</Label>
                        <Input
                            id="av"
                            type="password"
                            value={apiKeys.alphaVantage}
                            onChange={(e) => setApiKeys({ ...apiKeys, alphaVantage: e.target.value })}
                            placeholder="Enter your key..."
                        />
                    </div>
                </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-6">
                <div className="flex items-center gap-2 font-semibold text-lg border-b border-border pb-2">
                    <Monitor className="w-5 h-5" /> Appearance
                </div>

                <div className="grid grid-cols-3 gap-4">
                    <button
                        onClick={() => setTheme("light")}
                        className={cn(
                            "flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all",
                            theme === "light" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                        )}
                    >
                        <Sun className="w-6 h-6 mb-2" />
                        <span className="text-sm font-medium">Light</span>
                    </button>
                    <button
                        onClick={() => setTheme("dark")}
                        className={cn(
                            "flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all",
                            theme === "dark" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                        )}
                    >
                        <Moon className="w-6 h-6 mb-2" />
                        <span className="text-sm font-medium">Dark</span>
                    </button>
                    <button
                        onClick={() => setTheme("system")}
                        className={cn(
                            "flex flex-col items-center justify-center p-4 rounded-lg border-2 transition-all",
                            theme === "system" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                        )}
                    >
                        <Monitor className="w-6 h-6 mb-2" />
                        <span className="text-sm font-medium">System</span>
                    </button>
                </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-6">
                <div className="flex items-center gap-2 font-semibold text-lg border-b border-border pb-2">
                    <Bell className="w-5 h-5" /> Notifications
                </div>

                <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="alerts"
                            checked={notifications.alerts}
                            onCheckedChange={(checked) => setNotifications({ ...notifications, alerts: checked as boolean })}
                        />
                        <Label htmlFor="alerts">Price Alerts</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="news"
                            checked={notifications.news}
                            onCheckedChange={(checked) => setNotifications({ ...notifications, news: checked as boolean })}
                        />
                        <Label htmlFor="news">Breaking News</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="reports"
                            checked={notifications.reports}
                            onCheckedChange={(checked) => setNotifications({ ...notifications, reports: checked as boolean })}
                        />
                        <Label htmlFor="reports">Daily Reports</Label>
                    </div>
                </div>
            </div>

            <div className="flex justify-end">
                <Button onClick={handleSave} className="gap-2">
                    <Save className="w-4 h-4" /> Save Changes
                </Button>
            </div>
        </div>
    )
}
