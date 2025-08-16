markdown
# Airflow + ClickHouse + Superset в Docker

Комплексная установка Apache Airflow с интеграцией ClickHouse и Apache Superset в Docker-окружении

## 📋 Предварительные требования

- Docker Engine 20.10+ (версия с поддержкой Compose V2)
- Docker Compose 2.0+
- 4GB+ свободной оперативной памяти (8GB+ рекомендуется)
- WSL2 (для Windows пользователей)

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone git@github.com:qazsedc13/airflow_click.git
cd airflow_click
```
### 2. Инициализация окружения
<!-- Создаем необходимые директории -->
```bash
mkdir -p ./dags ./logs ./plugins ./superset
chmod -R 777 ./logs  # Только для разработки!
```
### 3. Первый запуск сервисов после клонирования репозитория
```bash
docker compose build --no-cache && docker compose up -d
```
### 4. Первый запуск сервисов
```bash
docker compose up -d --build
```
### 5. Доступ к интерфейсам
- Airflow: http://localhost:8080 (admin/admin)
- Superset: http://localhost:8088 (admin/admin)
- ClickHouse HTTP: http://localhost:8123

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
# Логи Airflow
docker compose logs -f airflow-webserver
docker compose logs -f airflow-scheduler

# Логи Superset
docker compose logs -f superset

# Логи ClickHouse
docker compose logs -f clickhouse
```
## 🔌 Основные сервисы
| Сервис              | Порт    | Описание                          |
|---------------------|---------|-----------------------------------|
| Airflow Webserver   | 8080    | Веб-интерфейс и REST API          |
| Airflow Scheduler   | -       | Обработка DAG и планирование задач|
| Superset            | 8088    | BI-панели и визуализации          |
| PostgreSQL          | 5432    | Метаданные Airflow и Superset     |
| ClickHouse (HTTP)   | 8123    | HTTP-интерфейс                    |
| ClickHouse (Native) | 9000    | Нативный протокол                 |
## 📊 Работа с Superset
### Начальная настройка

1. После первого запуска автоматически:
   - Создается admin-пользователь (`admin/admin`)
   - Настраивается подключение к ClickHouse
   - Импортируются базовые роли и разрешения

2. Для ручного добавления источника данных:
   - Перейдите в **Data** → **Databases**
   - Добавьте новое подключение:

     ```
     clickhouse://airflow:airflow@clickhouse:8123/airflow
     ```

### Примеры дашбордов

Поместите файлы конфигураций дашбордов в `./superset/dashboards/`

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
### Переменные окружения

Основные настройки в **docker-compose.yml**:

- `SUPERSET_SECRET_KEY`: Ключ безопасности Superset  
- `CLICKHOUSE_*`: Учетные данные ClickHouse  
- `AIRFLOW_*`: Настройки Airflow  

### Установка дополнительных пакетов

Для Superset добавьте в **superset/Dockerfile**:

```dockerfile
RUN pip install <ваш-пакет>
```
Для Airflow - в основной Dockerfile

и пересоберите контейнеры.

## 🏭 Продуктивная среда
Для production рекомендуется:

Заменить LocalExecutor на CeleryExecutor

Настроить правильные права доступа (не использовать 777)

Включить аутентификацию

Настроить SSL-шифрование

Реализовать ротацию логов
