import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Position {
    id: string
    ticker: string
    shares: number
    entryPrice: number
    currentPrice?: number
    dateAdded: string
}

interface PortfolioState {
    positions: Position[]
    addPosition: (position: Omit<Position, 'id' | 'dateAdded'>) => void
    removePosition: (id: string) => void
    updatePosition: (id: string, updates: Partial<Position>) => void
    getTotalValue: () => number
    getTotalPL: () => number
}

export const usePortfolio = create<PortfolioState>()(
    persist(
        (set, get) => ({
            positions: [],

            addPosition: (position) => set((state) => ({
                positions: [
                    ...state.positions,
                    {
                        ...position,
                        id: Math.random().toString(36).substr(2, 9),
                        dateAdded: new Date().toISOString(),
                        currentPrice: position.currentPrice || position.entryPrice // Default to entry if not provided
                    }
                ]
            })),

            removePosition: (id) => set((state) => ({
                positions: state.positions.filter((p) => p.id !== id)
            })),

            updatePosition: (id, updates) => set((state) => ({
                positions: state.positions.map((p) =>
                    p.id === id ? { ...p, ...updates } : p
                )
            })),

            getTotalValue: () => {
                const { positions } = get()
                return positions.reduce((total, pos) => {
                    const price = pos.currentPrice || pos.entryPrice
                    return total + (pos.shares * price)
                }, 0)
            },

            getTotalPL: () => {
                const { positions } = get()
                return positions.reduce((total, pos) => {
                    const currentVal = pos.shares * (pos.currentPrice || pos.entryPrice)
                    const costBasis = pos.shares * pos.entryPrice
                    return total + (currentVal - costBasis)
                }, 0)
            }
        }),
        {
            name: 'trading-portfolio-storage',
        }
    )
)
