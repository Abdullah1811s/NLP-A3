"""
Unit tests for portfolio service functions
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.portfolio_service import (
    get_or_create_portfolio,
    buy_asset,
    sell_asset,
    get_portfolio_positions,
    calculate_portfolio_value,
    calculate_sharpe_ratio,
    calculate_volatility,
    get_portfolio_summary,
    execute_strategy_from_forecast
)
from backend.models.portfolio import Portfolio, Position, Transaction
from backend.models.forecast import Forecast


@pytest.mark.unit
class TestPortfolioService:
    """Unit tests for portfolio service"""
    
    def test_get_or_create_portfolio_new(self, test_db, clean_portfolio):
        """Test creating a new portfolio"""
        portfolio = get_or_create_portfolio("test_portfolio", 50000.0)
        
        assert portfolio is not None
        assert portfolio.portfolio_id == "test_portfolio"
        assert portfolio.initial_cash == 50000.0
        assert portfolio.current_cash == 50000.0
        assert portfolio.total_value == 50000.0
    
    def test_get_or_create_portfolio_existing(self, test_db, clean_portfolio):
        """Test getting existing portfolio"""
        # Create portfolio first
        portfolio1 = get_or_create_portfolio("test_portfolio", 50000.0)
        portfolio1.save()
        
        # Get it again
        portfolio2 = get_or_create_portfolio("test_portfolio", 50000.0)
        
        assert portfolio1.id == portfolio2.id
        assert portfolio2.initial_cash == 50000.0
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_buy_asset_success(self, mock_price, test_db, clean_portfolio):
        """Test successful buy order"""
        mock_price.return_value = 150.0
        
        result = buy_asset("test_portfolio", "AAPL", 10.0, 150.0, "test")
        
        assert result["success"] is True
        assert "transaction_id" in result
        assert result["remaining_cash"] < 100000.0  # Default initial cash
        
        # Verify position was created
        position = Position.objects(ticker="AAPL").first()
        assert position is not None
        assert position.quantity == 10.0
        assert position.average_price == 150.0
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_buy_asset_insufficient_cash(self, mock_price, test_db, clean_portfolio):
        """Test buy order with insufficient cash"""
        mock_price.return_value = 150.0
        
        # Try to buy more than we have cash for
        result = buy_asset("test_portfolio", "AAPL", 10000.0, 150.0, "test")
        
        assert result["success"] is False
        assert "Insufficient cash" in result["message"]
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_sell_asset_success(self, mock_price, test_db, clean_portfolio):
        """Test successful sell order"""
        mock_price.return_value = 155.0
        
        # First buy
        buy_result = buy_asset("test_portfolio", "AAPL", 10.0, 150.0, "test")
        assert buy_result["success"] is True
        
        # Then sell
        result = sell_asset("test_portfolio", "AAPL", 5.0, 155.0, "test")
        
        assert result["success"] is True
        assert "transaction_id" in result
        
        # Verify position was updated
        position = Position.objects(ticker="AAPL").first()
        assert position.quantity == 5.0  # 10 - 5
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_sell_asset_insufficient_shares(self, mock_price, test_db, clean_portfolio):
        """Test sell order with insufficient shares"""
        mock_price.return_value = 155.0
        
        result = sell_asset("test_portfolio", "AAPL", 10.0, 155.0, "test")
        
        assert result["success"] is False
        assert "No position found" in result["message"] or "Insufficient shares" in result["message"]
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_get_portfolio_positions(self, mock_price, test_db, clean_portfolio):
        """Test getting portfolio positions"""
        mock_price.return_value = 155.0
        
        # Buy some assets
        buy_asset("test_portfolio", "AAPL", 10.0, 150.0, "test")
        buy_asset("test_portfolio", "MSFT", 5.0, 200.0, "test")
        
        positions = get_portfolio_positions("test_portfolio")
        
        assert len(positions) == 2
        assert any(p["symbol"] == "AAPL" for p in positions)
        assert any(p["symbol"] == "MSFT" for p in positions)
        
        # Check position data structure
        aapl_pos = next(p for p in positions if p["symbol"] == "AAPL")
        assert "quantity" in aapl_pos
        assert "averagePrice" in aapl_pos
        assert "currentPrice" in aapl_pos
        assert "pnl" in aapl_pos
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_calculate_portfolio_value(self, mock_price, test_db, clean_portfolio):
        """Test portfolio value calculation"""
        mock_price.return_value = 155.0
        
        portfolio = get_or_create_portfolio("test_portfolio")
        buy_asset("test_portfolio", "AAPL", 10.0, 150.0, "test")
        
        value = calculate_portfolio_value(portfolio)
        
        assert value > 0
        assert value == portfolio.current_cash + (155.0 * 10.0)  # Cash + positions
    
    def test_calculate_sharpe_ratio(self, test_db, clean_portfolio):
        """Test Sharpe ratio calculation"""
        portfolio = get_or_create_portfolio("test_portfolio")
        
        # Add some performance history
        portfolio.performance_history = [
            {"date": "2025-01-01", "total_value": 100000, "total_return": 0},
            {"date": "2025-01-02", "total_value": 101000, "total_return": 1.0},
            {"date": "2025-01-03", "total_value": 102000, "total_return": 2.0},
            {"date": "2025-01-04", "total_value": 101500, "total_return": 1.5},
        ]
        portfolio.save()
        
        sharpe = calculate_sharpe_ratio(portfolio)
        
        # Sharpe ratio should be a number (could be 0 if no variance)
        assert isinstance(sharpe, float)
    
    def test_get_portfolio_summary(self, test_db, clean_portfolio):
        """Test getting portfolio summary"""
        portfolio = get_or_create_portfolio("test_portfolio")
        
        summary = get_portfolio_summary("test_portfolio")
        
        assert summary["portfolio_id"] == "test_portfolio"
        assert "total_value" in summary
        assert "total_return" in summary
        assert "volatility" in summary
        assert "sharpe_ratio" in summary
        assert "positions" in summary
        assert "allocation" in summary
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_execute_strategy_momentum_buy(self, mock_price, test_db, clean_portfolio, clean_forecasts):
        """Test momentum strategy - buy signal"""
        mock_price.return_value = 150.0
        
        # Create forecast with upward trend
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
        
        result = execute_strategy_from_forecast("test_portfolio", "AAPL", None, "momentum")
        
        assert result["success"] is True
        assert result["forecast_analysis"]["action_taken"] == "buy"
        assert result["forecast_analysis"]["predicted_change_percent"] > 2.0
    
    @patch('backend.services.portfolio_service.get_current_price')
    def test_execute_strategy_momentum_hold(self, mock_price, test_db, clean_portfolio, clean_forecasts):
        """Test momentum strategy - hold signal"""
        mock_price.return_value = 150.0
        
        # Create forecast with small change
        forecast = Forecast(
            ticker="AAPL",
            horizon="5d",
            forecast_data=[
                {"Date": "2025-01-06", "Close": 150.0},
                {"Date": "2025-01-07", "Close": 151.0},  # 0.67% increase (below 2% threshold)
            ],
            model_info={"model_type": "LSTM"}
        )
        forecast.save()
        
        result = execute_strategy_from_forecast("test_portfolio", "AAPL", None, "momentum")
        
        assert result["success"] is True
        assert result["forecast_analysis"]["action_taken"] == "hold"

