from app.models.backtest import Backtest, Result
from app import db
from app.services.kafka_service import kafka_service
from app.services.mlflow_service import mlflow_service

def run_backtest_by_id(backtest_id):
    backtest = Backtest.query.get(backtest_id)
    if not backtest:
        return

    # Simulate backtest processing
    result = Result(
        backtest_id=backtest_id,
        total_return=10.5,
        number_of_trades=20,
        winning_trades=15,
        losing_trades=5,
        max_drawdown=3.5,
        sharpe_ratio=1.8
    )
    db.session.add(result)
    db.session.commit()

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
    kafka_service.produce('backtest_results', {
        "backtest_id": backtest_id,
        "metrics": metrics
    })
