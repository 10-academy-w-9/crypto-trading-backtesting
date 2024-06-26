import pandas as pd
import torch
from chronos import ChronosPipeline
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import create_engine
import os


# RDS connection information
rds_host = os.getenv('PG_HOST')
rds_port = os.getenv('PG_PORT')
rds_db = os.getenv('PG_DATABASE')
rds_user = os.getenv('PG_USER')
rds_password = os.getenv('PG_PASSWORD')

# Create engine for database connection
engine = create_engine(f'postgresql+psycopg2://{rds_user}:{rds_password}@{rds_host}:{rds_port}/{rds_db}')


def predict_and_plot_crypto_data(
    df,
    model_name="amazon/chronos-t5-small",
    prediction_length=12,
    num_samples=20):
    """
    Predicts and plots cryptocurrency data for a single coin.

    Args:
        df (pd.DataFrame): DataFrame containing OHLCV data with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
        model_name (str): Name of the pre-trained Chronos model (default: "amazon/chronos-t5-small").
        prediction_length (int): Number of future data points to predict (default: 12).
        num_samples (int): Number of prediction samples to generate (default: 20).

    Returns:
        tuple: Tuple containing forecast index and median prediction array.
    """

    # Initialize Chronos pipeline
    pipeline = ChronosPipeline.from_pretrained(
        model_name,
        device_map="cpu",  # use "cpu" for CPU inference and "mps" for Apple Silicon
        torch_dtype=torch.bfloat16,
    )

    # Perform prediction
    forecast = pipeline.predict(
        context=torch.tensor(df["close"].values),  # Assuming 'close' is the column name in your DataFrame
        prediction_length=prediction_length,
        num_samples=num_samples,
    )

    # Generate forecast index for plotting
    forecast_index = range(len(df), len(df) + prediction_length)
    low, median, high = np.quantile(forecast[0].numpy(), [0.1, 0.5, 0.9], axis=0)

    # Plot and visualize predictions
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    plt.plot(df["close"], label="History")  # Assuming 'close' is the column name in your DataFrame
    plt.plot(forecast_index, median, label="Median Prediction")
    plt.fill_between(forecast_index, low, high, alpha=0.2, label="Prediction Range")
    plt.title(f"Predicted Prices")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)  # Add gridlines
    plt.show()

    return forecast_index, median  # Optionally return forecast data for further use


def fetch_data_from_db(symbol):
    try:
        # Construct table name based on symbol
        table_name = f'ohlcv_{symbol.replace("-", "_")}'

        # Query to fetch data from database
        query = f"SELECT timestamp, open, high, low, close, volume FROM {table_name};"

        # Fetch data from database into a DataFrame
        df = pd.read_sql(query, con=engine, parse_dates=['timestamp'])

        # Set 'timestamp' column as index
        df.set_index('timestamp', inplace=True)

        return df

    except Exception as e:
        print(f"Error fetching data from database for {symbol}: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage: Fetch data for a specific symbol from database
    symbol = 'BTC-USD'
    df = fetch_data_from_db(symbol)
    
    if df is not None:
        print(f"Fetched data for {symbol}:")
        print(df.head())
        
        # Perform prediction and plotting
        predict_and_plot_crypto_data(df)
    else:
        print(f"Failed to fetch data for {symbol}")
