from mongoengine import Document, StringField, DictField, DateTimeField, ListField,ReferenceField
import datetime
from .lstmDb import lstmInfo

class Forecast(Document):
    ticker = StringField(required=True)
    horizon = StringField(required=True)
    forecast_data = ListField(DictField(), required=True)  # Stores forecast JSON records
    model_info = DictField(required=True)  # Stores any model metadata
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    lstm_model = ReferenceField(lstmInfo, required=False) 
    meta = {
        "collection": "forecasts"
    }
