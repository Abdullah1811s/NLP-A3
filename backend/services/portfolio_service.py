import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from backend.models.portfolio import Portfolio, Position, Transaction
from backend.services.data_fetcher import fetch
from backend.models.forecast import Forecast


def get_or_create_portfolio(portfolio_id: str = "default", initial_cash: float = 100000.0) -> Portfolio:
    """Get existing portfolio or create a new one"""
    portfolio = Portfolio.objects(portfolio_id=portfolio_id).first()
    if not portfolio:
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            initial_cash=initial_cash,
            current_cash=initial_cash,
            total_value=initial_cash,
            positions=[],
            transactions=[]
        )
        portfolio.save()
    return portfolio


def get_current_price(ticker: str) -> Optional[float]:
    """Get current market price for a ticker"""
    try:
        result = fetch(ticker=ticker, period="1d")
        if result and result.get("success") and result.get("hist_df"):
            hist_data = result.get("hist_df")
            if hist_data and len(hist_data) > 0:
                # Get the most recent close price
                latest = hist_data[-1]
                return float(latest.get("Close", 0))
    except Exception as e:
        print(f"Error fetching current price for {ticker}: {e}")
    return None


def update_position_prices(portfolio: Portfolio) -> Portfolio:
    """Update current prices for all positions in portfolio"""
    for position_ref in portfolio.positions:
        position = Position.objects(id=position_ref.id).first()
        if position:
            current_price = get_current_price(position.ticker)
            if current_price:
                position.current_price = current_price
                position.last_updated = datetime.utcnow()
                position.save()
    return Portfolio.objects(id=portfolio.id).first()


def calculate_portfolio_value(portfolio: Portfolio) -> float:
    """Calculate total portfolio value (cash + positions)"""
    total_positions_value = 0.0
    portfolio = update_position_prices(portfolio)
    
    for position_ref in portfolio.positions:
        position = Position.objects(id=position_ref.id).first()
        if position and position.quantity > 0:
            if position.current_price:
                total_positions_value += position.current_price * position.quantity
            else:
                # Fallback to average price if current price unavailable
                total_positions_value += position.average_price * position.quantity
    
    return portfolio.current_cash + total_positions_value


def buy_asset(
    portfolio_id: str,
    ticker: str,
    quantity: float,
    price: Optional[float] = None,
    reason: str = "user_manual"
) -> Dict:
    """Execute a buy order"""
    try:
        portfolio = get_or_create_portfolio(portfolio_id)
        
        # Get current price if not provided
        if price is None:
            price = get_current_price(ticker)
            if price is None:
                return {"success": False, "message": f"Could not fetch current price for {ticker}"}
        
        total_cost = quantity * price
        
        # Check if we have enough cash
        if total_cost > portfolio.current_cash:
            return {
                "success": False,
                "message": f"Insufficient cash. Required: ${total_cost:.2f}, Available: ${portfolio.current_cash:.2f}"
            }
        
        # Find or create position
        position = Position.objects(ticker=ticker).first()
        if position:
            # Update existing position (weighted average)
            old_cost = position.total_cost
            new_cost = total_cost
            total_quantity = position.quantity + quantity
            new_avg_price = ((old_cost + new_cost) / total_quantity) if total_quantity > 0 else price
            
            position.quantity = total_quantity
            position.average_price = new_avg_price
            position.total_cost = old_cost + new_cost
            position.current_price = price
            position.last_updated = datetime.utcnow()
        else:
            # Create new position
            position = Position(
                ticker=ticker,
                quantity=quantity,
                average_price=price,
                total_cost=total_cost,
                current_price=price
            )
            position.save()
            portfolio.positions.append(position)
        
        position.save()
        
        # Update portfolio cash
        portfolio.current_cash -= total_cost
        portfolio.total_value = calculate_portfolio_value(portfolio)
        portfolio.last_updated = datetime.utcnow()
        portfolio.save()
        
        # Create transaction record
        transaction = Transaction(
            ticker=ticker,
            action="buy",
            quantity=quantity,
            price=price,
            total_value=total_cost,
            reason=reason
        )
        transaction.save()
        portfolio.transactions.append(transaction)
        portfolio.save()
        
        return {
            "success": True,
            "message": f"Bought {quantity} {ticker} at ${price:.2f}",
            "transaction_id": str(transaction.id),
            "remaining_cash": portfolio.current_cash,
            "position": {
                "ticker": position.ticker,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "total_cost": position.total_cost
            }
        }
    
    except Exception as e:
        return {"success": False, "message": f"Error executing buy order: {str(e)}"}


