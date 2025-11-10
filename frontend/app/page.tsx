"use client"

import { useState } from "react"
import Sidebar from "@/components/layout/sidebar"
import DashboardContent from "@/components/dashboard/dashboard-content"
import { ForecastingProvider } from "@/contexts/forecasting-context"

export default function Home() {
  const [activeTab, setActiveTab] = useState("overview")

  return (
    <ForecastingProvider>
      <div className="flex h-screen bg-background">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className="flex-1 overflow-hidden">
          <DashboardContent activeTab={activeTab} />
        </main>
      </div>
    </ForecastingProvider>
  )
}
