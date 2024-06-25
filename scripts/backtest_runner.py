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

class MacdStrategy(bt.Strategy):
    params = (
        ('macd1_period', 12),
        ('macd2_period', 26),
        ('signal_period', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACDHisto(period_me1=self.params.macd1_period, period_me2=self.params.macd2_period, period_signal=self.params.signal_period)

    def next(self):
        if not self.position:
            if self.macd.lines.histo[0] > 0 and self.macd.lines.histo[-1] <= 0:
                self.buy()
        else:
            if self.macd.lines.histo[0] < 0 and self.macd.lines.histo[-1] >= 0:
                self.sell()

class StochasticOscillatorStrategy(bt.Strategy):
    params = (
        ('stoch_period', 14),
        ('stoch_low', 20),
        ('stoch_high', 80),
    )

    def __init__(self):
        self.stoch = bt.indicators.Stochastic(period=self.params.stoch_period)

    def next(self):
        if not self.position:
            if self.stoch.lines.percK[0] < self.params.stoch_low and self.stoch.lines.percK[-1] >= self.params.stoch_low:
                self.buy()
        else:
            if self.stoch.lines.percK[0] > self.params.stoch_high and self.stoch.lines.percK[-1] <= self.params.stoch_high:
                self.sell()

def run_backtest(strategy_class, symbol, initial_cash, fee, start_date, end_date):
    data = fetch_data(symbol, start_date, end_date)
    print('we back to data')
    data_feed = bt.feeds.PandasData(dataname=data)
    
    # Initialize cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy_class)
    cerebro.adddata(data_feed)
    cerebro.broker.set_cash(float(initial_cash))
    cerebro.broker.setcommission(commission=0.002)
    
    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name='sharpe')
    print(1)
    # Print starting conditions
    print(f'Starting Portfolio Value: {cerebro.broker.getvalue():.2f}')
    
    # Run backtest
    result = cerebro.run()
    print(2)
    
    # Extracting backtest metrics
    total_return = cerebro.broker.getvalue() / initial_cash - 1
    number_of_trades = result[0].analyzers.tradeanalyzer.get_analysis()['total']['closed']
    winning_trades = result[0].analyzers.tradeanalyzer.get_analysis()['won']['total']
    losing_trades = result[0].analyzers.tradeanalyzer.get_analysis()['lost']['total']
    max_drawdown = result[0].analyzers.drawdown.get_analysis()['max']['drawdown']
    sharpe_ratio = result[0].analyzers.sharpe.get_analysis().get('sharperatio', 0.0)
    
    # Print ending conditions
    print(f'Ending Portfolio Value: {cerebro.broker.getvalue():.2f}')
    print(1)
    
    # Return results as a dictionary
    return {
        'backtest_id': 0,
        'total_return': total_return,
        'number_of_trades': number_of_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio
    }

def score_backtest(result):
    # Define weights for each metric
    weights = {
        'total_return': 0.4,
        'sharpe_ratio': 0.4,
        'max_drawdown': 0.2,
    }
    
    # Normalize the values (example with min-max normalization)
    normalized_return = (result['total_return'] - min_return) / (max_return - min_return)
    normalized_sharpe = (result['sharpe_ratio'] - min_sharpe) / (max_sharpe - min_sharpe)
    normalized_drawdown = (max_drawdown - result['max_drawdown']) / (max_drawdown - min_drawdown)
    
    # Calculate the score
    score = (
        weights['total_return'] * normalized_return +
        weights['sharpe_ratio'] * normalized_sharpe +
        weights['max_drawdown'] * normalized_drawdown
    )
    return score


if __name__ == "__main__":
    symbol = 'ETH/USD'
    start_date = '2023-06-20'
    end_date = '2024-06-20'
    initial_cash = 10000
    fee = 0.001
    
    strategies = [
        RsiBollingerBandsStrategy,
        MacdStrategy,
        StochasticOscillatorStrategy
    ]
    
    results = []
    for strategy in strategies:
        result = run_backtest(strategy, symbol, initial_cash, fee, start_date, end_date)
        results.append(result)
    
    # Determine the min and max values for normalization
    min_return = min(result['total_return'] for result in results)
    max_return = max(result['total_return'] for result in results)
    min_sharpe = min(result['sharpe_ratio'] for result in results)
    max_sharpe = max(result['sharpe_ratio'] for result in results)
    min_drawdown = min(result['max_drawdown'] for result in results)
    max_drawdown = max(result['max_drawdown'] for result in results)
    
    # Score each strategy
    scores = [score_backtest(result) for result in results]
    
    # Select the best strategy
    best_strategy_index = scores.index(max(scores))
    best_strategy = strategies[best_strategy_index]
    
    print("Best Strategy:")
    print(best_strategy.__name__)
    print("Score:")
    print(scores[best_strategy_index])
    print("Metrics:")
    print(results[best_strategy_index])
