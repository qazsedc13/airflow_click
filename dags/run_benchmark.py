from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.base import BaseHook
from clickhouse_driver import Client
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_clickhouse_client():
    """Получаем параметры подключения из Airflow Connection"""
    conn = BaseHook.get_connection('clickhouse_conn')
    
    try:
        client = Client(
            host=conn.host,
            port=9000,
            user=conn.login,
            password=conn.password,
            database=conn.schema or 'default',
            secure=False,
            connect_timeout=10,
            settings={'use_numpy': False}  # Отключаем numpy для совместимости
        )
        client.execute('SELECT 1')  # Проверка подключения
        return client
    except Exception as e:
        logging.error(f"ClickHouse connection error: {str(e)}")
        raise

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
    @task(task_id='ch_aggregation')
    def ch_aggregation():
        client = get_clickhouse_client()
        
        # Вариант 1: Используем SYSTEM FLUSH LOGS и query_log
        # (требует прав администратора и включенного query_log)
        # client.execute("SYSTEM FLUSH LOGS")
        # result = client.execute("""
        #     SELECT 
        #         region_id, 
        #         COUNT(*) as users_count,
        #         AVG(group_id) as avg_group
        #     FROM users
        #     GROUP BY region_id
        #     ORDER BY users_count DESC;
        # """)
        # query_time = client.execute("""
        #     SELECT query_duration_ms / 1000
        #     FROM system.query_log
        #     WHERE type = 'QueryFinish'
        #     ORDER BY event_time DESC
        #     LIMIT 1
        # """)[0][0]
        
        # Вариант 2: Измеряем время выполнения на стороне Python
        import time
        start_time = time.time()
        result = client.execute("""
            SELECT 
                region_id, 
                COUNT(*) as users_count,
                AVG(group_id) as avg_group
            FROM users
            GROUP BY region_id
            ORDER BY users_count DESC;
        """)
        execution_time = time.time() - start_time
        
        # Возвращаем и результат запроса, и время выполнения
        return {
            "result": result,
            "execution_time": execution_time
        }

    @task(task_id='log_execution_time')
    def log_execution_time(**context):
        ti = context['ti']
        
        # Получаем время выполнения PostgreSQL
        pg_explain = ti.xcom_pull(task_ids='pg_aggregation')
        pg_time = float(pg_explain[0][0].split('actual time=')[1].split('..')[1].split(' ')[0])
        
        # Получаем время выполнения ClickHouse
        ch_data = ti.xcom_pull(task_ids='ch_aggregation')
        ch_time = ch_data['execution_time']
        
        log_msg = f"""
        ⏱️ Benchmark Results:
        PostgreSQL execution time: {pg_time:.3f} seconds
        ClickHouse execution time: {ch_time:.3f} seconds
        Difference: {pg_time/ch_time:.1f}x faster
        """
        print(log_msg)
        return log_msg

    # Порядок выполнения
    ch_aggregation_task = ch_aggregation()
    log_execution_time_task = log_execution_time()

    pg_aggregation >> log_execution_time_task
    ch_aggregation_task >> log_execution_time_task
