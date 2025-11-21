import { useState, useEffect } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"
import { TrendingUp, Target, Award, MessageSquare, ThumbsUp, Zap, Loader2 } from "lucide-react"
import { api } from "@/lib/api/client"
import { PromptAnalytics, PortfolioPerformance } from "@/lib/api/types"
import { toast } from "react-hot-toast"

export function AnalyticsView() {
    const [promptAnalytics, setPromptAnalytics] = useState<PromptAnalytics | null>(null)
    const [portfolioPerformance, setPortfolioPerformance] = useState<PortfolioPerformance | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                setIsLoading(true)
                const [promptData, performanceData] = await Promise.all([
                    api.getPromptAnalytics(),
                    api.getPortfolioPerformance()
                ])
                setPromptAnalytics(promptData)
                setPortfolioPerformance(performanceData)
            } catch (error) {
                console.error("Failed to fetch analytics:", error)
                toast.error("Failed to load analytics. Using sample data.")
                // Set fallback data
                setPortfolioPerformance({
                    monthly_returns: [
                        { month: "Jan", return: 5.2 },
                        { month: "Feb", return: -2.1 },
                        { month: "Mar", return: 8.4 },
                        { month: "Apr", return: 3.7 },
                        { month: "May", return: 1.2 },
                        { month: "Jun", return: 6.5 },
                    ],
                    sector_allocation: [
                        { name: "Technology", value: 45 },
                        { name: "Finance", value: 20 },
                        { name: "Healthcare", value: 15 },
                        { name: "Consumer", value: 10 },
                        { name: "Cash", value: 10 },
                    ],
                    ytd_return: 24.5,
                    win_rate: 68.4,
                    profit_factor: 2.15
                })
            } finally {
                setIsLoading(false)
            }
        }
        fetchAnalytics()
    }, [])

    const COLORS = ["#00C805", "#FF6B6B", "#3B82F6", "#F59E0B", "#9CA3AF"]

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                <span className="ml-3 text-muted-foreground">Loading analytics...</span>
            </div>
        )
    }

    return (
        <div className="space-y-6">
            {/* Key Performance Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <TrendingUp className="w-4 h-4" />
                        <span className="text-sm font-medium">YTD Return</span>
                    </div>
                    <div className="text-3xl font-bold font-mono text-bullish">
                        +{portfolioPerformance?.ytd_return?.toFixed(1) || "0.0"}%
                    </div>
                </div>
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <Target className="w-4 h-4" />
                        <span className="text-sm font-medium">Win Rate</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">
                        {portfolioPerformance?.win_rate?.toFixed(1) || "0.0"}%
                    </div>
                </div>
                <div className="bg-card border border-border rounded-xl p-6">
                    <div className="flex items-center gap-2 text-muted-foreground mb-2">
                        <Award className="w-4 h-4" />
                        <span className="text-sm font-medium">Profit Factor</span>
                    </div>
                    <div className="text-3xl font-bold font-mono">
                        {portfolioPerformance?.profit_factor?.toFixed(2) || "0.00"}
                    </div>
                </div>
            </div>

            {/* Prompt Analytics Section */}
            {promptAnalytics && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-card border border-border rounded-xl p-6">
                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                            <MessageSquare className="w-4 h-4" />
                            <span className="text-sm font-medium">Total Prompts</span>
                        </div>
                        <div className="text-3xl font-bold font-mono">{promptAnalytics.total_prompts}</div>
                    </div>
                    <div className="bg-card border border-border rounded-xl p-6">
                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                            <ThumbsUp className="w-4 h-4" />
                            <span className="text-sm font-medium">Avg Rating</span>
                        </div>
                        <div className="text-3xl font-bold font-mono text-primary">
                            {promptAnalytics.avg_rating.toFixed(1)}
                            <span className="text-sm text-muted-foreground font-normal ml-1">/ 5.0</span>
                        </div>
                    </div>
                    <div className="bg-card border border-border rounded-xl p-6">
                        <div className="flex items-center gap-2 text-muted-foreground mb-2">
                            <Zap className="w-4 h-4" />
                            <span className="text-sm font-medium">Top Category</span>
                        </div>
                        <div className="text-lg font-bold truncate">
                            {Object.entries(promptAnalytics.popular_categories).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A"}
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-card border border-border rounded-xl p-6 h-[400px]">
                    <h3 className="font-semibold mb-6">Monthly Performance</h3>
                    <ResponsiveContainer width="100%" height="85%">
                        <BarChart data={portfolioPerformance?.monthly_returns || []}>
                            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                            <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                            <Tooltip
                                contentStyle={{ backgroundColor: "hsl(var(--popover))", borderColor: "hsl(var(--border))", borderRadius: "8px" }}
                                cursor={{ fill: "hsl(var(--secondary))", opacity: 0.2 }}
                            />
                            <Bar dataKey="return" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 h-[400px]">
                    <h3 className="font-semibold mb-6">Asset Allocation</h3>
                    <ResponsiveContainer width="100%" height="85%">
                        <PieChart>
                            <Pie
                                data={portfolioPerformance?.sector_allocation || []}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={100}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {(portfolioPerformance?.sector_allocation || []).map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: "hsl(var(--popover))", borderColor: "hsl(var(--border))", borderRadius: "8px" }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="flex justify-center gap-4 flex-wrap mt-4">
                        {(portfolioPerformance?.sector_allocation || []).map((entry, index) => (
                            <div key={entry.name} className="flex items-center gap-2 text-xs">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                                <span>{entry.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Asset Comparison Section */}
            <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Target className="w-4 h-4" /> Asset Comparison
                </h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="font-medium text-muted-foreground">Metric</div>
                    <div className="font-bold text-center">NVDA</div>
                    <div className="font-bold text-center">AMD</div>

                    <div className="text-muted-foreground border-t border-border pt-2">YTD Return</div>
                    <div className="text-center border-t border-border pt-2 text-bullish">+165.4%</div>
                    <div className="text-center border-t border-border pt-2 text-bullish">+45.2%</div>

                    <div className="text-muted-foreground border-t border-border pt-2">Volatility (30d)</div>
                    <div className="text-center border-t border-border pt-2">45.2%</div>
                    <div className="text-center border-t border-border pt-2">38.7%</div>

                    <div className="text-muted-foreground border-t border-border pt-2">P/E Ratio</div>
                    <div className="text-center border-t border-border pt-2">72.5</div>
                    <div className="text-center border-t border-border pt-2">145.2</div>

                    <div className="text-muted-foreground border-t border-border pt-2">Analyst Rating</div>
                    <div className="text-center border-t border-border pt-2 text-bullish">Strong Buy</div>
                    <div className="text-center border-t border-border pt-2 text-primary">Buy</div>
                </div>
            </div>
        </div>
    )
}
