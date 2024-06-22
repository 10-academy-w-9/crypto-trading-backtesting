import pandas as pd
from sqlalchemy import create_engine
import backtrader as bt
import os
import mlflow
import mlflow.pyfunc
import mlflow.tracking
from mlflow import log_metric, log_param

experiment_name = "Crypto Trading Backtesting"

mlflow.set_experiment(experiment_name)
# RDS connection information
rds_host = os.getenv('PG_HOST', 'localhost')  # Replace 'localhost' with your actual host if needed
rds_port = int(os.getenv('PG_PORT', '5432'))  # Convert port to int, replace '5432' with your default port
rds_db = os.getenv('PG_DATABASE', 'backtest_db')  # Replace 'backtest_db' with your actual database name
rds_user = os.getenv('PG_USER', 'pguser')  # Replace 'pguser' with your actual username
rds_password = os.getenv('PG_PASSWORD', 'pgpwd')
print(f"PG_HOST: {rds_host}, PG_PORT: {rds_port}, PG_DATABASE: {rds_db}, PG_USER: {rds_user}, PG_PASSWORD: {rds_password}")

engine = create_engine(f'postgresql+psycopg2://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_db}')
print(f"PG_HOST: {rds_host}, PG_PORT: {rds_port}, PG_DATABASE: {rds_db}, PG_USER: {rds_user}, PG_PASSWORD: {rds_password}")

def fetch_data(symbol, start_date, end_date):
    query = f"""
        SELECT timestamp AS date, open AS open, high AS high, low AS low, close AS close, volume AS volume 
        FROM public."ohlcv_{symbol.replace('/', '_')}"
        WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}';
    """
    try:
        print(f"Executing query:\n{query}\n")  # Print the SQL query for debugging purposes
        
        data = pd.read_sql(query, con=engine)
        print(f"Fetched data:\n{data.head()}\n")  # Print the first few rows of fetched data for debugging
        
        # Check if data is empty
        if data.empty:
            raise ValueError("No data returned from query.")
        
        # Convert 'date' column to datetime
        data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
        
        # Set 'date' column as index
        data.set_index('date', inplace=True)
        
        # Ensure column names are correctly capitalized for Backtrader
        data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

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
        # Additional indicators for plotting
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

class RefinedSMAStrategy(bt.Strategy):
    params = (
        ('short_period', 10),
        ('long_period', 50),
    )

    def __init__(self):
        self.short_sma = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.short_period)
        self.long_sma = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.params.long_period)
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

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
            if self.short_sma[0] > self.long_sma[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:
            if self.short_sma[0] < self.long_sma[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
def run_backtest(strategy_class, symbol, start_date, end_date):
    # Fetch data for backtesting
    data = fetch_data(symbol, start_date, end_date)
    
    # Initialize cerebro
    cerebro = bt.Cerebro()
    
    # Add data feed
    cerebro.adddata(bt.feeds.PandasData(dataname=data))
    
    # Add strategy
    strategy = strategy_class
    cerebro.addstrategy(strategy)
    
    # Set broker settings
    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.002)

    # Add analyzers for performance metrics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    # Print starting conditions
    start_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {start_value:.2f}')

    # Run backtest
    with mlflow.start_run(run_name=strategy.__name__):  # Set run name to strategy class name
        results = cerebro.run()

        # Print ending conditions
        end_value = cerebro.broker.getvalue()
        print(f'Ending Portfolio Value: {end_value:.2f}')

        # Extract strategy parameters
        strategy_params = strategy.params.__dict__
        
        # Prepare results
        result_dict = {
            "Starting Portfolio Value": start_value,
            "Ending Portfolio Value": end_value,
            "Sharpe Ratio": results[0].analyzers.sharpe.get_analysis().get('sharperatio', 'N/A'),
            "Max Drawdown": results[0].analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 'N/A'),
            "Total Trades": results[0].analyzers.trades.get_analysis().get('total', {}).get('total', 'N/A'),
            "Winning Trades": results[0].analyzers.trades.get_analysis().get('won', {}).get('total', 'N/A'),
            "Losing Trades": results[0].analyzers.trades.get_analysis().get('lost', {}).get('total', 'N/A'),
            "Total Return": results[0].analyzers.returns.get_analysis().get('rtot', 'N/A')
        }

        # Log parameters and metrics to MLflow
        for param, value in strategy_params.items():
            mlflow.log_param(param, value)
            
        for key, value in result_dict.items():
            mlflow.log_metric(key, value)

    # Plot the results
    cerebro.plot(style='candlestick')

    return result_dict



if __name__ == "__main__":
    symbol = 'BTC/USDT'
    start_date = '2023-06-20'
    end_date = '2024-06-20'
    
    strategies = [RsiBollingerBandsStrategy, SimpleMovingAverageStrategy, RefinedSMAStrategy]
    
    for strategy in strategies:
        run_backtest(strategy, symbol, start_date, end_date)
