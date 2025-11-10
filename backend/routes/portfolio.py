from flask import Blueprint, request, jsonify
from backend.services.portfolio_service import (
    buy_asset,
    sell_asset,
    get_portfolio_positions,
    get_portfolio_summary,
    get_performance_history,
    execute_strategy_from_forecast
)

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/api/portfolio/summary", methods=["GET"])
def get_summary():
    """Get portfolio summary with all metrics"""
    try:
        portfolio_id = request.args.get("portfolio_id", "default")
        summary = get_portfolio_summary(portfolio_id)
        return jsonify({
            "success": True,
            "data": summary
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching portfolio summary: {str(e)}"
        }), 500


@portfolio_bp.route("/api/portfolio/positions", methods=["GET"])
def get_positions():
    """Get all positions in the portfolio"""
    try:
        portfolio_id = request.args.get("portfolio_id", "default")
        positions = get_portfolio_positions(portfolio_id)
        return jsonify({
            "success": True,
            "data": positions
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching positions: {str(e)}"
        }), 500


@portfolio_bp.route("/api/portfolio/buy", methods=["POST"])
def buy():
    """Execute a buy order"""
    try:
        data = request.get_json() or {}
        portfolio_id = data.get("portfolio_id", "default")
        ticker = data.get("ticker")
        quantity = data.get("quantity")
        price = data.get("price")  # Optional, will fetch current price if not provided
        reason = data.get("reason", "user_manual")
        
        if not ticker:
            return jsonify({
                "success": False,
                "message": "Ticker is required"
            }), 400
        
        if not quantity or quantity <= 0:
            return jsonify({
                "success": False,
                "message": "Quantity must be greater than 0"
            }), 400
        
        result = buy_asset(portfolio_id, ticker, float(quantity), price, reason)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error executing buy order: {str(e)}"
        }), 500


@portfolio_bp.route("/api/portfolio/sell", methods=["POST"])
def sell():
    """Execute a sell order"""
    try:
        data = request.get_json() or {}
        portfolio_id = data.get("portfolio_id", "default")
        ticker = data.get("ticker")
        quantity = data.get("quantity")
        price = data.get("price")  # Optional, will fetch current price if not provided
        reason = data.get("reason", "user_manual")
        
        if not ticker:
            return jsonify({
                "success": False,
                "message": "Ticker is required"
            }), 400
        
        if not quantity or quantity <= 0:
            return jsonify({
                "success": False,
                "message": "Quantity must be greater than 0"
            }), 400
        
        result = sell_asset(portfolio_id, ticker, float(quantity), price, reason)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error executing sell order: {str(e)}"
        }), 500


@portfolio_bp.route("/api/portfolio/performance", methods=["GET"])
def get_performance():
    """Get performance history for visualization"""
    try:
        portfolio_id = request.args.get("portfolio_id", "default")
        days = int(request.args.get("days", 30))
        
        history = get_performance_history(portfolio_id, days)
        return jsonify({
            "success": True,
            "data": history
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching performance history: {str(e)}"
        }), 500


@portfolio_bp.route("/api/portfolio/execute-strategy", methods=["POST"])
def execute_strategy():
    """Execute trading strategy based on forecast predictions"""
    try:
        data = request.get_json() or {}
        portfolio_id = data.get("portfolio_id", "default")
        ticker = data.get("ticker")
        strategy = data.get("strategy", "momentum")  # momentum, conservative, aggressive
        forecast_id = data.get("forecast_id")
        
        if not ticker:
            return jsonify({
                "success": False,
                "message": "Ticker is required"
            }), 400
        
        if strategy not in ["momentum", "conservative", "aggressive"]:
            return jsonify({
                "success": False,
                "message": "Strategy must be one of: momentum, conservative, aggressive"
            }), 400
        
        result = execute_strategy_from_forecast(portfolio_id, ticker, forecast_id, strategy)
        
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error executing strategy: {str(e)}"
        }), 500


@portfolio_bp.route("/api/portfolio/hold", methods=["POST"])
def hold():
    """Hold position (no action, but can be used for logging)"""
    try:
        data = request.get_json() or {}
        ticker = data.get("ticker")
        reason = data.get("reason", "user_manual")
        
        return jsonify({
            "success": True,
            "message": f"Holding position for {ticker}",
            "action": "hold",
            "reason": reason
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

