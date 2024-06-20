# Crypto Trading Backtesting

Crypto Trading Backtesting: Scalable Backtesting Infrastructure for Cryptocurrencies

## Overview 
The Crypto Trading Backtesting project aims to provide a robust, large-scale trading data pipeline designed to help users backtest cryptocurrency trading strategies. The system uses historical candlestick data to simulate trades and evaluate strategies, providing valuable insights and reducing the risk associated with trading cryptocurrencies.

## Features

- **Data Ingestion** : Fetches historical candlestick data from Binance and Yahoo Finance.

- **Backtesting Engine**: Utilizes advanced frameworks like Backtrader, Freqtrade, and Vectorbt to simulate trades based on various strategies.

- **Metrics Calculation**: Evaluates strategies using metrics such as returns, number of trades, winning trades, losing trades, max drawdown, and Sharpe ratio.

- **Dynamic Scene Generation**: Automates backtesting runs with customizable parameters.

- **MLOps Integration**: Incorporates tools like Apache Airflow, Kafka, MLflow, and CML for seamless pipeline automation and monitoring.

- **Frontend Interface**: Provides a user-friendly interface for running backtests and viewing results.

## Project Structure

```
crypto-trading-backtesting/
│
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── ISSUE_TEMPLATE.md
│
├── airflow/
│   ├── dags/
│   │   ├── backtest_dag.py
│   │   └── monitor_dag.py
│   └── plugins/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── backtest.py
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── backtest.py
│   │   └── index.py
│   ├── services/
│   │   ├── backtest_service.py
│   │   ├── kafka_service.py
│   │   └── mlflow_service.py
│   └── templates/
│       └── index.html
│
├── config/
│   ├── airflow.cfg
│   ├── config.py
│   ├── kafka-config.yaml
│   └── mlflow-config.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── backtests/
│
├── docs/
│   ├── README.md
│   ├── DESIGN.md
│   └── USAGE.md
│
├── notebooks/
│   ├── data_exploration.ipynb
│   ├── backtesting.ipynb
│   └── model_training.ipynb
│
├── scripts/
│   ├── backtest_runner.py
│   ├── data_ingestion.py
│   └── model_training.py
│
├── tests/
│   ├── unit/
│   │   ├── test_backtest_service.py
│   │   ├── test_kafka_service.py
│   │   └── test_mlflow_service.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   └── conftest.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── setup.py
```
    
### Installation

1. **Clone the repository:**

    ```sh
    git clone git@github.com:your-username/crypto_trading_backtesting.git
    cd crypto_trading_backtesting
    ```

2. **Set up a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3. **Install Requirements:**
    ```sh
    pip install -r requirements.txt
    ```
4. **Run Streamlit interface**
    ```sh
   streamlit run src/frontend/app.py
   ```

## Usage
1. **Provide input descriptions** of the trading strategies, including scenarios and expected outputs.

2. **Run the backtesting system** to simulate trades and evaluate strategies.
3. **Review the generated metrics** to assess the performance of different trading strategies.
4. **Select the desired strategies** for further use or real-time trading.

## License

This project is licensed under the MIT License.


## Contributors

- [@abyt101](https://github.com/AbYT101) - Abraham Teka
- Temesgen Gebreabzgi
- Selamawit Tibebu
- Dereje Hinsermu

## Challenge by

![10 Academy](https://static.wixstatic.com/media/081e5b_5553803fdeec4cbb817ed4e85e1899b2~mv2.png/v1/fill/w_246,h_106,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/10%20Academy%20FA-02%20-%20transparent%20background%20-%20cropped.png)