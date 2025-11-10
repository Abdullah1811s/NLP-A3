"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Line, ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { TrendingUp, RefreshCw, Download } from "lucide-react"

const candlestickData = [
  { time: "09:00", open: 44800, high: 45200, low: 44600, close: 45100, predicted: 45150 },
  { time: "10:00", open: 45100, high: 45600, low: 45000, close: 45400, predicted: 45350 },
  { time: "11:00", open: 45400, high: 46100, low: 45200, close: 46000, predicted: 45950 },
  { time: "12:00", open: 46000, high: 46200, low: 45800, close: 45950, predicted: 46100 },
  { time: "13:00", open: 45950, high: 46300, low: 45700, close: 46200, predicted: 46180 },
  { time: "14:00", open: 46200, high: 46800, low: 46000, close: 46750, predicted: 46700 },
]

export default function ForecastingView() {
  const [selectedInstrument, setSelectedInstrument] = useState("BTC/USD")
  const [forecastHorizon, setForecastHorizon] = useState("24h")

  const instruments = ["BTC/USD", "ETH/USD", "SPY", "EURUSD"]
  const horizons = ["1h", "4h", "24h", "7d"]

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Price Forecasting</h1>
          <p className="text-muted-foreground">Real-time predictions with adaptive learning</p>
        </div>
        <div className="flex gap-2">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground gap-2">
            <RefreshCw className="w-4 h-4" />
            Retrain Model
          </Button>
          <Button variant="outline" className="border-border hover:bg-card gap-2 bg-transparent">
            <Download className="w-4 h-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="bg-card border-border p-4">
          <label className="text-sm text-muted-foreground block mb-2">Instrument</label>
          <select
            value={selectedInstrument}
            onChange={(e) => setSelectedInstrument(e.target.value)}
            className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground"
          >
            {instruments.map((inst) => (
              <option key={inst} value={inst} className="bg-card">
                {inst}
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
          {selectedInstrument} - Candlestick & Predictions
        </h2>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={candlestickData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
            <XAxis dataKey="time" stroke="rgba(255, 255, 255, 0.5)" />
            <YAxis stroke="rgba(255, 255, 255, 0.5)" />
            <Tooltip
              contentStyle={{ backgroundColor: "rgba(20, 20, 30, 0.95)", border: "1px solid rgba(168, 85, 247, 0.3)" }}
            />
            <Bar dataKey="close" fill="rgba(168, 85, 247, 0.2)" name="Close Price" />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="rgb(168, 85, 247)"
              strokeWidth={3}
              name="Predicted"
              dot={{ fill: "rgb(168, 85, 247)", r: 4 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </Card>

      {/* Prediction Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Next Hour Prediction</p>
          <p className="text-3xl font-bold text-primary">$46,850</p>
          <p className="text-sm text-accent mt-2">+1.2% expected</p>
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">24h Target</p>
          <p className="text-3xl font-bold text-accent">$47,200</p>
          <p className="text-sm text-accent mt-2">+2.8% expected</p>
        </Card>

        <Card className="bg-card border-border p-6">
          <p className="text-muted-foreground text-sm mb-2">Confidence Level</p>
          <p className="text-3xl font-bold text-primary">87.3%</p>
          <div className="w-full bg-input rounded-full h-2 mt-3">
            <div className="bg-primary h-full rounded-full" style={{ width: "87.3%" }}></div>
          </div>
        </Card>
      </div>
    </div>
  )
}
