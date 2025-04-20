from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.base import BaseHook
from clickhouse_driver import Client
from datetime import datetime, timedelta
import json

# Параметры генерации
ROWS_COUNT = 1_000_000  # 1 млн строк
CHUNK_SIZE = 100_000    # Размер пачки для вставки

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def generate_fake_data(rows, offset=0):
    """Генерация данных для вставки."""
    return [
        (i + offset, f"user_{i + offset}", f"user_{i + offset}@example.com", datetime.now(), i % 100, i % 10)
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
            connect_timeout=10  # Таймаут подключения
        )
        # Проверяем подключение
        client.execute('SELECT 1')
        return client
    except Exception as e:
        print(f"ClickHouse connection error: {str(e)}")
        raise

def create_clickhouse_tables():
    """Создание таблиц в ClickHouse"""
    try:
        client = get_clickhouse_client()
        # Сначала создаем таблицу (если не существует)
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
        
        # Затем очищаем таблицу отдельным запросом
        client.execute("TRUNCATE TABLE users")
        
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        raise

def insert_clickhouse_data(**context):
    """Вставка тестовых данных в ClickHouse"""
    ti = context['ti']
    for i in range(ROWS_COUNT // CHUNK_SIZE):
        data = generate_fake_data(CHUNK_SIZE, offset=i * CHUNK_SIZE)
        client = get_clickhouse_client()
        client.execute("INSERT INTO users VALUES", data)

with DAG(
    'generate_test_data',
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    # 1. Создаём таблицы в PostgreSQL
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

    # 2. Создаём таблицы в ClickHouse
    create_ch_tables = PythonOperator(
        task_id='create_ch_tables',
        python_callable=create_clickhouse_tables
    )

    # 3. Вставляем данные в PostgreSQL (пачками)
    insert_pg_data = PythonOperator(
    task_id='insert_pg_data',
    python_callable=lambda: [
        PostgresOperator(
            task_id=f'insert_pg_data_{i}',
            postgres_conn_id='postgres_data_conn',
            sql=f"""
            INSERT INTO users (id, username, email, created_at, group_id, region_id)
            VALUES {','.join(['%s'] * CHUNK_SIZE)};
            """,
            parameters=generate_fake_data(CHUNK_SIZE, offset=i * CHUNK_SIZE),
        ).execute(None)
        for i in range(ROWS_COUNT // CHUNK_SIZE)
    ],
    )

    # 4. Вставляем данные в ClickHouse (пачками)
    insert_ch_data = PythonOperator(
        task_id='insert_ch_data',
        python_callable=insert_clickhouse_data,
        provide_context=True
    )

    create_pg_tables >> create_ch_tables >> [insert_pg_data, insert_ch_data]