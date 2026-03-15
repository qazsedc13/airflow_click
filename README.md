# Airflow + ClickHouse + Superset в Docker

![License](https://img.shields.io/github/license/qazsedc13/airflow_click)
![Airflow Version](https://img.shields.io/badge/Airflow-2.8.1-blue)
![Superset Version](https://img.shields.io/badge/Superset-3.0.1-red)
![Docker](https://img.shields.io/badge/Docker-Compose-green)

Комплексная инфраструктура для оркестрации данных с использованием Apache Airflow, высокопроизводительной OLAP СУБД ClickHouse и платформы бизнес-аналитики Apache Superset. Проект предназначен для демонстрации ETL-процессов, бенчмаркинга производительности между PostgreSQL и ClickHouse, а также визуализации результатов.

---

##  Основные возможности

- **Оркестрация**: Автоматизация сбора и обработки данных через Airflow.
- **OLAP**: Быстрая аналитика больших объемов данных в ClickHouse.
- **Визуализация**: Создание интерактивных дашбордов в Superset.
- **Бенчмаркинг**: Сравнение производительности агрегационных запросов в PostgreSQL и ClickHouse на больших датасетах.
- **Полная контейнеризация**: Быстрый запуск всей экосистемы через Docker Compose.

---

##  Технологический стек

- **Apache Airflow 2.8.1**: LocalExecutor, PostgreSQL backend.
- **ClickHouse latest**: OLAP хранилище.
- **PostgreSQL 13**: Метаданные инфраструктуры и отдельное хранилище данных (`postgres_data`).
- **Apache Superset 3.0.1**: BI инструмент.
- **Python 3.11**: Основной язык для DAG и скриптов.

### Ключевые зависимости (Python)
- `psycopg2-binary==2.9.9` (Обновлено)
- `SQLAlchemy==1.4.52` (Обновлено)
- `clickhouse-driver==0.2.7` (Обновлено)
- `clickhouse-sqlalchemy==0.3.0` (Обновлено)
- `apache-airflow-providers-jdbc==4.5.1`
- `tqdm`

---

##  Предварительные требования

- **Docker Engine**: 20.10+ (с поддержкой Compose V2)
- **Docker Compose**: 2.0+
- **RAM**: 4GB+ (рекомендуется 8GB+)
- **ОС**: Linux, macOS или Windows с WSL2

---

##  Установка и запуск

### 1. Клонирование репозитория
```bash
git clone git@github.com:qazsedc13/airflow_click.git
cd airflow_click
```

### 2. Инициализация окружения
Создайте необходимые директории и настройте права доступа:
```bash
mkdir -p ./dags ./logs ./plugins ./superset
chmod -R 777 ./logs  # Рекомендуется только для среды разработки
```

### 3. Сборка и запуск сервисов
Для первого запуска выполните полную сборку:
```bash
docker compose up -d --build
```
Для последующих запусков:
```bash
docker compose up -d
```

### 4. Доступ к интерфейсам
| Сервис | URL | Логин / Пароль |
| :--- | :--- | :--- |
| **Airflow** | [http://localhost:8080](http://localhost:8080) | `admin` / `admin` |
| **Superset** | [http://localhost:8088](http://localhost:8088) | `admin` / `admin` |
| **ClickHouse HTTP** | [http://localhost:8123](http://localhost:8123) | `airflow` / `airflow` |

---

##  Работа с проектом

### Запуск DAG (ETL & Benchmarking)
Все DAG-файлы находятся в директории `./dags`. Они автоматически подхватываются Airflow.
- `generate_test_data`: Генерация тестовых данных (10 млн строк) для PG и CH.
- `run_benchmark`: Сравнение скорости выполнения аналитических запросов.
- `clickhouse_example`: Пример базовых операций с ClickHouse.

### Настройка Superset
При первом запуске автоматически создаются подключения к базам. Если требуется ручное добавление:
1. Перейдите в **Data**  **Databases**.
2. Используйте URI для ClickHouse:
   ```text
   clickhouse://airflow:airflow@clickhouse:8123/airflow
   ```
3. Используйте URI для PostgresData:
   ```text
   postgresql+psycopg2://data_user:data_password@postgres_data/data_db
   ```

---

##  Управление инфраструктурой

**Остановка всех сервисов:**
```bash
docker compose down
```

**Полный сброс (с удалением данных):**
```bash
docker compose down -v
docker compose up -d --build
```

**Просмотр логов:**
```bash
docker compose logs -f airflow-webserver  # Airflow Web
docker compose logs -f clickhouse         # ClickHouse
docker compose logs -f superset           # Superset
```

---

##  Устранение неполадок

**DAG не отображаются в интерфейсе:**
Проверьте логи планировщика:
```bash
docker compose logs airflow-scheduler | grep -i "dag"
```
Убедитесь, что расширение файла  `.py`.

**Проверка подключения к ClickHouse:**
```bash
docker compose exec clickhouse clickhouse-client --user airflow --password airflow --query "SHOW DATABASES"
```

**Проверка списка соединений в Airflow:**
```bash
docker compose exec airflow-webserver airflow connections list
```

---

##  Рекомендации для Production

- Замените `LocalExecutor` на `CeleryExecutor` или `KubernetesExecutor`.
- Измените стандартные пароли (`admin/admin`, `airflow/airflow`).
- Настройте `SUPERSET_SECRET_KEY` в переменных окружения.
- Ограничьте права доступа к директориям (уберите `777`).
- Настройте SSL-сертификаты и ротацию логов.

---

##  Лицензия

Данный проект распространяется под лицензией **MIT**. Подробности в файле [LICENSE](LICENSE) (если применимо).

---

##  Контакты и поддержка

- **Автор**: [qazsedc13](https://github.com/qazsedc13)
- **Repository**: [GitHub Link](https://github.com/qazsedc13/airflow_click)

Если у вас возникли вопросы или предложения, создайте Issue в репозитории проекта.