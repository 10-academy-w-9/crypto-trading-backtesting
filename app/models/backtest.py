from app import db

class Backtest(db.Model):
    __tablename__ = 'backtests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    symbol = db.Column(db.String(20))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    inital_cash = db.Column(db.Integer)
    fee = db.Column(db.Integer)
    # status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Indicator(db.Model):
    __tablename__ = 'indicators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)

class Parameter(db.Model):
    __tablename__ = 'parameters'
    id = db.Column(db.Integer, primary_key=True)
    backtest_id = db.Column(db.Integer, db.ForeignKey('backtests.id'), nullable=False)
    indicator_id = db.Column(db.Integer, db.ForeignKey('indicators.id'), nullable=False)
    value = db.Column(db.String(255))

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    backtest_id = db.Column(db.Integer, db.ForeignKey('backtests.id'), nullable=False)
    total_return = db.Column(db.Numeric(10, 2))
    number_of_trades = db.Column(db.Integer)
    winning_trades = db.Column(db.Integer)
    losing_trades = db.Column(db.Integer)
    max_drawdown = db.Column(db.Numeric(10, 2))
    sharpe_ratio = db.Column(db.Numeric(10, 2))

class Metric(db.Model):
    __tablename__ = 'metrics'
    id = db.Column(db.Integer, primary_key=True)
    backtest_id = db.Column(db.Integer, db.ForeignKey('backtests.id'), nullable=False)
    metric_name = db.Column(db.String(255))
    metric_value = db.Column(db.Numeric(10, 2))

class Coin(db.Model):
    __tablename__ = 'coins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)