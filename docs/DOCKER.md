# Docker руководство для SQL Hero

Полное руководство по работе с Docker и Docker Compose в проекте SQL Hero.

---

## Обзор

Проект использует Docker Compose для orchestration трёх основных сервисов:

1. **MySQL** - База данных
2. **Backend** - FastAPI приложение
3. **Frontend** - React приложение (Vite dev server)

---

## Структура docker-compose.yml

```yaml
services:
  mysql:
    # MySQL 8.0 контейнер
    # Порт: 3306
    # Credentials: user/password, root/rootpassword
    # Database: sqlhero
    # Volume: mysql_data (персистентное хранилище)
    
  backend:
    # FastAPI backend
    # Порт: 8000
    # Зависит от: mysql
    # Volume mounts: app/, alembic/, alembic.ini
    
  frontend:
    # Vite dev server
    # Порт: 5173
    # Зависит от: backend
    # Volume mounts: src/, public/
```

---

## Основные команды

### Запуск сервисов

```bash
# Запустить все сервисы в фоновом режиме
docker-compose up -d

# Запустить с логами в терминале
docker-compose up

# Запустить только определённые сервисы
docker-compose up mysql backend -d
docker-compose up frontend

# Запустить с пересборкой образов
docker-compose up --build -d
```

### Остановка сервисов

```bash
# Остановить все сервисы (данные сохранятся)
docker-compose down

# Остановить и удалить volumes (БД будет очищена!)
docker-compose down -v

# Остановить конкретный сервис
docker-compose stop backend

# Перезапустить сервис
docker-compose restart backend
```

### Просмотр статуса

```bash
# Проверить статус всех контейнеров
docker-compose ps

# Детальная информация
docker-compose ps -a

# Использование ресурсов
docker stats
```

### Просмотр логов

```bash
# Все логи
docker-compose logs

# Логи с follow (в реальном времени)
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs backend
docker-compose logs -f frontend
docker-compose logs --tail=100 mysql

# Логи за последние 10 минут
docker-compose logs --since 10m
```

---

## Работа с контейнерами

### Выполнение команд в контейнерах

```bash
# Backend команды
docker-compose exec backend bash
docker-compose exec backend poetry run pytest
docker-compose exec backend poetry run alembic upgrade head
docker-compose exec backend poetry run python -m app.cli.seed_data

# Frontend команды
docker-compose exec frontend sh
docker-compose exec frontend pnpm lint

# MySQL команды
docker-compose exec mysql bash
docker-compose exec mysql mysql -u user -p sqlhero
docker-compose exec mysql mysqldump -u user -p sqlhero > backup.sql
```

### Запуск одноразовых команд

```bash
# Запустить команду без запуска основного процесса контейнера
docker-compose run --rm backend poetry run pytest
docker-compose run --rm frontend pnpm test

# С переопределением entrypoint
docker-compose run --rm --entrypoint bash backend
```

---

## Сборка образов

### Пересборка образов

```bash
# Пересобрать все образы
docker-compose build

# Пересобрать без кэша
docker-compose build --no-cache

# Пересобрать конкретный сервис
docker-compose build backend

# Pull последние base images и пересобрать
docker-compose build --pull
```

### Просмотр образов

```bash
# Список образов проекта
docker-compose images

# Все Docker образы
docker images

# Размер образов
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

---

## Работа с базой данных MySQL

### Подключение к MySQL

```bash
# Через docker-compose exec
docker-compose exec mysql mysql -u user -p
# Пароль: password

# Подключение к конкретной БД
docker-compose exec mysql mysql -u user -p sqlhero

# Как root
docker-compose exec mysql mysql -u root -p
# Пароль: rootpassword
```

### Backup и Restore

#### Создание backup

```bash
# Полный backup
docker-compose exec mysql mysqldump -u user -p sqlhero > backup_$(date +%Y%m%d_%H%M%S).sql

