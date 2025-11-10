import sys
import os
import pytest
from unittest.mock import patch

# Add backend folder to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app 


# Sample historical data for testing
sample_hist_data = [
    {"Date": "2025-10-01", "Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
    {"Date": "2025-10-02", "Open": 151.0, "High": 153.0, "Low": 150.0, "Close": 152.0, "Volume": 1100000},
    {"Date": "2025-10-03", "Open": 152.0, "High": 154.0, "Low": 151.0, "Close": 153.0, "Volume": 1200000},
]

sample_forecast_df = sample_hist_data  
sample_model_info = {"model": "LSTM", "rmse": 1.5, "mae": 1.2, "mape": 0.8}

@pytest.mark.integration
@patch("backend.services.data_fetcher.fetch")
@patch("backend.services.lstmModel.trainModel")
def test_lstm_forecast(mock_trainModel, mock_fetch, client, clean_forecasts):
    """Test LSTM forecast endpoint"""
    mock_fetch.return_value = {"success": True, "hist_df": sample_hist_data * 100}
    
    import pandas as pd
    from backend.models.lstmDb import lstmInfo
    forecast_df = pd.DataFrame(sample_forecast_df)
    mock_record = lstmInfo(ticker="AAPL", horizon="5d", forecast_data=sample_forecast_df, model_info=sample_model_info)
    
    mock_trainModel.return_value = (forecast_df, sample_model_info, mock_record)
    
    response = client.post("/api/forecast/start", json={
        "tickerName": "AAPL", 
        "horizon": "5d",
        "model_name": "LSTM"
    })
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["success"] is True
    assert "forecast" in data
    assert isinstance(data["forecast"], list)
    assert "model_info" in data

