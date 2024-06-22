import pandas as pd
from sqlalchemy import create_engine
import backtrader as bt
import os
import mlflow
import mlflow.pyfunc
import mlflow.tracking
from mlflow import log_metric, log_param, log_artifact

# RDS connection information
rds_host = os.getenv('PG_HOST')
rds_port = os.getenv('PG_PORT')
rds_db = os.getenv('PG_DATABASE')
rds_user = os.getenv('PG_USER')
rds_password = os.getenv('PG_PASSWORD')

engine = create_engine(f'postgresql+psycopg2://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_db}')

def fetch_data(symbol, start_date, end_date):
    query = f"""
        SELECT timestamp AS date, open AS open, high AS high, low AS low, close AS close, volume AS volume 
        FROM public."ohlcv_{symbol.replace('/', '_')}"
        WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}';
    """
    try:
        data = pd.read_sql(query, con=engine)
        if data.empty:
            raise ValueError("No data returned from query.")
        
        data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
        data.set_index('date', inplace=True)
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

        print(f"Fetched data from {data.index.min()} to {data.index.max()}")  # Add logging to check the date range

        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        raise

class RsiBollingerBandsStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('bb_period', 20),
        ('bb_dev', 2),
        ('oversold', 30),
        ('overbought', 70),
    )

    def __init__(self):
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
        self.bbands = bt.indicators.BollingerBands(period=self.params.bb_period, devfactor=self.params.bb_dev)

    def next(self):
        if not self.position:
            if self.rsi < self.params.oversold and self.data.close <= self.bbands.lines.bot:
                self.buy()
        else:
            if self.rsi > self.params.overbought or self.data.close >= self.bbands.lines.top:
                self.sell()

class StochasticOscillatorStrategy(bt.Strategy):
    params = (
        ('k_period', 14),
        ('d_period', 3),
        ('oversold', 20),
        ('overbought', 80),
    )

    def __init__(self):
        self.stoch = bt.indicators.StochasticSlow(
            period=self.params.k_period,
            period_dfast=self.params.d_period,
        )

    def next(self):
        if not self.position:
            if self.stoch.percK < self.params.oversold:
                self.buy()
        else:
            if self.stoch.percK > self.params.overbought:
                self.sell()

class SimpleMovingAverageStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

def run_backtest(strategy, symbol, start_date, end_date):
    data = fetch_data(symbol, start_date, end_date)
    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    cerebro.adddata(data_feed)
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.002)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

    initial_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_value:.2f}')

    results = cerebro.run()

    final_value = cerebro.broker.getvalue()
    print(f'Ending Portfolio Value: {final_value:.2f}')

    # Get analyzers data
    strat = results[0]

    # Prepare results
    result_dict = {
        "Starting Portfolio Value": start_value,
        "Ending Portfolio Value": end_value,
        "Sharpe Ratio": strat.analyzers.sharpe.get_analysis().get('sharperatio', 'N/A'),
        "Max Drawdown": strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 'N/A'),
        "Total Trades": strat.analyzers.trades.get_analysis().get('total', {}).get('total', 'N/A'),
        "Winning Trades": strat.analyzers.trades.get_analysis().get('won', {}).get('total', 'N/A'),
        "Losing Trades": strat.analyzers.trades.get_analysis().get('lost', {}).get('total', 'N/A'),
        "Total Return": strat.analyzers.returns.get_analysis().get('rtot', 'N/A')
    }

    # Plot the results
    cerebro.plot(style='candlestick')

    return result_dict

    trades = strat.analyzers.trades.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    sharpe = strat.analyzers.sharpe.get_analysis()

    # Initialize metrics
    total_trades = trades.total.total if 'total' in trades else 0
    winning_trades = trades.won.total if 'won' in trades else 0
    losing_trades = trades.lost.total if 'lost' in trades else 0
    max_drawdown = drawdown.max.drawdown if 'max' in drawdown and 'drawdown' in drawdown.max else 0.0
    sharpe_ratio = sharpe['sharperatio'] if 'sharperatio' in sharpe else 0.0

    returns = (final_value - initial_value) / initial_value

    # print(f"Total Trades: {total_trades}, Winning Trades: {winning_trades}, Losing Trades: {losing_trades}")
    # print(f"Max Drawdown: {max_drawdown:.2f}, Sharpe Ratio: {sharpe_ratio:.2f}")
    # print(f"Strategy: {strategy.__name__}, Initial Value: {initial_value}, Final Value: {final_value}, Returns: {returns:.2f}")

    return initial_value, final_value, returns, total_trades, winning_trades, losing_trades, max_drawdown, sharpe_ratio

def safe_log_metric(key, value):
    if value is not None and not (isinstance(value, float) and (value != value)):  # Check for NaN
        log_metric(key, value)
    else:
        log_metric(key, 0.0)  # Log zero if the value is None or NaN

if __name__ == "__main__":
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("Crypto Backtesting")

    symbol = 'BTC/USDT'
    start_date = '2023-06-20'
    end_date = '2024-06-20'

    strategies = [
        (RsiBollingerBandsStrategy, "RSI Bollinger Bands Strategy"),
        (StochasticOscillatorStrategy, "Stochastic Oscillator Strategy"),
        (SimpleMovingAverageStrategy, "Simple Moving Average Strategy"),
    ]

    for strategy, strategy_name in strategies:
        with mlflow.start_run(run_name=strategy_name):
            log_param("symbol", symbol)
            log_param("start_date", start_date)
            log_param("end_date", end_date)
            log_param("strategy", strategy_name)

            initial_value, final_value, returns, total_trades, winning_trades, losing_trades, max_drawdown, sharpe_ratio = run_backtest(strategy, symbol, start_date, end_date)

            safe_log_metric("initial_value", initial_value)
            safe_log_metric("final_value", final_value)
            safe_log_metric("returns", returns)
            safe_log_metric("total_trades", total_trades)
            safe_log_metric("winning_trades", winning_trades)
            safe_log_metric("losing_trades", losing_trades)
            safe_log_metric("max_drawdown", max_drawdown)
            safe_log_metric("sharpe_ratio", sharpe_ratio)

            print(f"Strategy: {strategy_name}")
            print(f"Initial Value: {initial_value}")
            print(f"Final Value: {final_value}")
            print(f"Returns: {returns}")
            print(f"Total Trades: {total_trades}")
            print(f"Winning Trades: {winning_trades}")
            print(f"Losing Trades: {losing_trades}")
            print(f"Max Drawdown: {max_drawdown}")
            print(f"Sharpe Ratio: {sharpe_ratio}")
