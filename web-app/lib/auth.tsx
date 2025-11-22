/*
 * Copyright (c) 2024. All rights reserved.
 * Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.
 */

"use client"

import React, { createContext, useContext, useState, useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"

interface AuthContextType {
    apiKey: string | null
    isAuthenticated: boolean
    login: (key: string) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [apiKey, setApiKey] = useState<string | null>(null)
    const [isAuthenticated, setIsAuthenticated] = useState(false)
    const [isLoading, setIsLoading] = useState(true)
    const router = useRouter()
    const pathname = usePathname()

    useEffect(() => {
        // Check for API key in localStorage on mount
        const storedKey = localStorage.getItem("api_key")
        if (storedKey) {
            setApiKey(storedKey)
            setIsAuthenticated(true)
        }
        setIsLoading(false)
    }, [])

    useEffect(() => {
        if (!isLoading && !isAuthenticated && pathname !== "/login") {
            router.push("/login")
        }
    }, [isLoading, isAuthenticated, pathname, router])

    const login = (key: string) => {
        localStorage.setItem("api_key", key)
        setApiKey(key)
        setIsAuthenticated(true)
        router.push("/")
    }

    const logout = () => {
        localStorage.removeItem("api_key")
        setApiKey(null)
        setIsAuthenticated(false)
        router.push("/login")
    }

    if (isLoading) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>
    }

    return (
        <AuthContext.Provider value={{ apiKey, isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider")
    }
    return context
}
