from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from app.services.backtest_service import run_backtest_by_id

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'backtest_dag',
    default_args=default_args,
    description='DAG for running backtests',
    schedule_interval=timedelta(days=1),
)

def run_backtest(task_id, *args, **kwargs):
    run_backtest_by_id(task_id)

run_backtest_task = PythonOperator(
    task_id='run_backtest',
    python_callable=run_backtest,
    op_args=['{{ task_instance.task_id }}'],
    dag=dag,
)
