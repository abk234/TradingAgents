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

interface Message {
    role: "user" | "assistant"
    content: string
    id?: string
}

interface ThinkingState {
    isThinking: boolean
    activeTools: string[]
    message: string
}

export function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "Hello! I'm Eddie, your advanced trading assistant. I can analyze stocks, explain trading concepts, and help you manage your portfolio. How can I help you today?",
            id: "welcome"
        }
    ])
    const [input, setInput] = useState("")
    const [isLoading, setIsLoading] = useState(false)
    const [loadingPromptId, setLoadingPromptId] = useState<string | null>(null)
    const [conversationId, setConversationId] = useState<string>("new_session")
    const [showPromptsPanel, setShowPromptsPanel] = useState(true)
    const [thinking, setThinking] = useState<ThinkingState>({
        isThinking: false,
        activeTools: [],
        message: ""
    })
    const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null)
    const [voiceError, setVoiceError] = useState<string | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    // Cleanup audio on unmount
    useEffect(() => {
        return () => {
            Object.values(audioRefs.current).forEach(audio => {
                audio.pause()
                audio.src = ""
            })
        }
    }, [])

    const sendMessage = async (text: string, metadata?: { promptType: string, promptId: string }) => {
        if (!text.trim() || isLoading) return

        const userMessage: Message = { role: "user", content: text }
        setMessages(prev => [...prev, userMessage])
        setInput("")
        setIsLoading(true)
        
        // Set loading state for specific prompt if metadata provided
        if (metadata?.promptId) {
            setLoadingPromptId(metadata.promptId)
        }

        // Hide prompts panel after first message
        if (messages.length === 1) {
            setShowPromptsPanel(false)
        }

        // Initialize streaming message
        const assistantMessageId = `msg-${Date.now()}`
        setStreamingMessageId(assistantMessageId)
        setMessages(prev => [...prev, {
            role: "assistant",
            content: "",
            id: assistantMessageId
        }])
        setThinking({ isThinking: true, activeTools: [], message: "Coordinating agents..." })

        try {
            // Call streaming API
            const requestBody: any = {
                message: userMessage.content,
                conversation_history: messages.map(m => ({ role: m.role, content: m.content })),
                conversation_id: conversationId
            }

            // Add prompt metadata if available
            if (metadata) {
                requestBody.prompt_type = metadata.promptType
                requestBody.prompt_id = metadata.promptId
            }

            const response = await fetch("http://127.0.0.1:8005/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody)
            })

            if (!response.ok) {
                const errorText = await response.text()
                console.error("API Error:", response.status, errorText)
                throw new Error(`Failed to fetch response: ${response.status} ${errorText}`)
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
                            
                            if (data.type === "connected") {
                                // Connection established, continue
                                continue
                            } else if (data.type === "progress") {
                                // Update thinking state with active tools
                                setThinking({
                                    isThinking: true,
                                    activeTools: data.tools || [],
                                    message: data.message || "Coordinating agents..."
                                })
                            } else if (data.type === "tools_completed") {
                                // Tools completed, still thinking but preparing response
                                setThinking({
                                    isThinking: true,
                                    activeTools: [],
                                    message: "Processing results..."
                                })
                            } else if (data.type === "content") {
                                // Hide thinking when content starts
                                setThinking(prev => prev.isThinking ? { isThinking: false, activeTools: [], message: "" } : prev)
                                // Append content chunk
                                fullContent += data.chunk
                                setMessages(prev => prev.map(msg => 
                                    msg.id === assistantMessageId 
                                        ? { ...msg, content: fullContent }
                                        : msg
                                ))
                            } else if (data.type === "done") {
                                // Streaming complete
                                if (data.conversation_id) {
                                    setConversationId(data.conversation_id)
                                }
                                // Update final message with metadata
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
                                setThinking({ isThinking: false, activeTools: [], message: "" })
                            } else if (data.type === "error") {
                                // Handle error from stream
                                const errorMsg = data.message || "An error occurred while processing your request"
                                setMessages(prev => prev.map(msg => 
                                    msg.id === assistantMessageId 
                                        ? { ...msg, content: msg.content || errorMsg }
                                        : msg
                                ))
                                setThinking({ isThinking: false, activeTools: [], message: "" })
                                break // Stop reading stream on error
                            }
                        } catch (e) {
                            console.error("Error parsing SSE data:", e)
                        }
                    }
                }
            }

        } catch (error) {
            console.error("Error:", error)
            const errorMessage = error instanceof Error 
                ? error.message 
                : "I apologize, but I encountered an error connecting to the server. Please ensure the backend API is running."
            
            setMessages(prev => prev.map(msg => 
                msg.id === assistantMessageId 
                    ? { 
                        ...msg, 
                        content: msg.content || errorMessage
                    }
                    : msg
            ))
            setThinking({ isThinking: false, activeTools: [], message: "" })
        } finally {
            setIsLoading(false)
            setLoadingPromptId(null)
            setStreamingMessageId(null)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        sendMessage(input)
    }

    const [feedbackGiven, setFeedbackGiven] = useState<Record<string, boolean>>({})
    const [playingAudio, setPlayingAudio] = useState<Record<string, boolean>>({})
    const audioRefs = useRef<Record<string, HTMLAudioElement>>({})

    const handlePlayVoice = async (messageId: string, text: string) => {
        if (playingAudio[messageId]) {
            // Stop playback (barge-in)
            const audio = audioRefs.current[messageId]
            if (audio) {
                audio.pause()
                audio.currentTime = 0
            }
            setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
            
            // Notify that user interrupted (barge-in)
            console.log("Barge-in: User stopped audio playback")
            return
        }

        try {
            setPlayingAudio(prev => ({ ...prev, [messageId]: true }))
            
            // Call voice synthesis API
            const response = await fetch("http://127.0.0.1:8005/voice/synthesize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: text,
                    tone: "professional",
                    return_base64: false
                })
            })

            if (!response.ok) {
                throw new Error("Failed to synthesize speech")
            }

            // Get audio blob
            const audioBlob = await response.blob()
            const audioUrl = URL.createObjectURL(audioBlob)
            
            // Create audio element and play
            const audio = new Audio(audioUrl)
            audioRefs.current[messageId] = audio
            
            // Set up barge-in detection (v2.0)
            let bargeInDetected = false
            let initialInput = input  // Capture input at start of playback
            
            const checkBargeIn = () => {
                // Simple barge-in: if user starts typing or sends message, stop audio
                // More sophisticated detection would use microphone monitoring
                const currentInput = input
                if (currentInput !== initialInput || isLoading) {
                    bargeInDetected = true
                    audio.pause()
                    audio.currentTime = 0
                    setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
                }
            }
            
            // Monitor for barge-in (check every 100ms)
            const bargeInInterval = setInterval(checkBargeIn, 100)
            
            audio.onended = () => {
                clearInterval(bargeInInterval)
                setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
                URL.revokeObjectURL(audioUrl)
            }
            
            audio.onerror = () => {
                clearInterval(bargeInInterval)
                setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
                URL.revokeObjectURL(audioUrl)
                console.error("Error playing audio")
            }
            
            audio.onpause = () => {
                if (bargeInDetected) {
                    clearInterval(bargeInInterval)
                    console.log("Audio paused due to barge-in")
                }
            }
            
            await audio.play()
        } catch (error) {
            console.error("Error synthesizing speech:", error)
            setPlayingAudio(prev => ({ ...prev, [messageId]: false }))
            alert("Voice synthesis failed. Make sure TTS is installed: pip install TTS")
        }
    }

    const handleFeedback = async (messageId: string, rating: number) => {
        if (!messageId || feedbackGiven[messageId]) return

        try {
            const response = await fetch("http://127.0.0.1:8005/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    message_id: messageId,
                    rating: rating,
                    comment: rating > 3 ? "Helpful" : "Not helpful"
                })
            })

            if (response.ok) {
                setFeedbackGiven(prev => ({ ...prev, [messageId]: true }))
            }
        } catch (error) {
            console.error("Error sending feedback:", error)
        }
    }

    return (
        <div className="flex h-screen max-w-7xl mx-auto">
            {/* Main Chat Area */}
            <div className="flex flex-col flex-1 p-4">
                <header className="flex items-center justify-between py-4 border-b border-border mb-4">
                    <div className="flex items-center gap-2">
                        <div className="bg-primary/10 p-2 rounded-lg">
                            <Bot className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold">Eddie AI</h1>
                            <p className="text-xs text-muted-foreground">Trading Intelligence Agent - Powered by Avinash V - v0.1</p>
                        </div>
                    </div>

                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowPromptsPanel(!showPromptsPanel)}
                        className="gap-2"
                    >
                        {showPromptsPanel ? (
                            <>
                                <X className="w-4 h-4" />
                                Hide Prompts
                            </>
                        ) : (
                            <>
                                <BookmarkPlus className="w-4 h-4" />
                                Show Prompts
                            </>
                        )}
                    </Button>
                </header>

                <div className="flex-1 overflow-y-auto space-y-6 pr-4 custom-scrollbar">
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
                                    "rounded-lg p-4 max-w-[80%]",
                                    msg.role === "user"
                                        ? "bg-primary text-primary-foreground"
                                        : "bg-secondary/50 border border-border"
                                )}>
                                    <div className="prose prose-invert prose-sm max-w-none">
                                        <ReactMarkdown 
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                table: ({node, ...props}) => (
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
                                                title="Play voice (v2.0)"
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

                    <AnimatePresence>
                        {thinking.isThinking && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="flex gap-4"
                            >
                                <div className="w-8 h-8 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center shrink-0">
                                    <Bot className="w-5 h-5" />
                                </div>
                                <div className="bg-secondary/50 border border-border rounded-lg p-4 flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <Loader2 className="w-4 h-4 animate-spin text-primary" />
                                        <span className="text-sm font-medium">{thinking.message}</span>
                                    </div>
                                    {thinking.activeTools.length > 0 && (
                                        <div className="mt-2 space-y-1">
                                            {thinking.activeTools.map((tool, idx) => (
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

                {voiceError && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="mb-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400"
                    >
                        <div className="flex items-start gap-2">
                            <X 
                                className="w-4 h-4 mt-0.5 cursor-pointer shrink-0" 
                                onClick={() => setVoiceError(null)}
                            />
                            <div className="flex-1">
                                <strong>Microphone Error:</strong> {voiceError}
                            </div>
                        </div>
                    </motion.div>
                )}
                <form onSubmit={handleSubmit} className="mt-4">
                    <div className="flex gap-2 relative">
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
                                setVoiceError(null) // Clear error on success
                                sendMessage(text)
                            }}
                            onError={(error) => {
                                console.error("Voice input error:", error)
                                setVoiceError(error)
                                // Auto-clear error after 8 seconds
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
                    </div>
                </form>
            </div>

            {/* Prompts Sidebar */}
            <AnimatePresence>
                {showPromptsPanel && (
                    <motion.div
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 360, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="border-l border-border overflow-hidden"
                    >
                        <div className="w-[360px] p-4 h-full overflow-y-auto custom-scrollbar">
                            <div className="mb-4">
                                <h2 className="text-lg font-bold">Quick Actions</h2>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Select a prompt to get started
                                </p>
                            </div>
                            <PromptCategories
                                onPromptSelect={sendMessage}
                                isLoading={isLoading}
                                loadingPromptId={loadingPromptId}
                            />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
