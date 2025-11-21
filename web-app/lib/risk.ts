import { Position } from "./hooks/usePortfolio"

export interface RiskMetrics {
    var: number
    sharpeRatio: number
    beta: number
    volatility: "Low" | "Medium" | "High"
    sectorExposure: Record<string, number>
}

export function calculateRiskMetrics(positions: Position[], totalValue: number): RiskMetrics {
    if (positions.length === 0 || totalValue === 0) {
        return {
            var: 0,
            sharpeRatio: 0,
            beta: 0,
            volatility: "Low",
            sectorExposure: {}
        }
    }

    // Calculate Sector Exposure
    const sectorExposure: Record<string, number> = {}
    positions.forEach(pos => {
        // Mock sector assignment based on ticker for demo purposes
        // In a real app, this would come from an API
        let sector = "Technology"
        if (["JPM", "BAC", "GS"].includes(pos.ticker)) sector = "Finance"
        if (["JNJ", "PFE", "UNH"].includes(pos.ticker)) sector = "Healthcare"
        if (["XOM", "CVX"].includes(pos.ticker)) sector = "Energy"
        if (["PG", "KO"].includes(pos.ticker)) sector = "Consumer"

        const value = pos.shares * pos.entryPrice
        sectorExposure[sector] = (sectorExposure[sector] || 0) + value
    })

    // Normalize exposure to percentage
    Object.keys(sectorExposure).forEach(key => {
        sectorExposure[key] = (sectorExposure[key] / totalValue) * 100
    })

    // Calculate Concentration Risk (Herfindahl-Hirschman Index - HHI)
    let hhi = 0
    Object.values(sectorExposure).forEach(pct => {
        hhi += (pct / 100) ** 2
    })

    // Estimate Volatility based on Concentration
    let volatility: "Low" | "Medium" | "High" = "Low"
    if (hhi > 0.25) volatility = "Medium"
    if (hhi > 0.5) volatility = "High"

    // Mock Beta calculation (weighted average of assumed betas)
    let weightedBeta = 0
    positions.forEach(pos => {
        // Mock beta values
        let beta = 1.0
        if (["NVDA", "TSLA", "AMD"].includes(pos.ticker)) beta = 1.8
        if (["AAPL", "MSFT", "GOOGL"].includes(pos.ticker)) beta = 1.2
        if (["JNJ", "PG", "KO"].includes(pos.ticker)) beta = 0.6

        const weight = (pos.shares * pos.entryPrice) / totalValue
        weightedBeta += beta * weight
    })

    // Value at Risk (Parametric VaR at 95% confidence)
    // Assuming daily volatility of 1.5% for the portfolio
    const dailyVolatility = 0.015 * (volatility === "High" ? 1.5 : volatility === "Medium" ? 1.2 : 1.0)
    const zScore95 = 1.645
    const varValue = totalValue * dailyVolatility * zScore95

    // Sharpe Ratio (Assumed annual return 10%, risk-free 4%)
    const annualReturn = 0.10
    const annualVolatility = dailyVolatility * Math.sqrt(252)
    const riskFreeRate = 0.04
    const sharpeRatio = (annualReturn - riskFreeRate) / annualVolatility

    return {
        var: varValue,
        sharpeRatio: parseFloat(sharpeRatio.toFixed(2)),
        beta: parseFloat(weightedBeta.toFixed(2)),
        volatility,
        sectorExposure
    }
}
