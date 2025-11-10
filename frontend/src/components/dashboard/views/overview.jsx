"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  Legend,
} from "recharts"
import { TrendingUp, TrendingDown, Activity, AlertCircle, Loader2 } from "lucide-react"
import { useForecasting } from "@/contexts/forecasting-context"
import { forecastAPI, portfolioAPI } from "@/services/api"

export default function OverviewDashboard() {
  const { metrics, portfolioValue, portfolioSummary, activeInstrument, loading } = useForecasting()
  const [chartData, setChartData] = useState([])
  const [portfolioGrowth, setPortfolioGrowth] = useState([])
  const [loadingData, setLoadingData] = useState(false)

  // Fetch forecast data for chart
  useEffect(() => {
    const fetchChartData = async () => {
      if (!activeInstrument) return
      
      try {
        setLoadingData(true)
        const response = await forecastAPI.getForecastWithErrors(activeInstrument)
        if (response.success && response.candlestick_data) {
          const formattedData = response.candlestick_data
            .filter((item) => item.has_actual) // Only show data with actual values
            .slice(-10) // Last 10 data points
            .map((item) => ({
              time: item.time || new Date(item.date).toLocaleTimeString(),
              predicted: item.predicted,
              actual: item.close,
              error: item.error || 0,
            }))
          setChartData(formattedData)
        }
      } catch (err) {
        console.error("Error fetching chart data:", err)
      } finally {
        setLoadingData(false)
      }
    }

    fetchChartData()
  }, [activeInstrument])

  // Fetch portfolio growth data
  useEffect(() => {
    const fetchPortfolioGrowth = async () => {
      try {
        const response = await portfolioAPI.getPerformance("default", 30)
        if (response.success && response.data) {
          const formattedData = response.data.map((item, index) => ({
            date: `Day ${index + 1}`,
            value: item.value || portfolioValue,
            returns: item.returns || 0,
          }))
          setPortfolioGrowth(formattedData)
        } else {
          // Fallback to initial value if no data
          setPortfolioGrowth([
            { date: "Day 1", value: portfolioValue || 100000, returns: 0 },
          ])
        }
      } catch (err) {
        console.error("Error fetching portfolio growth:", err)
        // Fallback
        setPortfolioGrowth([
          { date: "Day 1", value: portfolioValue || 100000, returns: 0 },
        ])
      }
    }

    fetchPortfolioGrowth()
  }, [portfolioSummary, portfolioValue])

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-foreground mb-2">Dashboard Overview</h1>
        <p className="text-muted-foreground">Real-time forecasting and portfolio analytics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border p-6 glow-primary-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">Model Accuracy</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <p className="text-3xl font-bold text-primary">{metrics.accuracy.toFixed(1)}%</p>
              )}
            </div>
            <Activity className="w-8 h-8 text-primary/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">MAE</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <p className="text-3xl font-bold text-accent">${metrics.mae.toFixed(2)}</p>
              )}
            </div>
            <TrendingDown className="w-8 h-8 text-accent/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">RMSE</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <p className="text-3xl font-bold text-accent">${metrics.rmse.toFixed(2)}</p>
              )}
            </div>
            <AlertCircle className="w-8 h-8 text-accent/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">Portfolio Value</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <p className="text-3xl font-bold text-primary">${(portfolioValue / 1000).toFixed(1)}K</p>
              )}
            </div>
            <TrendingUp className="w-8 h-8 text-primary/50" />
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Forecast Accuracy Chart */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Price Forecast vs Actual ({activeInstrument || "N/A"})
          </h2>
          {loadingData ? (
            <div className="flex items-center justify-center h-300">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="time" stroke="rgba(255, 255, 255, 0.5)" />
                <YAxis stroke="rgba(255, 255, 255, 0.5)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(20, 20, 30, 0.95)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="predicted" stroke="rgb(168, 85, 247)" strokeWidth={2} name="Predicted" />
                <Line type="monotone" dataKey="actual" stroke="rgb(34, 197, 94)" strokeWidth={2} name="Actual" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-muted-foreground">
              <p>No forecast data available. Generate a forecast to see predictions vs actual prices.</p>
            </div>
          )}
        </Card>

        {/* Portfolio Growth */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Portfolio Growth</h2>
          {portfolioGrowth.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={portfolioGrowth}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="rgb(168, 85, 247)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="rgb(168, 85, 247)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="date" stroke="rgba(255, 255, 255, 0.5)" />
                <YAxis stroke="rgba(255, 255, 255, 0.5)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(20, 20, 30, 0.95)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="rgb(168, 85, 247)"
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-muted-foreground">
              <p>No portfolio growth data available</p>
            </div>
          )}
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Error Analysis</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
              <XAxis dataKey="time" stroke="rgba(255, 255, 255, 0.5)" />
              <YAxis stroke="rgba(255, 255, 255, 0.5)" />
              <Tooltip
                contentStyle={{ backgroundColor: "rgba(20, 20, 30, 0.95)", border: "1px solid rgba(168, 85, 247, 0.3)" }}
              />
              <Bar dataKey="error" fill="rgb(168, 85, 247)" radius={[4, 4, 0, 0]} name="Error" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-200 text-muted-foreground">
            <p>No error data available</p>
          </div>
        )}
      </Card>
    </div>
  )
}
