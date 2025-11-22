/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api } from './client'

describe('ApiClient', () => {
    const mockFetch = vi.fn()
    global.fetch = mockFetch

    beforeEach(() => {
        mockFetch.mockReset()
    })

    it('sends chat message correctly', async () => {
        const mockResponse = {
            response: "Hello",
            conversation_id: "123"
        }

        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve(mockResponse)
        })

        const result = await api.chat({ message: 'Hello', conversation_history: [] })

        expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/chat'),
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ message: 'Hello', conversation_history: [] })
            })
        )
        expect(result).toEqual(mockResponse)
    })

    it('handles analysis request correctly', async () => {
        const mockAnalysis = {
            ticker: 'AAPL',
            analysis: 'Buy',
            confidence: 0.9
        }

        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve(mockAnalysis)
        })

        const result = await api.analyze({ ticker: 'AAPL', analysts: ['market'] })

        expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/analyze'),
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ ticker: 'AAPL', analysts: ['market'] })
            })
        )
        expect(result).toEqual(mockAnalysis)
    })
})
