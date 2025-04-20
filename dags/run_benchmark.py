from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_execution_time(response):
    """Извлекаем время выполнения из ответа ClickHouse"""
    try:
        return json.loads(response.text).get('elapsed', 0)
    except:
        return 0

with DAG(
    'run_benchmark',
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    wait_for_data = ExternalTaskSensor(
        task_id='wait_for_data',
        external_dag_id='generate_test_data',
        external_task_id='insert_ch_data',
        mode='reschedule',
        timeout=3600,
    )

    # 1. Запрос к PostgreSQL с замером времени
    pg_aggregation = PostgresOperator(
        task_id='pg_aggregation',
        postgres_conn_id='postgres_data_conn',
        sql="""
        EXPLAIN ANALYZE
        SELECT 
            region_id, 
            COUNT(*) as users_count,
            AVG(group_id) as avg_group
        FROM users
        GROUP BY region_id
        ORDER BY users_count DESC;
        """,
        do_xcom_push=True
    )

    # 2. Запрос к ClickHouse с замером времени
    ch_aggregation = SimpleHttpOperator(
        task_id='ch_aggregation',
        method='POST',
        endpoint='',
        data=json.dumps({
            "query": """
                SELECT 
                    region_id, 
                    COUNT(*) as users_count,
                    AVG(group_id) as avg_group,
                    toString(elapsed()) as execution_time
                FROM users
                GROUP BY region_id
                ORDER BY users_count DESC;
            """,
            "with_column_types": True
        }),
        headers={"Content-Type": "application/json"},
        http_conn_id='clickhouse_http',
        response_filter=lambda response: response.json(),
        do_xcom_push=True
    )

    @task
    def log_execution_time(**context):
        ti = context['ti']
        
        # Получаем время выполнения PostgreSQL
        pg_explain = ti.xcom_pull(task_ids='pg_aggregation')
        pg_time = float(pg_explain[0][0].split('actual time=')[1].split('..')[1].split(' ')[0])
        
        # Получаем время выполнения ClickHouse
        ch_result = ti.xcom_pull(task_ids='ch_aggregation')
        ch_time = float(ch_result['data'][0][3])  # execution_time из 4-го столбца
        
        log_msg = f"""
        ⏱️ Benchmark Results:
        PostgreSQL execution time: {pg_time:.3f} seconds
        ClickHouse execution time: {ch_time:.3f} seconds
        Difference: {pg_time/ch_time:.1f}x faster
        """
        print(log_msg)
        return log_msg

    # Порядок выполнения
    wait_for_data >> [pg_aggregation, ch_aggregation] >> log_execution_time()