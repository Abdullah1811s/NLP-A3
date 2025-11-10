from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_apscheduler import APScheduler
from mongoengine import connect as mongo_connect, get_connection
from backend.routes.forecast import forecast_bp
load_dotenv()

app = Flask(__name__)


CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
mongo_uri = os.getenv("MONGO_URI")
try:
    mongo_connect(host=mongo_uri)
    conn = get_connection()
    conn.server_info()  
    print("MongoDB connected successfully.")
except Exception as e:
    print("MongoDB connection failed:", e)


app.register_blueprint(forecast_bp)

@app.route("/")
def index():
    return jsonify({"message": "Forecasting API is working!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
