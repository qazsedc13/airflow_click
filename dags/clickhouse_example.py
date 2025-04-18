from airflow import DAG
from airflow.operators.python import PythonOperator
from clickhouse_driver import Client
from datetime import datetime

def execute_clickhouse_query(sql, **kwargs):
    """
    Выполняет запрос к ClickHouse и возвращает результат, 
    преобразованный в сериализуемые типы данных.
    """
    conn = Client(
        host='clickhouse',
        user='airflow',
        password='airflow',
        database='airflow'
    )
    result = conn.execute(sql)
    
    # Преобразуем все элементы в строки для сериализации
    serializable_result = []
    for row in result:
        serializable_row = []
        for value in row:
            # Преобразуем UUID и другие несериализуемые объекты
            if hasattr(value, '__str__'):
                serializable_row.append(str(value))
            else:
                serializable_row.append(value)
        serializable_result.append(serializable_row)
    
    return serializable_result

with DAG(
    'clickhouse_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    tags=['clickhouse'],
    default_args={
        'retries': 1,
    }
) as dag:

    create_table = PythonOperator(
        task_id='create_table',
        python_callable=execute_clickhouse_query,
        op_kwargs={
            'sql': '''
                CREATE TABLE IF NOT EXISTS test (
                    id Int32,
                    data String,
                    created_at DateTime DEFAULT now()
                ) ENGINE = MergeTree()
                ORDER BY (id, created_at)
            '''
        }
    )

    insert_data = PythonOperator(
        task_id='insert_data',
        python_callable=execute_clickhouse_query,
        op_kwargs={
            'sql': '''
                INSERT INTO test (id, data) VALUES
                (1, 'Пример данных 1'),
                (2, 'Пример данных 2')
            '''
        }
    )

    select_example = PythonOperator(
        task_id='select_example',
        python_callable=execute_clickhouse_query,
        op_kwargs={
            'sql': '''
                SELECT 
                    d.name as database_name,
                    t.name as table_name,
                    t.uuid as table_uuid
                FROM system.databases d
                JOIN system.tables t ON d.name = t.database
                WHERE d.name = 'airflow'
            '''
        }
    )

    create_table >> insert_data >> select_example