# Только структура (без данных)
docker-compose exec mysql mysqldump -u user -p --no-data sqlhero > schema.sql

# Только данные (без структуры)
docker-compose exec mysql mysqldump -u user -p --no-create-info sqlhero > data.sql

# Сжатый backup
docker-compose exec mysql mysqldump -u user -p sqlhero | gzip > backup.sql.gz
```

#### Восстановление из backup

```bash
# Восстановить из backup
docker-compose exec -T mysql mysql -u user -p sqlhero < backup.sql

# Восстановить из сжатого backup
gunzip < backup.sql.gz | docker-compose exec -T mysql mysql -u user -p sqlhero
```

### Пересоздание базы данных

```bash
# Остановить и удалить volume
docker-compose down -v

# Запустить MySQL
docker-compose up mysql -d

# Дождаться готовности (проверить health)
docker-compose ps mysql

# Применить миграции
docker-compose exec backend poetry run alembic upgrade head

# Загрузить данные
docker-compose exec backend poetry run python -m app.cli.seed_data
```

---

## Volumes

### Именованные volumes

Проект использует именованный volume `mysql_data` для хранения данных MySQL.

```bash
# Список volumes
docker volume ls

# Информация о volume
docker volume inspect sql-hero_mysql_data

# Удалить неиспользуемые volumes
docker volume prune

# Удалить конкретный volume (ОСТОРОЖНО!)
docker volume rm sql-hero_mysql_data
```

### Bind mounts

Backend и Frontend используют bind mounts для hot reload:

**Backend:**
- `./backend/app:/app/app` - код приложения
- `./backend/alembic:/app/alembic` - миграции
- `./backend/alembic.ini:/app/alembic.ini` - конфиг Alembic

**Frontend:**
- `./frontend/src:/app/src` - исходный код
- `./frontend/public:/app/public` - статические файлы

---

## Сети

### Просмотр сетей

```bash
# Список сетей
docker network ls

# Информация о сети проекта
docker network inspect sql-hero_default

# Контейнеры в сети
docker network inspect sql-hero_default --format '{{range .Containers}}{{.Name}} {{end}}'
```

### Подключение к сети

По умолчанию все сервисы находятся в одной сети и могут обращаться друг к другу по имени сервиса:
- `mysql` - MySQL сервер
- `backend` - Backend API
- `frontend` - Frontend dev server

---

## Production образы

### Backend Dockerfile

```dockerfile
# Production образ backend оптимизирован для размера и безопасности
# Использует multi-stage build
# Включает только production зависимости

# Сборка production образа backend
docker build -t sqlhero-backend:latest ./backend
```

### Frontend Dockerfile

```dockerfile
# Production образ frontend содержит статические файлы
# Использует nginx для serving

# Сборка production образа frontend
docker build -t sqlhero-frontend:latest ./frontend
```

### Запуск production образов

```bash
# Использовать production образы вместо dev
docker-compose -f docker-compose.prod.yml up -d
```

---

## Оптимизация

### Уменьшение размера образов

```bash
# Очистить неиспользуемые образы
docker image prune

# Очистить build cache
docker builder prune

# Очистить всё (ОСТОРОЖНО!)
docker system prune -a
```

### Ускорение сборки

```bash
# Использовать BuildKit для параллельной сборки
DOCKER_BUILDKIT=1 docker-compose build

# Или экспортировать переменную
export DOCKER_BUILDKIT=1
docker-compose build
```

### Layer caching

Docker кэширует слои образа. Для эффективного использования кэша:

1. Сначала копируйте файлы зависимостей (`pyproject.toml`, `package.json`)
2. Устанавливайте зависимости
3. Только потом копируйте исходный код

---

## Отладка

### Проверка health контейнеров

```bash
# Проверить health status
docker-compose ps

# Детальная информация о health check
docker inspect --format='{{json .State.Health}}' <container_id> | jq
```

### Inspect контейнеров

```bash
# Детальная информация о контейнере
docker-compose exec backend env
docker-compose inspect backend

