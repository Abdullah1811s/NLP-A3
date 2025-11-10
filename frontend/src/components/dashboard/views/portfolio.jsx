"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { TrendingUp, Plus, Minus, Loader2 } from "lucide-react"
import { useForecasting } from "@/contexts/forecasting-context"
import { portfolioAPI, formatTicker } from "@/services/api"

const colors = ["rgb(168, 85, 247)", "rgb(168, 120, 247)", "rgb(168, 150, 247)", "rgb(100, 100, 120)", "rgb(200, 150, 247)"]

export default function PortfolioView() {
  const { portfolioPositions, portfolioValue, portfolioSummary, refreshPortfolio, loading } = useForecasting()
  const [performanceData, setPerformanceData] = useState([])
  const [showBuyDialog, setShowBuyDialog] = useState(false)
  const [showSellDialog, setShowSellDialog] = useState(false)
  const [selectedTicker, setSelectedTicker] = useState("")
  const [quantity, setQuantity] = useState("")
  const [buySellLoading, setBuySellLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch performance history
  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        const response = await portfolioAPI.getPerformance("default", 30)
        if (response.success && response.data) {
          const formattedData = response.data.map((item, index) => ({
            date: `Day ${index + 1}`,
            returns: item.returns || 0,
            value: item.value || 0,
          }))
          setPerformanceData(formattedData)
        }
      } catch (err) {
        console.error("Error fetching performance:", err)
      }
    }
    fetchPerformance()
  }, [portfolioSummary])

  // Get allocation data
  const getAllocationData = () => {
    if (!portfolioSummary || !portfolioSummary.allocation) {
      return []
    }
    return portfolioSummary.allocation.map((item) => ({
      name: formatTicker(item.name),
      value: parseFloat(item.value.toFixed(1)),
    }))
  }

  // Handle buy
  const handleBuy = async () => {
    if (!selectedTicker || !quantity) {
      setError("Please enter ticker and quantity")
      return
    }

    try {
      setBuySellLoading(true)
      setError(null)
      const response = await portfolioAPI.buyAsset(selectedTicker, parseFloat(quantity))
      
      if (response.success) {
        refreshPortfolio()
        setShowBuyDialog(false)
        setSelectedTicker("")
        setQuantity("")
      } else {
        setError(response.message || "Failed to buy asset")
      }
    } catch (err) {
      setError(err.message || "Failed to buy asset")
    } finally {
      setBuySellLoading(false)
    }
  }

  // Handle sell
  const handleSell = async () => {
    if (!selectedTicker || !quantity) {
      setError("Please enter ticker and quantity")
      return
    }

    try {
      setBuySellLoading(true)
      setError(null)
      const response = await portfolioAPI.sellAsset(selectedTicker, parseFloat(quantity))
      
      if (response.success) {
        refreshPortfolio()
        setShowSellDialog(false)
        setSelectedTicker("")
        setQuantity("")
      } else {
        setError(response.message || "Failed to sell asset")
      }
    } catch (err) {
      setError(err.message || "Failed to sell asset")
    } finally {
      setBuySellLoading(false)
    }
  }

  const allocationData = getAllocationData()
  const totalReturn = portfolioSummary?.total_return || 0
  const sharpeRatio = portfolioSummary?.sharpe_ratio || 0
  const currentValue = portfolioValue || portfolioSummary?.total_value || 100000

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Portfolio Management</h1>
          <p className="text-muted-foreground">Simulated trading and performance tracking</p>
        </div>
        <div className="flex gap-2">
          <Button 
            className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2"
            onClick={() => setShowBuyDialog(true)}
          >
            <Plus className="w-4 h-4" />
            Buy
          </Button>
          <Button 
            variant="outline" 
            className="border-border hover:bg-card gap-2 bg-transparent"
            onClick={() => setShowSellDialog(true)}
          >
            <Minus className="w-4 h-4" />
            Sell
          </Button>
        </div>
      </div>

      {error && (
        <Card className="bg-destructive/10 border-destructive p-4">
          <p className="text-destructive">{error}</p>
        </Card>
      )}

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border p-6 glow-primary-sm">
          <p className="text-muted-foreground text-sm mb-2">Total Portfolio Value</p>
          {loading ? (
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          ) : (
            <>
              <p className="text-4xl font-bold text-primary">${(currentValue / 1000).toFixed(1)}K</p>
              <p className={`text-sm mt-2 ${totalReturn >= 0 ? "text-accent" : "text-destructive"}`}>
                {totalReturn >= 0 ? "↑" : "↓"} ${Math.abs(totalReturn).toFixed(2)} ({totalReturn.toFixed(2)}%)
              </p>
            </>
          )}
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Total Return</p>
          {loading ? (
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          ) : (
            <>
              <p className={`text-4xl font-bold ${totalReturn >= 0 ? "text-accent" : "text-destructive"}`}>
                {totalReturn.toFixed(2)}%
              </p>
              <p className="text-sm text-muted-foreground mt-2">From initial investment</p>
            </>
          )}
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Sharpe Ratio</p>
          {loading ? (
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          ) : (
            <>
              <p className="text-4xl font-bold text-primary">{sharpeRatio.toFixed(2)}</p>
              <p className="text-sm text-muted-foreground mt-2">Risk-adjusted returns</p>
            </>
          )}
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocation */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Portfolio Allocation</h2>
          {allocationData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(20, 20, 30, 0.95)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-muted-foreground">
              <p>No allocation data available</p>
            </div>
          )}
        </Card>

        {/* Performance */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Performance History</h2>
          {performanceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="date" stroke="rgba(255, 255, 255, 0.5)" />
                <YAxis stroke="rgba(255, 255, 255, 0.5)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(20, 20, 30, 0.95)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="returns"
                  stroke="rgb(168, 85, 247)"
                  strokeWidth={2}
                  dot={{ fill: "rgb(168, 85, 247)", r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-muted-foreground">
              <p>No performance data available</p>
            </div>
          )}
        </Card>
      </div>

      {/* Holdings */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          Current Holdings
        </h2>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : portfolioPositions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-border">
                <tr className="text-muted-foreground text-sm">
                  <th className="text-left py-3 px-4">Symbol</th>
                  <th className="text-left py-3 px-4">Quantity</th>
                  <th className="text-left py-3 px-4">Avg Price</th>
                  <th className="text-left py-3 px-4">Current</th>
                  <th className="text-left py-3 px-4">P&L</th>
                </tr>
              </thead>
              <tbody>
                {portfolioPositions.map((position) => {
                  const pnl = position.pnl || 0
                  const pnlPercent = position.pnlPercent || 0
                  return (
                    <tr key={position.symbol} className="border-b border-border hover:bg-input/50 transition-colors">
                      <td className="py-3 px-4 font-semibold text-foreground">{formatTicker(position.symbol)}</td>
                      <td className="py-3 px-4 text-foreground">{position.quantity.toFixed(4)}</td>
                      <td className="py-3 px-4 text-foreground">${position.averagePrice.toFixed(2)}</td>
                      <td className="py-3 px-4 text-foreground">${position.currentPrice.toFixed(2)}</td>
                      <td className={`py-3 px-4 font-semibold ${pnl >= 0 ? "text-accent" : "text-destructive"}`}>
                        ${pnl.toFixed(2)} ({pnlPercent >= 0 ? "+" : ""}{pnlPercent.toFixed(2)}%)
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <p>No positions yet. Click "Buy" to add assets to your portfolio.</p>
          </div>
        )}
      </Card>

      {/* Buy Dialog */}
      {showBuyDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-card border-border p-6 w-96">
            <h3 className="text-xl font-bold mb-4">Buy Asset</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-muted-foreground block mb-2">Ticker</label>
                <input
                  type="text"
                  value={selectedTicker}
                  onChange={(e) => setSelectedTicker(e.target.value.toUpperCase())}
                  className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground"
                  placeholder="e.g., AAPL"
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground block mb-2">Quantity</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground"
                  placeholder="e.g., 10"
                />
              </div>
              {error && <p className="text-destructive text-sm">{error}</p>}
              <div className="flex gap-2">
                <Button
                  className="flex-1"
                  onClick={handleBuy}
                  disabled={buySellLoading}
                >
                  {buySellLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Buy"}
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setShowBuyDialog(false)
                    setError(null)
                    setSelectedTicker("")
                    setQuantity("")
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Sell Dialog */}
      {showSellDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="bg-card border-border p-6 w-96">
            <h3 className="text-xl font-bold mb-4">Sell Asset</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-muted-foreground block mb-2">Ticker</label>
                <select
                  value={selectedTicker}
                  onChange={(e) => setSelectedTicker(e.target.value)}
                  className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground"
                >
                  <option value="">Select ticker</option>
                  {portfolioPositions.map((pos) => (
                    <option key={pos.symbol} value={pos.symbol}>
                      {formatTicker(pos.symbol)} (Qty: {pos.quantity.toFixed(4)})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm text-muted-foreground block mb-2">Quantity</label>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground"
                  placeholder="e.g., 5"
                />
              </div>
              {error && <p className="text-destructive text-sm">{error}</p>}
              <div className="flex gap-2">
                <Button
                  className="flex-1"
                  onClick={handleSell}
                  disabled={buySellLoading}
                >
                  {buySellLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Sell"}
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setShowSellDialog(false)
                    setError(null)
                    setSelectedTicker("")
                    setQuantity("")
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
