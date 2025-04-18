FROM apache/airflow:2.8.1

USER root
RUN rm -rf /root/.cache/pip
USER airflow

# Устанавливаем совместимые версии для Airflow 2.8.1
RUN pip install --no-cache-dir \
    "psycopg2-binary==2.9.6" \
    "SQLAlchemy==1.4.46" \
    "clickhouse-driver==0.2.6" \
    "clickhouse-sqlalchemy==0.2.4" \
    "apache-airflow-providers-jdbc==4.5.1" \
    && rm -rf /home/airflow/.cache/pip