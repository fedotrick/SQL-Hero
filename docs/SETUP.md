# Руководство по установке

Подробное руководство по настройке проекта для разработки.

## Системные требования

### Обязательно

- **Python 3.12+**
- **Node.js 20+**
- **Git**
- **Docker** и **Docker Compose**

### Проверка версий

```bash
python3 --version  # Python 3.12.3 или выше
node --version     # v20.19.5 или выше
docker --version   # Docker version 20.10+ или выше
git --version      # Git version 2.0+ или выше
```

## Пошаговая установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Установка Poetry (для бэкенда)

#### Linux/macOS/WSL

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Добавьте в PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

#### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 3. Установка pnpm (для фронтенда)

```bash
npm install -g pnpm
```

Или используйте corepack:
```bash
corepack enable
corepack prepare pnpm@latest --activate
```

### 4. Запуск скрипта установки

```bash
./infrastructure/scripts/setup.sh
```

Этот скрипт:
- Установит pre-commit хуки
- Установит зависимости бэкенда
- Установит зависимости фронтенда

### 5. Настройка переменных окружения

#### Backend

```bash
cp backend/.env.example backend/.env
```

Отредактируйте `backend/.env`:
```env
DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/appdb
DEBUG=true
```

#### Frontend

```bash
cp frontend/.env.example frontend/.env
```

Отредактируйте `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

## Варианты запуска

### Вариант 1: Docker Compose (Рекомендуется)

Самый простой способ запустить все сервисы:

```bash
docker compose up
```

Первый запуск займет больше времени для сборки образов.

Для запуска в фоновом режиме:
```bash
docker compose up -d
```

Просмотр логов:
```bash
docker compose logs -f
```

Остановка:
```bash
docker compose down
```

### Вариант 2: Локальная разработка

#### Запуск MySQL в Docker

```bash
docker compose up mysql -d
```

#### Запуск бэкенда локально

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

Бэкенд будет доступен: http://localhost:8000
API документация: http://localhost:8000/docs

#### Запуск фронтенда локально

```bash
cd frontend
pnpm dev
```

Фронтенд будет доступен: http://localhost:5173

### Вариант 3: Используя Makefile

```bash
# Установка
make setup

# Запуск с Docker
make docker-up

# Остановка
make docker-down

# Линтинг
make lint

# Тесты
make test
```

## Проверка установки

### 1. Проверка бэкенда

```bash
curl http://localhost:8000/
# Ожидаемый ответ: {"message":"Hello from FastAPI backend!"}

curl http://localhost:8000/health
# Ожидаемый ответ: {"status":"ok"}
```

Или откройте в браузере:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc

### 2. Проверка фронтенда

Откройте http://localhost:5173 в браузере.

Вы должны увидеть React приложение, которое взаимодействует с бэкендом.

### 3. Проверка MySQL

```bash
docker compose exec mysql mysql -u user -p appdb
# Пароль: password
```

Внутри MySQL:
```sql
SHOW DATABASES;
USE appdb;
SHOW TABLES;
```

## Решение проблем

### Порты уже используются

Если порты 3306, 5173 или 8000 уже используются:

```bash
# Найти процесс на порту
lsof -i :8000
# или
netstat -tulpn | grep 8000

# Остановить процесс
kill -9 <PID>
```

Или измените порты в `docker-compose.yml`.

### Docker проблемы

```bash
# Очистить все контейнеры и volumes
docker compose down -v

# Пересобрать образы
docker compose up --build

# Очистить Docker кэш
docker system prune -a
```

### Poetry проблемы

```bash
# Пересоздать виртуальное окружение
cd backend
poetry env remove python
poetry install
```

### pnpm проблемы

```bash
# Очистить кэш и переустановить
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Pre-commit проблемы

```bash
# Переустановить pre-commit хуки
pre-commit uninstall
pre-commit install

# Запустить вручную
pre-commit run --all-files
```

## Следующие шаги

После успешной установки:

1. Прочитайте [CONTRIBUTING.md](CONTRIBUTING.md) для понимания процесса разработки
2. Изучите [ARCHITECTURE.md](ARCHITECTURE.md) для понимания структуры проекта
3. Запустите тесты: `make test`
4. Начните разработку!

## Полезные команды

### Backend

```bash
# Добавить зависимость
cd backend
poetry add package-name

# Добавить dev зависимость
poetry add --group dev package-name

# Обновить зависимости
poetry update

# Запустить shell в виртуальном окружении
poetry shell
```

### Frontend

```bash
# Добавить зависимость
cd frontend
pnpm add package-name

# Добавить dev зависимость
pnpm add -D package-name

# Обновить зависимости
pnpm update

# Проверить устаревшие пакеты
pnpm outdated
```

### Docker

```bash
# Посмотреть запущенные контейнеры
docker compose ps

# Перезапустить сервис
docker compose restart backend

# Выполнить команду в контейнере
docker compose exec backend bash

# Посмотреть логи конкретного сервиса
docker compose logs -f backend

# Остановить и удалить всё
docker compose down -v
```

## Дополнительные инструменты

### Рекомендуемые расширения для VS Code

- Python
- Pylance
- Ruff
- ESLint
- Prettier
- Docker
- GitLens

### Рекомендуемые расширения для PyCharm

- Ruff (встроенная поддержка)
- Prettier
- Docker (встроенная поддержка)

## Получение помощи

Если возникли проблемы:

1. Проверьте Issues в репозитории
2. Создайте новый Issue с описанием проблемы
3. Включите вывод команд и логи

Удачной разработки! 🚀
