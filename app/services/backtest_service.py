from app.models.backtest import Backtest, Result
from app import db
from app.services.kafka_service import kafka_service
from app.services.mlflow_service import mlflow_service
from scripts.backtest_runner import RsiBollingerBandsStrategy, StochasticOscillatorStrategy, MacdStrategy
from scripts.backtest_runner import run_backtest, score_backtest

def run_backtest_by_id(backtest_id):
    backtest = Backtest.query.get(backtest_id)
    print('backtest', backtest.inital_cash)
    if not backtest:
        return
    
   
    run_and_evaluate_backtest(backtest_id=backtest_id, symbol=backtest.symbol, initial_cash=backtest.inital_cash, fee=backtest.fee, start_date=backtest.start_date, end_date = backtest.end_date)


def score_backtest(result, min_return, max_return, min_sharpe, max_sharpe, min_drawdown, max_drawdown):
    weights = {
        'total_return': 0.4,
        'sharpe_ratio': 0.4,
        'max_drawdown': 0.2,
    }
    
    normalized_return = (result['total_return'] - min_return) / (max_return - min_return)
    normalized_sharpe = (result['sharpe_ratio'] - min_sharpe) / (max_sharpe - min_sharpe)
    normalized_drawdown = (max_drawdown - result['max_drawdown']) / (max_drawdown - min_drawdown)
    
    score = (
        weights['total_return'] * normalized_return +
        weights['sharpe_ratio'] * normalized_sharpe +
        weights['max_drawdown'] * normalized_drawdown
    )
    return score

def run_and_evaluate_backtest(backtest_id, symbol, initial_cash, fee, start_date, end_date):
    strategies = [
        RsiBollingerBandsStrategy,
        MacdStrategy,
        StochasticOscillatorStrategy
    ]
    
    results = []
    for strategy in strategies:
        
        print(strategy, symbol, initial_cash, fee, start_date, end_date)
        result = run_backtest(strategy, symbol, initial_cash, fee, start_date, end_date)
        result['backtest_id'] = backtest_id
        if(strategy == RsiBollingerBandsStrategy):
            result['strategy'] = 'RsiBollingerBandsStrategy'
        elif (strategy == MacdStrategy):
            result['strategy'] = 'MacdStrategy'
        elif(strategy == StochasticOscillatorStrategy):
            result['strategy'] = 'StochasticOscillatorStrategy'
        result_obj = Result(**result)
        db.session.add(result_obj)
        
        metrics = {
            "total_return": result['total_return'],
            "number_of_trades": result['number_of_trades'],
            "winning_trades": result['winning_trades'],
            "losing_trades": result['losing_trades'],
            "max_drawdown": result['max_drawdown'],
            "sharpe_ratio": result['sharpe_ratio']
        }
        mlflow_service.log_metrics(run_name=f"Backtest_{backtest_id}", metrics=metrics)
        
        # Uncomment to publish results to Kafka
        # kafka_service.produce('backtest_results', {
        #     "backtest_id": backtest_id,
        #     "metrics": metrics
        # })
        
        db.session.commit()
        results.append(result)
    
    min_return = min(result['total_return'] for result in results)
    max_return = max(result['total_return'] for result in results)
    min_sharpe = min(result['sharpe_ratio'] for result in results)
    max_sharpe = max(result['sharpe_ratio'] for result in results)
    min_drawdown = min(result['max_drawdown'] for result in results)
    max_drawdown = max(result['max_drawdown'] for result in results)
    
    scores = [score_backtest(result, min_return, max_return, min_sharpe, max_sharpe, min_drawdown, max_drawdown) for result in results]
    
    best_strategy_index = scores.index(max(scores))
    best_strategy = strategies[best_strategy_index]
    
    print("Best Strategy:")
    print(best_strategy.__name__)
    print("Score:")
    print(scores[best_strategy_index])
    print("Metrics:")
    print(results[best_strategy_index])
    
    return results

