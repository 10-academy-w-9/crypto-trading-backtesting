import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import yfinance as yf
import pandas as pd
from time import sleep

load_dotenv()

# RDS connection information
rds_host = os.getenv('PG_HOST')
rds_port = os.getenv('PG_PORT')
rds_db = os.getenv('PG_DATABASE')
rds_user = os.getenv('PG_USER')
rds_password = os.getenv('PG_PASSWORD')

# Connect to RDS (PostgreSQL)
engine = create_engine(f'postgresql+psycopg2://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_db}')

def fetch_ohlcv(symbol, since):
    try:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        ohlcv = ticker.history(period='1d', start=since)
        return ohlcv.reset_index()
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def store_dataframe(df, table_name):
    df.to_sql(table_name, con=engine, if_exists='append', index=False)

# Fetch and store data for multiple symbols
symbols = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'SOL1-USD', 'DOGE-USD', 'DOT1-USD', 'SHIB-USD', 'MATIC-USD', 'LTC-USD', 'UNI-USD', 'BCH-USD', 'LINK-USD', 'XLM-USD', 'ATOM-USD', 'VET-USD', 'ICP-USD', 'FIL-USD', 'THETA-USD']
since = '2020-06-20'

for symbol in symbols:
    ohlcv = fetch_ohlcv(symbol, since)
    if ohlcv is not None and not ohlcv.empty:
        # Rename columns to match the existing structure if needed
        df = ohlcv.rename(columns={'Date': 'timestamp', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        store_dataframe(df, f'ohlcv_{symbol.replace("-", "_")}')
        print(f'Stored data for {symbol}')
    else:
        print(f'Failed to fetch data for {symbol}')
    sleep(1)  # Add a delay to avoid hitting rate limits

