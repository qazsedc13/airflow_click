from airflow import DAG
from airflow.providers.clickhouse.operators.clickhouse import ClickHouseOperator
from datetime import datetime

with DAG(
    'clickhouse_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
) as dag:

    create_table = ClickHouseOperator(
        task_id='create_table',
        sql='''
            CREATE TABLE IF NOT EXISTS airflow.test (
                id Int32,
                data String
            ) ENGINE = MergeTree()
            ORDER BY id
        ''',
        clickhouse_conn_id='clickhouse_conn'
    )

    select_example = ClickHouseOperator(
        task_id='select_example',
        sql='''
            SELECT * FROM system.databases
        ''',
        clickhouse_conn_id='clickhouse_conn'
    )