# Руководство по установке SQL Hero

Подробное руководство по настройке проекта SQL Hero для разработки.

---

## Системные требования

### Обязательно

- **Node.js** >= 18.0.0
- **Python** >= 3.11 (рекомендуется 3.12+)
- **MySQL** >= 8.0
- **pnpm** >= 8.0.0 (для frontend)
- **Docker** и **Docker Compose** (рекомендуется для разработки)
- **Git** >= 2.0

### Опционально

- **Poetry** >= 1.7.0 (для управления Python зависимостями)
- **Telegram Bot Token** (для полноценной работы)
- **Make** (для использования Makefile команд)

### Проверка версий

```bash
# Проверить установленные версии
python3 --version    # Python 3.11+ или выше
node --version       # v18.0.0 или выше
pnpm --version       # 8.0.0 или выше
docker --version     # Docker 20.10+ или выше
docker-compose --version  # 2.0+ или выше
git --version        # Git 2.0+ или выше
```

---

## Вариант А: Установка через Docker (Рекомендуется)

Это самый простой способ запустить проект для разработки.

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/fedotrick/SQL-Hero.git
cd SQL-Hero
```

### Шаг 2: Настройка переменных окружения

#### Backend

```bash
cp backend/.env.example backend/.env
```

Отредактируйте `backend/.env`:

```env
# Database (для Docker используйте mysql как хост)
DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/sqlhero

# Telegram Bot (получите токен у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username

# JWT Secret (сгенерируйте: openssl rand -hex 32)
JWT_SECRET_KEY=your-generated-secret-key-min-32-chars

# Sandbox (для Docker)
SANDBOX_ENABLED=true
SANDBOX_MYSQL_HOST=mysql
SANDBOX_MYSQL_PORT=3306
SANDBOX_MYSQL_ADMIN_USER=root
SANDBOX_MYSQL_ADMIN_PASSWORD=rootpassword

# CORS
CORS_ORIGINS=http://localhost:5173

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### Frontend

```bash
cp frontend/.env.example frontend/.env
```

Отредактируйте `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=SQL Hero
VITE_TELEGRAM_BOT_USERNAME=your_bot_username
```

### Шаг 3: Запуск через Docker Compose

```bash
# Запустить все сервисы (MySQL, Backend, Frontend)
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Проверить статус контейнеров
docker-compose ps
```

Первый запуск займет несколько минут для сборки образов.

### Шаг 4: Применение миграций и загрузка данных

```bash
# Применить миграции базы данных
docker-compose exec backend poetry run alembic upgrade head

# Загрузить начальные данные (модули, уроки, достижения)
docker-compose exec backend poetry run python -m app.cli.seed_data

# Проверить, что данные загружены
docker-compose exec backend poetry run python -m app.cli.check_db
```

### Шаг 5: Проверка работоспособности

**Backend:**
```bash
curl http://localhost:8000/health
# Ожидаемый ответ: {"status":"healthy","database":"connected"}
```

**Frontend:**
Откройте http://localhost:5173 в браузере.

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Вариант Б: Локальная установка (без Docker)

Этот вариант подходит, если вы хотите запускать сервисы локально.

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/fedotrick/SQL-Hero.git
cd SQL-Hero
```

### Шаг 2: Установка Poetry (Python package manager)

#### Linux/macOS/WSL

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Добавьте в PATH (добавьте в ~/.bashrc или ~/.zshrc):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Перезапустите терминал или выполните:
```bash
source ~/.bashrc  # или source ~/.zshrc
```

#### Windows (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Проверьте установку:
```bash
poetry --version
```

### Шаг 3: Установка pnpm (Node.js package manager)

```bash
# Через npm
npm install -g pnpm

# Или через corepack (Node.js 16+)
corepack enable
corepack prepare pnpm@latest --activate
```

Проверьте установку:
```bash
pnpm --version
```

### Шаг 4: Установка зависимостей Backend

```bash
cd backend

# Установить зависимости через Poetry
poetry install

# Активировать виртуальное окружение
poetry shell

cd ..
```

### Шаг 5: Установка зависимостей Frontend

```bash
cd frontend

# Установить зависимости через pnpm
pnpm install

cd ..
```

### Шаг 6: Настройка MySQL

#### Вариант 1: MySQL через Docker (рекомендуется)

```bash
# Запустить только MySQL контейнер
docker-compose up mysql -d

# Проверить статус
docker-compose ps mysql
```

MySQL будет доступна на `localhost:3306` с credentials из `docker-compose.yml`:
- User: `user`
- Password: `password`
- Database: `sqlhero`
- Root Password: `rootpassword`

#### Вариант 2: Локальный MySQL

Установите MySQL 8.0+ на вашу систему, затем создайте базу данных:

```bash
mysql -u root -p
```

```sql
-- Создать базу данных
CREATE DATABASE sqlhero CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создать пользователя
CREATE USER 'sqlhero_user'@'localhost' IDENTIFIED BY 'your_password';

