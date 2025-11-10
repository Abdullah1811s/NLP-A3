"""
Utility functions for test data management
This module helps extract and use the 20% test data from model training
"""
import sys
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def split_train_test_data(historical_data, train_ratio=0.8):
    """
    Split historical data into training and test sets
    
    Args:
        historical_data: List of dicts with Date, Open, High, Low, Close, Volume
        train_ratio: Ratio of data for training (default 0.8 = 80%)
    
    Returns:
        train_data: Training data (80%)
        test_data: Test data (20%)
        scaler: Fitted scaler for inverse transformation
    """
    # Convert to DataFrame
    df = pd.DataFrame(historical_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Scale data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df.values)
    
    # Split
    train_size = int(len(scaled_data) * train_ratio)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]
    
    return train_data, test_data, scaler, df


def prepare_test_data_for_evaluation(test_data, scaler, original_df, lookback=60):
    """
    Prepare test data for model evaluation
    
    Args:
        test_data: Scaled test data array
        scaler: Fitted scaler
        original_df: Original DataFrame with dates
        lookback: Lookback period for sequences
    
    Returns:
        X_test: Test sequences
        y_test: Test targets
        test_dates: Dates corresponding to test data
        test_actual: Actual (unscaled) test values
    """
    from backend.services.lstmModel import create_sequences
    
    if len(test_data) <= lookback:
        return None, None, None, None
    
    # Create sequences
    X_test, y_test = create_sequences(test_data, lookback)
    
    # Get corresponding dates
    train_size = len(original_df) - len(test_data)
    test_start_idx = train_size + lookback
    test_dates = original_df.index[test_start_idx:test_start_idx + len(y_test)]
    
    # Inverse transform to get actual values
    test_actual = scaler.inverse_transform(y_test)
    
    return X_test, y_test, test_dates, test_actual


def evaluate_model_predictions(model, X_test, y_test, scaler):
    """
    Evaluate model predictions on test data
    
    Args:
        model: Trained LSTM model
        X_test: Test sequences
        y_test: Test targets (scaled)
        scaler: Fitted scaler
    
    Returns:
        predictions: Unscaled predictions
        actual: Unscaled actual values
        metrics: Dictionary with MAE, RMSE, MAPE
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    
    # Make predictions
    y_pred_scaled = model.predict(X_test, verbose=0)
    
    # Inverse transform
    predictions = scaler.inverse_transform(y_pred_scaled)
    actual = scaler.inverse_transform(y_test)
    
    # Calculate metrics
    mae = mean_absolute_error(actual, predictions)
    rmse = np.sqrt(mean_squared_error(actual, predictions))
    mape = np.mean(np.abs((actual - predictions) / actual)) * 100
    
    metrics = {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape),
        "test_samples": len(actual)
    }
    
    return predictions, actual, metrics


def create_test_forecast_data(ticker, test_dates, predictions, actual=None):
    """
    Create forecast data structure for testing
    
    Args:
        ticker: Stock ticker
        test_dates: Dates for forecast
        predictions: Predicted values
        actual: Actual values (optional, for evaluation)
    
    Returns:
        forecast_data: List of dicts in forecast format
    """
    forecast_data = []
    
    for i, date in enumerate(test_dates):
        pred = predictions[i] if len(predictions.shape) > 1 else predictions
        act = actual[i] if actual is not None and len(actual.shape) > 1 else actual
        
        entry = {
            "Date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date),
            "Open": float(pred[0]) if len(pred) > 0 else 0,
            "High": float(pred[1]) if len(pred) > 1 else 0,
            "Low": float(pred[2]) if len(pred) > 2 else 0,
            "Close": float(pred[3]) if len(pred) > 3 else 0,
            "Volume": float(pred[4]) if len(pred) > 4 else 0,
        }
        
        if actual is not None:
            entry["actual_Close"] = float(act[3]) if len(act) > 3 else None
            entry["error"] = entry["actual_Close"] - entry["Close"] if entry["actual_Close"] else None
        
        forecast_data.append(entry)
    
    return forecast_data

