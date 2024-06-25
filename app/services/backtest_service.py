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
    # for res in results:
    #     result = Result(**res) 
    #     db.session.add(result)
    #     # Log metrics to MLflow
    #     metrics = {
    #         "total_return": res.total_return,
    #         "number_of_trades": res.number_of_trades,
    #         "winning_trades": res.winning_trades,
    #         "losing_trades": res.losing_trades,
    #         "max_drawdown": res.max_drawdown,
    #         "sharpe_ratio": res.sharpe_ratio
    #     }
    #     mlflow_service.log_metrics(run_name=f"Backtest_{backtest_id}", metrics=metrics)

        # Publish result to Kafka
        # kafka_service.produce('backtest_results', {
        #     "backtest_id": backtest_id,
        #     "metrics": metrics
        # })
    # db.session.commit()



def run_and_evaluate_backtest(backtest_id, symbol, initial_cash, fee, start_date, end_date):
    strategies = [
        RsiBollingerBandsStrategy,
        MacdStrategy,
        StochasticOscillatorStrategy
    ]
    
    results = []
    for strategy in strategies:
        result = run_backtest(strategy, symbol, initial_cash, fee, start_date, end_date)
        result.backtest_id = backtest_id
        result = Result(**result) 
        db.session.add(result)
        
        # Log metrics to MLflow
        metrics = {
            "total_return": result.total_return,
            "number_of_trades": result.number_of_trades,
            "winning_trades": result.winning_trades,
            "losing_trades": result.losing_trades,
            "max_drawdown": result.max_drawdown,
            "sharpe_ratio": result.sharpe_ratio
        }
        mlflow_service.log_metrics(run_name=f"Backtest_{backtest_id}", metrics=metrics)

        # Publish result to Kafka
        # kafka_service.produce('backtest_results', {
        #     "backtest_id": backtest_id,
        #     "metrics": metrics
        # })
        db.session.commit()

        results.append(result)
    
    # Determine the min and max values for normalization
    min_return = min(result['total_return'] for result in results)
    max_return = max(result['total_return'] for result in results)
    min_sharpe = min(result['sharpe_ratio'] for result in results)
    max_sharpe = max(result['sharpe_ratio'] for result in results)
    min_drawdown = min(result['max_drawdown'] for result in results)
    max_drawdown = max(result['max_drawdown'] for result in results)
    
    # Score each strategy
    scores = [score_backtest(result) for result in results]
    
    # Select the best strategy
    best_strategy_index = scores.index(max(scores))
    best_strategy = strategies[best_strategy_index]
    
    print("Best Strategy:")
    print(best_strategy.__name__)
    print("Score:")
    print(scores[best_strategy_index])
    print("Metrics:")
    print(results[best_strategy_index])
    return results