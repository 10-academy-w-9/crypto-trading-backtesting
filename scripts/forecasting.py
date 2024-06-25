import pandas as pd
import torch
from chronos import ChronosPipeline
import matplotlib.pyplot as plt
import numpy as np


# Define the crypto coins data source dictionary
crypto_data_dict = {
    'BTC': "/content/drive/MyDrive/backtesting/datas/yfinance/BTC-USD.csv",
    'BNB': "/content/drive/MyDrive/backtesting/datas/yfinance/BNB-USD.csv",
    'ETH': "/content/drive/MyDrive/backtesting/datas/yfinance/ETH-USD.csv"
}

def predict_and_plot_crypto_data(
    coin_name,
    crypto_data_dict,
    model_name="amazon/chronos-t5-small",
    prediction_length=12,
    num_samples=20):
    """
    Predicts and plots cryptocurrency data for a single coin.

    Args:
        coin_name (str): Name of the cryptocurrency (e.g., 'BTC', 'ETH').
        crypto_data_dict (dict): Dictionary containing data for each cryptocurrency.
            Keys should be coin names, values should be file paths to CSV data.
        model_name (str): Name of the pre-trained Chronos model (default: "amazon/chronos-t5-small").
        prediction_length (int): Number of future data points to predict (default: 12).
        num_samples (int): Number of prediction samples to generate (default: 20).

    Raises:
        ValueError: If coin_name is not found in crypto_data_dict.

    Returns:
        tuple: Tuple containing forecast index and median prediction array.
    """

    # Check if coin exists in data
    if coin_name not in crypto_data_dict:
        raise ValueError(f"Coin '{coin_name}' not found in data dictionary.")

    # Load data for the specified coin
    csv_file = crypto_data_dict[coin_name]
    df = pd.read_csv(csv_file)

    # Initialize Chronos pipeline
    pipeline = ChronosPipeline.from_pretrained(
        model_name,
        device_map="cpu",  # use "cpu" for CPU inference and "mps" for Apple Silicon
        torch_dtype=torch.bfloat16,
    )

    # Perform prediction
    forecast = pipeline.predict(
        context=torch.tensor(df["Close"]),
        prediction_length=prediction_length,
        num_samples=num_samples,
    )

    # Generate forecast index for plotting
    forecast_index = range(len(df), len(df) + prediction_length)
    low, median, high = np.quantile(forecast[0].numpy(), [0.1, 0.5, 0.9], axis=0)

    # Plot and visualize predictions
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    plt.plot(df["Close"], label="History")
    plt.plot(forecast_index, median, label="Median Prediction")
    plt.fill_between(forecast_index, low, high, alpha=0.2, label="Prediction Range")
    plt.title(f"Predicted {coin_name} Prices")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)  # Add gridlines
    plt.show()

    return forecast_index, median  # Optionally return forecast data for further use
