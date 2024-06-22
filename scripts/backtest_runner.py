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
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')  # Add Returns analyzer

    initial_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {initial_value:.2f}')

    results = cerebro.run()

    final_value = cerebro.broker.getvalue()
    print(f'Ending Portfolio Value: {final_value:.2f}')

    # Get analyzers data
    strat = results[0]
    trades = strat.analyzers.trades.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()
    sharpe = strat.analyzers.sharpe.get_analysis()
    returns = strat.analyzers.returns.get_analysis()  # Get returns analysis

    # Prepare results
    result_dict = {
        "Starting Portfolio Value": initial_value,
        "Ending Portfolio Value": final_value,
        "Sharpe Ratio": sharpe.get('sharperatio', 'N/A'),
        "Max Drawdown": drawdown.get('max', {}).get('drawdown', 'N/A'),
        "Total Trades": trades.get('total', {}).get('total', 'N/A'),
        "Winning Trades": trades.get('won', {}).get('total', 'N/A'),
        "Losing Trades": trades.get('lost', {}).get('total', 'N/A'),
        "Total Return": returns.get('rtot', 'N/A')  # Get total return
    }

    # Plot the results
    cerebro.plot(style='candlestick')

    return result_dict

def safe_log_metric(key, value):
    try:
        value = float(value)  # Convert to float
    except (TypeError, ValueError):
        value = 0.0  # Default to 0.0 if conversion fails
    log_metric(key, value)

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

            results = run_backtest(strategy, symbol, start_date, end_date)
            
            safe_log_metric("initial_value", results["Starting Portfolio Value"])
            safe_log_metric("final_value", results["Ending Portfolio Value"])
            safe_log_metric("returns", results["Total Return"])
            safe_log_metric("total_trades", results["Total Trades"])
            safe_log_metric("winning_trades", results["Winning Trades"])
            safe_log_metric("losing_trades", results["Losing Trades"])
            safe_log_metric("max_drawdown", results["Max Drawdown"])
            safe_log_metric("sharpe_ratio", results["Sharpe Ratio"])

            print(f"Strategy: {strategy_name}")
            print(f"Initial Value: {results['Starting Portfolio Value']}")
            print(f"Final Value: {results['Ending Portfolio Value']}")
            print(f"Returns: {results['Total Return']}")
            print(f"Total Trades: {results['Total Trades']}")
            print(f"Winning Trades: {results['Winning Trades']}")
            print(f"Losing Trades: {results['Losing Trades']}")
            print(f"Max Drawdown: {results['Max Drawdown']}")
            print(f"Sharpe Ratio: {results['Sharpe Ratio']}")
