FROM apache/airflow:2.7.3

# Установите конкретные версии пакетов
RUN pip install --no-cache-dir \
    "psycopg2-binary==2.9.6" \
    "SQLAlchemy<2.0.0" \
    clickhouse-driver \
    clickhouse-sqlalchemy