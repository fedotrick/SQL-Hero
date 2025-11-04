# Локальный запуск SQL Hero

Руководство по запуску проекта для локальной разработки.

---

## Перед началом

Убедитесь, что вы выполнили [инструкции по установке](SETUP.md).

**Требования:**
- Установлены зависимости backend (Poetry)
- Установлены зависимости frontend (pnpm)
- MySQL запущена и настроена
- Применены миграции базы данных
- Загружены начальные данные

---

## Вариант 1: Запуск через Docker Compose (Рекомендуется)

### Запуск всех сервисов

```bash
# Запустить все сервисы в фоновом режиме
docker-compose up -d

# Просмотр логов всех сервисов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

### Проверка статуса

```bash
# Проверить статус контейнеров
docker-compose ps

# Должны быть запущены:
# - mysql (port 3306)
# - backend (port 8000)
# - frontend (port 5173)
```

### Доступ к сервисам

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **MySQL:** localhost:3306 (credentials из docker-compose.yml)

### Остановка сервисов

```bash
# Остановить все сервисы (сохраняя данные)
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v
```

---

## Вариант 2: Локальный запуск (без Docker)

### Терминал 1: Запуск MySQL

Если MySQL не запущена локально, используйте Docker:

```bash
# Запустить только MySQL
docker-compose up mysql
```

Или если MySQL установлена локально:
```bash
# Проверить статус
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# Запустить
sudo systemctl start mysql  # Linux
brew services start mysql  # macOS
```

### Терминал 2: Запуск Backend

```bash
cd backend

# Активировать виртуальное окружение
poetry shell

# Запустить сервер разработки с hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Или через Poetry без активации shell
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend будет доступен:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Логи backend:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Терминал 3: Запуск Frontend

```bash
cd frontend

# Запустить dev сервер
pnpm dev

# Альтернативно можно указать хост и порт
pnpm dev --host 0.0.0.0 --port 5173
```

**Frontend будет доступен:**
- App: http://localhost:5173

**Логи frontend:**
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## Проверка работоспособности

### 1. Health Check Backend

```bash
# Проверить здоровье API
curl http://localhost:8000/health

# Ожидаемый ответ:
# {"status":"healthy","database":"connected"}
```

### 2. Проверка API endpoints

```bash
# Получить список модулей
curl http://localhost:8000/api/modules

# Получить информацию о модуле
curl http://localhost:8000/api/modules/1

# Получить уроки модуля
curl http://localhost:8000/api/modules/1/lessons
```

### 3. Проверка Frontend

Откройте http://localhost:5173 в браузере.

**Ожидаемый результат:**
- Загрузится интерфейс приложения
- Появится предупреждение "Opened outside Telegram" (это нормально для локальной разработки)
- Можно использовать demo режим для тестирования

### 4. Проверка Swagger UI

Откройте http://localhost:8000/docs в браузере.

**Ожидаемый результат:**
- Загрузится интерактивная документация API
- Можно тестировать endpoints прямо в браузере
- Все routes должны быть видны

---

## Работа с базой данных

### Подключение к MySQL

#### Через Docker

```bash
# Подключиться к MySQL контейнеру
docker-compose exec mysql mysql -u user -p sqlhero
# Пароль: password (из docker-compose.yml)
```

#### Локально

```bash
# Подключиться к локальному MySQL
mysql -u sqlhero_user -p sqlhero
# Пароль: ваш пароль из .env
```

### Полезные SQL команды

```sql
-- Показать таблицы
SHOW TABLES;

-- Проверить пользователей
SELECT id, telegram_id, username, xp, level FROM users LIMIT 10;

-- Проверить модули
SELECT id, title, order_index, lessons_count FROM modules ORDER BY order_index;

-- Проверить уроки
SELECT id, module_id, title, lesson_type, xp_reward FROM lessons LIMIT 10;

-- Проверить прогресс пользователя
SELECT u.username, l.title, up.is_completed, up.xp_earned
FROM user_progress up
JOIN users u ON up.user_id = u.id
JOIN lessons l ON up.lesson_id = l.id
LIMIT 10;

-- Проверить достижения
SELECT id, title, description, xp_reward FROM achievements;
```

### Применение миграций

```bash
cd backend

# Проверить текущую версию БД
poetry run alembic current

# Посмотреть историю миграций
poetry run alembic history

# Применить миграции
poetry run alembic upgrade head

# Откатить последнюю миграцию
poetry run alembic downgrade -1

# Откатить все миграции
poetry run alembic downgrade base
```

### Пересоздание базы данных

```bash
cd backend

# Откатить все миграции
poetry run alembic downgrade base

# Применить миграции
poetry run alembic upgrade head

# Загрузить данные
poetry run python -m app.cli.seed_data
```

---

## Hot Reload

### Backend Hot Reload

Backend запускается с флагом `--reload`, который автоматически перезапускает сервер при изменении файлов.

**Отслеживаемые файлы:**
- `app/**/*.py` - все Python файлы в директории app
- `.env` - изменения требуют ручного перезапуска

**Как работает:**
1. Редактируете файл в `backend/app/`
2. Сохраняете
3. Uvicorn автоматически перезапускает сервер
4. Изменения доступны сразу

