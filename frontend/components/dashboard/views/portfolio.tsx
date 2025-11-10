"use client"

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
import { TrendingUp, Plus, Minus } from "lucide-react"
import { useForecasting } from "@/contexts/forecasting-context"

const portfolioData = [
  { name: "BTC/USD", value: 40 },
  { name: "ETH/USD", value: 35 },
  { name: "SPY", value: 20 },
  { name: "Cash", value: 5 },
]

const colors = ["rgb(168, 85, 247)", "rgb(168, 120, 247)", "rgb(168, 150, 247)", "rgb(100, 100, 120)"]

const performanceData = [
  { date: "Week 1", returns: 5.2 },
  { date: "Week 2", returns: 8.4 },
  { date: "Week 3", returns: 12.1 },
  { date: "Week 4", returns: 15.8 },
]

export default function PortfolioView() {
  const { portfolioPositions, portfolioValue } = useForecasting()

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Portfolio Management</h1>
          <p className="text-muted-foreground">Simulated trading and performance tracking</p>
        </div>
        <div className="flex gap-2">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2">
            <Plus className="w-4 h-4" />
            Buy
          </Button>
          <Button variant="outline" className="border-border hover:bg-card gap-2 bg-transparent">
            <Minus className="w-4 h-4" />
            Sell
          </Button>
        </div>
      </div>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border p-6 glow-primary-sm">
          <p className="text-muted-foreground text-sm mb-2">Total Portfolio Value</p>
          <p className="text-4xl font-bold text-primary">${(portfolioValue / 1000).toFixed(1)}K</p>
          <p className="text-sm text-accent mt-2">↑ $3,240 (3.2%) today</p>
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">YTD Return</p>
          <p className="text-4xl font-bold text-accent">24.8%</p>
          <p className="text-sm text-muted-foreground mt-2">vs S&P 500: 18.2%</p>
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Sharpe Ratio</p>
          <p className="text-4xl font-bold text-primary">1.85</p>
          <p className="text-sm text-muted-foreground mt-2">Risk-adjusted returns</p>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocation */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Portfolio Allocation</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={portfolioData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {portfolioData.map((entry, index) => (
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
        </Card>

        {/* Performance */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Weekly Performance</h2>
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
        </Card>
      </div>

      {/* Holdings */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          Current Holdings
        </h2>
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
                const pnl = (position.currentPrice - position.averagePrice) * position.quantity
                const pnlPercent = ((position.currentPrice - position.averagePrice) / position.averagePrice) * 100
                return (
                  <tr key={position.symbol} className="border-b border-border hover:bg-input/50 transition-colors">
                    <td className="py-3 px-4 font-semibold text-foreground">{position.symbol}</td>
                    <td className="py-3 px-4 text-foreground">{position.quantity}</td>
                    <td className="py-3 px-4 text-foreground">${position.averagePrice.toLocaleString()}</td>
                    <td className="py-3 px-4 text-foreground">${position.currentPrice.toLocaleString()}</td>
                    <td className={`py-3 px-4 font-semibold ${pnl >= 0 ? "text-accent" : "text-destructive"}`}>
                      ${pnl.toFixed(2)} ({pnlPercent > 0 ? "+" : ""}
                      {pnlPercent.toFixed(2)}%)
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
