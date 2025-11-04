# Production Deployment SQL Hero

Руководство по деплою SQL Hero в production окружение.

---

## Checklist перед деплоем

- [ ] Все тесты проходят (`pytest`, `pnpm test`)
- [ ] Security тесты проходят 100%
- [ ] Линтинг без ошибок (`ruff`, `eslint`)
- [ ] Type checking проходит (`mypy`, `tsc`)
- [ ] `.env` файлы настроены для production
- [ ] JWT_SECRET_KEY уникальный и безопасный (минимум 32 символа)
- [ ] TELEGRAM_BOT_TOKEN для production бота
- [ ] Production база данных создана и настроена
- [ ] SSL сертификаты готовы
- [ ] Домен настроен и указывает на серверы
- [ ] CORS настроен для production доменов
- [ ] Backup стратегия определена

---

## Архитектура Production

```
                    ┌─────────────┐
                    │   Telegram  │
                    │    Users    │
                    └──────┬──────┘
                           │
                           ▼
                 ┌─────────────────┐
                 │  Telegram Bot   │
                 │    (BotFather)  │
                 └────────┬─────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                  │
         ▼                                  ▼
┌──────────────────┐            ┌──────────────────┐
│  Frontend        │            │  Backend API     │
│  (Vercel/        │◄──────────►│  (Railway/       │
│   Netlify)       │   HTTPS    │   Render/VPS)    │
└──────────────────┘            └────────┬─────────┘
                                         │
                                         ▼
                                ┌──────────────────┐
                                │  MySQL Database  │
                                │  (Managed DB)    │
                                └──────────────────┘
```

---

## Backend Deployment

### Вариант 1: Railway (Рекомендуется)

#### Шаг 1: Подготовка

```bash
# Установить Railway CLI
npm install -g @railway/cli

# Login
railway login
```

#### Шаг 2: Создание проекта

```bash
# В корне проекта
railway init

# Выбрать "Empty Project"
# Назвать проект: sql-hero
```

#### Шаг 3: Добавление MySQL

```bash
# Добавить MySQL plugin
railway add mysql

# Получить DATABASE_URL
railway variables
```

#### Шаг 4: Настройка переменных окружения

В Railway Dashboard → Variables добавьте:

```env
DATABASE_URL=<автоматически создан Railway MySQL>
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_BOT_USERNAME=sql_hero_bot
JWT_SECRET_KEY=<сгенерируйте: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
SANDBOX_ENABLED=true
SANDBOX_TIMEOUT_SECONDS=5
SANDBOX_MAX_RESULT_ROWS=1000
SANDBOX_MYSQL_HOST=<Railway MySQL host>
SANDBOX_MYSQL_PORT=<Railway MySQL port>
SANDBOX_MYSQL_ADMIN_USER=<Railway MySQL user>
SANDBOX_MYSQL_ADMIN_PASSWORD=<Railway MySQL password>
CORS_ORIGINS=https://your-frontend-domain.vercel.app
ENVIRONMENT=production
DEBUG=false
```

#### Шаг 5: Deploy

```bash
# Deploy backend
railway up

# Или через GitHub integration
# Подключите GitHub репозиторий в Railway Dashboard
```

#### Шаг 6: Миграции

```bash
# Подключиться к Railway shell
railway shell

# Применить миграции
poetry run alembic upgrade head

# Загрузить данные
poetry run python -m app.cli.seed_data
```

#### Получить URL

```bash
# Railway автоматически создаст URL вида:
# https://sql-hero-production.railway.app
```

---

### Вариант 2: Render

#### Шаг 1: Создание Web Service

