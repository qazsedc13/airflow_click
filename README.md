# Airflow + ClickHouse + Superset in Docker (Superset Edition)

![License](https://img.shields.io/github/license/qazsedc13/airflow_click)
![Airflow Version](https://img.shields.io/badge/Airflow-2.8.1-blue)
![Superset Version](https://img.shields.io/badge/Superset-latest-red)
![ClickHouse Version](https://img.shields.io/badge/ClickHouse-latest-green)
![Docker](https://img.shields.io/badge/Docker-Compose-green)

Данная ветка проекта реализует полноценную BI-платформу, интегрирующую инструменты оркестрации (Airflow), высокопроизводительного хранения (ClickHouse) и визуализации данных (Superset). Решение идеально подходит для создания сквозных аналитических конвейеров: от сбора данных до построения интерактивных дашбордов.

---

##  Основные возможности

- **Сквозная аналитика**: Полный цикл обработки данных — сбор, трансформация (ETL) и визуализация.
- **Интеграция Superset**: Предустановленная и настроенная BI-платформа с поддержкой ClickHouse.
- **Оркестрация**: Автоматизация задач через Apache Airflow с использованием `LocalExecutor`.
- **OLAP хранилище**: Использование ClickHouse для мгновенного выполнения агрегационных запросов на больших объемах данных.
- **Автоматическая инициализация**: Сервис `superset-init` автоматически настраивает учетные данные администратора и базовые подключения.

---

##  Технологический стек

- **Apache Airflow 2.8.1**: Оркестратор задач.
- **Apache Superset**: Платформа для бизнес-аналитики и визуализации.
- **ClickHouse latest**: Аналитическая СУБД.
- **PostgreSQL 13**: База данных для метаданных Airflow.
- **Python 3.11**: Среда исполнения для DAG и кастомных образов.

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
- **RAM**: Минимум 4GB свободного объема (рекомендуется 8GB для комфортной работы Superset).
- **ОС**: Linux, macOS или Windows с WSL2.

---

##  Установка и запуск

### 1. Клонирование и переход в ветку
```bash
git clone git@github.com:qazsedc13/airflow_click.git
cd airflow_click
git checkout Arflow_clickhous_superset
```

### 2. Сборка и запуск
Запустите все сервисы (Airflow, ClickHouse, Superset):
```bash
docker compose up -d --build
```

### 3. Доступ к интерфейсам
| Сервис | URL | Логин / Пароль |
| :--- | :--- | :--- |
| **Airflow** | [http://localhost:8080](http://localhost:8080) | `admin` / `admin` |
| **Superset** | [http://localhost:8088](http://localhost:8088) | `admin` / `admin` |
| **ClickHouse HTTP** | [http://localhost:8123](http://localhost:8123) | `airflow` / `airflow` |

---

##  Работа с проектом

### Настройка визуализации в Superset
После запуска проекта:
1. Войдите в Superset под учетными данными `admin/admin`.
2. База данных ClickHouse должна быть добавлена автоматически. Если нет, перейдите в **Settings -> Database Connections** и добавьте новое подключение:
   ```text
   clickhouse://airflow:airflow@clickhouse:8123/airflow
   ```
3. Создайте свой первый Dataset на основе таблиц ClickHouse и приступайте к созданию графиков (Charts).

### Разработка DAG
Помещайте ваши Python-скрипты в директорию `./dags`. Airflow автоматически обнаружит их. Используйте `clickhouse-driver` для выполнения запросов к хранилищу внутри ваших задач.

---

##  Управление инфраструктурой

**Остановка всех сервисов:**
```bash
docker compose down
```

**Просмотр состояния инициализации Superset:**
```bash
docker compose logs -f superset-init
```

**Полный сброс данных:**
```bash
docker compose down -v
```

---

##  Устранение неполадок

**Superset не подключается к ClickHouse:**
Убедитесь, что контейнер `clickhouse` находится в состоянии `healthy`. Проверить статус можно командой `docker compose ps`.

**Ошибка инициализации Airflow:**
Если база данных метаданных не успела подняться, планировщик может завершиться с ошибкой. В проекте настроены `healthcheck`, но при первом запуске может потребоваться перезапуск:
```bash
docker compose restart airflow-webserver airflow-scheduler
```

---

##  Лицензия

Проект распространяется под лицензией **MIT**.

---

##  Контакты

- **Автор**: [qazsedc13](https://github.com/qazsedc13)
- **Репозиторий**: [airflow_click](https://github.com/qazsedc13/airflow_click)
