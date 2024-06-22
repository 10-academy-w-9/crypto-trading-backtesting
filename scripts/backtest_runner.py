import pandas as pd
from sqlalchemy import create_engine
import backtrader as bt
import os

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

def run_backtest(strategy, symbol, start_date, end_date):
    data = fetch_data(symbol, start_date, end_date)
    
    # Create a data feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Initialize cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    cerebro.adddata(data_feed)
    cerebro.broker.set_cash(100000)
    cerebro.broker.setcommission(commission=0.002)
    # cerebro.addsizer(bt.sizers.FixedSize, stake=5)

    # Add analyzers for performance metrics
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    # Print starting conditions
    start_value = cerebro.broker.getvalue()
    print(f'Starting Portfolio Value: {start_value:.2f}')

    # Run backtest
    results = cerebro.run()

    # Print ending conditions
    end_value = cerebro.broker.getvalue()
    print(f'Ending Portfolio Value: {end_value:.2f}')

    # Extract and print analyzers results
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


if __name__ == "__main__":
    symbol = 'BTC/USDT'
    start_date = '2023-06-20'
    end_date = '2024-06-20'
    
    for strategy in [RsiBollingerBandsStrategy,SimpleMovingAverageStrategy]:
        run_backtest(strategy, symbol, start_date, end_date)
    
    try:
        data = fetch_data(symbol, start_date, end_date)
        print(data.head())  
    except Exception as e:
        print(f"Error running backtest: {e}")
