markdown
# Airflow + ClickHouse в Docker

<!-- Основной заголовок проекта -->
Комплексная установка Apache Airflow с интеграцией ClickHouse в Docker-окружении

## 📋 Предварительные требования

<!-- Требования к системе -->
- Docker Engine 20.10+ (версия с поддержкой Compose V2)
- Docker Compose 2.0+
- 4GB+ свободной оперативной памяти
- WSL2 (для Windows пользователей)

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone git@github.com:qazsedc13/airflow_click.git
cd airflow-clickhouse-docker
```
### 2. Инициализация окружения
<!-- Создаем необходимые директории -->
```bash
mkdir -p ./dags ./logs ./plugins
chmod -R 777 ./logs  # Только для разработки!
```
### 3. Запуск сервисов
```bash
docker compose up -d --build
```
### 4. Доступ к Airflow
Откройте в браузере:
http://localhost:8080
Логин/пароль по умолчанию: admin / admin

## 🛠 Управление сервисами
Старт всех сервисов
```bash
docker compose up -d
```
Остановка всех сервисов
```bash
docker compose down
```
Полный перезапуск (с очисткой)
```bash
docker compose down -v  # Удаляет тома с данными
docker compose up -d --build
```
Проверка статуса
```bash
docker compose ps
```
Просмотр логов
```bash
# Логи Airflow webserver
docker compose logs -f airflow-webserver

# Логи планировщика
docker compose logs -f airflow-scheduler

# Логи ClickHouse
docker compose logs -f clickhouse
```
## 🔌 Основные сервисы
| Сервис              | Порт    | Описание                          |
|---------------------|---------|-----------------------------------|
| Airflow Webserver   | 8080    | Веб-интерфейс и REST API          |
| Airflow Scheduler   | -       | Обработка DAG и планирование задач|
| PostgreSQL          | 5432    | Метаданные Airflow                |
| ClickHouse (HTTP)   | 8123    | HTTP-интерфейс                    |
| ClickHouse (Native) | 9000    | Нативный протокол                 |
## 📂 Работа с DAG
Поместите ваши DAG-файлы в папку ./dags

DAG появятся в интерфейсе Airflow через 1-5 минут

Для принудительного обновления:

```bash
docker compose exec airflow-webserver airflow dags reserialize
```
## ⚠️ Частые проблемы
DAG не появляются
Проверьте логи scheduler:

```bash
docker compose logs airflow-scheduler | grep -i "dag"
```
Убедитесь, что файлы имеют расширение .py

Проверьте синтаксис:

```bash
docker compose exec airflow-webserver python /opt/airflow/dags/ваш_dag.py
```
Проблемы с подключениями
Проверьте список подключений:

```bash
docker compose exec airflow-webserver airflow connections list
```
Тест подключения к ClickHouse
```bash
docker compose exec clickhouse clickhouse-client --user airflow --password airflow --query "SHOW DATABASES"
```
## ⚙️ Конфигурация
Переменные окружения
Основные настройки в docker compose.yml:

AIRFLOW__CORE__EXECUTOR: Исполняющая система (LocalExecutor/CeleryExecutor)

AIRFLOW_CONN_*: Настройки подключений

CLICKHOUSE_*: Учетные данные ClickHouse

Установка дополнительных пакетов
Добавьте в Dockerfile:

```dockerfile
RUN pip install <ваш-пакет>
```
и пересоберите контейнеры.

## 🏭 Продуктивная среда
Для production рекомендуется:

Заменить LocalExecutor на CeleryExecutor

Настроить правильные права доступа (не использовать 777)

Включить аутентификацию

Настроить SSL-шифрование

Реализовать ротацию логов
