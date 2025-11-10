# Testing Guide

This directory contains automated tests for the FinTech forecasting application.

## Test Structure

- **`test_model_evaluation.py`**: Tests for model training and evaluation using 20% test data
- **`test_portfolio_unit.py`**: Unit tests for portfolio service functions
- **`test_portfolio_integration.py`**: Integration tests for API endpoints
- **`test_forecast.py`**: Tests for forecast API endpoints
- **`test_data_utils.py`**: Utility functions for test data management
- **`conftest.py`**: Pytest configuration and shared fixtures

## Test Data Split

The model training uses an **80/20 split**:
- **80%** of data is used for training
- **20%** of data is used for testing/evaluation

This is implemented in `backend/services/lstmModel.py`:
```python
train_size = int(len(scaled_data) * 0.8)  # 80% for training
train_data = scaled_data[:train_size]
test_data = scaled_data[train_size:]  # 20% for testing
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Run All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py
```

### Run Specific Test Types

```bash
# Unit tests only
python run_tests.py --unit
# or
pytest -m unit

# Integration tests only
python run_tests.py --integration
# or
pytest -m integration

# Model evaluation tests only
python run_tests.py --model
# or
pytest -m model
```

### Run with Coverage

```bash
python run_tests.py --coverage
# or
pytest --cov=backend --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_portfolio_unit.py
pytest tests/test_model_evaluation.py
```

### Run Specific Test Function

```bash
pytest tests/test_portfolio_unit.py::TestPortfolioService::test_buy_asset_success
```

## Test Markers

Tests are marked with categories:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.model` - Model evaluation tests
- `@pytest.mark.slow` - Slow running tests

## Test Database

Tests use **mongomock** (in-memory MongoDB) to avoid affecting your actual database. No real database connection is needed for tests.

## Writing New Tests

### Unit Test Example

```python
@pytest.mark.unit
def test_my_function():
    result = my_function(input_data)
    assert result == expected_output
```

### Integration Test Example

```python
@pytest.mark.integration
def test_api_endpoint(client):
    response = client.post("/api/endpoint", json={"data": "value"})
    assert response.status_code == 200
```

### Using Test Data Utilities

```python
from tests.test_data_utils import split_train_test_data, prepare_test_data_for_evaluation

# Split data into 80/20
train_data, test_data, scaler, df = split_train_test_data(historical_data)

# Prepare test data for evaluation
X_test, y_test, test_dates, test_actual = prepare_test_data_for_evaluation(
    test_data, scaler, df, lookback=60
)
```

## Test Fixtures

Common fixtures available in `conftest.py`:
- `test_db`: Test database connection
- `client`: Flask test client
- `sample_hist_data`: Sample historical data
- `sample_forecast_data`: Sample forecast data
- `clean_portfolio`: Clean portfolio for testing
- `clean_forecasts`: Clean forecasts for testing

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest --cov=backend --cov-report=xml
```

## Troubleshooting

### Import Errors
Make sure you're running tests from the `backend` directory:
```bash
cd backend
pytest
```

### Database Connection Errors
Tests use `mongomock`, so no real MongoDB is needed. If you see connection errors, check that `mongomock` is installed:
```bash
pip install mongomock
```

### Module Not Found
Ensure the backend directory is in the Python path. The test files include:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## Test Coverage Goals

- **Unit Tests**: >80% coverage for service functions
- **Integration Tests**: All API endpoints covered
- **Model Tests**: Training and evaluation workflows tested

