/**
 * API service for backend communication
 */

const API_BASE_URL = "http://localhost:5001";

/**
 * Helper function to make API requests
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "Request failed" }));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Forecast API
 */
export const forecastAPI = {
  /**
   * Start forecasting for a ticker
   */
  async startForecast(tickerName, horizon, modelName = "LSTM", scheduledTime = null) {
    return apiRequest("/api/forecast/start", {
      method: "POST",
      body: JSON.stringify({
        tickerName,
        horizon,
        model_name: modelName,
        scheduledTime,
      }),
    });
  },

  /**
   * Get forecast with error overlays for visualization
   */
  async getForecastWithErrors(ticker, forecastId = null) {
    const params = forecastId 
      ? `?forecast_id=${forecastId}` 
      : `?ticker=${ticker}`;
    return apiRequest(`/api/forecast/evaluate${params}`);
  },

  /**
   * Update forecast evaluation with latest actual prices
   */
  async updateEvaluation(ticker, forecastId = null) {
    return apiRequest("/api/forecast/update-evaluation", {
      method: "POST",
      body: JSON.stringify({ ticker, forecast_id: forecastId }),
    });
  },
};

/**
 * Portfolio API
 */
export const portfolioAPI = {
  /**
   * Get portfolio summary with all metrics
   */
  async getSummary(portfolioId = "default") {
    return apiRequest(`/api/portfolio/summary?portfolio_id=${portfolioId}`);
  },

  /**
   * Get all positions in portfolio
   */
  async getPositions(portfolioId = "default") {
    return apiRequest(`/api/portfolio/positions?portfolio_id=${portfolioId}`);
  },

  /**
   * Buy asset
   */
  async buyAsset(ticker, quantity, price = null, reason = "user_manual", portfolioId = "default") {
    return apiRequest("/api/portfolio/buy", {
      method: "POST",
      body: JSON.stringify({
        ticker,
        quantity,
        price,
        reason,
        portfolio_id: portfolioId,
      }),
    });
  },

  /**
   * Sell asset
   */
  async sellAsset(ticker, quantity, price = null, reason = "user_manual", portfolioId = "default") {
    return apiRequest("/api/portfolio/sell", {
      method: "POST",
      body: JSON.stringify({
        ticker,
        quantity,
        price,
        reason,
        portfolio_id: portfolioId,
      }),
    });
  },

  /**
   * Get performance history
   */
  async getPerformance(portfolioId = "default", days = 30) {
    return apiRequest(`/api/portfolio/performance?portfolio_id=${portfolioId}&days=${days}`);
  },

  /**
   * Execute trading strategy based on forecast
   */
  async executeStrategy(ticker, strategy = "momentum", forecastId = null, portfolioId = "default") {
    return apiRequest("/api/portfolio/execute-strategy", {
      method: "POST",
      body: JSON.stringify({
        ticker,
        strategy,
        forecast_id: forecastId,
        portfolio_id: portfolioId,
      }),
    });
  },
};

/**
 * Helper function to convert ticker format
 * Frontend: "BTC/USD" -> Backend: "BTC-USD"
 * Frontend: "AAPL" -> Backend: "AAPL"
 */
export function normalizeTicker(ticker) {
  if (ticker.includes("/")) {
    return ticker.replace("/", "-");
  }
  return ticker;
}

/**
 * Helper function to convert ticker format back
 * Backend: "BTC-USD" -> Frontend: "BTC/USD"
 */
export function formatTicker(ticker) {
  if (ticker.includes("-") && ticker.length > 6) {
    return ticker.replace("-", "/");
  }
  return ticker;
}

