"use client"

import { createContext, useContext, useState } from "react"

const ForecastingContext = createContext()

export function ForecastingProvider({ children }) {
  const [activeInstrument, setActiveInstrument] = useState("BTC/USD")
  const [metrics, setMetrics] = useState({
    mae: 245.32,
    rmse: 312.18,
    mape: 2.34,
    accuracy: 94.2,
  })
  const [portfolioPositions, setPortfolioPositions] = useState([
    { symbol: "BTC/USD", quantity: 0.5, averagePrice: 42000, currentPrice: 45000 },
    { symbol: "ETH/USD", quantity: 5, averagePrice: 2200, currentPrice: 2450 },
  ])
  const [portfolioValue, setPortfolioValue] = useState(45000)
  const [modelVersions] = useState(["v1.2.5", "v1.2.4", "v1.2.3"])

  return (
    <ForecastingContext.Provider
      value={{
        activeInstrument,
        setActiveInstrument,
        metrics,
        setMetrics,
        portfolioPositions,
        setPortfolioPositions,
        portfolioValue,
        setPortfolioValue,
        modelVersions,
      }}
    >
      {children}
    </ForecastingContext.Provider>
  )
}

export function useForecasting() {
  const context = useContext(ForecastingContext)
  if (!context) {
    throw new Error("useForecasting must be used within ForecastingProvider")
  }
  return context
}
