import mlflow
import mlflow.sklearn

class MLflowService:
    def __init__(self, tracking_uri):
        mlflow.set_tracking_uri(tracking_uri)

    def log_metrics(self, run_name, metrics):
        with mlflow.start_run(run_name=run_name):
            for key, value in metrics.items():
                mlflow.log_metric(key, value)

mlflow_service = MLflowService(tracking_uri='http://localhost:5000')
