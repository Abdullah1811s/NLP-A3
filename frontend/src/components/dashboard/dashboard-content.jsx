import OverviewDashboard from "./views/overview"
import ForecastingView from "./views/forecasting"
import MonitoringView from "./views/monitoring"
import PortfolioView from "./views/portfolio"
import SettingsView from "./views/settings"

export default function DashboardContent({ activeTab }) {
  return (
    <div className="h-full overflow-auto bg-background">
      {activeTab === "overview" && <OverviewDashboard />}
      {activeTab === "forecasting" && <ForecastingView />}
      {activeTab === "monitoring" && <MonitoringView />}
      {activeTab === "portfolio" && <PortfolioView />}
      {activeTab === "settings" && <SettingsView />}
    </div>
  )
}
