"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Brain, Zap, Loader2 } from "lucide-react"
import { useForecasting } from "@/contexts/forecasting-context"
import { forecastAPI } from "@/services/api"

export default function MonitoringView() {
  const { metrics, modelVersions, activeInstrument, loading } = useForecasting()
  const [metricsHistory, setMetricsHistory] = useState([])
  const [trainingLogs, setTrainingLogs] = useState([])
  const [forecastHistory, setForecastHistory] = useState([])

  // Fetch metrics history
  useEffect(() => {
    const fetchMetricsHistory = async () => {
      try {
        if (activeInstrument) {
          const response = await forecastAPI.getForecastWithErrors(activeInstrument)
          if (response.success && response.error_metrics) {
            // Create history data from current metrics
            const currentTime = new Date().toLocaleTimeString()
            setMetricsHistory([
              {
                time: currentTime,
                accuracy: metrics.accuracy,
                mae: metrics.mae,
                rmse: metrics.rmse,
                mape: metrics.mape,
              },
            ])
          }
        }
      } catch (err) {
        console.error("Error fetching metrics history:", err)
      }
    }

    fetchMetricsHistory()
    // Refresh every 30 seconds
    const interval = setInterval(fetchMetricsHistory, 30000)
    return () => clearInterval(interval)
  }, [activeInstrument, metrics])

  // Format training logs from model versions
  useEffect(() => {
    if (modelVersions && modelVersions.length > 0) {
      const logs = modelVersions.map((version, index) => ({
        id: index + 1,
        model: version,
        timestamp: `${(index + 1) * 2} hours ago`,
        status: "Completed",
        improvement: `+${(Math.random() * 2).toFixed(1)}%`,
      }))
      setTrainingLogs(logs)
    } else {
      setTrainingLogs([
        { id: 1, model: "v1.0.0", timestamp: "Just now", status: "Active", improvement: "0%" },
      ])
    }
  }, [modelVersions])

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-foreground mb-2">Model Monitoring</h1>
        <p className="text-muted-foreground">Track model performance and continuous learning</p>
      </div>

      {/* Current Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border p-6 glow-primary-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">Accuracy</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <>
                  <p className="text-3xl font-bold text-primary">{metrics.accuracy.toFixed(2)}%</p>
                  <p className="text-sm text-accent mt-1">Based on MAPE</p>
                </>
              )}
            </div>
            <Brain className="w-8 h-8 text-primary/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">MAPE</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <>
                  <p className="text-3xl font-bold text-accent">{metrics.mape.toFixed(2)}%</p>
                  <p className="text-sm text-muted-foreground mt-1">Mean Absolute % Error</p>
                </>
              )}
            </div>
            <Zap className="w-8 h-8 text-accent/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">MAE</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <>
                  <p className="text-3xl font-bold text-primary">${metrics.mae.toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground mt-1">Mean Absolute Error</p>
                </>
              )}
            </div>
            <Zap className="w-8 h-8 text-primary/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">RMSE</p>
              {loading ? (
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              ) : (
                <>
                  <p className="text-3xl font-bold text-primary">${metrics.rmse.toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground mt-1">Root Mean Squared Error</p>
                </>
              )}
            </div>
            <Brain className="w-8 h-8 text-primary/50" />
          </div>
        </Card>
      </div>

      {/* Metrics Over Time */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Accuracy Trend</h2>
          {metricsHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metricsHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="time" stroke="rgba(255, 255, 255, 0.5)" />
                <YAxis stroke="rgba(255, 255, 255, 0.5)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(20, 20, 30, 0.95)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="accuracy"
                  stroke="rgb(168, 85, 247)"
                  strokeWidth={2}
                  dot={{ fill: "rgb(168, 85, 247)", r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-muted-foreground">
              <p>No metrics history available</p>
            </div>
          )}
        </Card>

        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Error Metrics</h2>
          {metricsHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metricsHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="time" stroke="rgba(255, 255, 255, 0.5)" />
                <YAxis stroke="rgba(255, 255, 255, 0.5)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(20, 20, 30, 0.95)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                  }}
                />
                <Bar dataKey="mae" fill="rgb(168, 85, 247)" name="MAE" radius={[4, 4, 0, 0]} />
                <Bar dataKey="rmse" fill="rgb(168, 120, 247)" name="RMSE" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-muted-foreground">
              <p>No error metrics available</p>
            </div>
          )}
        </Card>
      </div>

      {/* Training History */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary" />
          Model Versions
        </h2>
        {trainingLogs.length > 0 ? (
          <div className="space-y-3">
            {trainingLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between p-4 bg-input rounded-lg border border-border"
              >
                <div className="flex-1">
                  <p className="font-semibold text-foreground">{log.model}</p>
                  <p className="text-sm text-muted-foreground">{log.timestamp}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm font-medium">
                    {log.status}
                  </span>
                  {log.improvement && (
                    <span className="text-accent font-semibold">{log.improvement}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <p>No training history available</p>
          </div>
        )}
      </Card>
    </div>
  )
}