1. Зайдите на [render.com](https://render.com)
2. New → Web Service
3. Подключите GitHub репозиторий
4. Настройки:
   - **Name:** sql-hero-backend
   - **Environment:** Python 3
   - **Build Command:** `cd backend && pip install poetry && poetry install --no-dev`
   - **Start Command:** `cd backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free или Starter

#### Шаг 2: Создание PostgreSQL Database

Render использует PostgreSQL вместо MySQL:

1. New → PostgreSQL
2. Скопируйте Internal Database URL

#### Шаг 3: Environment Variables

Добавьте в Render Dashboard:

```env
DATABASE_URL=<Render PostgreSQL URL>
TELEGRAM_BOT_TOKEN=your_production_bot_token
TELEGRAM_BOT_USERNAME=sql_hero_bot
JWT_SECRET_KEY=<generate_secure_key>
# ... остальные переменные
```

#### Шаг 4: Deploy

Render автоматически задеплоит при push в main branch.

---

### Вариант 3: VPS (DigitalOcean, AWS EC2, Hetzner)

#### Шаг 1: Подготовка сервера

```bash
# Подключиться к VPS
ssh root@your-server-ip

# Обновить систему
apt update && apt upgrade -y

# Установить зависимости
apt install python3.12 python3.12-venv python3-pip nginx mysql-server git -y

# Установить Poetry
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"
```

#### Шаг 2: Клонирование проекта

```bash
# Создать пользователя для приложения
useradd -m -s /bin/bash sqlhero
su - sqlhero

# Клонировать репозиторий
git clone https://github.com/fedotrick/SQL-Hero.git
cd SQL-Hero/backend

# Настроить окружение
poetry install --no-dev

# Настроить .env
cp .env.example .env
nano .env  # Отредактировать
```

#### Шаг 3: Настройка MySQL

```bash
# Подключиться к MySQL
mysql -u root -p

# Создать базу данных
CREATE DATABASE sqlhero CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sqlhero'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON sqlhero.* TO 'sqlhero'@'localhost';
GRANT ALL PRIVILEGES ON `sandbox_%`.* TO 'sqlhero'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Шаг 4: Применить миграции

```bash
cd /home/sqlhero/SQL-Hero/backend
poetry run alembic upgrade head
poetry run python -m app.cli.seed_data
```

#### Шаг 5: Systemd Service

```bash
# Создать systemd service
sudo nano /etc/systemd/system/sqlhero.service
```

```ini
[Unit]
Description=SQL Hero Backend
After=network.target mysql.service

[Service]
Type=simple
User=sqlhero
Group=sqlhero
WorkingDirectory=/home/sqlhero/SQL-Hero/backend
Environment="PATH=/home/sqlhero/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/sqlhero/.local/bin/poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Запустить сервис
sudo systemctl daemon-reload
sudo systemctl enable sqlhero
sudo systemctl start sqlhero

# Проверить статус
sudo systemctl status sqlhero
```

#### Шаг 6: Nginx Reverse Proxy

```bash
# Создать конфигурацию Nginx
sudo nano /etc/nginx/sites-available/sqlhero
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активировать конфигурацию
sudo ln -s /etc/nginx/sites-available/sqlhero /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Шаг 7: SSL с Let's Encrypt

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить SSL сертификат
sudo certbot --nginx -d api.yourdomain.com

# Автоматическое обновление
sudo certbot renew --dry-run
```

---

## Frontend Deployment

### Вариант 1: Vercel (Рекомендуется)

#### Шаг 1: Установка Vercel CLI

```bash
npm install -g vercel
```

#### Шаг 2: Login

```bash
vercel login
```

#### Шаг 3: Deploy

```bash
cd frontend

# Deploy в preview
vercel

# Deploy в production
vercel --prod
```

#### Шаг 4: Environment Variables

В Vercel Dashboard → Settings → Environment Variables:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_NAME=SQL Hero
VITE_TELEGRAM_BOT_USERNAME=sql_hero_bot
```

#### Шаг 5: Custom Domain

1. Vercel Dashboard → Settings → Domains
2. Добавить домен: `sqlhero.app`
3. Настроить DNS записи (Vercel покажет инструкции)

---

### Вариант 2: Netlify

#### Шаг 1: Подключение GitHub

1. Зайдите на [netlify.com](https://netlify.com)
2. New site from Git
3. Выберите GitHub репозиторий

#### Шаг 2: Build Settings

```yaml
Base directory: frontend
Build command: pnpm build
Publish directory: frontend/dist
```

#### Шаг 3: Environment Variables

```env
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_APP_NAME=SQL Hero
VITE_TELEGRAM_BOT_USERNAME=sql_hero_bot
```

#### Шаг 4: Deploy

Netlify автоматически деплоит при push в main.

---

### Вариант 3: VPS + Nginx

```bash
# На VPS
cd /home/sqlhero/SQL-Hero/frontend

# Установить Node.js и pnpm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pnpm

# Установить зависимости
pnpm install

# Build для production
pnpm build

# Переместить dist в nginx директорию
sudo cp -r dist/* /var/www/sqlhero/
```

Nginx конфигурация:

```nginx
server {
    listen 80;
    server_name sqlhero.app www.sqlhero.app;
    root /var/www/sqlhero;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Кэширование статических файлов
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Database Management

### Managed Database (Railway, Render, AWS RDS)

#### Railway MySQL

```bash
# Автоматически создаётся при добавлении MySQL plugin
# Credentials доступны в Environment Variables
```

#### DigitalOcean Managed Database

1. Create → Databases → MySQL
2. Select region и plan
3. Скопировать connection string
4. Настроить firewall (разрешить доступ от backend)

#### AWS RDS

1. RDS → Create database
2. Engine: MySQL 8.0
3. Templates: Free tier или Production
4. Настроить Security Group
5. Скопировать endpoint

### Backup стратегия

```bash
# Автоматический backup (cron job на VPS)
crontab -e

# Backup каждый день в 3:00 AM
0 3 * * * mysqldump -u sqlhero -p'password' sqlhero | gzip > /backups/sqlhero_$(date +\%Y\%m\%d).sql.gz

# Удаление старых backups (старше 30 дней)
0 4 * * * find /backups -name "sqlhero_*.sql.gz" -mtime +30 -delete
```

---

## Мониторинг и Логирование

### Application Monitoring

#### Sentry (Error Tracking)

```bash
# Backend
poetry add sentry-sdk

# Frontend
pnpm add @sentry/react
```

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    environment="production",
)
```

#### Uptime Monitoring

- [UptimeRobot](https://uptimerobot.com/) - бесплатный
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

### Логирование

```python
# backend/app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
logging.basicConfig(handlers=[handler], level=logging.INFO)
```

---

## CI/CD Pipeline

### GitHub Actions

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install poetry
          poetry install
          poetry run pytest tests/e2e/ -v

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Security Checklist

- [ ] JWT_SECRET_KEY уникальный и безопасный
- [ ] HTTPS enabled на всех доменах
- [ ] CORS настроен только для production доменов
- [ ] Database credentials в переменных окружения
- [ ] Firewall настроен (только необходимые порты открыты)
- [ ] Rate limiting настроен
- [ ] SQL Injection защита активна (validator)
- [ ] Sandbox изоляция работает
- [ ] Secrets не закоммичены в Git
- [ ] Security headers настроены (Helmet)
- [ ] Regular security updates

---

## Rollback Plan

### Backend Rollback (Railway/Render)

```bash
# Railway
railway rollback

# Render - через Dashboard
# Deployments → Previous deployment → Rollback
```

### Database Rollback

```bash
# Откатить миграцию
poetry run alembic downgrade -1

# Восстановить из backup
mysql -u sqlhero -p sqlhero < backup_20240315.sql
```

---

## Post-Deployment

### Проверка

```bash
# Backend health
curl https://api.yourdomain.com/health

# Frontend
curl https://sqlhero.app

# Telegram Bot
# Открыть в Telegram и протестировать
```

### Мониторинг первых 24 часов

- [ ] Проверить логи на ошибки
- [ ] Проверить performance metrics
- [ ] Проверить database connections
- [ ] Проверить disk space
- [ ] Проверить error rate
- [ ] Собрать feedback от пользователей

---

**Успешного деплоя! 🚀**
