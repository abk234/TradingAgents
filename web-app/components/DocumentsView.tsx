/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import { useState, useEffect } from "react"
import { Upload, FileText, Search, Trash2, Eye, Loader2, File, CheckCircle2, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "react-hot-toast"
import { api } from "@/lib/api/client"

interface Document {
    document_id: number
    filename: string
    original_filename: string
    document_type: string
    processing_status: string
    file_size_bytes: number
    uploaded_at: string
    processed_at?: string
    summary?: any
}

export function DocumentsView() {
    const [documents, setDocuments] = useState<Document[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [isUploading, setIsUploading] = useState(false)
    const [searchTerm, setSearchTerm] = useState("")
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [ticker, setTicker] = useState("")

    useEffect(() => {
        loadDocuments()
    }, [])

    const loadDocuments = async () => {
        try {
            setIsLoading(true)
            const response = await api.listDocuments()
            setDocuments(response.documents || [])
        } catch (error) {
            console.error("Failed to load documents:", error)
            toast.error("Failed to load documents")
        } finally {
            setIsLoading(false)
        }
    }

    const handleUpload = async () => {
        if (!selectedFile) {
            toast.error("Please select a file")
            return
        }

        try {
            setIsUploading(true)
            const response = await api.uploadDocument(selectedFile, ticker || undefined)
            toast.success(`Document uploaded successfully! ID: ${response.document_id}`)
            setSelectedFile(null)
            setTicker("")
            loadDocuments()
        } catch (error: any) {
            console.error("Failed to upload document:", error)
            toast.error(`Upload failed: ${error.message || "Unknown error"}`)
        } finally {
            setIsUploading(false)
        }
    }

    const handleDelete = async (documentId: number) => {
        if (!confirm("Are you sure you want to delete this document?")) return

        try {
            await api.deleteDocument(documentId)
            toast.success("Document deleted")
            loadDocuments()
        } catch (error) {
            console.error("Failed to delete document:", error)
            toast.error("Failed to delete document")
        }
    }

    const handleViewDocument = async (documentId: number) => {
        try {
            const doc: any = await api.getDocument(documentId)
            const insights = await api.getDocumentInsights(documentId)
            
            const info = `
Document: ${doc.original_filename}
Type: ${doc.document_type}
Status: ${doc.processing_status}
Size: ${(doc.file_size_bytes / 1024).toFixed(2)} KB
Uploaded: ${new Date(doc.uploaded_at).toLocaleString()}
${doc.processed_at ? `Processed: ${new Date(doc.processed_at).toLocaleString()}` : ""}

Summary:
${JSON.stringify(doc.summary, null, 2)}

Financial Data:
${JSON.stringify(doc.financial_data, null, 2)}

Insights: ${insights.count} found
            `.trim()
            
            alert(info)
        } catch (error) {
            console.error("Failed to load document details:", error)
            toast.error("Failed to load document details")
        }
    }

    const filteredDocuments = documents.filter(doc =>
        doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.document_type.toLowerCase().includes(searchTerm.toLowerCase())
    )

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "completed":
                return <CheckCircle2 className="w-4 h-4 text-green-500" />
            case "processing":
                return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
            case "failed":
                return <XCircle className="w-4 h-4 text-red-500" />
            default:
                return <File className="w-4 h-4 text-gray-500" />
        }
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">Documents</h2>
                <p className="text-muted-foreground">Upload and manage financial documents</p>
            </div>

            {/* Upload Section */}
            <Card>
                <CardHeader>
                    <CardTitle>Upload Document</CardTitle>
                    <CardDescription>Upload PDF, HTML, TXT, or DOCX files for analysis</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <Input
                                type="file"
                                accept=".pdf,.html,.htm,.txt,.docx"
                                onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                            />
                        </div>
                        <div className="w-48">
                            <Input
                                placeholder="Ticker (optional)"
                                value={ticker}
                                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                            />
                        </div>
                        <Button
                            onClick={handleUpload}
                            disabled={!selectedFile || isUploading}
                        >
                            {isUploading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload className="mr-2 h-4 w-4" />
                                    Upload
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Documents List */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Documents ({filteredDocuments.length})</CardTitle>
                            <CardDescription>Manage your uploaded documents</CardDescription>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="relative">
                                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="Search documents..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-8 w-64"
                                />
                            </div>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {isLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-primary" />
                        </div>
                    ) : filteredDocuments.length === 0 ? (
                        <div className="text-center py-12 text-muted-foreground">
                            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                            <p>No documents found</p>
                            <p className="text-sm">Upload a document to get started</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {filteredDocuments.map((doc) => (
                                <div
                                    key={doc.document_id}
                                    className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-card/50 transition-colors"
                                >
                                    <div className="flex items-center gap-4 flex-1">
                                        <FileText className="w-5 h-5 text-muted-foreground" />
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                                <span className="font-medium">{doc.original_filename}</span>
                                                {getStatusIcon(doc.processing_status)}
                                                <span className="text-xs text-muted-foreground">
                                                    {doc.processing_status}
                                                </span>
                                            </div>
                                            <div className="text-sm text-muted-foreground">
                                                {doc.document_type.toUpperCase()} • {(doc.file_size_bytes / 1024).toFixed(2)} KB • {new Date(doc.uploaded_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleViewDocument(doc.document_id)}
                                        >
                                            <Eye className="w-4 h-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDelete(doc.document_id)}
                                        >
                                            <Trash2 className="w-4 h-4 text-red-500" />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}

