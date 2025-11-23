/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState, useEffect } from "react"
import { Terminal, Play, Loader2, Search, Settings, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { toast } from "react-hot-toast"
import { api } from "@/lib/api/client"

interface MCPTool {
    name: string
    description: string
    inputSchema: any
}

export function MCPToolsView() {
    const [tools, setTools] = useState<MCPTool[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [selectedTool, setSelectedTool] = useState<string>("")
    const [toolArgs, setToolArgs] = useState("{}")
    const [toolOutput, setToolOutput] = useState("")
    const [isExecuting, setIsExecuting] = useState(false)
    const [searchTerm, setSearchTerm] = useState("")
    const [capabilities, setCapabilities] = useState<any>(null)

    useEffect(() => {
        loadMCPData()
    }, [])

    const loadMCPData = async () => {
        try {
            setIsLoading(true)
            const [toolsResponse, capabilitiesResponse] = await Promise.all([
                api.listMCPTools(),
                api.getMCPCapabilities()
            ])
            setTools(toolsResponse.tools || [])
            setCapabilities(capabilitiesResponse)
        } catch (error) {
            console.error("Failed to load MCP data:", error)
            toast.error("Failed to load MCP tools. Make sure MCP server is initialized.")
        } finally {
            setIsLoading(false)
        }
    }

    const handleExecuteTool = async () => {
        if (!selectedTool) {
            toast.error("Please select a tool")
            return
        }

        try {
            setIsExecuting(true)
            setToolOutput("")
            
            let parsedArgs = {}
            try {
                parsedArgs = JSON.parse(toolArgs)
            } catch (e) {
                toast.error("Invalid JSON arguments")
                return
            }

            // Validate required arguments if schema is available
            if (selectedToolData?.inputSchema) {
                const required = selectedToolData.inputSchema.required || []
                const missing = required.filter((field: string) => !(field in parsedArgs) || parsedArgs[field] === undefined || parsedArgs[field] === "")
                
                if (missing.length > 0) {
                    toast.error(`Missing required arguments: ${missing.join(", ")}`)
                    return
                }
            }

            const result = await api.callMCPTool(selectedTool, parsedArgs)
            
            // Handle MCP response format
            if (result.isError) {
                const errorText = result.content?.[0]?.text || JSON.stringify(result, null, 2)
                setToolOutput(errorText)
                toast.error("Tool execution failed")
            } else {
                const resultText = result.content?.[0]?.text || JSON.stringify(result, null, 2)
                setToolOutput(resultText)
                toast.success("Tool executed successfully")
            }
        } catch (error: any) {
            console.error("Failed to execute tool:", error)
            const errorMessage = error.message || error.response?.data?.detail || "Unknown error"
            setToolOutput(`Error: ${errorMessage}`)
            toast.error("Tool execution failed")
        } finally {
            setIsExecuting(false)
        }
    }

    const filteredTools = tools.filter(tool =>
        tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchTerm.toLowerCase())
    )

    const selectedToolData = tools.find(t => t.name === selectedTool)

    // Generate default arguments from schema
    const generateDefaultArguments = (schema: any): any => {
        if (!schema || !schema.properties) {
            return {}
        }

        const args: any = {}
        const properties = schema.properties
        const required = schema.required || []

        // Process all properties (both required and optional)
        for (const [key, prop] of Object.entries(properties)) {
            const property = prop as any
            const propType = property.type
            const hasDefault = property.default !== undefined

            // Use default value if available
            if (hasDefault) {
                args[key] = property.default
            } else {
                // Generate default based on type
                switch (propType) {
                    case "string":
                        // Check for enum values
                        if (property.enum && property.enum.length > 0) {
                            args[key] = property.enum[0]
                        } else {
                            // Use example if available, otherwise empty string
                            args[key] = property.example || property.examples?.[0] || ""
                        }
                        break
                    case "number":
                    case "integer":
                        // Use minimum, example, or default to 0
                        args[key] = property.minimum ?? property.example ?? property.examples?.[0] ?? 0
                        break
                    case "boolean":
                        args[key] = property.example ?? false
                        break
                    case "array":
                        // Use example array or empty array
                        args[key] = property.example ?? property.examples?.[0] ?? []
                        break
                    case "object":
                        // Use example object or empty object
                        args[key] = property.example ?? property.examples?.[0] ?? {}
                        break
                    default:
                        args[key] = property.example ?? property.examples?.[0] ?? null
                }
            }
        }

        return args
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">MCP Tools</h2>
                <p className="text-muted-foreground">Model Context Protocol - Manage and execute tools</p>
            </div>

            {/* Capabilities Info */}
            {capabilities && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Settings className="w-5 h-5" />
                            MCP Server Capabilities
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-muted-foreground">Protocol Version:</span>
                                <span className="ml-2 font-mono">{capabilities.protocolVersion || "N/A"}</span>
                            </div>
                            <div>
                                <span className="text-muted-foreground">Server Name:</span>
                                <span className="ml-2">{capabilities.serverInfo?.name || "N/A"}</span>
                            </div>
                            <div>
                                <span className="text-muted-foreground">Server Version:</span>
                                <span className="ml-2">{capabilities.serverInfo?.version || "N/A"}</span>
                            </div>
                            <div>
                                <span className="text-muted-foreground">Tools Available:</span>
                                <span className="ml-2 font-bold">{tools.length}</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Tools List */}
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle>Available Tools ({filteredTools.length})</CardTitle>
                                <CardDescription>Select a tool to execute</CardDescription>
                            </div>
                            <div className="relative">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search tools..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-8 w-48"
                                />
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex items-center justify-center py-12">
                                <Loader2 className="w-8 h-8 animate-spin text-primary" />
                            </div>
                        ) : filteredTools.length === 0 ? (
                            <div className="text-center py-12 text-muted-foreground">
                                <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
                                <p>No tools found</p>
                            </div>
                        ) : (
                            <div className="space-y-2 max-h-96 overflow-y-auto">
                                {filteredTools.map((tool) => (
                                    <div
                                        key={tool.name}
                                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                                            selectedTool === tool.name
                                                ? "border-primary bg-primary/5"
                                                : "border-border hover:border-primary/50"
                                        }`}
                                        onClick={() => {
                                            setSelectedTool(tool.name)
                                            // Generate pre-filled arguments from schema
                                            const preFilledArgs = generateDefaultArguments(tool.inputSchema)
                                            setToolArgs(JSON.stringify(preFilledArgs, null, 2))
                                            setToolOutput("")
                                        }}
                                    >
                                        <div className="flex items-center gap-2">
                                            <Terminal className="w-4 h-4 text-primary" />
                                            <span className="font-medium">{tool.name}</span>
                                            {selectedTool === tool.name && (
                                                <CheckCircle2 className="w-4 h-4 text-primary ml-auto" />
                                            )}
                                        </div>
                                        <p className="text-sm text-muted-foreground mt-1">{tool.description}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Tool Execution */}
                <Card>
                    <CardHeader>
                        <CardTitle>Execute Tool</CardTitle>
                        <CardDescription>
                            {selectedTool ? `Execute: ${selectedTool}` : "Select a tool to execute"}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {selectedToolData && (
                            <>
                                <div>
                                    <Label>Tool: {selectedTool}</Label>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {selectedToolData.description}
                                    </p>
                                </div>
                                {selectedToolData.inputSchema && (
                                    <div>
                                        <Label>Input Schema</Label>
                                        <div className="mt-2 p-3 bg-muted rounded-lg text-xs">
                                            {selectedToolData.inputSchema.required && selectedToolData.inputSchema.required.length > 0 && (
                                                <div className="mb-2">
                                                    <span className="font-semibold text-red-600">Required: </span>
                                                    <span>{selectedToolData.inputSchema.required.join(", ")}</span>
                                                </div>
                                            )}
                                            {selectedToolData.inputSchema.properties && (
                                                <div className="mb-2">
                                                    <span className="font-semibold">Properties:</span>
                                                    <pre className="mt-1 overflow-auto max-h-32">
                                                        {JSON.stringify(selectedToolData.inputSchema.properties, null, 2)}
                                                    </pre>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                        <div>
                            <Label>Arguments (JSON)</Label>
                            <Textarea
                                value={toolArgs}
                                onChange={(e) => setToolArgs(e.target.value)}
                                className="font-mono mt-2 min-h-32"
                                placeholder='{"key": "value"}'
                            />
                            {selectedToolData?.inputSchema && (
                                <div className="mt-2 space-y-1">
                                    {selectedToolData.inputSchema.required && selectedToolData.inputSchema.required.length > 0 && (
                                        <p className="text-xs text-red-600 font-semibold">
                                            Required: {selectedToolData.inputSchema.required.join(", ")}
                                        </p>
                                    )}
                                    {selectedToolData.inputSchema.properties && (
                                        <p className="text-xs text-muted-foreground">
                                            All fields pre-filled with defaults. Edit as needed.
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                        <Button
                            onClick={handleExecuteTool}
                            disabled={!selectedTool || isExecuting}
                            className="w-full"
                        >
                            {isExecuting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Executing...
                                </>
                            ) : (
                                <>
                                    <Play className="mr-2 h-4 w-4" />
                                    Execute Tool
                                </>
                            )}
                        </Button>
                        {toolOutput && (
                            <div>
                                <Label>Output</Label>
                                <pre className="mt-2 p-3 bg-muted rounded-lg text-xs overflow-auto max-h-64">
                                    {toolOutput}
                                </pre>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}

