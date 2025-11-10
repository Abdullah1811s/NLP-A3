"use client"

import { Card } from "@/components/ui/card"
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Brain, Zap } from "lucide-react"
import { useForecasting } from "@/contexts/forecasting-context"

const metricsHistory = [
  { time: "00:00", accuracy: 91.2, mae: 310, rmse: 420 },
  { time: "04:00", accuracy: 92.1, mae: 285, rmse: 385 },
  { time: "08:00", accuracy: 93.5, mae: 265, rmse: 350 },
  { time: "12:00", accuracy: 93.8, mae: 248, rmse: 312 },
  { time: "16:00", accuracy: 94.0, mae: 245, rmse: 312 },
  { time: "20:00", accuracy: 94.2, mae: 245, rmse: 312 },
]

const trainingLogs = [
  { id: 1, model: "v1.2.5", timestamp: "2 hours ago", status: "Completed", improvement: "+1.2%" },
  { id: 2, model: "v1.2.4", timestamp: "6 hours ago", status: "Completed", improvement: "+0.8%" },
  { id: 3, model: "v1.2.3", timestamp: "12 hours ago", status: "Completed", improvement: "+1.5%" },
]

export default function MonitoringView() {
  const { metrics, modelVersions } = useForecasting()

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
              <p className="text-muted-foreground text-sm mb-2">Accuracy Trend</p>
              <p className="text-3xl font-bold text-primary">{metrics.accuracy}%</p>
              <p className="text-sm text-accent mt-1">↑ 0.2% vs 4h ago</p>
            </div>
            <Brain className="w-8 h-8 text-primary/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">MAPE</p>
              <p className="text-3xl font-bold text-accent">{metrics.mape}%</p>
              <p className="text-sm text-accent mt-1">↓ 0.1% vs 4h ago</p>
            </div>
            <Zap className="w-8 h-8 text-accent/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">Training Status</p>
              <p className="text-3xl font-bold text-primary">Active</p>
              <p className="text-sm text-muted-foreground mt-1">Retrain every 2h</p>
            </div>
            <Zap className="w-8 h-8 text-primary/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-muted-foreground text-sm mb-2">Active Model</p>
              <p className="text-3xl font-bold text-primary">{modelVersions[0]}</p>
              <p className="text-sm text-muted-foreground mt-1">+2 available</p>
            </div>
            <Brain className="w-8 h-8 text-primary/50" />
          </div>
        </Card>
      </div>

      {/* Metrics Over Time */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Accuracy Trend (24h)</h2>
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
        </Card>

        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Error Metrics Trend</h2>
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
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Training History */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-primary" />
          Training History
        </h2>
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
                <span className="text-accent font-semibold">{log.improvement}</span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
