from mongoengine import Document, StringField, DictField, DateTimeField, ListField, FloatField
import datetime

class lstmInfo(Document):
    ticker = StringField(required=True)  # e.g., "AAPL"
    horizon = StringField(required=True)  # e.g., "5d", "1mo"
    
    # The forecasted values: list of dicts like [{"Date": "2025-11-11", "Open": 123, ...}, ...]
    forecast_data = ListField(DictField(), required=True)
    
    # Model info: training metrics and configuration
    model_info = DictField(required=True)  
    # Example content:
    # {
    #     "model_type": "LSTM",
    #     "lookback_period": 60,
    #     "layers": "...",
    #     "total_params": 12345,
    #     "epochs_trained": 50,
    #     "final_loss": 0.0012,
    #     "rmse": 2.34,
    #     "mae": 1.12,
    #     "mape": 0.98,
    #     "train_size": 1000,
    #     "test_size": 200,
    #     "weights_file": "AAPL_lstm_weights.h5"
    # }

    # Optional: path or name of saved weights
    weights_file = StringField(required=False)

    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        "collection": "lstmInfo",
        "ordering": ["-created_at"]  # newest first
    }
