import sys
import os
import pytest
from unittest.mock import patch

# Add backend folder to Python path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app 


#u might need to change this 
sample_hist_data = [
    {"Date": "2025-10-01", "Close": 150},
    {"Date": "2025-10-02", "Close": 152},
    {"Date": "2025-10-03", "Close": 151},
]


sample_forecast_df = sample_hist_data  
sample_model_info = {"model": "VAR", "parameters": {"lags": 2}}

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch("services.data_fetcher.fetch")
@patch("services.varModel.trainModel")
def test_var_forecast(mock_trainModel, mock_fetch, client):
    
    mock_fetch.return_value = {"success": True, "hist_df": sample_hist_data}
    
    
    mock_trainModel.return_value = (sample_forecast_df, sample_model_info)
    
    response = client.post("/api/forecast/start", json={"tickerName": "AAPL", "horizon": "5d"})
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["success"] is True
    assert "forecast" in data
    assert isinstance(data["forecast"], list)
    assert data["forecast"][0]["Date"] == "2025-10-01"
    assert data["model_info"]["model"] == "VAR"

