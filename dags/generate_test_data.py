from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.base import BaseHook
from clickhouse_driver import Client
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from tqdm import tqdm
import logging

# Параметры
ROWS_COUNT = 10_000_000
CHUNK_SIZE = 100_000

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def generate_fake_data(rows, offset=0):
    """Генерация данных для вставки."""
    return [
        (i + offset, f"user_{i + offset}", f"user_{i + offset}@example.com", 
         datetime.now(), i % 100, i % 10)
        for i in range(rows)
    ]

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

def create_clickhouse_tables():
    """Создание таблиц в ClickHouse"""
    try:
        client = get_clickhouse_client()
        client.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id Int32,
            username String,
            email String,
            created_at DateTime,
            group_id Int32,
            region_id Int32
        ) ENGINE = MergeTree()
        ORDER BY (id)
        """)
        client.execute("TRUNCATE TABLE users")
    except Exception as e:
        logging.error(f"Error creating ClickHouse tables: {str(e)}")
        raise

def insert_pg_data():
    """Вставка данных в PostgreSQL"""
    try:
        hook = PostgresHook(postgres_conn_id='postgres_data_conn')
        conn = hook.get_conn()
        cursor = conn.cursor()
        
        for i in tqdm(range(0, ROWS_COUNT, CHUNK_SIZE), desc="PostgreSQL Insert"):
            data = generate_fake_data(CHUNK_SIZE, offset=i)
            values = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s,%s)", row).decode('utf-8') 
                      for row in data)
            cursor.execute(f"""
                INSERT INTO users (id, username, email, created_at, group_id, region_id)
                VALUES {values}
            """)
            conn.commit()
            
    except Exception as e:
        logging.error(f"PostgreSQL Error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def insert_clickhouse_data(**context):
    """Вставка данных в ClickHouse"""
    try:
        client = get_clickhouse_client()
        
        for i in tqdm(range(0, ROWS_COUNT, CHUNK_SIZE), desc="ClickHouse Insert"):
            data = generate_fake_data(CHUNK_SIZE, offset=i)
            client.execute(
                "INSERT INTO users VALUES",
                data,
                types_check=True,
                settings={
                    'max_insert_block_size': 100000,
                    'async_insert': 1,
                    'wait_for_async_insert': 0
                }
            )
            
    except Exception as e:
        logging.error(f"ClickHouse Error: {str(e)}")
        raise

def verify_results():
    """Проверка количества записей в обеих БД"""
    try:
        # Проверка PostgreSQL
        pg_hook = PostgresHook(postgres_conn_id='postgres_data_conn')
        pg_count = pg_hook.get_first("SELECT COUNT(*) FROM users")[0]
        
        # Проверка ClickHouse
        ch_client = get_clickhouse_client()
        ch_count = ch_client.execute("SELECT COUNT(*) FROM users")[0][0]
        
        logging.info(f"PostgreSQL rows: {pg_count}, ClickHouse rows: {ch_count}")
        
        if pg_count != ROWS_COUNT or ch_count != ROWS_COUNT:
            raise ValueError(f"Data count mismatch! Expected: {ROWS_COUNT}, PG: {pg_count}, CH: {ch_count}")
            
    except Exception as e:
        logging.error(f"Verification failed: {str(e)}")
        raise

with DAG(
    'generate_test_data',
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:

    create_pg_tables = PostgresOperator(
        task_id='create_pg_tables',
        postgres_conn_id='postgres_data_conn',
        sql="""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            username TEXT,
            email TEXT,
            created_at TIMESTAMP,
            group_id INT,
            region_id INT
        );
        TRUNCATE TABLE users;
        """
    )

    create_ch_tables = PythonOperator(
        task_id='create_ch_tables',
        python_callable=create_clickhouse_tables
    )

    insert_pg_data_task = PythonOperator(
        task_id='insert_pg_data',
        python_callable=insert_pg_data
    )

    insert_ch_data_task = PythonOperator(
        task_id='insert_ch_data',
        python_callable=insert_clickhouse_data
    )

    verify_task = PythonOperator(
        task_id='verify_results',
        python_callable=verify_results,
        trigger_rule='all_done'
    )

    create_pg_tables >> create_ch_tables >> [insert_pg_data_task, insert_ch_data_task] >> verify_task