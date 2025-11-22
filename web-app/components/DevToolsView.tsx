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
import { Terminal, Mic, Search, Play, FileAudio, Loader2, MicOff, Upload } from "lucide-react"
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
    
    // STT State
    const [isRecording, setIsRecording] = useState(false)
    const [transcription, setTranscription] = useState("")
    const [sttLoading, setSttLoading] = useState(false)
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
    const [audioChunks, setAudioChunks] = useState<Blob[]>([])

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

    const checkMicrophonePermission = async (): Promise<boolean> => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                toast.error("Microphone access not available in this browser. Please use Chrome, Firefox, or Safari.")
                return false
            }

            // Check permission status
            if (navigator.permissions) {
                const permissionStatus = await navigator.permissions.query({ name: 'microphone' as PermissionName })
                if (permissionStatus.state === 'denied') {
                    toast.error("Microphone permission denied. Please enable it in your browser settings.")
                    return false
                }
            }

            return true
        } catch (error) {
            // Permission API might not be supported, continue anyway
            return true
        }
    }

    const startRecording = async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                toast.error("Microphone access not available in this browser. Please use Chrome, Firefox, or Safari.")
                return
            }

            // Check permissions first
            const hasPermission = await checkMicrophonePermission()
            if (!hasPermission) {
                return
            }

            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            })
            
            const recorder = new MediaRecorder(stream, {
                mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus") 
                    ? "audio/webm;codecs=opus"
                    : MediaRecorder.isTypeSupported("audio/webm")
                    ? "audio/webm"
                    : "audio/mp4"
            })
            
            const chunks: Blob[] = []
            recorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunks.push(event.data)
                }
            }

            recorder.onstop = async () => {
                stream.getTracks().forEach(track => track.stop())
                if (chunks.length > 0) {
                    const audioBlob = new Blob(chunks, { type: recorder.mimeType })
                    await transcribeAudio(audioBlob)
                }
                setAudioChunks([])
            }

            recorder.onerror = (event) => {
                console.error("MediaRecorder error:", event)
                toast.error("Recording error occurred. Please try again.")
                setIsRecording(false)
            }

            recorder.start(100) // Collect data every 100ms
            setMediaRecorder(recorder)
            setIsRecording(true)
            setTranscription("")
            toast.success("Recording started - speak now")
        } catch (error: any) {
            console.error("Recording error:", error)
            setIsRecording(false)
            
            let errorMessage = "Failed to start recording. "
            
            if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
                errorMessage += "Microphone permission denied. Please:\n" +
                    "1. Click the microphone icon in your browser's address bar\n" +
                    "2. Select 'Allow' for microphone access\n" +
                    "3. Refresh the page and try again"
                toast.error(errorMessage, { duration: 6000 })
            } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
                errorMessage += "No microphone found. Please connect a microphone and try again."
                toast.error(errorMessage)
            } else if (error.name === "NotReadableError" || error.name === "TrackStartError") {
                errorMessage += "Microphone is being used by another application. Please close other apps using the microphone."
                toast.error(errorMessage)
            } else {
                errorMessage += error.message || "Unknown error occurred."
                toast.error(errorMessage)
            }
        }
    }

    const stopRecording = () => {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop()
            setIsRecording(false)
            toast.success("Recording stopped")
        }
    }

    const convertWebmToWav = async (webmBlob: Blob): Promise<Blob> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader()
            reader.onload = async (e) => {
                try {
                    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
                    const arrayBuffer = e.target?.result as ArrayBuffer
                    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
                    
                    // Convert to WAV
                    const wav = audioBufferToWav(audioBuffer)
                    const wavBlob = new Blob([wav], { type: "audio/wav" })
                    resolve(wavBlob)
                } catch (error) {
                    reject(error)
                }
            }
            reader.onerror = reject
            reader.readAsArrayBuffer(webmBlob)
        })
    }

    const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
        const length = buffer.length
        const numberOfChannels = buffer.numberOfChannels
        const sampleRate = buffer.sampleRate
        const bytesPerSample = 2
        const blockAlign = numberOfChannels * bytesPerSample
        const byteRate = sampleRate * blockAlign
        const dataSize = length * blockAlign
        const bufferSize = 44 + dataSize
        const arrayBuffer = new ArrayBuffer(bufferSize)
        const view = new DataView(arrayBuffer)

        // WAV header
        const writeString = (offset: number, string: string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i))
            }
        }

        writeString(0, "RIFF")
        view.setUint32(4, bufferSize - 8, true)
        writeString(8, "WAVE")
        writeString(12, "fmt ")
        view.setUint32(16, 16, true)
        view.setUint16(20, 1, true)
        view.setUint16(22, numberOfChannels, true)
        view.setUint32(24, sampleRate, true)
        view.setUint32(28, byteRate, true)
        view.setUint16(32, blockAlign, true)
        view.setUint16(34, 16, true)
        writeString(36, "data")
        view.setUint32(40, dataSize, true)

        // Convert audio data
        let offset = 44
        for (let i = 0; i < length; i++) {
            for (let channel = 0; channel < numberOfChannels; channel++) {
                const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]))
                view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true)
                offset += 2
            }
        }

        return arrayBuffer
    }

    const transcribeAudio = async (audioBlob: Blob) => {
        setSttLoading(true)
        try {
            const apiKey = localStorage.getItem("api_key") || "";
            if (!apiKey) {
                toast.error("API key not found. Please set it in Settings or login page.")
                setSttLoading(false)
                return
            }

            // Convert WebM to WAV if needed
            let wavBlob = audioBlob
            if (audioBlob.type.includes("webm") || audioBlob.type.includes("ogg")) {
                // Show loading toast for conversion
                const loadingToast = toast.loading("Converting audio format...")
                try {
                    wavBlob = await convertWebmToWav(audioBlob)
                    toast.dismiss(loadingToast)
                } catch (error) {
                    toast.dismiss(loadingToast)
                    throw error
                }
            }

            const formData = new FormData()
            formData.append("audio", wavBlob, "recording.wav")
            formData.append("audio_format", "wav")
            formData.append("sample_rate", "16000")

            const response = await fetch("http://localhost:8005/voice/transcribe", {
                method: "POST",
                headers: {
                    "X-API-Key": apiKey
                },
                body: formData
            })

            if (response.ok) {
                const data = await response.json()
                const transcribedText = data.text || data.transcription || ""
                setTranscription(transcribedText)
                toast.success("Transcription completed")
            } else {
                const errorText = await response.text()
                console.error("STT Error:", response.status, errorText)
                toast.error(`Transcription failed: ${response.status === 401 ? "Unauthorized" : errorText}`)
            }
        } catch (error) {
            console.error("STT Error:", error)
            toast.error(`Error transcribing audio: ${error}`)
        } finally {
            setSttLoading(false)
        }
    }

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file) return

        if (!file.type.startsWith("audio/")) {
            toast.error("Please upload an audio file")
            return
        }

        const audioBlob = new Blob([file], { type: file.type })
        await transcribeAudio(audioBlob)
    }

    const useTranscriptionForTTS = () => {
        if (transcription) {
            setTtsText(transcription)
            toast.success("Transcription copied to TTS input")
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

                    {/* Speech-to-Text Section */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Speech to Text (STT)</CardTitle>
                            <CardDescription>Convert audio to text using the backend engine</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-4">
                                <div className="flex gap-2">
                                    <Button 
                                        onClick={isRecording ? stopRecording : startRecording}
                                        disabled={sttLoading}
                                        variant={isRecording ? "destructive" : "default"}
                                        className="flex-1"
                                    >
                                        {sttLoading ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Processing...
                                            </>
                                        ) : isRecording ? (
                                            <>
                                                <MicOff className="mr-2 h-4 w-4" />
                                                Stop Recording
                                            </>
                                        ) : (
                                            <>
                                                <Mic className="mr-2 h-4 w-4" />
                                                Start Recording
                                            </>
                                        )}
                                    </Button>
                                    <div className="relative">
                                        <Input
                                            type="file"
                                            accept="audio/*"
                                            onChange={handleFileUpload}
                                            className="hidden"
                                            id="audio-upload"
                                            disabled={sttLoading || isRecording}
                                        />
                                        <Button
                                            variant="outline"
                                            onClick={() => document.getElementById("audio-upload")?.click()}
                                            disabled={sttLoading || isRecording}
                                        >
                                            <Upload className="mr-2 h-4 w-4" />
                                            Upload Audio
                                        </Button>
                                    </div>
                                </div>

                                {!navigator.mediaDevices && (
                                    <div className="p-3 border border-yellow-500/50 rounded-lg bg-yellow-500/10 text-sm text-yellow-600 dark:text-yellow-400">
                                        <strong>Note:</strong> Microphone access requires HTTPS or localhost. If you're having permission issues:
                                        <ul className="list-disc list-inside mt-2 space-y-1">
                                            <li>Check your browser's address bar for a microphone icon</li>
                                            <li>Click it and select "Allow" for microphone access</li>
                                            <li>Or use the "Upload Audio" button to test with audio files</li>
                                        </ul>
                                    </div>
                                )}

                                {transcription && (
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between">
                                            <Label>Transcription</Label>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={useTranscriptionForTTS}
                                            >
                                                Use for TTS →
                                            </Button>
                                        </div>
                                        <div className="p-4 border rounded-lg bg-muted/50 min-h-[100px]">
                                            <p className="text-sm whitespace-pre-wrap">{transcription}</p>
                                        </div>
                                    </div>
                                )}

                                {!transcription && !sttLoading && (
                                    <div className="p-4 border rounded-lg bg-muted/20 text-center text-muted-foreground text-sm">
                                        {isRecording 
                                            ? "Recording... Click 'Stop Recording' when done."
                                            : "Record audio or upload a file to transcribe"}
                                    </div>
                                )}
                            </div>
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