# Переменные окружения
docker-compose exec backend printenv

# Mounted volumes
docker inspect <container_id> --format='{{json .Mounts}}' | jq
```

### Логи контейнеров

```bash
# Логи с timestamps
docker-compose logs -f -t backend

# Цветные логи
docker-compose logs --no-log-prefix -f backend | bat -l log

# Экспорт логов в файл
docker-compose logs backend > backend_logs.txt
```

---

## Troubleshooting

### Контейнер не запускается

```bash
# Проверить логи
docker-compose logs backend

# Проверить exit code
docker-compose ps -a

# Попробовать запустить вручную
docker-compose run --rm backend bash
```

### Порты заняты

```bash
# Найти процесс на порту
lsof -i :8000
netstat -tulpn | grep 8000

# Изменить порт в docker-compose.yml
ports:
  - "8001:8000"  # host:container
```

### Проблемы с volumes

```bash
# Пересоздать volumes
docker-compose down -v
docker volume prune
docker-compose up -d

# Проверить permissions
docker-compose exec backend ls -la /app
```

### Медленная работа (особенно на Mac/Windows)

```bash
# Использовать delegated mount для лучшей производительности
volumes:
  - ./backend/app:/app/app:delegated

# Или использовать Docker Desktop с включённым VirtioFS
```

### Нехватка места

```bash
# Проверить использование места
docker system df

# Очистить неиспользуемые данные
docker system prune -a --volumes

# Очистить build cache
docker builder prune -a
```

---

## Best Practices

### Development

1. **Используйте bind mounts** для hot reload
2. **Не используйте `--no-cache`** без необходимости (замедляет сборку)
3. **Запускайте в фоне** (`-d`) для удобства
4. **Следите за логами** (`logs -f`) при отладке
5. **Регулярно обновляйте** base images

### Production

1. **Используйте specific tags** вместо `latest`
2. **Multi-stage builds** для оптимизации размера
3. **Non-root user** внутри контейнера
4. **Health checks** для мониторинга
5. **Secrets через environment** или Docker secrets
6. **Read-only filesystem** где возможно

---

## Полезные алиасы

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
# Docker Compose алиасы
alias dc='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcexec='docker-compose exec'
alias dcbuild='docker-compose build'
alias dcrestart='docker-compose restart'

# SQL Hero specific
alias sqlhero-up='docker-compose up -d'
alias sqlhero-down='docker-compose down'
alias sqlhero-logs='docker-compose logs -f'
alias sqlhero-backend='docker-compose exec backend bash'
alias sqlhero-frontend='docker-compose exec frontend sh'
alias sqlhero-mysql='docker-compose exec mysql mysql -u user -p sqlhero'
alias sqlhero-migrate='docker-compose exec backend poetry run alembic upgrade head'
alias sqlhero-seed='docker-compose exec backend poetry run python -m app.cli.seed_data'
alias sqlhero-test='docker-compose exec backend poetry run pytest'
```

---

## Docker Compose Override

Для локальных изменений без модификации основного файла:

Создайте `docker-compose.override.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Другой порт
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
  
  frontend:
    ports:
      - "3000:5173"
    command: pnpm dev --port 5173 --host 0.0.0.0
```

Docker Compose автоматически применит override файл.

---

## Мониторинг

### Использование ресурсов

```bash
# Real-time статистика
docker stats

# Только SQL Hero контейнеры
docker stats $(docker-compose ps -q)

# Форматированный вывод
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Проверка здоровья

```bash
# Health check всех сервисов
docker-compose ps

# Автоматическая проверка
watch -n 5 'docker-compose ps'
```

---

## Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

**Следующие шаги:**
- [RUN_LOCAL.md](RUN_LOCAL.md) - Локальная разработка
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production деплой
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Решение проблем

---

**Happy Dockering! 🐳**
