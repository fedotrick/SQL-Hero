# Решение проблем SQL Hero

Руководство по решению распространённых проблем при разработке и эксплуатации SQL Hero.

---

## Backend проблемы

### ModuleNotFoundError: No module named 'app'

**Проблема:** Python не может найти модуль приложения.

**Решение:**

```bash
cd backend

# Переустановите зависимости
poetry install

# Убедитесь, что виртуальное окружение активировано
poetry shell

# Или запускайте через poetry run
poetry run uvicorn app.main:app --reload
```

---

### MySQL Connection Refused

**Проблема:** `Can't connect to MySQL server on 'localhost'` или `Connection refused`

**Решение 1: Проверить MySQL**

```bash
# Проверить статус MySQL контейнера
docker-compose ps mysql

# Если не запущен, запустить
docker-compose up mysql -d

# Проверить логи
docker-compose logs mysql
```

**Решение 2: Проверить DATABASE_URL**

```bash
# В backend/.env проверьте:
# Для Docker:
DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/sqlhero

# Для локального MySQL:
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/sqlhero
```

**Решение 3: Проверить что MySQL готова**

```bash
# Подключиться к MySQL вручную
docker-compose exec mysql mysql -u user -p
# Пароль: password

# Проверить что БД существует
SHOW DATABASES;
```

---

### Alembic Migration Errors

**Проблема:** `Target database is not up to date` или migration errors.

**Решение 1: Проверить текущую версию**

```bash
cd backend
poetry run alembic current
poetry run alembic history
```

**Решение 2: Применить миграции**

```bash
poetry run alembic upgrade head
```

**Решение 3: Откатить и применить заново**

```bash
# Откатить все миграции
poetry run alembic downgrade base

# Применить все заново
poetry run alembic upgrade head

# Загрузить данные
poetry run python -m app.cli.seed_data
```

**Решение 4: Конфликт миграций**

```bash
# Если несколько веток миграций
poetry run alembic branches

# Объединить ветки
poetry run alembic merge heads
```

---

### SQLAlchemy Reserved Attribute Name

**Проблема:** `Attribute name 'metadata' is reserved when using Declarative`

**Решение:**

```python
# НЕ ДЕЛАЙТЕ ТАК:
metadata: Mapped[dict] = mapped_column(JSON)

# ПРАВИЛЬНО:
notification_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
```

Другие зарезервированные имена: `registry`, `__table__`, `__mapper__`.

---

### Poetry Lock Issues

**Проблема:** `Unable to find installation candidates for ...` или lock errors.

**Решение:**

```bash
cd backend

# Удалить lock file и переустановить
rm poetry.lock
poetry install

# Обновить poetry
poetry self update

# Очистить cache
poetry cache clear pypi --all
```

---

### Sandbox не выполняет SQL запросы

**Проблема:** SQL запросы не выполняются в песочнице или timeout.

**Решение 1: Проверить настройки**

```bash
# В backend/.env:
SANDBOX_ENABLED=true
SANDBOX_TIMEOUT_SECONDS=5
SANDBOX_MYSQL_HOST=mysql  # для Docker
SANDBOX_MYSQL_ADMIN_USER=root
SANDBOX_MYSQL_ADMIN_PASSWORD=rootpassword
```

**Решение 2: Проверить права MySQL**

```bash
# Подключиться как root
docker-compose exec mysql mysql -u root -p

# Проверить права
SHOW GRANTS FOR 'root'@'%';

# Дать необходимые права
GRANT ALL PRIVILEGES ON `sandbox_%`.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

**Решение 3: Увеличить timeout**

```bash
# В .env увеличьте timeout
SANDBOX_TIMEOUT_SECONDS=10
```

---

## Frontend проблемы

### Command not found: pnpm

**Проблема:** pnpm не установлен.

**Решение:**

```bash
# Установить через npm
npm install -g pnpm

# Или через corepack
corepack enable
corepack prepare pnpm@latest --activate

# Проверить установку
pnpm --version
```

---

### Network Error при вызове API

**Проблема:** Frontend не может подключиться к backend.

**Решение 1: Проверить VITE_API_BASE_URL**

```bash
# В frontend/.env:
VITE_API_BASE_URL=http://localhost:8000

# Убедитесь, что нет trailing slash
```

**Решение 2: Проверить что backend запущен**

```bash
# Проверить backend
curl http://localhost:8000/health

# Должно вернуть: {"status":"healthy","database":"connected"}
```

**Решение 3: CORS проблемы**

```bash
# В backend/.env добавьте frontend URL:
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

