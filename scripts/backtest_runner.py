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

def run_backtest(strategy, symbol, start_date, end_date):
    data = fetch_data(symbol, start_date, end_date)
    
    # Create a data feed
    data_feed = bt.feeds.PandasData(dataname=data)

    # Initialize cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    cerebro.adddata(data_feed)
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.002)

    # Print starting conditions
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')

    # Run backtest
    cerebro.run()

    # Print ending conditions
    print(f'Ending Portfolio Value: {cerebro.broker.getvalue():.2f}')

    # Plot the results
    cerebro.plot()

if __name__ == "__main__":
    symbol = 'BTC/USDT'
    start_date = '2023-06-20'
    end_date = '2024-06-20'
    
    for strategy in [RsiBollingerBandsStrategy]:
        run_backtest(strategy, symbol, start_date, end_date)
    
    try:
        data = fetch_data(symbol, start_date, end_date)
        print(data.head())  
    except Exception as e:
        print(f"Error running backtest: {e}")
