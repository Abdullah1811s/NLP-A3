"""
Pytest configuration and shared fixtures
"""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from mongoengine import connect, disconnect

# Add backend folder to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from backend.models.portfolio import Portfolio, Position, Transaction
from backend.models.forecast import Forecast

# Test database configuration
TEST_DB_NAME = "test_fintech_db"


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Set up test database connection"""
    # Connect to test database using mongomock
    try:
        connect(TEST_DB_NAME, host='mongomock://localhost', alias='default')
    except:
        # If already connected, just use existing connection
        pass
    yield
    # Clean up after test
    try:
        disconnect(alias='default')
    except:
        pass


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_hist_data():
    """Sample historical data for testing"""
    return [
        {"Date": "2025-01-01", "Open": 150.0, "High": 152.0, "Low": 149.0, "Close": 151.0, "Volume": 1000000},
        {"Date": "2025-01-02", "Open": 151.0, "High": 153.0, "Low": 150.0, "Close": 152.0, "Volume": 1100000},
        {"Date": "2025-01-03", "Open": 152.0, "High": 154.0, "Low": 151.0, "Close": 153.0, "Volume": 1200000},
        {"Date": "2025-01-04", "Open": 153.0, "High": 155.0, "Low": 152.0, "Close": 154.0, "Volume": 1300000},
        {"Date": "2025-01-05", "Open": 154.0, "High": 156.0, "Low": 153.0, "Close": 155.0, "Volume": 1400000},
    ]


@pytest.fixture
def sample_forecast_data():
    """Sample forecast data for testing"""
    return [
        {"Date": "2025-01-06", "Open": 155.0, "High": 157.0, "Low": 154.0, "Close": 156.0, "Volume": 1500000},
        {"Date": "2025-01-07", "Open": 156.0, "High": 158.0, "Low": 155.0, "Close": 157.0, "Volume": 1600000},
    ]


@pytest.fixture
def clean_portfolio(test_db):
    """Clean portfolio for testing"""
    Portfolio.objects().delete()
    Position.objects().delete()
    Transaction.objects().delete()
    yield
    Portfolio.objects().delete()
    Position.objects().delete()
    Transaction.objects().delete()


@pytest.fixture
def clean_forecasts(test_db):
    """Clean forecasts for testing"""
    Forecast.objects().delete()
    yield
    Forecast.objects().delete()