-- Дать права
GRANT ALL PRIVILEGES ON sqlhero.* TO 'sqlhero_user'@'localhost';

-- Дать права root для песочницы (создание схем)
GRANT ALL PRIVILEGES ON `sandbox_%`.* TO 'sqlhero_user'@'localhost';

FLUSH PRIVILEGES;
EXIT;
```

### Шаг 7: Настройка переменных окружения

#### Backend

```bash
cp backend/.env.example backend/.env
```

Отредактируйте `backend/.env`:

```env
# Database (для локального MySQL)
DATABASE_URL=mysql+aiomysql://sqlhero_user:your_password@localhost:3306/sqlhero

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username

# JWT Secret (сгенерируйте: openssl rand -hex 32)
JWT_SECRET_KEY=your-generated-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Sandbox
SANDBOX_ENABLED=true
SANDBOX_TIMEOUT_SECONDS=5
SANDBOX_MAX_RESULT_ROWS=1000
SANDBOX_MYSQL_HOST=localhost
SANDBOX_MYSQL_PORT=3306
SANDBOX_MYSQL_ADMIN_USER=root
SANDBOX_MYSQL_ADMIN_PASSWORD=your_mysql_root_password

# CORS
CORS_ORIGINS=http://localhost:5173

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### Frontend

```bash
cp frontend/.env.example frontend/.env
```

Отредактируйте `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=SQL Hero
VITE_TELEGRAM_BOT_USERNAME=your_bot_username
```

### Шаг 8: Применение миграций и загрузка данных

```bash
cd backend

# Применить миграции
poetry run alembic upgrade head

# Загрузить начальные данные
poetry run python -m app.cli.seed_data

cd ..
```

### Шаг 9: Запуск Backend

```bash
cd backend

# Запустить сервер разработки (с hot reload)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend будет доступен на http://localhost:8000

### Шаг 10: Запуск Frontend (в отдельном терминале)

```bash
cd frontend

# Запустить dev сервер
pnpm dev
```

Frontend будет доступен на http://localhost:5173

---

## Настройка Telegram Bot (Опционально для разработки)

Для полноценной работы с Telegram WebApp вам нужен Telegram Bot Token.

### Шаг 1: Создание бота

1. Откройте Telegram и найдите **@BotFather**
2. Отправьте команду `/newbot`
3. Введите название бота: `SQL Hero Dev Bot` (или любое другое)
4. Введите username бота: `sql_hero_dev_bot` (должен заканчиваться на `_bot`)
5. Скопируйте полученный **Bot Token**

### Шаг 2: Добавление токена в .env

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_USERNAME=sql_hero_dev_bot
```

### Шаг 3: Настройка Web App кнопки (опционально)

Для локальной разработки можно использовать ngrok:

```bash
# Установить ngrok
npm install -g ngrok

# Запустить туннель для frontend
ngrok http 5173
```

Затем в BotFather:
```
/setmenubutton
Выберите бота
URL: https://your-ngrok-url.ngrok.io
Button text: Начать обучение
```

---

## Проверка установки

### 1. Проверка Backend

```bash
# Health check
curl http://localhost:8000/health

# Ожидаемый ответ:
# {"status":"healthy","database":"connected"}

# Проверка API
curl http://localhost:8000/api/modules

# Должен вернуть список модулей
```

### 2. Проверка Frontend

Откройте http://localhost:5173 в браузере. Вы должны увидеть:
- Предупреждение "Opened outside Telegram" (это нормально для локальной разработки)
- Интерфейс приложения

### 3. Проверка MySQL

```bash
# Через Docker
docker-compose exec mysql mysql -u user -p sqlhero
# Пароль: password

# Локально
mysql -u sqlhero_user -p sqlhero
```

Внутри MySQL:
```sql
-- Проверить таблицы
SHOW TABLES;

-- Должны быть: users, modules, lessons, achievements, etc.

-- Проверить модули
SELECT id, title, order_index FROM modules ORDER BY order_index;

-- Должно быть 10 модулей
```

### 4. Проверка Swagger UI

Откройте http://localhost:8000/docs — должна загрузиться интерактивная документация API.

---

## Полезные команды

### Backend