def sell_asset(
    portfolio_id: str,
    ticker: str,
    quantity: float,
    price: Optional[float] = None,
    reason: str = "user_manual"
) -> Dict:
    """Execute a sell order"""
    try:
        portfolio = get_or_create_portfolio(portfolio_id)
        
        # Find position
        position = Position.objects(ticker=ticker).first()
        if not position or position.quantity <= 0:
            return {"success": False, "message": f"No position found for {ticker}"}
        
        if quantity > position.quantity:
            return {
                "success": False,
                "message": f"Insufficient shares. Requested: {quantity}, Owned: {position.quantity}"
            }
        
        # Get current price if not provided
        if price is None:
            price = get_current_price(ticker)
            if price is None:
                price = position.average_price  # Fallback to average price
        
        total_value = quantity * price
        
        # Update position
        # Calculate cost basis proportionally
        total_quantity_before = position.quantity
        cost_basis_sold = (quantity / total_quantity_before) * position.total_cost if total_quantity_before > 0 else 0
        
        position.quantity -= quantity
        position.total_cost -= cost_basis_sold
        
        # Clean up if position is fully sold
        if position.quantity <= 0:
            position.quantity = 0
            position.total_cost = 0
        
        position.current_price = price
        position.last_updated = datetime.utcnow()
        position.save()
        
        # Update portfolio cash
        portfolio.current_cash += total_value
        portfolio.total_value = calculate_portfolio_value(portfolio)
        portfolio.last_updated = datetime.utcnow()
        portfolio.save()
        
        # Create transaction record
        transaction = Transaction(
            ticker=ticker,
            action="sell",
            quantity=quantity,
            price=price,
            total_value=total_value,
            reason=reason
        )
        transaction.save()
        portfolio.transactions.append(transaction)
        portfolio.save()
        
        return {
            "success": True,
            "message": f"Sold {quantity} {ticker} at ${price:.2f}",
            "transaction_id": str(transaction.id),
            "remaining_cash": portfolio.current_cash,
            "position": {
                "ticker": position.ticker,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "total_cost": position.total_cost
            } if position.quantity > 0 else None
        }
    
    except Exception as e:
        return {"success": False, "message": f"Error executing sell order: {str(e)}"}


def get_portfolio_positions(portfolio_id: str = "default") -> List[Dict]:
    """Get all positions in the portfolio with current values"""
    portfolio = get_or_create_portfolio(portfolio_id)
    portfolio = update_position_prices(portfolio)
    
    positions = []
    for position_ref in portfolio.positions:
        position = Position.objects(id=position_ref.id).first()
        if position and position.quantity > 0:
            current_price = position.current_price or position.average_price
            pnl = position.calculate_pnl()
            pnl_percent = position.calculate_pnl_percent()
            
            positions.append({
                "symbol": position.ticker,
                "quantity": position.quantity,
                "averagePrice": position.average_price,
                "currentPrice": current_price,
                "totalCost": position.total_cost,
                "currentValue": current_price * position.quantity,
                "pnl": pnl,
                "pnlPercent": pnl_percent,
                "lastUpdated": position.last_updated.isoformat() if position.last_updated else None
            })
    
    return positions


def calculate_returns(portfolio: Portfolio, days: int = 30) -> List[float]:
    """Calculate daily returns for the portfolio over the specified period"""
    # Get performance history or calculate from transactions
    returns = []
    
    # For now, we'll calculate from transactions and current value
    # In a production system, you'd store daily snapshots
    if portfolio.performance_history:
        history = portfolio.performance_history[-days:] if len(portfolio.performance_history) > days else portfolio.performance_history
        if len(history) > 1:
            for i in range(1, len(history)):
                prev_value = history[i-1].get("total_value", portfolio.initial_cash)
                curr_value = history[i].get("total_value", portfolio.total_value)
                daily_return = ((curr_value - prev_value) / prev_value) * 100 if prev_value > 0 else 0
                returns.append(daily_return)
    
    return returns


def calculate_volatility(portfolio: Portfolio, days: int = 30) -> float:
    """Calculate portfolio volatility (standard deviation of returns)"""
    returns = calculate_returns(portfolio, days)
    if len(returns) < 2:
        return 0.0
    return float(np.std(returns))


