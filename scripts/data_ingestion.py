import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import ccxt
import pandas as pd
from time import sleep
from requests.exceptions import ReadTimeout


load_dotenv()

# RDS connection information
rds_host = os.getenv('PG_HOST')
rds_port = os.getenv('PG_PORT')
rds_db = os.getenv('PG_DATABASE')
rds_user = os.getenv('PG_USER')
rds_password = os.getenv('PG_PASSWORD')

# Connect to RDS (PostgreSQL)
engine = create_engine(f'postgresql+psycopg2://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_db}')

# Connect to Binance
binance = ccxt.binance()

binance = ccxt.binance({
    'options': {
        'adjustForTimeDifference': True,
    },
    'timeout': 20000, 
})

def fetch_ohlcv(symbol, timeframe, since=None, limit=1000):
    try:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        return ohlcv
    except ReadTimeout:
        print(f"Timeout occurred for {symbol}. Retrying...")
        sleep(5)  # Delay before retrying
        return fetch_ohlcv(symbol, timeframe, since, limit)

def ohlcv_to_dataframe(ohlcv):
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def store_dataframe(df, table_name):
    df.to_sql(table_name, con=engine, if_exists='append', index=False)

# Fetch and store data for multiple symbols
symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'SOL/USDT', 'DOGE/USDT', 'DOT/USDT', 'SHIB/USDT', 'MATIC/USDT', 'LTC/USDT', 'UNI/USDT', 'BCH/USDT', 'LINK/USDT', 'XLM/USDT', 'ATOM/USDT', 'VET/USDT', 'ICP/USDT', 'FIL/USDT', 'THETA/USDT']
timeframe = '1d'
since = binance.parse8601('2023-06-20T00:00:00Z')

for symbol in symbols:
    ohlcv = fetch_ohlcv(symbol, timeframe, since)
    if ohlcv:
        df = ohlcv_to_dataframe(ohlcv)
        store_dataframe(df, f'ohlcv_{symbol.replace("/", "_")}')
        print(f'Stored data for {symbol}')
    else:
        print(f'Failed to fetch data for {symbol}')