```bash
cd backend

# Активировать виртуальное окружение
poetry shell

# Добавить зависимость
poetry add package-name

# Добавить dev зависимость
poetry add --group dev package-name

# Обновить зависимости
poetry update

# Создать новую миграцию
poetry run alembic revision --autogenerate -m "description"

# Применить миграции
poetry run alembic upgrade head

# Откатить миграцию
poetry run alembic downgrade -1

# Запустить тесты
poetry run pytest

# Запустить E2E тесты (SQLite, быстро)
poetry run pytest tests/e2e/ -v

# Тесты с покрытием
poetry run pytest --cov=app --cov-report=html

# Линтинг
poetry run ruff check app

# Форматирование
poetry run ruff format app

# Проверка типов
poetry run mypy app
```

### Frontend

```bash
cd frontend

# Запустить dev сервер
pnpm dev

# Сборка для production
pnpm build

# Preview production build
pnpm preview

# Добавить зависимость
pnpm add package-name

# Добавить dev зависимость
pnpm add -D package-name

# Обновить зависимости
pnpm update

# Линтинг
pnpm lint

# Форматирование
pnpm format

# Проверка форматирования
pnpm format:check

# Проверка типов
pnpm type-check
```

### Docker

```bash
# Запустить все сервисы
docker-compose up -d

# Остановить все сервисы
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v

# Пересобрать образы
docker-compose build

# Пересобрать и запустить
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Перезапустить сервис
docker-compose restart backend

# Выполнить команду в контейнере
docker-compose exec backend bash
docker-compose exec mysql mysql -u user -p

# Проверить статус
docker-compose ps
```

---

## Решение проблем

### Порты уже используются

**Проблема:** `Address already in use` для портов 3306, 5173 или 8000

**Решение:**
```bash
# Найти процесс на порту (Linux/Mac)
lsof -i :8000
netstat -tulpn | grep 8000

# Найти процесс на порту (Windows)
netstat -ano | findstr :8000

# Остановить процесс
kill -9 <PID>  # Linux/Mac
taskkill /F /PID <PID>  # Windows

# Или измените порты в docker-compose.yml
```

### Docker проблемы

**Проблема:** Контейнеры не запускаются или падают

**Решение:**
```bash
# Очистить всё и пересобрать
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Очистить Docker кэш
docker system prune -a

# Проверить логи
docker-compose logs backend
docker-compose logs mysql
```

### MySQL connection refused

**Проблема:** `Can't connect to MySQL server`

**Решение:**
```bash
# Проверить, что MySQL контейнер запущен
docker-compose ps mysql

# Проверить логи MySQL
docker-compose logs mysql

# Проверить DATABASE_URL в backend/.env
# Для Docker должно быть: mysql+aiomysql://user:password@mysql:3306/sqlhero
# Для локального: mysql+aiomysql://user:password@localhost:3306/sqlhero

# Перезапустить MySQL
docker-compose restart mysql
```

### Poetry проблемы

**Проблема:** `Poetry not found` или проблемы с зависимостями

**Решение:**
```bash
# Переустановить Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Добавить в PATH
export PATH="$HOME/.local/bin:$PATH"

# Пересоздать виртуальное окружение
cd backend
poetry env remove python
poetry install
```

### pnpm проблемы

**Проблема:** `pnpm not found` или проблемы с зависимостями

**Решение:**
```bash
# Переустановить pnpm
npm install -g pnpm

# Очистить кэш и переустановить
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Alembic migration errors

**Проблема:** Ошибки при применении миграций

**Решение:**
```bash
cd backend

# Проверить текущую версию БД
poetry run alembic current

# Посмотреть историю миграций
poetry run alembic history

# Откатить все миграции
poetry run alembic downgrade base

# Применить все миграции заново
poetry run alembic upgrade head
```

### Seed data errors

**Проблема:** Ошибки при загрузке начальных данных

**Решение:**
```bash
cd backend

# Проверить подключение к БД
poetry run python -c "from app.core.database import get_session; print('OK')"

# Удалить и заново загрузить данные
poetry run python -m app.cli.clear_db
poetry run python -m app.cli.seed_data
```

---

## Следующие шаги

После успешной установки:

1. Прочитайте [RUN_LOCAL.md](RUN_LOCAL.md) для подробностей о локальной разработке
2. Изучите [ARCHITECTURE.md](ARCHITECTURE.md) для понимания структуры проекта
3. Прочитайте [TESTING.md](TESTING.md) для запуска тестов
4. Изучите [CONTRIBUTING.md](CONTRIBUTING.md) для понимания процесса разработки
5. Начните разработку!

---

## Получение помощи

Если возникли проблемы:

1. Проверьте [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Ищите похожие [Issues на GitHub](https://github.com/fedotrick/SQL-Hero/issues)
3. Создайте новый Issue с описанием проблемы и логами
4. Свяжитесь с разработчиками в Telegram

---

**Удачной разработки! 🚀**
