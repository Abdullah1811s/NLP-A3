from statsmodels.tsa.api import VAR
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

def parse_horizon(horizon_str):
    if horizon_str.endswith('d'):
        return int(horizon_str[:-1])
    elif horizon_str.endswith('mo'):
        return int(horizon_str[:-2]) * 30
    elif horizon_str.endswith('yr'):
        return int(horizon_str[:-2]) * 365
    else:
        return int(horizon_str) 

def trainModel(historical_data, horizon, ticker='AAPL'):
    
    df = pd.DataFrame(historical_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]  

    
    train_size = int(len(df) * 0.8)
    train, test = df[:train_size], df[train_size:]

    
    model = VAR(train)
    n_obs = len(train)
    n_vars = train.shape[1]
    maxlags = min(5, n_obs // (n_vars + 1)) 
    lag_order = model.select_order(maxlags=maxlags)
    best_lag = lag_order.aic  
    model_fitted = model.fit(best_lag)

    
    last_obs = train.values[-best_lag:]
    steps = parse_horizon(horizon)
    forecast = model_fitted.forecast(y=last_obs, steps=steps)
    
    
    forecast_df = pd.DataFrame(forecast, columns=train.columns)
    last_date = df.index[-1]
    forecast_df.index = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                      periods=steps, freq='B')

    
    test_subset = test[:steps].values if len(test) >= steps else test.values
    rmse = np.sqrt(mean_squared_error(test_subset, forecast[:len(test_subset)]))
    mae = mean_absolute_error(test_subset, forecast[:len(test_subset)])

    model_info = {
        "best_lag": model_fitted.k_ar,
        "aic": model_fitted.aic,
        "bic": model_fitted.bic,
        "rmse": rmse,
        "mae": mae
    }

    return forecast_df, model_info
