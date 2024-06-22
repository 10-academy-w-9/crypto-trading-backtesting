import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from scripts.backtest_runner import run_backtest, RsiBollingerBandsStrategy

class BacktestService:
    @staticmethod
    def execute_backtest(symbol, start_date, end_date):
        return run_backtest(RsiBollingerBandsStrategy, symbol, start_date, end_date)
