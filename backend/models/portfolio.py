from mongoengine import Document, StringField, FloatField, DateTimeField, ListField, DictField, ReferenceField, IntField
import datetime

class Transaction(Document):
    """Represents a buy or sell transaction"""
    ticker = StringField(required=True)
    action = StringField(required=True, choices=['buy', 'sell'])  # 'buy' or 'sell'
    quantity = FloatField(required=True)
    price = FloatField(required=True)  # Price per unit at transaction time
    total_value = FloatField(required=True)  # quantity * price
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    reason = StringField(required=False)  # e.g., "forecast_prediction", "user_manual", "strategy_rule"
    forecast_id = StringField(required=False)  # Reference to forecast that triggered this
    
    meta = {
        "collection": "transactions",
        "ordering": ["-timestamp"]
    }

class Position(Document):
    """Represents a current position in the portfolio"""
    ticker = StringField(required=True, unique=True)
    quantity = FloatField(required=True, default=0.0)
    average_price = FloatField(required=True)  # Average purchase price
    total_cost = FloatField(required=True)  # Total cost basis
    current_price = FloatField(required=False)  # Current market price (updated)
    last_updated = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        "collection": "positions",
        "indexes": ["ticker"]
    }
    
    def calculate_pnl(self):
        """Calculate profit/loss for this position"""
        if self.current_price and self.quantity > 0:
            current_value = self.current_price * self.quantity
            return current_value - self.total_cost
        return 0.0
    
    def calculate_pnl_percent(self):
        """Calculate profit/loss percentage"""
        if self.average_price > 0 and self.current_price:
            return ((self.current_price - self.average_price) / self.average_price) * 100
        return 0.0

class Portfolio(Document):
    """Main portfolio document tracking overall portfolio state"""
    portfolio_id = StringField(required=True, unique=True, default="default")
    initial_cash = FloatField(required=True, default=100000.0)  # Starting cash
    current_cash = FloatField(required=True, default=100000.0)  # Available cash
    total_value = FloatField(required=True, default=100000.0)  # Total portfolio value (cash + positions)
    positions = ListField(ReferenceField(Position), required=False)
    transactions = ListField(ReferenceField(Transaction), required=False)
    performance_history = ListField(DictField(), required=False)  # Historical performance snapshots
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    last_updated = DateTimeField(default=datetime.datetime.utcnow)
    
    # Performance metrics (calculated)
    total_return = FloatField(required=False, default=0.0)  # Total return percentage
    volatility = FloatField(required=False, default=0.0)  # Portfolio volatility
    sharpe_ratio = FloatField(required=False, default=0.0)  # Sharpe ratio
    max_drawdown = FloatField(required=False, default=0.0)  # Maximum drawdown
    
    meta = {
        "collection": "portfolios",
        "indexes": ["portfolio_id"]
    }

