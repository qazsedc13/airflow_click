# Airflow + ClickHouse Integration in Docker (Main)

![License](https://img.shields.io/github/license/qazsedc13/airflow_click)
![Airflow Version](https://img.shields.io/badge/Airflow-2.8.1-blue)
![ClickHouse Version](https://img.shields.io/badge/ClickHouse-latest-green)
![Docker](https://img.shields.io/badge/Docker-Compose-green)

Данный проект представляет собой легковесную и готовую к работе инфраструктуру для оркестрации задач обработки данных с использованием Apache Airflow и аналитической СУБД ClickHouse. Основная цель репозитория — предоставить надежный шаблон для разработки ETL-процессов, взаимодействующих с высокопроизводительными хранилищами.

---

##  Основные возможности

- **Оркестрация**: Управление рабочими процессами через Apache Airflow с использованием `LocalExecutor`.
- **Высокая производительность**: Интеграция с ClickHouse для быстрой обработки аналитических запросов.
- **Автоматизация**: Автоматическое создание соединений (Connections) в Airflow при запуске контейнеров.
- **Контейнеризация**: Полная изоляция сервисов через Docker, что гарантирует идентичность среды разработки и запуска.

---

##  Технологический стек

- **Apache Airflow 2.8.1**: Использование `LocalExecutor` для параллельного выполнения задач.
- **ClickHouse latest**: Основное аналитическое хранилище.
- **PostgreSQL 13**: База данных для хранения метаданных Airflow.
- **Python 3.11**: Базовая среда исполнения внутри контейнеров Airflow.

### Ключевые зависимости (Python)
- `psycopg2-binary==2.9.6`
- `SQLAlchemy==1.4.46`
- `clickhouse-driver==0.2.6`
- `clickhouse-sqlalchemy==0.2.4`
- `apache-airflow-providers-jdbc==4.5.1`

---

##  Предварительные требования

- **Docker Engine**: 20.10+
- **Docker Compose**: 2.0+
- **RAM**: Минимум 2GB свободного объема (рекомендуется 4GB).
- **ОС**: Любая ОС с поддержкой Docker (Linux, macOS, Windows с WSL2).

---

##  Установка и запуск

### 1. Клонирование репозитория
```bash
git clone git@github.com:qazsedc13/airflow_click.git
cd airflow_click
```

### 2. Сборка и запуск
Выполните сборку кастомного образа Airflow и запуск всех сервисов:
```bash
docker compose up -d --build
```

### 3. Доступ к интерфейсам
| Сервис | URL | Логин / Пароль |
| :--- | :--- | :--- |
| **Airflow Webserver** | [http://localhost:8080](http://localhost:8080) | `admin` / `admin` |
| **ClickHouse HTTP** | [http://localhost:8123](http://localhost:8123) | `airflow` / `airflow` |

---

##  Работа с проектом

### Пример DAG
В репозитории предустановлен демонстрационный DAG `clickhouse_example`, который выполняет:
1. Создание таблицы в ClickHouse с использованием движка `MergeTree`.
2. Вставку тестовых данных.
3. Выполнение JOIN-запроса к системным таблицам ClickHouse для проверки метаданных.

### Настройка соединений
При запуске контейнера `airflow-webserver` автоматически выполняется команда инициализации соединения `clickhouse_conn`. Если вам нужно добавить другие соединения вручную, используйте интерфейс Airflow (Admin -> Connections) или CLI:
```bash
docker compose exec airflow-webserver airflow connections add --conn-uri 'clickhouse://user:pass@host:8123/db' my_conn
```

---

##  Управление инфраструктурой

**Остановка сервисов:**
```bash
docker compose down
```

**Просмотр логов:**
```bash
docker compose logs -f airflow-webserver  # Веб-интерфейс Airflow
docker compose logs -f clickhouse         # Логи ClickHouse
```

**Очистка данных:**
```bash
docker compose down -v  # Удалит все тома (Postgres и ClickHouse)
```

---

##  Устранение неполадок

**Ошибка подключения к ClickHouse:**
Проверьте доступность порта и корректность учетных данных:
```bash
docker compose exec clickhouse clickhouse-client --user airflow --password airflow --query "SELECT 1"
```

**Airflow не видит новые DAG:**
Убедитесь, что файлы находятся в папке `./dags` и не содержат синтаксических ошибок. Проверить ошибки парсинга можно в UI Airflow или через логи планировщика.

---

##  Лицензия

Проект распространяется под лицензией **MIT**.

---

##  Контакты

- **Автор**: [qazsedc13](https://github.com/qazsedc13)
- **Репозиторий**: [airflow_click](https://github.com/qazsedc13/airflow_click)
