"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Line, ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { TrendingUp, RefreshCw, Download, Loader2 } from "lucide-react"
import { forecastAPI, normalizeTicker, formatTicker } from "@/services/api"
import { useForecasting } from "@/contexts/forecasting-context"

export default function ForecastingView() {
  const { setActiveInstrument, refreshPortfolio } = useForecasting()
  const [selectedInstrument, setSelectedInstrument] = useState("AAPL")
  const [forecastHorizon, setForecastHorizon] = useState("24d")
  const [candlestickData, setCandlestickData] = useState([])
  const [loading, setLoading] = useState(false)
  const [forecasting, setForecasting] = useState(false)
  const [error, setError] = useState(null)
  const [forecastInfo, setForecastInfo] = useState(null)

  const instruments = ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC-USD", "ETH-USD", "SPY"]
  const horizons = ["5d", "10d", "24d", "30d"]

  // Convert horizon format for backend
  const getBackendHorizon = (horizon) => {
    return horizon // Backend expects "24d" format
  }

  // Fetch forecast data
  const fetchForecastData = async (ticker) => {
    try {
      setLoading(true)
      setError(null)
      const normalizedTicker = normalizeTicker(ticker)
      const response = await forecastAPI.getForecastWithErrors(normalizedTicker)
      
      if (response.success && response.candlestick_data && response.candlestick_data.length > 0) {
        // Transform data for chart
        const chartData = response.candlestick_data.map((item) => ({
          date: item.date ? new Date(item.date).toLocaleDateString() : item.time || "",
          time: item.time || (item.date ? new Date(item.date).toLocaleTimeString() : ""),
          open: item.open || 0,
          high: item.high || 0,
          low: item.low || 0,
          close: item.close || 0,
          predicted: item.predicted || 0,
          error: item.error,
          hasActual: item.has_actual || false,
        }))
        setCandlestickData(chartData)
        setForecastInfo(response)
      } else {
        // No forecast data yet - this is okay, user needs to start a forecast
        setCandlestickData([])
        setForecastInfo(null)
      }
    } catch (err) {
      // Don't show error if it's just that no forecast exists yet
      if (!err.message.includes("No forecast found")) {
        console.error("Error fetching forecast data:", err)
        setError(err.message)
      }
      setCandlestickData([])
      setForecastInfo(null)
    } finally {
      setLoading(false)
    }
  }

  // Start forecast
  const handleStartForecast = async () => {
    try {
      setForecasting(true)
      setError(null)
      const normalizedTicker = normalizeTicker(selectedInstrument)
      const horizon = getBackendHorizon(forecastHorizon)
      
      const response = await forecastAPI.startForecast(normalizedTicker, horizon, "LSTM")
      
      if (response.success) {
        // Refresh forecast data after a short delay
        setTimeout(() => {
          fetchForecastData(selectedInstrument)
          refreshPortfolio()
        }, 2000)
      } else {
        setError(response.message || "Failed to start forecast")
      }
    } catch (err) {
      console.error("Error starting forecast:", err)
      setError(err.message || "Failed to start forecast")
    } finally {
      setForecasting(false)
    }
  }

  // Fetch data when instrument changes
  useEffect(() => {
    if (selectedInstrument) {
      setActiveInstrument(selectedInstrument)
      fetchForecastData(selectedInstrument)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedInstrument])

  // Get next prediction
  const getNextPrediction = () => {
    if (candlestickData.length > 0) {
      const last = candlestickData[candlestickData.length - 1]
      return last.predicted || last.close
    }
    return 0
  }

  // Get target prediction
  const getTargetPrediction = () => {
    if (candlestickData.length > 0) {
      const avgPredicted = candlestickData.reduce((sum, item) => sum + (item.predicted || 0), 0) / candlestickData.length
      return avgPredicted
    }
    return 0
  }

  // Calculate confidence (inverse of MAPE)
  const getConfidence = () => {
    if (forecastInfo && forecastInfo.error_metrics && forecastInfo.error_metrics.mape) {
      return Math.max(0, Math.min(100, 100 - forecastInfo.error_metrics.mape))
    }
    return 0
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Price Forecasting</h1>
          <p className="text-muted-foreground">Real-time predictions with adaptive learning</p>
        </div>
        <div className="flex gap-2">
          <Button 
            className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2"
            onClick={handleStartForecast}
            disabled={forecasting || loading}
          >
            {forecasting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Training...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                Start Forecast
              </>
            )}
          </Button>
        </div>
      </div>

      {error && (
        <Card className="bg-destructive/10 border-destructive p-4">
          <p className="text-destructive">{error}</p>
        </Card>
      )}

      {/* Controls */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-card border-border p-4">
          <label className="text-sm text-muted-foreground block mb-2">Instrument</label>
          <select
            value={selectedInstrument}
            onChange={(e) => setSelectedInstrument(e.target.value)}
            className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground"
            disabled={loading || forecasting}
          >
            {instruments.map((inst) => (
              <option key={inst} value={inst} className="bg-card">
                {formatTicker(inst)}
              </option>
            ))}
          </select>
        </Card>

        <Card className="bg-card border-border p-4">
          <label className="text-sm text-muted-foreground block mb-2">Forecast Horizon</label>
          <div className="flex gap-2">
            {horizons.map((h) => (
              <button
                key={h}
                onClick={() => setForecastHorizon(h)}
                disabled={loading || forecasting}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                  forecastHorizon === h
                    ? "bg-primary text-primary-foreground glow-primary-sm"
                    : "bg-input text-foreground hover:bg-border"
                }`}
              >
                {h}
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* Main Candlestick Chart with Predictions */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          {formatTicker(selectedInstrument)} - Candlestick & Predictions
        </h2>
        {loading ? (
          <div className="flex items-center justify-center h-400">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : candlestickData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={candlestickData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
              <XAxis dataKey="date" stroke="rgba(255, 255, 255, 0.5)" />
              <YAxis stroke="rgba(255, 255, 255, 0.5)" />
              <Tooltip
                contentStyle={{ backgroundColor: "rgba(20, 20, 30, 0.95)", border: "1px solid rgba(168, 85, 247, 0.3)" }}
              />
              <Legend />
              <Bar dataKey="close" fill="rgba(168, 85, 247, 0.3)" name="Close Price" />
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="rgb(168, 85, 247)"
                strokeWidth={3}
                name="Predicted"
                dot={{ fill: "rgb(168, 85, 247)", r: 4 }}
              />
              {candlestickData.some((d) => d.hasActual) && (
                <Line
                  type="monotone"
                  dataKey="close"
                  stroke="rgb(34, 197, 94)"
                  strokeWidth={2}
                  name="Actual"
                  strokeDasharray="5 5"
                  dot={{ fill: "rgb(34, 197, 94)", r: 3 }}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-400 text-muted-foreground">
            <p>No forecast data available. Click "Start Forecast" to generate predictions.</p>
          </div>
        )}
      </Card>

      {/* Prediction Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Next Prediction</p>
          <p className="text-3xl font-bold text-primary">${getNextPrediction().toFixed(2)}</p>
          <p className="text-sm text-accent mt-2">
            {candlestickData.length > 0 && candlestickData[0].close 
              ? `${(((getNextPrediction() - candlestickData[0].close) / candlestickData[0].close) * 100).toFixed(2)}% expected`
              : "No data"}
          </p>
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Average Target</p>
          <p className="text-3xl font-bold text-accent">${getTargetPrediction().toFixed(2)}</p>
          <p className="text-sm text-accent mt-2">
            {forecastInfo && forecastInfo.error_metrics 
              ? `MAPE: ${forecastInfo.error_metrics.mape?.toFixed(2) || 0}%`
              : "No data"}
          </p>
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Confidence Level</p>
          <p className="text-3xl font-bold text-primary">{getConfidence().toFixed(1)}%</p>
          <div className="w-full bg-input rounded-full h-2 mt-3">
            <div 
              className="bg-primary h-full rounded-full transition-all" 
              style={{ width: `${getConfidence()}%` }}
            ></div>
          </div>
        </Card>
      </div>
    </div>
  )
}
