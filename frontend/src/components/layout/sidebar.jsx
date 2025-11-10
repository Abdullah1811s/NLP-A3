"use client"

import { BarChart3, TrendingUp, Wallet, Settings, Brain } from "lucide-react"
import { cn } from "@/lib/utils"

export default function Sidebar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "forecasting", label: "Forecasting", icon: TrendingUp },
    { id: "monitoring", label: "Monitoring", icon: Brain },
    { id: "portfolio", label: "Portfolio", icon: Wallet },
    { id: "settings", label: "Settings", icon: Settings },
  ]

  return (
    <aside className="w-64 bg-sidebar border-r border-border flex flex-col p-0">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center glow-primary">
            <Brain className="w-6 h-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-sidebar-foreground">ForecaAI</h1>
            <p className="text-xs text-muted-foreground">Adaptive Learner</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200",
                activeTab === tab.id
                  ? "bg-sidebar-primary text-sidebar-primary-foreground glow-primary-sm"
                  : "text-sidebar-foreground hover:bg-sidebar-accent",
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{tab.label}</span>
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="bg-sidebar-accent/30 rounded-lg p-3 text-xs text-sidebar-foreground">
          <p className="font-semibold mb-1">Model Status</p>
          <p className="text-sidebar-foreground/70">Active: v1.2.5</p>
          <p className="text-sidebar-foreground/70">Last updated: 2 hours ago</p>
        </div>
      </div>
    </aside>
  )
}
