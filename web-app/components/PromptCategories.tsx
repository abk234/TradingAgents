"use client"

import * as React from "react"
import { useState } from "react"
import {
    TrendingUp, Star, Rocket, Search, Scale, LineChart, FileText,
    AlertTriangle, DoorOpen, Target, Activity, Layers, Newspaper,
    Calendar, Shield, Globe, ChevronDown, ChevronUp, Loader2
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import {
    PREDEFINED_PROMPTS,
    PROMPT_CATEGORIES,
    PromptCategory,
    PromptConfig
} from "@/lib/prompts.config"

const ICON_MAP = {
    Star, Rocket, TrendingUp, Search, Scale, LineChart, FileText,
    AlertTriangle, DoorOpen, Target, Activity, Layers, Newspaper,
    Calendar, Shield, Globe
} as const

interface PromptCategoriesProps {
    onPromptSelect: (prompt: string, metadata?: { promptType: string, promptId: string }) => void
    isLoading?: boolean
    loadingPromptId?: string | null
}

export function PromptCategories({ onPromptSelect, isLoading, loadingPromptId }: PromptCategoriesProps) {
    const [expandedCategories, setExpandedCategories] = useState<Set<PromptCategory>>(
        new Set(['quick_wins'])
    )
    const [tickerInputs, setTickerInputs] = useState<Record<string, string>>({})

    const toggleCategory = (category: PromptCategory) => {
        setExpandedCategories(prev => {
            const next = new Set(prev)
            if (next.has(category)) {
                next.delete(category)
            } else {
                next.add(category)
            }
            return next
        })
    }

    const handlePromptClick = (promptConfig: PromptConfig) => {
        if (promptConfig.requiresTicker) {
            const ticker = tickerInputs[promptConfig.id]?.trim().toUpperCase()
            if (!ticker) {
                // Focus the input if no ticker provided
                document.getElementById(`ticker-${promptConfig.id}`)?.focus()
                return
            }
            const filledPrompt = promptConfig.prompt.replace('{TICKER}', ticker)
            onPromptSelect(filledPrompt, {
                promptType: promptConfig.category,
                promptId: promptConfig.id
            })
            // Clear the ticker input after use
            setTickerInputs(prev => ({ ...prev, [promptConfig.id]: '' }))
        } else {
            onPromptSelect(promptConfig.prompt, {
                promptType: promptConfig.category,
                promptId: promptConfig.id
            })
        }
    }

    const handleTickerInput = (promptId: string, value: string) => {
        setTickerInputs(prev => ({ ...prev, [promptId]: value }))
    }

    const getIcon = (iconName: string) => {
        const Icon = ICON_MAP[iconName as keyof typeof ICON_MAP]
        return Icon ? <Icon className="w-4 h-4" /> : null
    }

    const categories = Object.entries(PROMPT_CATEGORIES) as [PromptCategory, typeof PROMPT_CATEGORIES[PromptCategory]][]

    return (
        <div className="space-y-3">
            {categories.map(([categoryKey, categoryInfo]) => {
                const isExpanded = expandedCategories.has(categoryKey)
                const categoryPrompts = PREDEFINED_PROMPTS.filter(p => p.category === categoryKey)
                const CategoryIcon = ICON_MAP[categoryInfo.icon as keyof typeof ICON_MAP]

                return (
                    <div key={categoryKey} className="border border-border/50 rounded-lg overflow-hidden bg-secondary/20">
                        <button
                            onClick={() => toggleCategory(categoryKey)}
                            className="w-full px-4 py-3 flex items-center justify-between hover:bg-secondary/50 transition-colors"
                        >
                            <div className="flex items-center gap-3">
                                <div className={cn(
                                    "p-2 rounded-md bg-gradient-to-br",
                                    categoryInfo.color
                                )}>
                                    {CategoryIcon && <CategoryIcon className="w-5 h-5 text-white" />}
                                </div>
                                <div className="text-left">
                                    <div className="font-semibold text-sm">{categoryInfo.title}</div>
                                    <div className="text-xs text-muted-foreground">{categoryInfo.description}</div>
                                </div>
                            </div>
                            {isExpanded ? (
                                <ChevronUp className="w-5 h-5 text-muted-foreground" />
                            ) : (
                                <ChevronDown className="w-5 h-5 text-muted-foreground" />
                            )}
                        </button>

                        {isExpanded && (
                            <div className="p-3 pt-0 space-y-2">
                                {categoryPrompts.map(promptConfig => (
                                    <div key={promptConfig.id} className="space-y-2">
                                        {promptConfig.requiresTicker && (
                                            <Input
                                                id={`ticker-${promptConfig.id}`}
                                                placeholder="Enter ticker (e.g., AAPL)"
                                                value={tickerInputs[promptConfig.id] || ''}
                                                onChange={(e) => handleTickerInput(promptConfig.id, e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') {
                                                        handlePromptClick(promptConfig)
                                                    }
                                                }}
                                                className="h-8 text-xs bg-background/50"
                                                disabled={isLoading}
                                            />
                                        )}
                                        <Button
                                            variant="prompt"
                                            size="sm"
                                            categoryColor={categoryInfo.color}
                                            onClick={() => handlePromptClick(promptConfig)}
                                            disabled={isLoading}
                                            className={cn(
                                                "w-full justify-start text-left h-auto py-2 px-3 relative",
                                                loadingPromptId === promptConfig.id && "opacity-75"
                                            )}
                                        >
                                            <div className="flex items-start gap-2 w-full">
                                                <div className="mt-0.5 shrink-0">
                                                    {loadingPromptId === promptConfig.id ? (
                                                        <Loader2 className="w-4 h-4 animate-spin" />
                                                    ) : (
                                                        getIcon(promptConfig.icon)
                                                    )}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="text-xs font-medium">{promptConfig.label}</div>
                                                    <div className="text-[10px] opacity-70 mt-0.5">
                                                        {loadingPromptId === promptConfig.id 
                                                            ? "Processing..." 
                                                            : promptConfig.description}
                                                    </div>
                                                </div>
                                            </div>
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )
            })}
        </div>
    )
}