def calculate_sharpe_ratio(portfolio: Portfolio, risk_free_rate: float = 0.02, days: int = 30) -> float:
    """Calculate Sharpe ratio (risk-adjusted returns)"""
    returns = calculate_returns(portfolio, days)
    if len(returns) < 2:
        return 0.0
    
    avg_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0.0
    
    # Annualize returns and risk-free rate
    annual_return = avg_return * 252  # Trading days per year
    annual_std = std_return * np.sqrt(252)
    annual_rf_rate = risk_free_rate * 100  # Convert to percentage
    
    sharpe = (annual_return - annual_rf_rate) / annual_std if annual_std > 0 else 0.0
    return float(sharpe)


def calculate_max_drawdown(portfolio: Portfolio) -> float:
    """Calculate maximum drawdown"""
    if not portfolio.performance_history or len(portfolio.performance_history) < 2:
        return 0.0
    
    values = [h.get("total_value", portfolio.initial_cash) for h in portfolio.performance_history]
    peak = values[0]
    max_dd = 0.0
    
    for value in values:
        if value > peak:
            peak = value
        drawdown = ((peak - value) / peak) * 100 if peak > 0 else 0
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd


def get_portfolio_summary(portfolio_id: str = "default") -> Dict:
    """Get comprehensive portfolio summary with all metrics"""
    portfolio = get_or_create_portfolio(portfolio_id)
    portfolio = update_position_prices(portfolio)
    portfolio.total_value = calculate_portfolio_value(portfolio)
    
    # Calculate metrics
    total_return = ((portfolio.total_value - portfolio.initial_cash) / portfolio.initial_cash) * 100
    volatility = calculate_volatility(portfolio)
    sharpe_ratio = calculate_sharpe_ratio(portfolio)
    max_drawdown = calculate_max_drawdown(portfolio)
    
    # Update portfolio metrics
    portfolio.total_return = total_return
    portfolio.volatility = volatility
    portfolio.sharpe_ratio = sharpe_ratio
    portfolio.max_drawdown = max_drawdown
    
    # Save performance snapshot
    snapshot = {
        "date": datetime.utcnow().isoformat(),
        "total_value": portfolio.total_value,
        "cash": portfolio.current_cash,
        "positions_value": portfolio.total_value - portfolio.current_cash,
        "total_return": total_return
    }
    
    if not portfolio.performance_history:
        portfolio.performance_history = []
    portfolio.performance_history.append(snapshot)
    
    # Keep only last 365 days of history
    if len(portfolio.performance_history) > 365:
        portfolio.performance_history = portfolio.performance_history[-365:]
    
    portfolio.save()
    
    positions = get_portfolio_positions(portfolio_id)
    
    # Calculate allocation
    allocation = []
    for pos in positions:
        allocation.append({
            "name": pos["symbol"],
            "value": (pos["currentValue"] / portfolio.total_value) * 100 if portfolio.total_value > 0 else 0
        })
    
    # Add cash allocation
    if portfolio.current_cash > 0:
        allocation.append({
            "name": "Cash",
            "value": (portfolio.current_cash / portfolio.total_value) * 100 if portfolio.total_value > 0 else 0
        })
    
    return {
        "portfolio_id": portfolio.portfolio_id,
        "initial_cash": portfolio.initial_cash,
        "current_cash": portfolio.current_cash,
        "total_value": portfolio.total_value,
        "total_return": total_return,
        "volatility": volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "positions": positions,
        "allocation": allocation,
        "positions_count": len(positions),
        "last_updated": portfolio.last_updated.isoformat() if portfolio.last_updated else None
    }


def get_performance_history(portfolio_id: str = "default", days: int = 30) -> List[Dict]:
    """Get performance history for visualization"""
    portfolio = get_or_create_portfolio(portfolio_id)
    
    if not portfolio.performance_history:
        return []
    
    # Return last N days
    history = portfolio.performance_history[-days:] if len(portfolio.performance_history) > days else portfolio.performance_history
    
    return [
        {
            "date": h.get("date"),
            "value": h.get("total_value", 0),
            "returns": h.get("total_return", 0)
        }
        for h in history
    ]


