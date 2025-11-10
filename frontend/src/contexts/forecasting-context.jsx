"use client"

import { createContext, useContext, useState, useEffect, useCallback } from "react"
import { portfolioAPI, forecastAPI } from "@/services/api"

const ForecastingContext = createContext()

export function ForecastingProvider({ children }) {
  const [activeInstrument, setActiveInstrument] = useState("AAPL")
  const [metrics, setMetrics] = useState({
    mae: 0,
    rmse: 0,
    mape: 0,
    accuracy: 0,
  })
  const [portfolioPositions, setPortfolioPositions] = useState([])
  const [portfolioValue, setPortfolioValue] = useState(100000)
  const [portfolioSummary, setPortfolioSummary] = useState(null)
  const [modelVersions, setModelVersions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch portfolio summary
  const fetchPortfolioSummary = useCallback(async () => {
    try {
      setLoading(true)
      const response = await portfolioAPI.getSummary()
      if (response.success) {
        const data = response.data
        setPortfolioSummary(data)
        setPortfolioValue(data.total_value || 100000)
        setPortfolioPositions(data.positions || [])
        
        // Update metrics from latest forecast if available
        if (data.positions && data.positions.length > 0) {
          // We'll update metrics when forecast data is loaded
        }
      }
    } catch (err) {
      console.error("Error fetching portfolio summary:", err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch metrics from latest forecast
  const fetchMetrics = useCallback(async (ticker) => {
    try {
      const response = await forecastAPI.getForecastWithErrors(ticker)
      if (response.success && response.error_metrics) {
        const errorMetrics = response.error_metrics
        setMetrics({
          mae: errorMetrics.mae || 0,
          rmse: errorMetrics.rmse || 0,
          mape: errorMetrics.mape || 0,
          accuracy: errorMetrics.mape ? Math.max(0, 100 - errorMetrics.mape) : 0,
        })
      }
    } catch (err) {
      // Silently fail if no forecast exists yet
      if (!err.message || !err.message.includes("No forecast found")) {
        console.error("Error fetching metrics:", err)
      }
    }
  }, [])

  // Initial load
  useEffect(() => {
    fetchPortfolioSummary()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Fetch metrics when instrument changes (with debounce to avoid too many calls)
  useEffect(() => {
    if (activeInstrument) {
      const timer = setTimeout(() => {
        fetchMetrics(activeInstrument)
      }, 500) // Small delay to avoid rapid API calls
      return () => clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeInstrument])

  // Refresh portfolio
  const refreshPortfolio = useCallback(() => {
    fetchPortfolioSummary()
  }, [fetchPortfolioSummary])

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
        portfolioSummary,
        modelVersions,
        loading,
        error,
        refreshPortfolio,
        fetchPortfolioSummary,
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
