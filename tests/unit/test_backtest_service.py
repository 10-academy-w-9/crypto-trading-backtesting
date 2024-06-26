import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
import os
import sys

root_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(root_path)

with patch.dict('os.environ', {
    'PG_HOST': 'localhost',
    'PG_PORT': '5432',
    'PG_DATABASE': 'test_db',
    'PG_USER': 'user',
    'PG_PASSWORD': 'password'
}):
    from scripts.backtest_runner import fetch_data, run_backtest, score_backtest, RsiBollingerBandsStrategy, MacdStrategy, StochasticOscillatorStrategy

class TestBacktestService(unittest.TestCase):

    @patch('scripts.backtest_runner.create_engine')
    @patch('scripts.backtest_runner.pd.read_sql')
    def test_fetch_data(self, mock_read_sql, mock_create_engine):
        with patch.dict('os.environ', {'PG_HOST': 'localhost', 'PG_PORT': '5432', 'PG_DATABASE': 'test_db', 'PG_USER': 'user', 'PG_PASSWORD': 'password'}):
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine

            sample_data = pd.DataFrame({
                'date': pd.date_range(start='2023-06-20', periods=5, freq='D'),
                'open': [1, 2, 3, 4, 5],
                'high': [2, 3, 4, 5, 6],
                'low': [0.5, 1.5, 2.5, 3.5, 4.5],
                'close': [1.5, 2.5, 3.5, 4.5, 5.5],
                'volume': [100, 200, 300, 400, 500]
            })
            mock_read_sql.return_value = sample_data

            data = fetch_data('ETH/USD', '2023-06-20', '2023-06-25')

            self.assertFalse(data.empty)
            self.assertEqual(data.shape[0], 5)
            self.assertIn('Open', data.columns)
            self.assertIn('High', data.columns)
            self.assertIn('Low', data.columns)
            self.assertIn('Close', data.columns)
            self.assertIn('Volume', data.columns)

    @patch('scripts.backtest_runner.fetch_data')
    @patch('backtrader.Cerebro')
    def test_run_backtest(self, mock_cerebro, mock_fetch_data):
        sample_data = pd.DataFrame({
            'date': pd.date_range(start='2023-06-20', periods=5, freq='D'),
            'Open': [1, 2, 3, 4, 5],
            'High': [2, 3, 4, 5, 6],
            'Low': [0.5, 1.5, 2.5, 3.5, 4.5],
            'Close': [1.5, 2.5, 3.5, 4.5, 5.5],
            'Volume': [100, 200, 300, 400, 500]
        })
        mock_fetch_data.return_value = sample_data

        mock_instance = MagicMock()
        mock_cerebro.return_value = mock_instance
        mock_instance.broker.getvalue.return_value = 11000

        # Adjust the structure to return analyzers properly
        mock_analyzer = MagicMock()
        mock_analyzer.get_analysis.return_value = {
            'total': {'closed': 10},
            'won': {'total': 6},
            'lost': {'total': 4}
        }
        mock_drawdown = MagicMock()
        mock_drawdown.get_analysis.return_value = {'max': {'drawdown': 10}}
        mock_sharpe = MagicMock()
        mock_sharpe.get_analysis.return_value = {'sharperatio': 1.5}

        mock_run_result = MagicMock()
        mock_run_result.analyzers = {
            'tradeanalyzer': mock_analyzer,
            'drawdown': mock_drawdown,
            'sharpe': mock_sharpe
        }
        mock_instance.run.return_value = [mock_run_result]

        result = run_backtest(RsiBollingerBandsStrategy, 'ETH/USD', 10000, 0.001, '2023-06-20', '2023-06-25')

        self.assertEqual(result['total_return'], 0.1)
        self.assertEqual(result['number_of_trades'], 10)
        self.assertEqual(result['winning_trades'], 6)
        self.assertEqual(result['losing_trades'], 4)
        self.assertEqual(result['max_drawdown'], 10)
        self.assertEqual(result['sharpe_ratio'], 1.5)
    @patch('scripts.backtest_runner.fetch_data')
    @patch('backtrader.Cerebro')
    def test_score_backtest(self, mock_cerebro, mock_fetch_data):
        sample_data = pd.DataFrame({
            'date': pd.date_range(start='2023-06-20', periods=5, freq='D'),
            'Open': [1, 2, 3, 4, 5],
            'High': [2, 3, 4, 5, 6],
            'Low': [0.5, 1.5, 2.5, 3.5, 4.5],
            'Close': [1.5, 2.5, 3.5, 4.5, 5.5],
            'Volume': [100, 200, 300, 400, 500]
        })
        mock_fetch_data.return_value = sample_data

        mock_instance = MagicMock()
        mock_cerebro.return_value = mock_instance
        mock_instance.broker.getvalue.return_value = 11000

        # Adjust the structure to return analyzers properly
        mock_analyzer = MagicMock()
        mock_analyzer.get_analysis.return_value = {
            'total': {'closed': 10},
            'won': {'total': 6},
            'lost': {'total': 4}
        }
        mock_drawdown = MagicMock()
        mock_drawdown.get_analysis.return_value = {'max': {'drawdown': 10}}
        mock_sharpe = MagicMock()
        mock_sharpe.get_analysis.return_value = {'sharperatio': 1.5}

        mock_run_result = MagicMock()
        mock_run_result.analyzers = {
            'tradeanalyzer': mock_analyzer,
            'drawdown': mock_drawdown,
            'sharpe': mock_sharpe
        }
        mock_instance.run.return_value = [mock_run_result]

        result = run_backtest(RsiBollingerBandsStrategy, 'ETH/USD', 10000, 0.001, '2023-06-20', '2023-06-25')

        self.assertEqual(result['total_return'], 0.1)
        self.assertEqual(result['number_of_trades'], 10)
        self.assertEqual(result['winning_trades'], 6)
        self.assertEqual(result['losing_trades'], 4)
        self.assertEqual(result['max_drawdown'], 10)
        self.assertEqual(result['sharpe_ratio'], 1.5)

if __name__ == '__main__':
    unittest.main()