def execute_strategy_from_forecast(
    portfolio_id: str,
    ticker: str,
    forecast_id: Optional[str] = None,
    strategy: str = "momentum"
) -> Dict:
    """
    Execute trading strategy based on forecast predictions
    
    Strategies:
    - 'momentum': Buy if forecast predicts upward trend, sell if downward
    - 'conservative': Only buy if strong upward prediction, hold otherwise
    - 'aggressive': Buy/sell based on forecast direction
    """
    try:
        # Get latest forecast for ticker
        forecast = Forecast.objects(ticker=ticker).order_by("-created_at").first()
        if not forecast:
            return {"success": False, "message": f"No forecast found for {ticker}"}
        
        forecast_data = forecast.forecast_data
        if not forecast_data or len(forecast_data) < 2:
            return {"success": False, "message": "Insufficient forecast data"}
        
        # Get current price
        current_price = get_current_price(ticker)
        if not current_price:
            return {"success": False, "message": f"Could not fetch current price for {ticker}"}
        
        # Analyze forecast trend
        # Compare first and last predicted close prices
        first_predicted_close = forecast_data[0].get("Close", current_price)
        last_predicted_close = forecast_data[-1].get("Close", current_price)
        
        price_change = last_predicted_close - first_predicted_close
        price_change_percent = (price_change / first_predicted_close) * 100 if first_predicted_close > 0 else 0
        
        # Get current position
        portfolio = get_or_create_portfolio(portfolio_id)
        position = Position.objects(ticker=ticker).first()
        current_quantity = position.quantity if position else 0
        
        # Strategy logic
        action_taken = None
        result = {"success": True, "strategy": strategy, "forecast_analysis": {}}
        
        if strategy == "momentum":
            # Buy if forecast predicts >2% increase, sell if >2% decrease
            if price_change_percent > 2.0 and current_quantity == 0:
                # Buy signal
                available_cash = portfolio.current_cash
                # Use 10% of available cash
                investment_amount = available_cash * 0.1
                quantity = investment_amount / current_price
                if quantity > 0:
                    buy_result = buy_asset(portfolio_id, ticker, quantity, current_price, f"forecast_momentum_{forecast_id}")
                    action_taken = "buy"
                    result.update(buy_result)
            
            elif price_change_percent < -2.0 and current_quantity > 0:
                # Sell signal - sell 50% of position
                sell_quantity = current_quantity * 0.5
                sell_result = sell_asset(portfolio_id, ticker, sell_quantity, current_price, f"forecast_momentum_{forecast_id}")
                action_taken = "sell"
                result.update(sell_result)
            else:
                action_taken = "hold"
                result["message"] = f"Hold - Forecast change: {price_change_percent:.2f}%"
        
        elif strategy == "conservative":
            # Only buy if forecast predicts >5% increase
            if price_change_percent > 5.0 and current_quantity == 0:
                available_cash = portfolio.current_cash
                investment_amount = available_cash * 0.05  # Only 5% of cash
                quantity = investment_amount / current_price
                if quantity > 0:
                    buy_result = buy_asset(portfolio_id, ticker, quantity, current_price, f"forecast_conservative_{forecast_id}")
                    action_taken = "buy"
                    result.update(buy_result)
            else:
                action_taken = "hold"
                result["message"] = f"Hold - Forecast change: {price_change_percent:.2f}% (threshold: 5%)"
        
        elif strategy == "aggressive":
            # More aggressive trading
            if price_change_percent > 1.0 and current_quantity == 0:
                available_cash = portfolio.current_cash
                investment_amount = available_cash * 0.2  # 20% of cash
                quantity = investment_amount / current_price
                if quantity > 0:
                    buy_result = buy_asset(portfolio_id, ticker, quantity, current_price, f"forecast_aggressive_{forecast_id}")
                    action_taken = "buy"
                    result.update(buy_result)
            elif price_change_percent < -1.0 and current_quantity > 0:
                sell_quantity = current_quantity * 0.75  # Sell 75%
                sell_result = sell_asset(portfolio_id, ticker, sell_quantity, current_price, f"forecast_aggressive_{forecast_id}")
                action_taken = "sell"
                result.update(sell_result)
            else:
                action_taken = "hold"
                result["message"] = f"Hold - Forecast change: {price_change_percent:.2f}%"
        
        result["forecast_analysis"] = {
            "current_price": current_price,
            "first_predicted_close": first_predicted_close,
            "last_predicted_close": last_predicted_close,
            "predicted_change": price_change,
            "predicted_change_percent": price_change_percent,
            "action_taken": action_taken
        }
        
        return result
    
    except Exception as e:
        return {"success": False, "message": f"Error executing strategy: {str(e)}"}

