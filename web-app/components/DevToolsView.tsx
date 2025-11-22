/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Terminal, Mic, Search, Play, FileAudio, Loader2 } from "lucide-react"
import { toast } from "react-hot-toast"

export function DevToolsView() {
    const [activeTab, setActiveTab] = useState("tools")

    // Tool Tester State
    const [selectedTool, setSelectedTool] = useState("analyze_stock")
    const [toolArgs, setToolArgs] = useState('{\n  "ticker": "AAPL",\n  "portfolio_value": 100000\n}')
    const [toolOutput, setToolOutput] = useState("")
    const [toolLoading, setToolLoading] = useState(false)

    // Voice Tester State
    const [ttsText, setTtsText] = useState("Hello, I am Eddie. How can I help you today?")
    const [ttsTone, setTtsTone] = useState("professional")
    const [ttsLoading, setTtsLoading] = useState(false)
    const [audioUrl, setAudioUrl] = useState<string | null>(null)

    // RAG Tester State
    const [ragQuery, setRagQuery] = useState("")
    const [ragResults, setRagResults] = useState<any[]>([])
    const [ragLoading, setRagLoading] = useState(false)

    const tools = [
        { name: "run_screener", defaultArgs: '{\n  "sector_analysis": true,\n  "top_n": 5\n}' },
        { name: "get_top_stocks", defaultArgs: '{\n  "limit": 5\n}' },
        { name: "analyze_sector", defaultArgs: '{\n  "sector_name": "Technology"\n}' },
        { name: "search_stocks", defaultArgs: '{\n  "sector": "Technology",\n  "min_score": 50\n}' },
        { name: "analyze_stock", defaultArgs: '{\n  "ticker": "AAPL",\n  "portfolio_value": 100000\n}' },
        { name: "get_stock_summary", defaultArgs: '{\n  "ticker": "MSFT"\n}' },
        { name: "get_stock_info", defaultArgs: '{\n  "ticker": "NVDA"\n}' },
        { name: "explain_metric", defaultArgs: '{\n  "metric_name": "RSI"\n}' },
        { name: "show_legend", defaultArgs: '{}' }
    ]

    const handleToolSelect = (value: string) => {
        setSelectedTool(value)
        const tool = tools.find(t => t.name === value)
        if (tool) {
            setToolArgs(tool.defaultArgs)
        }
    }

    const executeTool = async () => {
        setToolLoading(true)
        setToolOutput("")
        try {
            let parsedArgs = {}
            try {
                parsedArgs = JSON.parse(toolArgs)
            } catch (e) {
                toast.error("Invalid JSON arguments")
                setToolLoading(false)
                return
            }

            const apiKey = localStorage.getItem("api_key") || "";
            const response = await fetch(`http://localhost:8005/debug/execute_tool?tool_name=${selectedTool}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(apiKey ? { "X-API-Key": apiKey } : {})
                },
                body: JSON.stringify(parsedArgs)
            })

            const data = await response.json()
            if (data.status === "success") {
                const result = data.result || ""
                setToolOutput(result)
                // Check if result contains an error message (tools may return error strings)
                if (result.startsWith("Error analyzing") || result.startsWith("Error:") || result.toLowerCase().includes("connection error")) {
                    toast.error("Tool execution encountered an error")
                } else {
                    toast.success("Tool executed successfully")
                }
            } else {
                setToolOutput(`Error: ${data.error}`)
                toast.error("Tool execution failed")
            }
        } catch (error) {
            setToolOutput(`Error: ${error}`)
            toast.error("Failed to connect to backend")
        } finally {
            setToolLoading(false)
        }
    }

    const synthesizeSpeech = async () => {
        if (!ttsText) return
        setTtsLoading(true)
        setAudioUrl(null) // Clear previous audio
        try {
            const apiKey = localStorage.getItem("api_key") || "";
            if (!apiKey) {
                toast.error("API key not found. Please set it in Settings or login page.")
                setTtsLoading(false)
                return
            }
            
            const response = await fetch(`http://localhost:8005/voice/synthesize?text=${encodeURIComponent(ttsText)}&tone=${ttsTone}&return_base64=true`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-API-Key": apiKey
                }
            })

            if (response.ok) {
                const data = await response.json()
                if (data.audio_base64 && data.audio_base64.length > 0) {
                    const audioSrc = `data:audio/wav;base64,${data.audio_base64}`
                    setAudioUrl(audioSrc)
                    toast.success("Speech synthesized successfully")
                } else {
                    console.error("No audio data in response:", data)
                    toast.error("No audio data received")
                }
            } else {
                const errorText = await response.text()
                console.error("API Error:", response.status, errorText)
                if (response.status === 401) {
                    toast.error("Unauthorized - API key is invalid or missing. Check Settings.")
                } else {
                    toast.error(`Failed to synthesize speech: ${errorText}`)
                }
            }
        } catch (error) {
            console.error("TTS Error:", error)
            toast.error(`Error connecting to TTS service: ${error}`)
        } finally {
            setTtsLoading(false)
        }
    }

    const searchRag = async () => {
        if (!ragQuery) return
        setRagLoading(true)
        try {
            const apiKey = localStorage.getItem("api_key") || "";
            const response = await fetch(`http://localhost:8005/debug/rag_search?query=${encodeURIComponent(ragQuery)}`, {
                method: "POST",
                headers: {
                    ...(apiKey ? { "X-API-Key": apiKey } : {})
                }
            })

            if (response.ok) {
                const data = await response.json()
                setRagResults(data.results)
                toast.success("Search completed")
            } else {
                toast.error("Search failed")
            }
        } catch (error) {
            toast.error("Error connecting to RAG service")
        } finally {
            setRagLoading(false)
        }
    }

    return (
        <div className="space-y-6 p-6 h-full overflow-y-auto">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Developer Playground</h2>
                    <p className="text-muted-foreground">Test backend components in isolation</p>
                </div>
            </div>

            <Tabs defaultValue="tools" value={activeTab} onValueChange={setActiveTab} className="space-y-4">
                <TabsList>
                    <TabsTrigger value="tools"><Terminal className="mr-2 h-4 w-4" /> Tool Tester</TabsTrigger>
                    <TabsTrigger value="voice"><Mic className="mr-2 h-4 w-4" /> Voice Tester</TabsTrigger>
                    <TabsTrigger value="rag"><Search className="mr-2 h-4 w-4" /> RAG Tester</TabsTrigger>
                </TabsList>

                {/* TOOL TESTER */}
                <TabsContent value="tools" className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2 h-[600px]">
                        <Card className="flex flex-col">
                            <CardHeader>
                                <CardTitle>Input</CardTitle>
                                <CardDescription>Select a tool and provide arguments</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-1 flex flex-col gap-4">
                                <div className="space-y-2">
                                    <Label>Select Tool</Label>
                                    <Select value={selectedTool} onValueChange={handleToolSelect}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select tool" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {tools.map(t => (
                                                <SelectItem key={t.name} value={t.name}>{t.name}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2 flex-1 flex flex-col">
                                    <Label>Arguments (JSON)</Label>
                                    <Textarea
                                        value={toolArgs}
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setToolArgs(e.target.value)}
                                        className="font-mono flex-1 resize-none"
                                    />
                                </div>
                                <Button onClick={executeTool} disabled={toolLoading}>
                                    {toolLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                                    Execute Tool
                                </Button>
                            </CardContent>
                        </Card>

                        <Card className="flex flex-col">
                            <CardHeader>
                                <CardTitle>Output</CardTitle>
                                <CardDescription>Raw result from the tool</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-1 bg-muted/50 p-4 rounded-md overflow-auto font-mono text-sm whitespace-pre-wrap">
                                {toolOutput || <span className="text-muted-foreground italic">No output generated yet...</span>}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* VOICE TESTER */}
                <TabsContent value="voice" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Text to Speech (TTS)</CardTitle>
                            <CardDescription>Convert text to audio using the backend engine</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-4">
                                <div className="space-y-2">
                                    <Label>Text to Synthesize</Label>
                                    <Textarea
                                        value={ttsText}
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTtsText(e.target.value)}
                                        rows={3}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Emotional Tone</Label>
                                    <Select value={ttsTone} onValueChange={setTtsTone}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="professional">Professional</SelectItem>
                                            <SelectItem value="calm">Calm</SelectItem>
                                            <SelectItem value="energetic">Energetic</SelectItem>
                                            <SelectItem value="technical">Technical</SelectItem>
                                            <SelectItem value="reassuring">Reassuring</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <Button onClick={synthesizeSpeech} disabled={ttsLoading}>
                                    {ttsLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileAudio className="mr-2 h-4 w-4" />}
                                    Synthesize Speech
                                </Button>
                            </div>

                            {audioUrl && (
                                <div className="mt-6 p-4 border rounded-lg bg-accent/20">
                                    <Label className="mb-2 block">Audio Output</Label>
                                    <audio 
                                        controls 
                                        src={audioUrl} 
                                        className="w-full" 
                                        autoPlay
                                        onError={(e) => {
                                            console.error("Audio loading error:", e)
                                            toast.error("Failed to load audio. Check console for details.")
                                        }}
                                        onLoadedData={() => {
                                            console.log("Audio loaded successfully")
                                        }}
                                    />
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* RAG TESTER */}
                <TabsContent value="rag" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Knowledge Base Search</CardTitle>
                            <CardDescription>Query the vector database directly</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex gap-2">
                                <Input
                                    placeholder="Enter search query..."
                                    value={ragQuery}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRagQuery(e.target.value)}
                                    onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => e.key === 'Enter' && searchRag()}
                                />
                                <Button onClick={searchRag} disabled={ragLoading}>
                                    {ragLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
                                    Search
                                </Button>
                            </div>

                            <div className="space-y-4 mt-4">
                                {ragResults.length > 0 ? (
                                    ragResults.map((result, i) => (
                                        <div key={i} className="p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                                            <p className="text-sm mb-2">{result.content}</p>
                                            <div className="flex gap-2 text-xs text-muted-foreground">
                                                <span className="bg-muted px-2 py-1 rounded">Source: {result.metadata?.source || "Unknown"}</span>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="text-center py-12 text-muted-foreground">
                                        No results found. Try a different query.
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
