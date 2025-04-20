from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG("test_postgres", start_date=datetime(2023, 1, 1)) as dag:
    test_query = PostgresOperator(
        task_id="test_query",
        postgres_conn_id="postgres_data_conn",
        sql="SELECT 1;"
    )