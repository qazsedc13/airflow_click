FROM apache/superset:3.0.1

USER root

# Установка зависимостей для ClickHouse
RUN pip install --no-cache-dir \
    sqlalchemy==1.4.52 \
    clickhouse-driver==0.2.6 \
    clickhouse-sqlalchemy==0.2.4 \
    psycopg2-binary==2.9.6

# Очистка кеша
RUN rm -rf /root/.cache/pip

USER superset