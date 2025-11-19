export type PromptCategory = 'quick_wins' | 'analysis' | 'risk' | 'market'

export interface PromptConfig {
    id: string
    category: PromptCategory
    label: string
    prompt: string
    description: string
    icon: string
    requiresTicker?: boolean
}

export const PROMPT_CATEGORIES = {
    quick_wins: {
        title: "Quick Wins",
        description: "Immediate profit opportunities",
        color: "from-green-500 to-emerald-600",
        icon: "TrendingUp"
    },
    analysis: {
        title: "Deep Analysis",
        description: "Detailed stock evaluation",
        color: "from-blue-500 to-cyan-600",
        icon: "LineChart"
    },
    risk: {
        title: "Risk Management",
        description: "Risk assessment tools",
        color: "from-amber-500 to-orange-600",
        icon: "Shield"
    },
    market: {
        title: "Market Intelligence",
        description: "Market context & trends",
        color: "from-purple-500 to-pink-600",
        icon: "Globe"
    }
} as const

export const PREDEFINED_PROMPTS: PromptConfig[] = [
    // Quick Wins
    {
        id: "top-3-stocks",
        category: "quick_wins",
        label: "Top 3 Stocks to Buy Today",
        prompt: "Show me the top 3 stocks to buy TODAY with clear justification, entry points, and confidence scores.",
        description: "AI-powered picks with multi-agent validation",
        icon: "Star"
    },
    {
        id: "breakout-stocks",
        category: "quick_wins",
        label: "Stocks Breaking Out Now",
        prompt: "What stocks are breaking out right now? Show me momentum plays with technical breakout patterns and news catalysts.",
        description: "Identify momentum opportunities",
        icon: "Rocket"
    },
    {
        id: "undervalued-ready",
        category: "quick_wins",
        label: "Undervalued Stocks Ready to Move",
        prompt: "Find me undervalued stocks that are ready to move. Look for value plays with positive catalysts and reversal signals.",
        description: "Value + catalyst screening",
        icon: "TrendingUp"
    },

    // Deep Analysis
    {
        id: "analyze-ticker",
        category: "analysis",
        label: "Should I Buy This Stock?",
        prompt: "Analyze {TICKER} - should I buy it? Provide a comprehensive multi-agent analysis with buy/hold/sell recommendation.",
        description: "Full analysis with recommendation",
        icon: "Search",
        requiresTicker: true
    },
    {
        id: "bull-bear-case",
        category: "analysis",
        label: "Bullish vs Bearish Cases",
        prompt: "What are the bullish and bearish cases for {TICKER}? Show me both sides with detailed reasoning and a confidence score.",
        description: "Debate-style analysis",
        icon: "Scale",
        requiresTicker: true
    },
    {
        id: "technical-setup",
        category: "analysis",
        label: "Technical Setup Analysis",
        prompt: "Show me the technical setup for {TICKER}. Include chart patterns, key support/resistance levels, indicators, entry point, stop loss, and price targets.",
        description: "Chart patterns & indicators",
        icon: "LineChart",
        requiresTicker: true
    },
    {
        id: "fundamental-deep-dive",
        category: "analysis",
        label: "Fundamental Deep Dive",
        prompt: "Give me a fundamental analysis of {TICKER}. Cover financials, valuation metrics, growth prospects, and competitive position.",
        description: "Financial health check",
        icon: "FileText",
        requiresTicker: true
    },

    // Risk Management
    {
        id: "risk-assessment",
        category: "risk",
        label: "What's the Risk?",
        prompt: "What's the risk on {TICKER}? Provide a risk score, potential downside scenarios, and recommended position sizing.",
        description: "Downside analysis",
        icon: "AlertTriangle",
        requiresTicker: true
    },
    {
        id: "exit-signal",
        category: "risk",
        label: "Should I Exit?",
        prompt: "Should I exit {TICKER}? Re-analyze the stock and tell me if I should hold or sell with clear reasoning.",
        description: "Hold or sell decision",
        icon: "DoorOpen",
        requiresTicker: true
    },
    {
        id: "stop-loss-target",
        category: "risk",
        label: "Stop Loss & Price Targets",
        prompt: "Calculate optimal stop loss and price targets for {TICKER} based on technical analysis and volatility.",
        description: "Entry/exit levels",
        icon: "Target",
        requiresTicker: true
    },

    // Market Intelligence
    {
        id: "market-movers",
        category: "market",
        label: "What's Moving the Market?",
        prompt: "What's moving the market today? Show me key market drivers, news events, and how they're affecting stocks.",
        description: "Daily market drivers",
        icon: "Activity"
    },
    {
        id: "hot-sectors",
        category: "market",
        label: "Hot Sectors Right Now",
        prompt: "What sectors are hot right now? Identify trending sectors with specific stock picks in each.",
        description: "Sector rotation plays",
        icon: "Layers"
    },
    {
        id: "news-catalysts",
        category: "market",
        label: "Stocks with Positive Catalysts",
        prompt: "Show me stocks with positive news catalysts today that could drive price movement.",
        description: "News-driven opportunities",
        icon: "Newspaper"
    },
    {
        id: "earnings-this-week",
        category: "market",
        label: "Key Earnings This Week",
        prompt: "What are the most important earnings reports this week and which stocks should I watch?",
        description: "Earnings calendar highlights",
        icon: "Calendar"
    }
]