**Решение 4: Перезапустить dev server**

```bash
# Ctrl+C остановить
# Перезапустить
cd frontend
pnpm dev
```

---

### Module not found или Import errors

**Проблема:** `Cannot find module` или import errors в TypeScript.

**Решение:**

```bash
cd frontend

# Переустановить node_modules
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Перезапустить TypeScript server в VS Code
# Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"
```

---

### Vite HMR не работает

**Проблема:** Изменения в коде не отражаются автоматически.

**Решение 1: Проверить browser console**

```
Откройте DevTools → Console
Поищите ошибки HMR
```

**Решение 2: Очистить cache**

```bash
cd frontend

# Удалить Vite cache
rm -rf node_modules/.vite

# Перезапустить
pnpm dev
```

**Решение 3: Проверить файловую систему**

```bash
# На Linux могут быть проблемы с inotify
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## Telegram WebApp проблемы

### Invalid initData signature

**Проблема:** Backend отклоняет Telegram авторизацию.

**Решение 1: Проверить TELEGRAM_BOT_TOKEN**

```bash
# В backend/.env
# Токен должен совпадать с токеном из BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# БЕЗ пробелов в начале/конце!
```

**Решение 2: Проверить что используете правильного бота**

```bash
# TELEGRAM_BOT_USERNAME должен совпадать
TELEGRAM_BOT_USERNAME=sql_hero_bot
```

**Решение 3: Перезапустить backend**

```bash
# Перезапустите после изменения .env
docker-compose restart backend
# или
# Ctrl+C и poetry run uvicorn app.main:app --reload
```

---

### "Opened outside Telegram" warning

**Проблема:** Предупреждение при открытии в браузере напрямую.

**Решение:**

**Это нормально для разработки!** Приложение проверяет `window.Telegram.WebApp.initData`.

Для тестирования:
1. Используйте ngrok для локальной разработки
2. Настройте бота через BotFather
3. Открывайте через Telegram

Или игнорируйте предупреждение при локальной разработке.

---

### WebApp не открывается в Telegram

**Проблема:** Кнопка не открывает приложение или показывает ошибку.

**Решение 1: Проверить URL в BotFather**

```bash
# Отправьте BotFather:
/setmenubutton

# Убедитесь, что URL правильный:
# Production: https://your-domain.com
# Dev (ngrok): https://abc123.ngrok.io
```

**Решение 2: Проверить HTTPS**

Telegram WebApp требует HTTPS (кроме localhost):
- ✅ https://your-domain.com
- ✅ http://localhost:5173 (только для разработки)
- ❌ http://your-domain.com

**Решение 3: Проверить SSL сертификат**

```bash
# Проверить сертификат
curl -v https://your-domain.com

# Должен быть валидный SSL
```

---

## Docker проблемы

### Containers не запускаются

**Проблема:** `docker-compose up` падает с ошибками.

**Решение 1: Проверить логи**

```bash
docker-compose logs backend
docker-compose logs mysql
docker-compose logs frontend
```

**Решение 2: Пересоздать контейнеры**

```bash
# Остановить и удалить всё
docker-compose down -v

# Пересобрать образы
docker-compose build --no-cache

# Запустить заново
docker-compose up -d
```

**Решение 3: Очистить Docker**

```bash
# Очистить неиспользуемые ресурсы
docker system prune -a

# Удалить volumes (ОСТОРОЖНО: потеряете данные БД!)
docker volume prune
```

---

### Порты уже используются

**Проблема:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Решение 1: Найти процесс**

```bash
# Linux/Mac
lsof -i :8000
netstat -tulpn | grep 8000

# Windows
netstat -ano | findstr :8000

# Убить процесс
kill -9 <PID>  # Linux/Mac
taskkill /F /PID <PID>  # Windows
```

**Решение 2: Изменить порт**

В `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # host:container
```

---

### MySQL health check fails

**Проблема:** MySQL контейнер показывает unhealthy status.

**Решение:**

```bash
# Проверить логи MySQL
docker-compose logs mysql

# Подключиться вручную
docker-compose exec mysql mysql -u root -p

# Если не работает, пересоздать
docker-compose down -v
docker-compose up mysql -d

# Подождать 30-60 секунд для инициализации
```

---

## Testing проблемы

### E2E тесты падают

**Проблема:** Pytest тесты не проходят.

**Решение 1: Переустановить зависимости**

```bash
cd backend
poetry install
```

**Решение 2: Проверить fixtures**

```bash
# Запустить с verbose output
poetry run pytest tests/e2e/ -v

