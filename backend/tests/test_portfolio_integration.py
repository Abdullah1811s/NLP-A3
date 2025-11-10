"""
Integration tests for portfolio API endpoints
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from backend.models.portfolio import Portfolio, Position, Transaction
from backend.models.forecast import Forecast


@pytest.mark.integration
class TestPortfolioAPI:
    """Integration tests for portfolio API"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_buy_endpoint(self, mock_price, client, test_db, clean_portfolio):
        """Test POST /api/portfolio/buy"""
        mock_price.return_value = 150.0
        
        response = client.post("/api/portfolio/buy", json={
            "ticker": "AAPL",
            "quantity": 10.0,
            "price": 150.0,
            "reason": "test"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "transaction_id" in data
        assert "remaining_cash" in data
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_buy_endpoint_missing_ticker(self, mock_price, client, test_db, clean_portfolio):
        """Test POST /api/portfolio/buy with missing ticker"""
        response = client.post("/api/portfolio/buy", json={
            "quantity": 10.0
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Ticker is required" in data["message"]
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_sell_endpoint(self, mock_price, client, test_db, clean_portfolio):
        """Test POST /api/portfolio/sell"""
        mock_price.return_value = 155.0
        
        # First buy
        buy_response = client.post("/api/portfolio/buy", json={
            "ticker": "AAPL",
            "quantity": 10.0,
            "price": 150.0
        })
        assert buy_response.status_code == 200
        
        # Then sell
        response = client.post("/api/portfolio/sell", json={
            "ticker": "AAPL",
            "quantity": 5.0,
            "price": 155.0
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "transaction_id" in data
    
    def test_get_positions_endpoint(self, client, test_db, clean_portfolio):
        """Test GET /api/portfolio/positions"""
        with patch('backend.services.portfolio_service.get_current_price', return_value=150.0):
            # Buy some assets first
            client.post("/api/portfolio/buy", json={
                "ticker": "AAPL",
                "quantity": 10.0,
                "price": 150.0
            })
        
        response = client.get("/api/portfolio/positions")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_summary_endpoint(self, client, test_db, clean_portfolio):
        """Test GET /api/portfolio/summary"""
        response = client.get("/api/portfolio/summary")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        summary = data["data"]
        assert "total_value" in summary
        assert "total_return" in summary
        assert "sharpe_ratio" in summary
        assert "positions" in summary
    
    def test_get_performance_endpoint(self, client, test_db, clean_portfolio):
        """Test GET /api/portfolio/performance"""
        response = client.get("/api/portfolio/performance?days=30")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_execute_strategy_endpoint(self, mock_price, client, test_db, clean_portfolio, clean_forecasts):
        """Test POST /api/portfolio/execute-strategy"""
        mock_price.return_value = 150.0
        
        # Create a forecast
        forecast = Forecast(
            ticker="AAPL",
            horizon="5d",
            forecast_data=[
                {"Date": "2025-01-06", "Close": 150.0},
                {"Date": "2025-01-07", "Close": 155.0},  # 3.3% increase
            ],
            model_info={"model_type": "LSTM"}
        )
        forecast.save()
        
        response = client.post("/api/portfolio/execute-strategy", json={
            "ticker": "AAPL",
            "strategy": "momentum"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "forecast_analysis" in data
        assert "action_taken" in data["forecast_analysis"]
    
    def test_execute_strategy_invalid_strategy(self, client, test_db, clean_portfolio):
        """Test POST /api/portfolio/execute-strategy with invalid strategy"""
        response = client.post("/api/portfolio/execute-strategy", json={
            "ticker": "AAPL",
            "strategy": "invalid_strategy"
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Strategy must be" in data["message"]


@pytest.mark.integration
class TestForecastAPI:
    """Integration tests for forecast API endpoints"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @patch('backend.services.data_fetcher.fetch')
    @patch('backend.services.lstmModel.trainModel')
    def test_forecast_start_endpoint(self, mock_train, mock_fetch, client, test_db, clean_forecasts):
        """Test POST /api/forecast/start"""
        # Mock data fetch
        mock_fetch.return_value = {
            "success": True,
            "hist_df": [
                {"Date": "2025-01-01", "Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
            ] * 100
        }
        
        # Mock model training
        import pandas as pd
        forecast_df = pd.DataFrame([{"Date": "2025-01-06", "Close": 155.0}])
        model_info = {"model_type": "LSTM", "rmse": 1.5, "mae": 1.2, "mape": 0.8}
        from backend.models.lstmDb import lstmInfo
        mock_record = lstmInfo(ticker="AAPL", horizon="5d", forecast_data=[], model_info=model_info)
        
        mock_train.return_value = (forecast_df, model_info, mock_record)
        
        response = client.post("/api/forecast/start", json={
            "tickerName": "AAPL",
            "horizon": "5d",
            "model_name": "LSTM"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "forecast" in data
        assert "model_info" in data
    
    @patch('backend.services.forecast_evaluator.fetch')
    def test_forecast_evaluate_endpoint(self, mock_fetch, client, test_db, clean_forecasts):
        """Test GET /api/forecast/evaluate"""
        # Create a forecast
        forecast = Forecast(
            ticker="AAPL",
            horizon="2d",
            forecast_data=[
                {"Date": "2025-01-06", "Open": 155.0, "High": 157.0, "Low": 154.0, "Close": 156.0, "Volume": 1500000},
            ],
            model_info={"model_type": "LSTM"}
        )
        forecast.save()
        
        # Mock actual price data
        mock_fetch.return_value = {
            "success": True,
            "hist_df": [
                {"Date": "2025-01-06", "Open": 155.5, "High": 157.2, "Low": 154.1, "Close": 156.5, "Volume": 1500000},
            ]
        }
        
        response = client.get("/api/forecast/evaluate?ticker=AAPL")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "candlestick_data" in data
        assert "error_metrics" in data

