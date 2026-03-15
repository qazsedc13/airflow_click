# Airflow ClickHouse Integration

Проект для демонстрации интеграции Apache Airflow с аналитической СУБД ClickHouse.

## Описание
Этот проект содержит настроенную среду для оркестрации задач, взаимодействующих с ClickHouse. Включает в себя кастомный Docker-образ Airflow с предустановленным драйвером для ClickHouse и пример DAG, который создает таблицы, вставляет данные и выполняет запросы к системным таблицам ClickHouse.

## Технологический стек
- **Оркестрация:** Apache Airflow (LocalExecutor)
- **СУБД:** ClickHouse, PostgreSQL 13 (метаданные Airflow)
- **Контейнеризация:** Docker, Docker Compose
- **Язык программирования:** Python
- **Библиотеки Python:** `clickhouse-driver`

## Установка и запуск

1. Убедитесь, что у вас установлены **Docker** и **Docker Compose**.
2. Склонируйте репозиторий:
   ```bash
   git clone git@github.com:qazsedc13/airflow_click.git
   ```
   И перейдите в папку проекта.
3. Соберите и запустите контейнеры:
   ```bash
   docker-compose up --build -d
   ```
4. Airflow будет доступен по адресу: [http://localhost:8080](http://localhost:8080)
   - Логин: `admin`
   - Пароль: `admin`

## Примеры использования
В Airflow UI активируйте и запустите DAG `clickhouse_example`. Он выполнит следующие шаги:
1. `create_table`: Создает таблицу `test` в ClickHouse с движком `MergeTree`.
2. `insert_data`: Вставляет тестовые записи в таблицу.
3. `select_example`: Выполняет JOIN-запрос к системным таблицам ClickHouse (`system.databases` и `system.tables`) для получения информации о созданных таблицах.

## Структура проекта
- `dags/` — содержит `clickhouse_example.py` с логикой взаимодействия с БД.
- `Dockerfile` — кастомный образ на базе Airflow с установкой необходимых зависимостей.
- `docker-compose.yml` — конфигурация сервисов: Airflow Webserver, Scheduler, PostgreSQL и ClickHouse Server.
- `.gitignore` — исключение временных файлов из контроля версий.

## Зависимости и требования
- Docker Engine 20.10.0+
- Минимум 2 ГБ выделенной памяти для контейнера ClickHouse.
- Соединение с ClickHouse настраивается через переменные окружения в `docker-compose.yml`.