**Логи при перезапуске:**
```
INFO:     Detected file change in 'app/routers/auth.py'
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Hot Reload

Frontend использует Vite HMR (Hot Module Replacement).

**Как работает:**
1. Редактируете файл в `frontend/src/`
2. Сохраняете
3. Vite мгновенно обновляет модуль в браузере без перезагрузки страницы

**Логи при изменении:**
```
hmr update /src/pages/Dashboard.tsx
```

**Типы обновлений:**
- React компоненты: обновляются без потери state
- CSS/стили: обновляются мгновенно
- Изменения в .env: требуют ручного перезапуска (`Ctrl+C`, `pnpm dev`)

---

## Отладка

### Backend Debugging

#### VS Code

Создайте `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

Запустите через `F5` или "Run and Debug".

#### PyCharm

1. Run → Edit Configurations
2. Add New Configuration → Python
3. Script path: `uvicorn`
4. Parameters: `app.main:app --reload --host 0.0.0.0 --port 8000`
5. Working directory: `/path/to/project/backend`
6. Run

#### Логирование

```python
import logging

logger = logging.getLogger(__name__)

# В вашем коде
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", exc_info=True)
```

### Frontend Debugging

#### Browser DevTools

1. Откройте http://localhost:5173
2. Нажмите `F12` для открытия DevTools
3. Используйте Console, Network, React DevTools

#### VS Code

Создайте `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Chrome: Frontend",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

#### React DevTools

Установите расширение [React Developer Tools](https://react.dev/learn/react-developer-tools) для Chrome/Firefox.

---

## Работа с Telegram WebApp

### Локальная разработка без Telegram

Приложение можно открыть напрямую в браузере: http://localhost:5173

**Особенности:**
- Появится предупреждение "Opened outside Telegram"
- Telegram WebApp API будет недоступен
- Используйте demo режим для тестирования UI

### Локальная разработка с Telegram (через ngrok)

#### Установка ngrok

```bash
# Установить через npm
npm install -g ngrok

# Или скачать с https://ngrok.com/download
```

#### Запуск ngrok

```bash
# Запустить туннель для frontend
ngrok http 5173

# Вы получите URL вида: https://abcd1234.ngrok.io
```

#### Настройка бота

1. Откройте Telegram и найдите **@BotFather**
2. Отправьте `/setmenubutton`
3. Выберите вашего бота
4. URL: `https://abcd1234.ngrok.io` (ваш ngrok URL)
5. Button text: `Начать обучение`

#### Тестирование

1. Откройте вашего бота в Telegram
2. Нажмите на кнопку меню "Начать обучение"
3. Приложение откроется в Telegram WebApp
4. Все изменения в коде будут доступны через ngrok URL

---

## Полезные команды разработки

### Backend

```bash
cd backend

# Запустить с debug логами
poetry run uvicorn app.main:app --reload --log-level debug

# Запустить на другом порту
poetry run uvicorn app.main:app --reload --port 8001

# Запустить без reload (быстрее)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Запустить с конкретным worker
poetry run uvicorn app.main:app --workers 4

# Интерактивная Python консоль с доступом к приложению
poetry run python
>>> from app.main import app
>>> from app.core.database import engine
```

### Frontend

```bash
cd frontend

# Запустить с открытием браузера
pnpm dev --open

# Запустить на другом порту
pnpm dev --port 3000

# Запустить с debug режимом
pnpm dev --debug

# Очистить кэш и запустить
rm -rf node_modules/.vite && pnpm dev
```

### Database

```bash
# Экспортировать схему БД
docker-compose exec mysql mysqldump -u user -p sqlhero --no-data > schema.sql

# Экспортировать данные
docker-compose exec mysql mysqldump -u user -p sqlhero > backup.sql

# Импортировать данные
docker-compose exec -T mysql mysql -u user -p sqlhero < backup.sql
```

---

## Мониторинг и логи

### Backend логи

```bash
# Docker
docker-compose logs -f backend

# Локально
# Логи выводятся в терминал где запущен uvicorn
```

### Frontend логи

```bash
# Docker
docker-compose logs -f frontend

# Локально
# Логи выводятся в терминал где запущен pnpm dev
```

### MySQL логи

```bash
# Docker
docker-compose logs -f mysql

# Проверить slow queries (если настроены)
docker-compose exec mysql mysql -u root -p -e "SELECT * FROM mysql.slow_log LIMIT 10;"
```

---

## Производительность

### Backend

```bash
# Установить profiler
cd backend
poetry add --group dev py-spy

# Профилировать запущенное приложение
py-spy top --pid <uvicorn-pid>

# Создать flamegraph
py-spy record -o profile.svg --pid <uvicorn-pid>
```

### Frontend

1. Откройте DevTools → Performance
2. Нажмите Record
3. Взаимодействуйте с приложением
4. Остановите запись
5. Анализируйте результаты

---

## Следующие шаги

- [TESTING.md](TESTING.md) - Запуск тестов
- [DOCKER.md](DOCKER.md) - Подробнее о Docker workflow
- [DEPLOYMENT.md](DEPLOYMENT.md) - Деплой в production
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Решение проблем

---

**Приятной разработки! 🚀**
