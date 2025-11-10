import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from backend.models.lstmDb import lstmInfo
import warnings
import os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
np.random.seed(42)
tf.random.set_seed(42)



warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

def parse_horizon(horizon_str):
    if horizon_str.endswith('d'):
        return int(horizon_str[:-1])
    elif horizon_str.endswith('mo'):
        return int(horizon_str[:-2]) * 30
    elif horizon_str.endswith('yr'):
        return int(horizon_str[:-2]) * 365
    else:
        return int(horizon_str)

def create_sequences(data, lookback=60):
    X, y = [], []

    for i in range(lookback, len(data)):
        X.append(data[i-lookback:i])
        y.append(data[i])
    return np.array(X), np.array(y)

def build_lstm_model(input_shape, n_features):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(n_features)
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def trainModel(historical_data, horizon, ticker='AAPL', weights_path=None):
    """
    weights_path: optional string path to save/load model weights, e.g., 'AAPL_lstm_weights.h5'
    """
    df = pd.DataFrame(historical_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df = df.fillna(method='ffill').fillna(method='bfill')

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df.values)

    train_size = int(len(scaled_data) * 0.8)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]

    lookback = min(60, len(train_data) // 2)
    X_train, y_train = create_sequences(train_data, lookback)
    X_test, y_test = create_sequences(test_data, lookback) if len(test_data) > lookback else (None, None)

    n_features = df.shape[1]
    model = build_lstm_model((lookback, n_features), n_features)

    # --- Load existing weights if available ---
    if weights_path is not None and os.path.exists(weights_path):
        model.load_weights(weights_path)
        print(f"Loaded existing weights from {weights_path}")

    early_stop = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)

    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        callbacks=[early_stop],
        verbose=0
    )

    # --- Save weights after training ---
    if weights_path is not None:
    # Ensure directory exists
        weights_dir = os.path.dirname(weights_path)
        if weights_dir and not os.path.exists(weights_dir):
            os.makedirs(weights_dir, exist_ok=True)
            print(f"Created directory for weights: {weights_dir}")

    model.save_weights(weights_path)
    print(f"Saved model weights to {weights_path}")

    # Forecasting
    steps = parse_horizon(horizon)
    forecast = []
    current_sequence = scaled_data[-lookback:].copy()
    for _ in range(steps):
        current_batch = current_sequence.reshape(1, lookback, n_features)
        next_pred = model.predict(current_batch, verbose=0)[0]
        forecast.append(next_pred)
        current_sequence = np.vstack([current_sequence[1:], next_pred])

    forecast = np.array(forecast)
    forecast_original = scaler.inverse_transform(forecast)

    forecast_df = pd.DataFrame(forecast_original, columns=df.columns)
    last_date = df.index[-1]
    forecast_df.index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='B')

    # Metrics
    if X_test is not None and len(X_test) > 0:
        test_predictions = model.predict(X_test, verbose=0)
        test_pred_original = scaler.inverse_transform(test_predictions)
        test_actual_original = scaler.inverse_transform(y_test)
        rmse = np.sqrt(mean_squared_error(test_actual_original, test_pred_original))
        mae = mean_absolute_error(test_actual_original, test_pred_original)
        mape = np.mean(np.abs((test_actual_original - test_pred_original) / test_actual_original)) * 100
    else:
        train_predictions = model.predict(X_train, verbose=0)
        train_pred_original = scaler.inverse_transform(train_predictions)
        train_actual_original = scaler.inverse_transform(y_train)
        rmse = np.sqrt(mean_squared_error(train_actual_original, train_pred_original))
        mae = mean_absolute_error(train_actual_original, train_pred_original)
        mape = np.mean(np.abs((train_actual_original - train_pred_original) / train_actual_original)) * 100

    model_info = {
        "model_type": "LSTM",
        "lookback_period": lookback,
        "layers": str(model.summary()),
        "total_params": model.count_params(),
        "epochs_trained": len(history.history['loss']),
        "final_loss": float(history.history['loss'][-1]),
        "rmse": float(rmse),
        "mae": float(mae),
        "mape": float(mape),
        "train_size": train_size,
        "test_size": len(scaled_data) - train_size
    }

    forecast_list = forecast_df.reset_index().to_dict(orient="records")
    recordLSTM = lstmInfo(
        ticker=ticker,
        horizon=horizon,
        forecast_data=forecast_list,
        model_info={**model_info, "weights_file": weights_path} if weights_path else model_info,
        weights_file=weights_path
    )
    recordLSTM.save()
    print(f"Saved forecast to MongoDB with ID: {recordLSTM.id}")
    print("\n==============================")
    print(f"Forecast training complete for {ticker}")
    print("==============================")
    print("Model Summary:")
    model.summary()
    print("\nModel Info:")
    for key, value in model_info.items():
        print(f"   {key}: {value}")

    print("\n🧠 Forecast Sample (first 5 days):")
    print(forecast_df.head())

    print(f"\n💾 Saved forecast to MongoDB with ID: {recordLSTM.id}")
    print("==============================\n")   
    return forecast_df, model_info , recordLSTM
