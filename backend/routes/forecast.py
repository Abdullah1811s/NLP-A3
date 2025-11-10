from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from backend.services.data_fetcher import fetch
# from backend.services.varModel import trainModel as trainVARModel  # VAR model not yet implemented
from backend.services.lstmModel import trainModel as trainLSTMModel
from backend.services.forecast_evaluator import get_forecast_with_errors, evaluate_forecast_against_actual
from backend.models.forecast import Forecast

forecast_bp = Blueprint("forecast", __name__)

def retrain_lstm_job(tickerName, horizon, weights_path):
    
    print(f"\nScheduled retraining triggered for {tickerName}")
    result = fetch(ticker=tickerName)

    if not result or not result.get("success"):
        print(f"Failed to fetch data for {tickerName} during scheduled retraining")
        return

    historical_data = result.get("hist_df", [])
    forecast_df, model_info, recordLSTM = trainLSTMModel(
        historical_data=historical_data,
        horizon=horizon,
        ticker=tickerName,
        weights_path=weights_path
    )

    forecast_json = (
        forecast_df.reset_index()
        .rename(columns={"index": "Date"})
        .to_dict(orient="records")
    )

    forecast_entry = Forecast(
        ticker=tickerName,
        horizon=horizon,
        forecast_data=forecast_json,
        model_info=model_info,      
        lstm_model=recordLSTM
    )
    forecast_entry.save()
    print(f"[OK] Retrained LSTM and saved new forecast for {tickerName}")


@forecast_bp.route("/api/forecast/start", methods=["POST"])
def start_fetching():
    try:
        data = request.get_json() or {}
        tickerName = data.get("tickerName", "AAPL")
        horizon = data.get("horizon", "24d")
        model_name = data.get("model_name", "VAR").upper()
        scheduledTime = data.get("scheduledTime") 

        print(f"Selected model: {model_name}")
        print(f"Fetching data for ticker: {tickerName}, horizon: {horizon}")

        result = fetch(ticker=tickerName)
        if not result or not result.get("success"):
            return jsonify({
                "success": False,
                "message": "Failed to fetch data for the given ticker and horizon."
            }), 400

        historical_data = result.get("hist_df", [])
        weights_path = f"backend/weights/{tickerName}_lstm.weights.h5"

        if model_name == "LSTM":
            print("Training LSTM model...")
            forecast_df, model_info, recordLSTM = trainLSTMModel(
                historical_data=historical_data,
                horizon=horizon,
                ticker=tickerName,
                weights_path=weights_path
            )

        forecast_json = (
            forecast_df.reset_index()
            .rename(columns={"index": "Date"})
            .to_dict(orient="records")
        )

        forecast_entry = Forecast(
            ticker=tickerName,
            horizon=horizon,
            forecast_data=forecast_json,
            model_info=model_info,  
            lstm_model=recordLSTM
        )
        forecast_entry.save()

        if scheduledTime:
            scheduler = current_app.apscheduler
            job_id = f"retrain_{tickerName}_{model_name}"
            
            run_date = datetime.fromisoformat(scheduledTime.replace("Z", "+00:00"))
            print(f"[SCHEDULE] About to schedule retraining job for {tickerName} at {run_date}") 

            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)

            scheduler.add_job(
                id=job_id,
                func=retrain_lstm_job,
                trigger='date',
                run_date=run_date,
                args=[tickerName, horizon, weights_path]
            )
            print(f"[SCHEDULED] Retraining scheduled for {tickerName} at {run_date}")

        return jsonify({
            "success": True,
            "message": f"{model_name} forecast generated and saved successfully.",
            "scheduled_retrain": scheduledTime or None,
            "model_used": model_name,
            "forecast": forecast_json,
            "model_info": model_info
        }), 200

    except Exception as e:
        print("Error in /api/forecast/start:", e)
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@forecast_bp.route("/api/forecast/evaluate", methods=["GET"])
def evaluate_forecast():
    """Get forecast data with error overlays for candlestick visualization"""
    try:
        ticker = request.args.get("ticker")
        forecast_id = request.args.get("forecast_id")
        
        if not ticker and not forecast_id:
            return jsonify({
                "success": False,
                "message": "Either ticker or forecast_id is required"
            }), 400
        
        result = get_forecast_with_errors(ticker, forecast_id)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error evaluating forecast: {str(e)}"
        }), 500


@forecast_bp.route("/api/forecast/update-evaluation", methods=["POST"])
def update_evaluation():
    """Update forecast evaluation with latest actual prices"""
    try:
        data = request.get_json() or {}
        ticker = data.get("ticker")
        forecast_id = data.get("forecast_id")
        
        if not ticker and not forecast_id:
            return jsonify({
                "success": False,
                "message": "Either ticker or forecast_id is required"
            }), 400
        
        result = evaluate_forecast_against_actual(ticker, forecast_id)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error updating evaluation: {str(e)}"
        }), 500
