import json
import pytest
from flask import Flask
from flask_testing import TestCase
from app import create_app, db
from app.models.backtest import Indicator, Backtest, Parameter, Result

class BacktestTestCase(TestCase):
    def create_app(self):
        app = create_app('testing')  # Assume you have a testing config
        return app

    def setUp(self):
        db.create_all()
        # Add sample indicators
        indicator1 = Indicator(name='Indicator 1', description='Description 1')
        indicator2 = Indicator(name='Indicator 2', description='Description 2')
        db.session.add(indicator1)
        db.session.add(indicator2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_run_backtest(self):
        with open('backtest_request.json') as f:
            data = json.load(f)

        response = self.client.post('/backtest', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('backtest_id', response.json)

if __name__ == '__main__':
    pytest.main()
