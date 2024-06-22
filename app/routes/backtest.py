from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.backtest_runner import run_backtest, RsiBollingerBandsStrategy
app = Flask(__name__)

@app.route('/backtest', methods=['GET','POST'])
def backtest():
    data = request.get_json()
    symbol = data['symbol']
    start_date = data['start_date']
    end_date = data['end_date']
    strategy_name = data['strategy']
    
    strategies = {
        'rsi_bollinger': RsiBollingerBandsStrategy
    }
    
    strategy = strategies.get(strategy_name.lower())
    if not strategy:
        return jsonify({'error': 'Invalid strategy name'}), 400
    
    try:
        stats = run_backtest(strategy, symbol, start_date, end_date)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# def backtest():
#     return 'Backtest endpoint accessed successfully'

if __name__ == '__main__':
    app.run(debug=True)
