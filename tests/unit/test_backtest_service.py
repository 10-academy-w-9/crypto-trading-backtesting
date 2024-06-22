import unittest
from app.services.backtest_service import BacktestService

class TestBacktestService(unittest.TestCase):
    def test_execute_backtest(self):
        result = BacktestService.execute_backtest('BTC/USDT', '2023-06-20', '2024-06-20')
        self.assertIn('Ending Portfolio Value', result)

if __name__ == '__main__':
    unittest.main()
