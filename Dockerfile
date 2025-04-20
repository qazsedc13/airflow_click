FROM apache/airflow:2.8.1

USER root
RUN rm -rf /root/.cache/pip

# Установка дополнительных инструментов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        libsasl2-dev \
        libldap2-dev && \
    rm -rf /var/lib/apt/lists/*

USER airflow

# Устанавливаем только нужные для Airflow пакеты
RUN pip install --no-cache-dir \
    "psycopg2-binary==2.9.6" \
    "SQLAlchemy==1.4.46" \
    "clickhouse-driver==0.2.6" \
    "clickhouse-sqlalchemy==0.2.4" \
    "apache-airflow-providers-jdbc==4.5.1" \
    "tqdm" \
    && rm -rf /home/airflow/.cache/pip