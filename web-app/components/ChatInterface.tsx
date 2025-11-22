/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import * as React from "react"
import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Loader2, ThumbsUp, ThumbsDown, BookmarkPlus, X, Volume2, VolumeX } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { motion, AnimatePresence } from "framer-motion"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PromptCategories } from "@/components/PromptCategories"
import { VoiceInput } from "@/components/VoiceInput"
import { cn } from "@/lib/utils"
import { useAnalysis } from "@/lib/hooks/useAnalysis"
import { api } from "@/lib/api/client"

export function ChatInterface() {
    const {
        messages,
        isLoading,
        isThinking,
        activeTools,
        thinkingMessage,
        conversationId,
        sendMessage
    } = useAnalysis()

    const [input, setInput] = useState("")
    const [showPromptsPanel, setShowPromptsPanel] = useState(true)
    const [voiceError, setVoiceError] = useState<string | null>(null)
    const [loadingPromptId, setLoadingPromptId] = useState<string | null>(null)

    const messagesEndRef = useRef<HTMLDivElement>(null)
    const audioRefs = useRef<Record<string, HTMLAudioElement>>({})
    const [playingAudio, setPlayingAudio] = useState<Record<string, boolean>>({})
    const [feedbackGiven, setFeedbackGiven] = useState<Record<string, boolean>>({})

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages, isThinking])

    // Hide prompts panel after first user interaction
    useEffect(() => {
        if (messages.length > 1 && showPromptsPanel) {
            setShowPromptsPanel(false)
        }
    }, [messages.length])

    // Cleanup audio on unmount
    useEffect(() => {
        return () => {
            Object.values(audioRefs.current).forEach(audio => {
                audio.pause()
                audio.src = ""
            })
        }
    }, [])

    const handleSendMessage = async (text: string, metadata?: { promptType: string, promptId: string }) => {
        if (!text.trim() || isLoading) return

        if (metadata?.promptId) {
            setLoadingPromptId(metadata.promptId)
        }

        setInput("")
        await sendMessage(text, metadata)
        setLoadingPromptId(null)
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        handleSendMessage(input)
    }

    const handlePlayVoice = async (messageId: string, text: string) => {
        if (playingAudio[messageId]) {
            const audio = audioRefs.current[messageId]
            if (audio) {
                audio.pause()
                audio.currentTime = 0
            }
            setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
            return
        }

        try {
            setPlayingAudio(prev => ({ ...prev, [messageId]: true }))

            const audioBlob = await api.synthesizeVoice(text)
            
            // Verify blob is valid before creating URL
            if (!audioBlob || audioBlob.size === 0) {
                throw new Error("Invalid audio blob received")
            }
            
            const audioUrl = URL.createObjectURL(audioBlob)

            const audio = new Audio(audioUrl)
            audioRefs.current[messageId] = audio

            // Barge-in detection
            let bargeInDetected = false
            let initialInput = input

            const checkBargeIn = () => {
                if (input !== initialInput || isLoading) {
                    bargeInDetected = true
                    audio.pause()
                    audio.currentTime = 0
                    setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
                }
            }

            const bargeInInterval = setInterval(checkBargeIn, 100)

            audio.onended = () => {
                clearInterval(bargeInInterval)
                setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
                URL.revokeObjectURL(audioUrl)
            }

            audio.onerror = (e) => {
                clearInterval(bargeInInterval)
                console.error("Audio playback error:", e)
                setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
                URL.revokeObjectURL(audioUrl)
                // Show user-friendly error
                if (typeof window !== "undefined" && (window as any).toast) {
                    (window as any).toast.error("Failed to play audio. Please try again.")
                }
            }

            await audio.play()
        } catch (error) {
            console.error("Error playing voice:", error)
            setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
            // Show user-friendly error message
            const errorMessage = error instanceof Error ? error.message : String(error)
            if (errorMessage.includes("RIFF")) {
                console.error("Audio format error - this should not happen with the fixed API client")
            }
        }
    }

    const handleFeedback = async (messageId: string, rating: number) => {
        if (!messageId || feedbackGiven[messageId]) return

        try {
            await api.sendFeedback({
                conversation_id: conversationId,
                message_id: messageId,
                rating: rating,
                comment: rating > 3 ? "Helpful" : "Not helpful"
            })
            setFeedbackGiven(prev => ({ ...prev, [messageId]: true }))
        } catch (error) {
            console.error("Error sending feedback:", error)
        }
    }

    return (
        <div className="flex h-full gap-6">
            {/* Chat Area */}
            <div className="flex flex-col flex-1 min-w-0 bg-card rounded-xl border border-border shadow-sm overflow-hidden">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
                    <AnimatePresence initial={false}>
                        {messages.map((msg, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={cn(
                                    "flex gap-4",
                                    msg.role === "user" ? "flex-row-reverse" : "flex-row"
                                )}
                            >
                                <div className={cn(
                                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                                    msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
                                )}>
                                    {msg.role === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                                </div>

                                <div className={cn(
                                    "rounded-lg p-4 max-w-[85%]",
                                    msg.role === "user"
                                        ? "bg-primary text-primary-foreground"
                                        : "bg-secondary/50 border border-border"
                                )}>
                                    <div className="prose prose-invert prose-sm max-w-none">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                table: ({ node, ...props }) => (
                                                    <div className="overflow-x-auto my-4 rounded-lg border border-border/50 shadow-lg">
                                                        <table className="min-w-full" {...props} />
                                                    </div>
                                                ),
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>

                                    {msg.role === "assistant" && msg.id !== "welcome" && (
                                        <div className="flex gap-2 mt-2 pt-2 border-t border-border/50">
                                            <button
                                                onClick={() => msg.id && handlePlayVoice(msg.id, msg.content)}
                                                className={cn(
                                                    "text-xs flex items-center gap-1 transition-colors",
                                                    playingAudio[msg.id || ""]
                                                        ? "text-primary hover:text-primary/80"
                                                        : "text-muted-foreground hover:text-primary"
                                                )}
                                            >
                                                {playingAudio[msg.id || ""] ? (
                                                    <>
                                                        <VolumeX className="w-3 h-3" /> Stop
                                                    </>
                                                ) : (
                                                    <>
                                                        <Volume2 className="w-3 h-3" /> Play Voice
                                                    </>
                                                )}
                                            </button>
                                            <button
                                                onClick={() => msg.id && handleFeedback(msg.id, 5)}
                                                disabled={msg.id ? feedbackGiven[msg.id] : false}
                                                className={cn(
                                                    "text-xs flex items-center gap-1 transition-colors",
                                                    msg.id && feedbackGiven[msg.id] ? "text-muted-foreground cursor-not-allowed" : "text-muted-foreground hover:text-green-400"
                                                )}
                                            >
                                                <ThumbsUp className="w-3 h-3" /> Helpful
                                            </button>
                                            <button
                                                onClick={() => msg.id && handleFeedback(msg.id, 1)}
                                                disabled={msg.id ? feedbackGiven[msg.id] : false}
                                                className={cn(
                                                    "text-xs flex items-center gap-1 transition-colors",
                                                    msg.id && feedbackGiven[msg.id] ? "text-muted-foreground cursor-not-allowed" : "text-muted-foreground hover:text-red-400"
                                                )}
                                            >
                                                <ThumbsDown className="w-3 h-3" /> Not Helpful
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {/* Thinking State */}
                    <AnimatePresence>
                        {isThinking && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="flex gap-4"
                            >
                                <div className="w-8 h-8 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center shrink-0">
                                    <Bot className="w-5 h-5" />
                                </div>
                                <div className="bg-secondary/50 border border-border rounded-lg p-4 flex-1 max-w-[85%]">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                                        <span className="text-sm font-medium">{thinkingMessage}</span>
                                    </div>
                                    {activeTools.length > 0 && (
                                        <div className="mt-2 space-y-1">
                                            {activeTools.map((tool, idx) => (
                                                <motion.div
                                                    key={idx}
                                                    initial={{ opacity: 0, x: -10 }}
                                                    animate={{ opacity: 1, x: 0 }}
                                                    className="text-xs text-muted-foreground flex items-center gap-2"
                                                >
                                                    <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                                                    <span className="font-mono">{tool}</span>
                                                </motion.div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-border bg-card/50 backdrop-blur-sm">
                    {voiceError && (
                        <div className="mb-2 p-2 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive flex items-center justify-between">
                            <span>{voiceError}</span>
                            <X className="w-3 h-3 cursor-pointer" onClick={() => setVoiceError(null)} />
                        </div>
                    )}
                    <form onSubmit={handleSubmit} className="flex gap-2 relative">
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask about stocks, strategies, or market concepts..."
                            className="flex-1 pr-12 py-6 bg-secondary/30 border-border focus-visible:ring-primary/20"
                            disabled={isLoading}
                        />
                        <VoiceInput
                            onTranscription={(text) => {
                                setInput(text)
                                setVoiceError(null)
                                handleSendMessage(text)
                            }}
                            onError={(error) => {
                                setVoiceError(error)
                                setTimeout(() => setVoiceError(null), 8000)
                            }}
                            className="shrink-0"
                        />
                        <Button
                            type="submit"
                            size="icon"
                            className="absolute right-1 top-1 h-10 w-10"
                            disabled={!input.trim() || isLoading}
                        >
                            <Send className="w-4 h-4" />
                        </Button>
                    </form>
                </div>
            </div>

            {/* Right Sidebar (Prompts) */}
            <div className="relative">
                <Button
                    variant="ghost"
                    size="icon"
                    className="absolute -left-10 top-0 z-10 bg-card border border-border shadow-sm rounded-r-none"
                    onClick={() => setShowPromptsPanel(!showPromptsPanel)}
                    title={showPromptsPanel ? "Hide Prompts" : "Show Prompts"}
                >
                    {showPromptsPanel ? <X className="w-4 h-4" /> : <BookmarkPlus className="w-4 h-4" />}
                </Button>

                <AnimatePresence>
                    {showPromptsPanel && (
                        <motion.div
                            initial={{ width: 0, opacity: 0 }}
                            animate={{ width: 320, opacity: 1 }}
                            exit={{ width: 0, opacity: 0 }}
                            className="h-full border border-border rounded-xl bg-card shadow-sm overflow-hidden"
                        >
                            <div className="w-[320px] h-full flex flex-col">
                                <div className="p-4 border-b border-border">
                                    <h2 className="font-semibold">Quick Actions</h2>
                                    <p className="text-xs text-muted-foreground">Select a prompt to start</p>
                                </div>
                                <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                                    <PromptCategories
                                        onPromptSelect={handleSendMessage}
                                        isLoading={isLoading}
                                        loadingPromptId={loadingPromptId}
                                    />
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    )
}
