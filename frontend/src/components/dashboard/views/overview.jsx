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
} from "recharts"
import { TrendingUp, TrendingDown, Activity, AlertCircle } from "lucide-react"
import { useForecasting } from "@/contexts/forecasting-context"

const chartData = [
  { time: "00:00", predicted: 45200, actual: 45100, error: 100 },
  { time: "04:00", predicted: 45600, actual: 45400, error: 200 },
  { time: "08:00", predicted: 46100, actual: 46000, error: 100 },
  { time: "12:00", predicted: 45800, actual: 45950, error: -150 },
  { time: "16:00", predicted: 46300, actual: 46200, error: 100 },
  { time: "20:00", predicted: 46800, actual: 46750, error: 50 },
]

const portfolioGrowth = [
  { date: "Day 1", value: 100000, returns: 0 },
  { date: "Day 5", value: 105200, returns: 5.2 },
  { date: "Day 10", value: 112800, returns: 12.8 },
  { date: "Day 15", value: 118300, returns: 18.3 },
  { date: "Day 20", value: 125600, returns: 25.6 },
  { date: "Day 25", value: 132400, returns: 32.4 },
]

export default function OverviewDashboard() {
  const { metrics, portfolioValue } = useForecasting()

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
              <p className="text-3xl font-bold text-primary">{metrics.accuracy.toFixed(1)}%</p>
            </div>
            <Activity className="w-8 h-8 text-primary/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">MAE</p>
              <p className="text-3xl font-bold text-accent">${metrics.mae.toFixed(2)}</p>
            </div>
            <TrendingDown className="w-8 h-8 text-accent/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">RMSE</p>
              <p className="text-3xl font-bold text-accent">${metrics.rmse.toFixed(2)}</p>
            </div>
            <AlertCircle className="w-8 h-8 text-accent/50" />
          </div>
        </Card>

        <Card className="bg-card border-border p-6">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-muted-foreground text-sm mb-2">Portfolio Value</p>
              <p className="text-3xl font-bold text-primary">${(portfolioValue / 1000).toFixed(1)}K</p>
            </div>
            <TrendingUp className="w-8 h-8 text-primary/50" />
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Forecast Accuracy Chart */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Price Forecast vs Actual (BTC/USD)</h2>
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
              <Line type="monotone" dataKey="predicted" stroke="rgb(168, 85, 247)" strokeWidth={2} name="Predicted" />
              <Line type="monotone" dataKey="actual" stroke="rgb(100, 200, 100)" strokeWidth={2} name="Actual" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Portfolio Growth */}
        <Card className="bg-card border-border p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Portfolio Growth</h2>
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
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Error Analysis (Last 24h)</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
            <XAxis dataKey="time" stroke="rgba(255, 255, 255, 0.5)" />
            <YAxis stroke="rgba(255, 255, 255, 0.5)" />
            <Tooltip
              contentStyle={{ backgroundColor: "rgba(20, 20, 30, 0.95)", border: "1px solid rgba(168, 85, 247, 0.3)" }}
            />
            <Bar dataKey="error" fill="rgb(168, 85, 247)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  )
}
