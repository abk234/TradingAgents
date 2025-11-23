/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState, useEffect } from "react"
import { Folder, Plus, Edit, Trash2, Star, Loader2, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "react-hot-toast"
import { api } from "@/lib/api/client"

interface Workspace {
    workspace_id: number
    name: string
    description?: string
    is_default: boolean
    is_active: boolean
    created_at: string
}

export function WorkspacesView() {
    const [workspaces, setWorkspaces] = useState<Workspace[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isCreating, setIsCreating] = useState(false)
    const [showCreateForm, setShowCreateForm] = useState(false)
    const [newWorkspaceName, setNewWorkspaceName] = useState("")
    const [newWorkspaceDesc, setNewWorkspaceDesc] = useState("")
    const [searchTerm, setSearchTerm] = useState("")

    useEffect(() => {
        loadWorkspaces()
    }, [])

    const loadWorkspaces = async () => {
        try {
            setIsLoading(true)
            const response = await api.listWorkspaces()
            setWorkspaces(response.workspaces || [])
        } catch (error) {
            console.error("Failed to load workspaces:", error)
            toast.error("Failed to load workspaces")
        } finally {
            setIsLoading(false)
        }
    }

    const handleCreateWorkspace = async () => {
        if (!newWorkspaceName.trim()) {
            toast.error("Workspace name is required")
            return
        }

        try {
            setIsCreating(true)
            await api.createWorkspace({
                name: newWorkspaceName,
                description: newWorkspaceDesc || undefined,
                is_default: false
            })
            toast.success("Workspace created successfully")
            setNewWorkspaceName("")
            setNewWorkspaceDesc("")
            setShowCreateForm(false)
            loadWorkspaces()
        } catch (error: any) {
            console.error("Failed to create workspace:", error)
            toast.error(`Failed to create workspace: ${error.message || "Unknown error"}`)
        } finally {
            setIsCreating(false)
        }
    }

    const handleDeleteWorkspace = async (workspaceId: number) => {
        if (!confirm("Are you sure you want to delete this workspace?")) return

        try {
            await api.deleteWorkspace(workspaceId, true)
            toast.success("Workspace deleted")
            loadWorkspaces()
        } catch (error) {
            console.error("Failed to delete workspace:", error)
            toast.error("Failed to delete workspace")
        }
    }

    const handleSetDefault = async (workspaceId: number) => {
        try {
            await api.updateWorkspace(workspaceId, { is_default: true })
            toast.success("Default workspace updated")
            loadWorkspaces()
        } catch (error) {
            console.error("Failed to update workspace:", error)
            toast.error("Failed to update workspace")
        }
    }

    const filteredWorkspaces = workspaces.filter(ws =>
        ws.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ws.description?.toLowerCase().includes(searchTerm.toLowerCase())
    )

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Workspaces</h2>
                    <p className="text-muted-foreground">Organize your trading strategies and analyses</p>
                </div>
                <Button onClick={() => setShowCreateForm(!showCreateForm)}>
                    <Plus className="mr-2 h-4 w-4" />
                    New Workspace
                </Button>
            </div>

            {/* Create Form */}
            {showCreateForm && (
                <Card>
                    <CardHeader>
                        <CardTitle>Create New Workspace</CardTitle>
                        <CardDescription>Create a workspace to organize your analyses</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="text-sm font-medium mb-2 block">Workspace Name</label>
                            <Input
                                placeholder="e.g., Growth Portfolio"
                                value={newWorkspaceName}
                                onChange={(e) => setNewWorkspaceName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium mb-2 block">Description (optional)</label>
                            <Input
                                placeholder="Description of this workspace"
                                value={newWorkspaceDesc}
                                onChange={(e) => setNewWorkspaceDesc(e.target.value)}
                            />
                        </div>
                        <div className="flex gap-2">
                            <Button onClick={handleCreateWorkspace} disabled={isCreating}>
                                {isCreating ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Creating...
                                    </>
                                ) : (
                                    "Create Workspace"
                                )}
                            </Button>
                            <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                                Cancel
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Workspaces List */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Workspaces ({filteredWorkspaces.length})</CardTitle>
                            <CardDescription>Manage your workspaces</CardDescription>
                        </div>
                        <div className="relative">
                            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                placeholder="Search workspaces..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-8 w-64"
                            />
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-primary" />
                        </div>
                    ) : filteredWorkspaces.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <Folder className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>No workspaces found</p>
                            <p className="text-sm">Create a workspace to get started</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {filteredWorkspaces.map((workspace) => (
                                <Card key={workspace.workspace_id} className="relative">
                                    <CardHeader>
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-2">
                                                <Folder className="w-5 h-5 text-primary" />
                                                <CardTitle className="text-lg">{workspace.name}</CardTitle>
                                            </div>
                                            {workspace.is_default && (
                                                <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                                            )}
                                        </div>
                                        {workspace.description && (
                                            <CardDescription>{workspace.description}</CardDescription>
                                        )}
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex items-center justify-between">
                                            <div className="text-sm text-muted-foreground">
                                                Created {new Date(workspace.created_at).toLocaleDateString()}
                                            </div>
                                            <div className="flex gap-2">
                                                {!workspace.is_default && (
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleSetDefault(workspace.workspace_id)}
                                                        title="Set as default"
                                                    >
                                                        <Star className="w-4 h-4" />
                                                    </Button>
                                                )}
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => handleDeleteWorkspace(workspace.workspace_id)}
                                                >
                                                    <Trash2 className="w-4 h-4 text-red-500" />
                                                </Button>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

