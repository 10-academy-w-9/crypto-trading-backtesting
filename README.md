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

- **Index Fund**: Algorithm that shows the best backtested strategy and implements a recommendation based on a combination of best returns.


## Skills and Knowledge

- **Skills**: Technical analysis, backtesting, trading, data pipeline building, structured streaming, workflow orchestration.
- **Knowledge**: Financial prediction, enterprise-grade data engineering using Apache and Databricks tools.

## Technical Skills

- **Python Programming**
- **SQL Programming**
- **Data & Analytics Engineering**
- **MLOps**
- **Software Development Frameworks**

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
├── docs/
│   ├── DESIGN.md
│   └── USAGE.md
│
├── notebooks/
│   ├── backtesting_yfinance.ipynb
│   ├── backtesting.ipynb
│   ├── Chronos.ipynb
│   ├── data_exploration.ipynb
│   └── model_training.ipynb
│   └── moirai_forcast.ipynb
│
├── scripts/
│   ├── backtest_runner.py
│   ├── data_ingestion.py
│   ├── forecast_backtest_runner.py
│   ├── forecast.py
│   ├── mlflow_backtest.py
│   └── model_training.py
│   └── moirai_forcast.py
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
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── LICENSE
├── README.md
└── setup.py
```
    
### Set up Instructions

1. **Clone the repository:**

    ```sh
    git clone https://github.com/10-academy-w-9/crypto-trading-backtesting.git
    cd crypto-trading-backtesting
    ```

2. **Set up a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate  #linux and Mac
    `venv\Scripts\activate`   #On Windows 
    ```
3. **Install Requirements:**
    ```sh
    pip install -r requirements.txt
    ```
4. **Run React interface**
    ```sh
   streamlit run src/frontend/app.py
   ```
5. **Run Chronos**
    ```sh
    pip install git+https://github.com/amazon-science/chronos-forecasting.git

    pip install pandas numpy torch sqlalchemy psycopg2-binary matplotlib chronos
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
- [@temesgen5335](https://github.com/temesgen5335)- Temesgen Gebreabzgi
- [@SelamT94](https://github.com/SelamT94) - Selamawit Tibebu
- [@derejehinsermu](https://github.com/derejehinsermu) - Dereje Hinsermu

## Challenge by

![10 Academy](https://static.wixstatic.com/media/081e5b_5553803fdeec4cbb817ed4e85e1899b2~mv2.png/v1/fill/w_246,h_106,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/10%20Academy%20FA-02%20-%20transparent%20background%20-%20cropped.png)