# Запустить конкретный тест для debug
poetry run pytest tests/e2e/test_e2e_auth.py::test_register_new_user -v -s
```

**Решение 3: Очистить pytest cache**

```bash
rm -rf .pytest_cache
poetry run pytest tests/e2e/ -v
```

---

### Integration тесты требуют MySQL

**Проблема:** 168 тестов падают без MySQL.

**Решение:**

```bash
# Запустить только E2E тесты (SQLite, быстро)
poetry run pytest tests/e2e/ -v

# Или запустить MySQL для всех тестов
docker-compose up mysql -d
poetry run pytest tests/ -v
```

---

## Performance проблемы

### Backend медленно отвечает

**Проблема:** API endpoints имеют высокую latency.

**Решение 1: Проверить database queries**

```python
# Включить SQL logging
# В backend/app/core/database.py
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Показывает все SQL queries
)
```

**Решение 2: Добавить indexes**

```sql
-- Проверить slow queries
SELECT * FROM mysql.slow_log LIMIT 10;

-- Добавить indexes где нужно
CREATE INDEX idx_user_telegram_id ON users(telegram_id);
```

**Решение 3: Увеличить workers**

```bash
# Запустить с несколькими workers
uvicorn app.main:app --workers 4
```

---

### Frontend медленно загружается

**Проблема:** Приложение долго грузится в Telegram.

**Решение 1: Проверить bundle size**

```bash
cd frontend
pnpm build

# Анализировать bundle
pnpm add -D rollup-plugin-visualizer
```

**Решение 2: Lazy loading**

```typescript
// Используйте React.lazy для code splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
```

**Решение 3: Оптимизировать images**

```bash
# Compress images
npm install -g imagemin-cli
imagemin public/images/*.png --out-dir=public/images/optimized
```

---

## Production проблемы

### 502 Bad Gateway

**Проблема:** Nginx возвращает 502 Bad Gateway.

**Решение 1: Проверить backend**

```bash
# Проверить что backend запущен
systemctl status sqlhero
# или
docker-compose ps backend

# Проверить логи
journalctl -u sqlhero -f
# или
docker-compose logs backend
```

**Решение 2: Проверить Nginx конфигурацию**

```bash
# Тест конфигурации
sudo nginx -t

# Перезапустить Nginx
sudo systemctl restart nginx
```

---

### SSL Certificate errors

**Проблема:** SSL сертификат не работает или expired.

**Решение:**

```bash
# Обновить Let's Encrypt сертификат
sudo certbot renew

# Проверить сертификат
sudo certbot certificates

# Если проблема не решилась, удалить и пересоздать
sudo certbot delete --cert-name your-domain.com
sudo certbot --nginx -d your-domain.com
```

---

### Out of Memory

**Проблема:** Сервер падает из-за нехватки памяти.

**Решение 1: Проверить использование памяти**

```bash
# Проверить memory usage
free -h
htop

# Docker containers memory
docker stats
```

**Решение 2: Ограничить memory для Docker**

```yaml
# docker-compose.yml
services:
  backend:
    mem_limit: 512m
    memswap_limit: 512m
```

**Решение 3: Оптимизировать приложение**

```python
# Использовать connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)
```

---

## Получение помощи

Если проблема не решена:

1. **Проверьте документацию:**
   - [SETUP.md](SETUP.md)
   - [RUN_LOCAL.md](RUN_LOCAL.md)
   - [DOCKER.md](DOCKER.md)

2. **Поищите в Issues:**
   - [GitHub Issues](https://github.com/fedotrick/SQL-Hero/issues)

3. **Создайте новый Issue:**
   - Опишите проблему
   - Приложите логи
   - Укажите версии (OS, Python, Node.js)
   - Шаги для воспроизведения

4. **Telegram сообщество:**
   - [@fedotrick](https://t.me/fedotrick)

---

## Полезные команды для диагностики

### Системная информация

```bash
# Версии
python3 --version
node --version
pnpm --version
docker --version
docker-compose --version

# Disk space
df -h

# Memory
free -h

# CPU
top
htop
```

### Логи

```bash
# Backend логи
docker-compose logs backend --tail=100 -f
journalctl -u sqlhero -f

# Frontend логи
docker-compose logs frontend --tail=100 -f

# MySQL логи
docker-compose logs mysql --tail=100 -f

# Nginx логи
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Network

```bash
# Проверить connectivity
curl http://localhost:8000/health
curl http://localhost:5173

# Проверить DNS
nslookup your-domain.com

# Проверить открытые порты
netstat -tulpn
```

---

**Удачи в решении проблем! 🔧**
