import mlflow
import mlflow.sklearn

class MLflowService:
    def __init__(self, tracking_uri, experiment_name):
        mlflow.set_tracking_uri(tracking_uri)
        self.experiment_name = experiment_name
        self.experiment_id = self.get_or_create_experiment_id(experiment_name)

    def get_or_create_experiment_id(self, experiment_name):
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
        else:
            experiment_id = experiment.experiment_id
        return experiment_id

    def log_metrics(self, run_name, metrics):
        with mlflow.start_run(experiment_id=self.experiment_id, run_name=run_name):
            for key, value in metrics.items():
                print(key, value)
                mlflow.log_metric(key, value)

# Initialize the MLflowService with the desired experiment name
mlflow_service = MLflowService(tracking_uri='http://localhost:5050', experiment_name='Backtest_Results')
