"use client"

import { useMemo } from "react"
import {
    Area,
    AreaChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from "recharts"
import { format } from "date-fns"
import { cn } from "@/lib/utils"

interface StockDataPoint {
    date: string
    price: number
    volume?: number
}

interface StockChartProps {
    data: StockDataPoint[]
    ticker: string
    period?: string
    color?: string
    className?: string
}

export function StockChart({
    data,
    ticker,
    period = "1M",
    color = "hsl(var(--primary))",
    className
}: StockChartProps) {

    const formattedData = useMemo(() => {
        return data.map(point => ({
            ...point,
            formattedDate: format(new Date(point.date), "MMM dd")
        }))
    }, [data])

    const startPrice = data[0]?.price || 0
    const endPrice = data[data.length - 1]?.price || 0
    const isPositive = endPrice >= startPrice

    const chartColor = isPositive ? "hsl(var(--bullish))" : "hsl(var(--bearish))"

    return (
        <div className={cn("w-full h-[300px] bg-card rounded-xl border border-border p-4", className)}>
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-bold text-lg">{ticker}</h3>
                    <div className={cn(
                        "text-sm font-medium flex items-center gap-2",
                        isPositive ? "text-bullish" : "text-bearish"
                    )}>
                        <span className="text-2xl font-bold text-foreground">
                            ${endPrice.toFixed(2)}
                        </span>
                        <span>
                            {isPositive ? "+" : ""}
                            {((endPrice - startPrice) / startPrice * 100).toFixed(2)}%
                        </span>
                    </div>
                </div>
                <div className="flex gap-2">
                    {["1D", "1W", "1M", "3M", "1Y"].map((p) => (
                        <button
                            key={p}
                            className={cn(
                                "px-2 py-1 text-xs rounded-md transition-colors",
                                period === p
                                    ? "bg-primary text-primary-foreground"
                                    : "bg-secondary text-muted-foreground hover:text-foreground"
                            )}
                        >
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={formattedData}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={chartColor} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={chartColor} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                        <XAxis
                            dataKey="formattedDate"
                            stroke="hsl(var(--muted-foreground))"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis
                            stroke="hsl(var(--muted-foreground))"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `$${value}`}
                            domain={['auto', 'auto']}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "hsl(var(--popover))",
                                borderColor: "hsl(var(--border))",
                                borderRadius: "8px",
                                color: "hsl(var(--popover-foreground))"
                            }}
                            itemStyle={{ color: chartColor }}
                            formatter={(value: number) => [`$${value.toFixed(2)}`, "Price"]}
                        />
                        <Area
                            type="monotone"
                            dataKey="price"
                            stroke={chartColor}
                            fillOpacity={1}
                            fill="url(#colorPrice)"
                            strokeWidth={2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}
