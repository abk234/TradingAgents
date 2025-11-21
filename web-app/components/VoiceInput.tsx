"use client"

import * as React from "react"
import { useState, useRef, useEffect } from "react"
import { Mic, MicOff, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface VoiceInputProps {
    onTranscription: (text: string) => void
    onError?: (error: string) => void
    className?: string
}

export function VoiceInput({ onTranscription, onError, className }: VoiceInputProps) {
    const [isRecording, setIsRecording] = useState(false)
    const [isConnected, setIsConnected] = useState(false)
    const [isProcessing, setIsProcessing] = useState(false)
    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const websocketRef = useRef<WebSocket | null>(null)
    const audioChunksRef = useRef<Blob[]>([])

    useEffect(() => {
        // Cleanup on unmount
        return () => {
            if (websocketRef.current) {
                websocketRef.current.close()
            }
            if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
                mediaRecorderRef.current.stop()
            }
        }
    }, [])

    const connectWebSocket = async () => {
        try {
            const ws = new WebSocket("ws://localhost:8005/voice/ws")

            ws.onopen = () => {
                setIsConnected(true)
                console.log("WebSocket connected")
            }

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data)

                if (data.type === "transcription") {
                    setIsProcessing(false)
                    onTranscription(data.text)
                } else if (data.type === "error") {
                    setIsProcessing(false)
                    setIsRecording(false)
                    onError?.(data.message || "Transcription error")
                }
            }

            ws.onerror = (error) => {
                console.error("WebSocket error:", error)
                setIsConnected(false)
                onError?.("Connection error")
            }

            ws.onclose = () => {
                setIsConnected(false)
                console.log("WebSocket disconnected")
            }

            websocketRef.current = ws
        } catch (error) {
            console.error("Error connecting WebSocket:", error)
            onError?.("Failed to connect to voice service")
        }
    }

    const startRecording = async () => {
        try {
            // Check if mediaDevices API is available
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                onError?.("Microphone access is not available in this browser. Please use a modern browser like Chrome, Firefox, or Safari.")
                return
            }

            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            })

            // Connect WebSocket if not connected
            if (!websocketRef.current || websocketRef.current.readyState !== WebSocket.OPEN) {
                await connectWebSocket()
                // Wait a bit for connection
                await new Promise(resolve => setTimeout(resolve, 500))
            }

            // Create MediaRecorder
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: "audio/webm;codecs=opus"
            })

            mediaRecorderRef.current = mediaRecorder
            audioChunksRef.current = []

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data)

                    // Send audio chunk to WebSocket
                    if (websocketRef.current?.readyState === WebSocket.OPEN) {
                        const reader = new FileReader()
                        reader.onloadend = () => {
                            const base64Audio = reader.result?.toString().split(',')[1]
                            if (base64Audio) {
                                websocketRef.current?.send(JSON.stringify({
                                    type: "audio_chunk",
                                    audio: base64Audio
                                }))
                            }
                        }
                        reader.readAsDataURL(event.data)
                    }
                }
            }

            mediaRecorder.onstop = () => {
                // Send end signal
                if (websocketRef.current?.readyState === WebSocket.OPEN) {
                    websocketRef.current.send(JSON.stringify({
                        type: "audio_end"
                    }))
                    setIsProcessing(true)
                }

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop())
            }

            // Start recording
            mediaRecorder.start(100) // Send chunks every 100ms
            setIsRecording(true)

        } catch (error: any) {
            // Only log non-permission errors to avoid console noise for expected user actions
            if (error.name !== "NotAllowedError" && error.name !== "PermissionDeniedError") {
                console.error("Error starting recording:", error)
            }

            // Provide specific error messages based on error type
            let errorMessage = "Failed to access microphone. "

            if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
                errorMessage += "Please allow microphone access in your browser settings. " +
                    "Look for the microphone icon in the address bar and click 'Allow', or check your browser's site permissions."
            } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
                errorMessage += "No microphone found. Please connect a microphone and try again."
            } else if (error.name === "NotReadableError" || error.name === "TrackStartError") {
                errorMessage += "Microphone is being used by another application. Please close other apps using the microphone."
            } else if (error.name === "OverconstrainedError") {
                errorMessage += "Microphone doesn't support the required settings. Please try a different microphone."
            } else {
                errorMessage += `Error: ${error.message || "Unknown error"}.`
            }

            onError?.(errorMessage)
        }
    }

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
            mediaRecorderRef.current.stop()
            setIsRecording(false)
        }
    }

    const handleToggleRecording = () => {
        if (isRecording) {
            stopRecording()
        } else {
            startRecording()
        }
    }

    return (
        <Button
            onClick={handleToggleRecording}
            disabled={isProcessing}
            className={cn(
                "gap-2",
                isRecording && "bg-red-500 hover:bg-red-600",
                className
            )}
            variant={isRecording ? "default" : "outline"}
            title={isRecording ? "Stop recording" : "Start voice input"}
        >
            {isProcessing ? (
                <>
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Processing...
                </>
            ) : isRecording ? (
                <>
                    <MicOff className="w-4 h-4" />
                    Stop
                </>
            ) : (
                <>
                    <Mic className="w-4 h-4" />
                    Voice Input
                </>
            )}
        </Button>
    )
}

