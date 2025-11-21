"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog"
import {
    Activity,
    Database,
    Server,
    RefreshCw,
    Plus,
    Trash2,
    Edit,
    AlertTriangle,
    CheckCircle,
    ExternalLink
} from "lucide-react"
import { toast } from "react-hot-toast"

interface SystemStatus {
    status: string
    services: {
        database: string
        redis: string
        pgvector?: string
    }
    stats: {
        tickers?: { total: number, active: number }
        scans?: { total: number, days_scanned: number, last_scan_date: string }
        analyses?: { total: number }
        signals?: { total: number }
    }
    missing_data: {
        missing_scans: any[]
        missing_analysis: any[]
    }
    timestamp: string
}

interface Ticker {
    ticker_id: number
    symbol: string
    company_name: string
    sector: string
    industry: string
    active: boolean
    priority_tier: number
}

export function SystemView() {
    const [status, setStatus] = useState<SystemStatus | null>(null)
    const [tickers, setTickers] = useState<Ticker[]>([])
    const [loading, setLoading] = useState(true)
    const [refreshing, setRefreshing] = useState(false)
    const [activeTab, setActiveTab] = useState("dashboard")

    // New ticker form state
    const [newTickerOpen, setNewTickerOpen] = useState(false)
    const [newTicker, setNewTicker] = useState({ symbol: "", company_name: "", sector: "" })

    useEffect(() => {
        fetchSystemStatus()
        fetchTickers()
    }, [])

    const fetchSystemStatus = async () => {
        try {
            const response = await fetch("http://localhost:8005/system/status")
            if (response.ok) {
                const data = await response.json()
                setStatus(data)
            }
        } catch (error) {
            console.error("Failed to fetch system status", error)
            toast.error("Failed to fetch system status")
        } finally {
            setLoading(false)
        }
    }

    const fetchTickers = async () => {
        try {
            const response = await fetch("http://localhost:8005/data/tickers?active_only=false")
            if (response.ok) {
                const data = await response.json()
                setTickers(data)
            }
        } catch (error) {
            console.error("Failed to fetch tickers", error)
        }
    }

    const handleAddTicker = async () => {
        if (!newTicker.symbol) return

        try {
            const response = await fetch("http://localhost:8005/data/tickers", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newTicker)
            })

            if (response.ok) {
                toast.success(`Ticker ${newTicker.symbol} added`)
                setNewTickerOpen(false)
                setNewTicker({ symbol: "", company_name: "", sector: "" })
                fetchTickers()
                fetchSystemStatus()
            } else {
                toast.error("Failed to add ticker")
            }
        } catch (error) {
            toast.error("Error adding ticker")
        }
    }

    const handleDeleteTicker = async (symbol: string) => {
        if (!confirm(`Are you sure you want to remove ${symbol}?`)) return

        try {
            const response = await fetch(`http://localhost:8005/data/tickers/${symbol}`, {
                method: "DELETE"
            })

            if (response.ok) {
                toast.success(`Ticker ${symbol} removed`)
                fetchTickers()
                fetchSystemStatus()
            } else {
                toast.error("Failed to remove ticker")
            }
        } catch (error) {
            toast.error("Error removing ticker")
        }
    }

    const handleRefreshData = async (type: string) => {
        setRefreshing(true)
        try {
            const response = await fetch(`http://localhost:8005/data/refresh/${type}`, {
                method: "POST"
            })

            if (response.ok) {
                toast.success(`${type} refresh started`)
            } else {
                toast.error(`Failed to start ${type} refresh`)
            }
        } catch (error) {
            toast.error("Error triggering refresh")
        } finally {
            setRefreshing(false)
        }
    }

    if (loading) {
        return <div className="flex items-center justify-center h-full">Loading system data...</div>
    }

    return (
        <div className="space-y-6 p-6 h-full overflow-y-auto">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">System & Data</h2>
                    <p className="text-muted-foreground">Monitor system health and manage data sources</p>
                </div>
                <Button variant="outline" onClick={fetchSystemStatus} disabled={refreshing}>
                    <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                    Refresh Status
                </Button>
            </div>

            <Tabs defaultValue="dashboard" value={activeTab} onValueChange={setActiveTab} className="space-y-4">
                <TabsList>
                    <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                    <TabsTrigger value="data">Data Management</TabsTrigger>
                </TabsList>

                <TabsContent value="dashboard" className="space-y-4">
                    {/* Service Status */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">API Status</CardTitle>
                                <Activity className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold flex items-center gap-2">
                                    {status?.status === "online" ? (
                                        <span className="text-green-500 flex items-center text-sm"><CheckCircle className="mr-1 h-4 w-4" /> Online</span>
                                    ) : (
                                        <span className="text-red-500 flex items-center text-sm"><AlertTriangle className="mr-1 h-4 w-4" /> Offline</span>
                                    )}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">Backend API</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Database</CardTitle>
                                <Database className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold flex items-center gap-2">
                                    {status?.services.database === "online" ? (
                                        <span className="text-green-500 flex items-center text-sm"><CheckCircle className="mr-1 h-4 w-4" /> Connected</span>
                                    ) : (
                                        <span className="text-red-500 flex items-center text-sm"><AlertTriangle className="mr-1 h-4 w-4" /> Disconnected</span>
                                    )}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">PostgreSQL</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">PGVector</CardTitle>
                                <Database className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold flex items-center gap-2">
                                    {status?.services.pgvector === "online" ? (
                                        <span className="text-green-500 flex items-center text-sm"><CheckCircle className="mr-1 h-4 w-4" /> Active</span>
                                    ) : (
                                        <span className="text-amber-500 flex items-center text-sm"><AlertTriangle className="mr-1 h-4 w-4" /> {status?.services.pgvector || "Unknown"}</span>
                                    )}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">Vector Extension</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Tickers</CardTitle>
                                <Activity className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{status?.stats.tickers?.total || 0}</div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {status?.stats.tickers?.active || 0} active
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Daily Scans</CardTitle>
                                <Activity className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{status?.stats.scans?.total || 0}</div>
                                <p className="text-xs text-muted-foreground mt-1">
                                    Last scan: {status?.stats.scans?.last_scan_date || "Never"}
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* External Tools Links */}
                    <div className="grid gap-4 md:grid-cols-3">
                        <Card className="cursor-pointer hover:bg-accent/50 transition-colors" onClick={() => window.open('http://localhost:3000', '_blank')}>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" /> Grafana
                                    <ExternalLink className="h-4 w-4 ml-auto opacity-50" />
                                </CardTitle>
                                <CardDescription>View system metrics and dashboards</CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="cursor-pointer hover:bg-accent/50 transition-colors" onClick={() => window.open('http://localhost:9090', '_blank')}>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Server className="h-5 w-5" /> Prometheus
                                    <ExternalLink className="h-4 w-4 ml-auto opacity-50" />
                                </CardTitle>
                                <CardDescription>Raw metrics data explorer</CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="cursor-pointer hover:bg-accent/50 transition-colors" onClick={() => window.open('http://localhost:8000/docs', '_blank')}>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Database className="h-5 w-5" /> API Docs
                                    <ExternalLink className="h-4 w-4 ml-auto opacity-50" />
                                </CardTitle>
                                <CardDescription>Backend API Documentation</CardDescription>
                            </CardHeader>
                        </Card>
                    </div>

                    {/* Missing Data Alerts */}
                    <div className="grid gap-4 md:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-amber-500">
                                    <AlertTriangle className="h-5 w-5" /> Missing Scans
                                </CardTitle>
                                <CardDescription>Active tickers with no recent scan data</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {status?.missing_data?.missing_scans?.length === 0 ? (
                                    <div className="text-sm text-muted-foreground flex items-center gap-2">
                                        <CheckCircle className="h-4 w-4 text-green-500" /> All active tickers scanned recently
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {status?.missing_data?.missing_scans?.slice(0, 5).map((item: any) => (
                                            <div key={item.ticker_id} className="flex justify-between items-center text-sm border-b pb-2 last:border-0">
                                                <span className="font-medium">{item.symbol}</span>
                                                <span className="text-muted-foreground text-xs">Last: {item.last_scan || "Never"}</span>
                                            </div>
                                        ))}
                                        {status?.missing_data?.missing_scans?.length > 5 && (
                                            <div className="text-xs text-center text-muted-foreground pt-2">
                                                + {status.missing_data.missing_scans.length - 5} more
                                            </div>
                                        )}
                                        <Button size="sm" className="w-full mt-4" onClick={() => handleRefreshData('scan')}>
                                            Run Scan for Missing
                                        </Button>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-amber-500">
                                    <AlertTriangle className="h-5 w-5" /> Missing Analysis
                                </CardTitle>
                                <CardDescription>Active tickers with no recent AI analysis</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {status?.missing_data?.missing_analysis?.length === 0 ? (
                                    <div className="text-sm text-muted-foreground flex items-center gap-2">
                                        <CheckCircle className="h-4 w-4 text-green-500" /> All active tickers analyzed recently
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {status?.missing_data?.missing_analysis?.slice(0, 5).map((item: any) => (
                                            <div key={item.ticker_id} className="flex justify-between items-center text-sm border-b pb-2 last:border-0">
                                                <span className="font-medium">{item.symbol}</span>
                                                <span className="text-muted-foreground text-xs">Last: {item.last_analysis || "Never"}</span>
                                            </div>
                                        ))}
                                        {status?.missing_data?.missing_analysis?.length > 5 && (
                                            <div className="text-xs text-center text-muted-foreground pt-2">
                                                + {status.missing_data.missing_analysis.length - 5} more
                                            </div>
                                        )}
                                        <Button size="sm" className="w-full mt-4" onClick={() => handleRefreshData('analysis')}>
                                            Run Analysis for Missing
                                        </Button>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="data" className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="text-lg font-medium">Ticker Management</h3>
                        <Dialog open={newTickerOpen} onOpenChange={setNewTickerOpen}>
                            <DialogTrigger asChild>
                                <Button><Plus className="mr-2 h-4 w-4" /> Add Ticker</Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Add New Ticker</DialogTitle>
                                    <DialogDescription>
                                        Add a stock ticker to the watchlist for monitoring and analysis.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-4 py-4">
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="symbol" className="text-right">Symbol</Label>
                                        <Input
                                            id="symbol"
                                            value={newTicker.symbol}
                                            onChange={(e) => setNewTicker({ ...newTicker, symbol: e.target.value.toUpperCase() })}
                                            className="col-span-3"
                                            placeholder="AAPL"
                                        />
                                    </div>
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="name" className="text-right">Name</Label>
                                        <Input
                                            id="name"
                                            value={newTicker.company_name}
                                            onChange={(e) => setNewTicker({ ...newTicker, company_name: e.target.value })}
                                            className="col-span-3"
                                            placeholder="Apple Inc."
                                        />
                                    </div>
                                    <div className="grid grid-cols-4 items-center gap-4">
                                        <Label htmlFor="sector" className="text-right">Sector</Label>
                                        <Input
                                            id="sector"
                                            value={newTicker.sector}
                                            onChange={(e) => setNewTicker({ ...newTicker, sector: e.target.value })}
                                            className="col-span-3"
                                            placeholder="Technology"
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button onClick={handleAddTicker}>Add Ticker</Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>

                    <Card>
                        <CardContent className="p-0">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Symbol</TableHead>
                                        <TableHead>Company</TableHead>
                                        <TableHead>Sector</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead className="text-right">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {tickers.map((ticker) => (
                                        <TableRow key={ticker.ticker_id}>
                                            <TableCell className="font-medium">{ticker.symbol}</TableCell>
                                            <TableCell>{ticker.company_name}</TableCell>
                                            <TableCell>{ticker.sector}</TableCell>
                                            <TableCell>
                                                {ticker.active ? (
                                                    <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Active</Badge>
                                                ) : (
                                                    <Badge variant="outline" className="text-muted-foreground">Inactive</Badge>
                                                )}
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleDeleteTicker(ticker.symbol)}>
                                                    <Trash2 className="h-4 w-4 text-muted-foreground hover:text-red-500" />
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                    {tickers.length === 0 && (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                                No tickers found. Add one to get started.
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
