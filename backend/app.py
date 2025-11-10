from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_apscheduler import APScheduler
from mongoengine import connect as mongo_connect, get_connection
from backend.routes.forecast import forecast_bp
from backend.routes.portfolio import portfolio_bp
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow all localhost ports for development
# This applies CORS to all routes including blueprints
CORS(app, 
     origins=["http://localhost:5173", "http://localhost:5175", "http://127.0.0.1:5173", "http://127.0.0.1:5175"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=True,
     expose_headers=["Content-Type"])

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
app.register_blueprint(portfolio_bp)

@app.route("/")
def index():
    return jsonify({"message": "Forecasting API is working!"})

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)
