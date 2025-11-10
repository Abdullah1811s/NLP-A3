"""
Model evaluation tests using the 20% test data split
"""
import sys
import os
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.lstmModel import trainModel, create_sequences, parse_horizon
from backend.services.forecast_evaluator import get_forecast_with_errors, evaluate_forecast_against_actual
from backend.models.forecast import Forecast
from backend.models.lstmDb import lstmInfo


@pytest.mark.model
class TestModelEvaluation:
    """Test model evaluation with 20% test data"""
    
    @pytest.mark.unit
    def test_train_test_split(self):
        """Test that 80/20 split is correctly implemented"""
        # Create sample data
        data_length = 100
        sample_data = [
            {"Date": f"2025-01-{i+1:02d}", "Open": 150.0 + i, "High": 152.0 + i, 
             "Low": 149.0 + i, "Close": 151.0 + i, "Volume": 1000000 + i*10000}
            for i in range(data_length)
        ]
        
        # Convert to DataFrame
        df = pd.DataFrame(sample_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Simulate the scaling and split logic from lstmModel
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df.values)
        
        train_size = int(len(scaled_data) * 0.8)
        train_data = scaled_data[:train_size]
        test_data = scaled_data[train_size:]
        
        # Verify split
        assert len(train_data) == 80, "Training data should be 80%"
        assert len(test_data) == 20, "Test data should be 20%"
        assert len(train_data) + len(test_data) == len(scaled_data), "Split should preserve all data"
    
    @pytest.mark.model
    @patch('backend.services.lstmModel.get_current_price')
    def test_model_training_with_test_data(self, mock_price):
        """Test that model training correctly uses test data for evaluation"""
        mock_price.return_value = 155.0
        
        # Create sample historical data (100 days)
        sample_data = []
        base_date = pd.Timestamp("2024-01-01")
        for i in range(100):
            date = base_date + pd.Timedelta(days=i)
            sample_data.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Open": 150.0 + np.random.randn() * 2,
                "High": 152.0 + np.random.randn() * 2,
                "Low": 148.0 + np.random.randn() * 2,
                "Close": 151.0 + np.random.randn() * 2,
                "Volume": 1000000 + int(np.random.randn() * 100000)
            })
        
        # Train model
        forecast_df, model_info, recordLSTM = trainModel(
            historical_data=sample_data,
            horizon="5d",
            ticker="TEST",
            weights_path=None  # Don't save weights in tests
        )
        
        # Verify model info contains test metrics
        assert "rmse" in model_info, "Model info should contain RMSE"
        assert "mae" in model_info, "Model info should contain MAE"
        assert "mape" in model_info, "Model info should contain MAPE"
        assert "test_size" in model_info, "Model info should contain test_size"
        assert model_info["test_size"] > 0, "Test size should be greater than 0"
        
        # Verify forecast was generated
        assert forecast_df is not None, "Forecast should be generated"
        assert len(forecast_df) > 0, "Forecast should have data"
    
    @pytest.mark.unit
    def test_create_sequences(self):
        """Test sequence creation for LSTM"""
        # Create sample data
        data = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8]])
        lookback = 3
        
        X, y = create_sequences(data, lookback)
        
        # Verify shapes
        assert len(X) == len(data) - lookback, "X should have correct length"
        assert len(y) == len(data) - lookback, "y should have correct length"
        assert X.shape[1] == lookback, "X should have correct lookback dimension"
        assert X.shape[2] == data.shape[1], "X should have correct feature dimension"
        assert y.shape[1] == data.shape[1], "y should have correct feature dimension"
    
    @pytest.mark.unit
    def test_parse_horizon(self):
        """Test horizon parsing"""
        from backend.services.lstmModel import parse_horizon
        
        assert parse_horizon("5d") == 5
        assert parse_horizon("1mo") == 30
        assert parse_horizon("2mo") == 60
        assert parse_horizon("1yr") == 365
        assert parse_horizon("10") == 10


@pytest.mark.model
class TestForecastEvaluation:
    """Test forecast evaluation against actual prices"""
    
    @pytest.fixture
    def sample_forecast(self, test_db):
        """Create a sample forecast for testing"""
        forecast_data = [
            {"Date": "2025-01-06", "Open": 155.0, "High": 157.0, "Low": 154.0, "Close": 156.0, "Volume": 1500000},
            {"Date": "2025-01-07", "Open": 156.0, "High": 158.0, "Low": 155.0, "Close": 157.0, "Volume": 1600000},
        ]
        
        forecast = Forecast(
            ticker="TEST",
            horizon="2d",
            forecast_data=forecast_data,
            model_info={"model_type": "LSTM", "rmse": 1.5, "mae": 1.2, "mape": 0.8}
        )
        forecast.save()
        return forecast
    
    @pytest.mark.integration
    @patch('backend.services.forecast_evaluator.fetch')
    def test_get_forecast_with_errors(self, mock_fetch, sample_forecast):
        """Test getting forecast with error overlays"""
        # Mock actual price data
        mock_fetch.return_value = {
            "success": True,
            "hist_df": [
                {"Date": "2025-01-06", "Open": 155.5, "High": 157.2, "Low": 154.1, "Close": 156.5, "Volume": 1500000},
                {"Date": "2025-01-07", "Open": 156.3, "High": 158.1, "Low": 155.2, "Close": 157.2, "Volume": 1600000},
            ]
        }
        
        result = get_forecast_with_errors("TEST", str(sample_forecast.id))
        
        assert result["success"] is True
        assert "candlestick_data" in result
        assert len(result["candlestick_data"]) == 2
        assert "error_metrics" in result
        assert result["error_metrics"]["mae"] is not None
        assert result["error_metrics"]["rmse"] is not None
    
    @pytest.mark.integration
    @patch('backend.services.forecast_evaluator.fetch')
    def test_evaluate_forecast_against_actual(self, mock_fetch, sample_forecast):
        """Test evaluating forecast against actual prices"""
        mock_fetch.return_value = {
            "success": True,
            "hist_df": [
                {"Date": "2025-01-06", "Open": 155.5, "High": 157.2, "Low": 154.1, "Close": 156.5, "Volume": 1500000},
                {"Date": "2025-01-07", "Open": 156.3, "High": 158.1, "Low": 155.2, "Close": 157.2, "Volume": 1600000},
            ]
        }
        
        result = evaluate_forecast_against_actual("TEST", str(sample_forecast.id))
        
        assert result["success"] is True
        assert "error_metrics" in result
        
        # Verify forecast was updated with evaluation
        updated_forecast = Forecast.objects(id=sample_forecast.id).first()
        assert "evaluation" in updated_forecast.model_info
        assert updated_forecast.model_info["evaluation"]["evaluation_status"] == "completed"

