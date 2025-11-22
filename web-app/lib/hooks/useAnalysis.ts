/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

import { useState, useCallback, useRef } from "react"
import { api } from "../api/client"
import { Message, ChatRequest } from "../api/types"
import { toast } from "react-hot-toast"

interface UseAnalysisReturn {
    messages: Message[]
    isLoading: boolean
    isThinking: boolean
    activeTools: string[]
    thinkingMessage: string
    conversationId: string
    sendMessage: (text: string, metadata?: { promptType: string, promptId: string }) => Promise<void>
    resetAnalysis: () => void
}

export function useAnalysis(): UseAnalysisReturn {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "Hello! I'm Eddie, your advanced trading assistant. I can analyze stocks, explain trading concepts, and help you manage your portfolio. How can I help you today?",
            id: "welcome"
        }
    ])
    const [isLoading, setIsLoading] = useState(false)
    const [isThinking, setIsThinking] = useState(false)
    const [activeTools, setActiveTools] = useState<string[]>([])
    const [thinkingMessage, setThinkingMessage] = useState("")
    const [conversationId, setConversationId] = useState<string>("new_session")

    const abortControllerRef = useRef<AbortController | null>(null)

    const resetAnalysis = useCallback(() => {
        setMessages([
            {
                role: "assistant",
                content: "Hello! I'm Eddie, your advanced trading assistant. I can analyze stocks, explain trading concepts, and help you manage your portfolio. How can I help you today?",
                id: "welcome"
            }
        ])
        setConversationId("new_session")
        setIsLoading(false)
        setIsThinking(false)
        setActiveTools([])
    }, [])

    const sendMessage = useCallback(async (text: string, metadata?: { promptType: string, promptId: string }) => {
        if (!text.trim() || isLoading) return

        const userMessage: Message = { role: "user", content: text }
        setMessages(prev => [...prev, userMessage])
        setIsLoading(true)
        setIsThinking(true)
        setThinkingMessage("Coordinating agents...")
        setActiveTools([])

        // Initialize streaming message
        const assistantMessageId = `msg-${Date.now()}`
        setMessages(prev => [...prev, {
            role: "assistant",
            content: "",
            id: assistantMessageId
        }])

        // Create new abort controller
        if (abortControllerRef.current) {
            abortControllerRef.current.abort()
        }
        abortControllerRef.current = new AbortController()

        try {
            const requestBody: ChatRequest = {
                message: text,
                conversation_history: messages,
                conversation_id: conversationId,
                prompt_type: metadata?.promptType,
                prompt_id: metadata?.promptId
            }

            const response = await fetch(api.getStreamUrl(), {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody),
                signal: abortControllerRef.current.signal
            })

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`)
            }

            const reader = response.body?.getReader()
            const decoder = new TextDecoder()
            let buffer = ""
            let fullContent = ""

            if (!reader) throw new Error("No response body")

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split("\n")
                buffer = lines.pop() || ""

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.slice(6))

                            switch (data.type) {
                                case "connected":
                                    break

                                case "progress":
                                    setIsThinking(true)
                                    setActiveTools(data.tools || [])
                                    setThinkingMessage(data.message || "Processing...")
                                    break

                                case "tools_completed":
                                    setActiveTools([])
                                    setThinkingMessage("Processing results...")
                                    break

                                case "content":
                                    setIsThinking(false)
                                    fullContent += data.chunk
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === assistantMessageId
                                            ? { ...msg, content: fullContent }
                                            : msg
                                    ))
                                    break

                                case "done":
                                    if (data.conversation_id) {
                                        setConversationId(data.conversation_id)
                                    }
                                    setMessages(prev => prev.map(msg =>
                                        msg.id === assistantMessageId
                                            ? {
                                                ...msg,
                                                content: fullContent,
                                                id: data.metadata?.interaction_id
                                                    ? String(data.metadata.interaction_id)
                                                    : assistantMessageId
                                            }
                                            : msg
                                    ))
                                    setIsThinking(false)
                                    setActiveTools([])
                                    break

                                case "error":
                                    throw new Error(data.message || "Stream error")
                            }
                        } catch (e) {
                            console.error("Error parsing SSE data:", e)
                        }
                    }
                }
            }

        } catch (error) {
            const err = error as Error
            if (err.name === 'AbortError') return

            console.error("Analysis Error:", err)
            toast.error("Failed to complete analysis")

            setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                    ? {
                        ...msg,
                        content: msg.content || "I apologize, but I encountered an error. Please try again."
                    }
                    : msg
            ))
        } finally {
            setIsLoading(false)
            setIsThinking(false)
            setActiveTools([])
            abortControllerRef.current = null
        }
    }, [conversationId, messages, isLoading])

    return {
        messages,
        isLoading,
        isThinking,
        activeTools,
        thinkingMessage,
        conversationId,
        sendMessage,
        resetAnalysis
    }
}
