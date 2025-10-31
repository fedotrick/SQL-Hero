# Monorepo проект

Полностью интегрированный monorepo проект с бэкендом на FastAPI и фронтендом на React.

## 📁 Структура проекта

```
.
├── backend/              # FastAPI бэкенд
│   ├── app/             # Исходный код приложения
│   ├── tests/           # Тесты
│   ├── Dockerfile       # Production Dockerfile
│   ├── pyproject.toml   # Конфигурация Poetry и инструментов
│   └── .env.example     # Пример переменных окружения
├── frontend/            # React фронтенд
│   ├── src/            # Исходный код приложения
│   ├── public/         # Статические файлы
│   ├── Dockerfile      # Production Dockerfile
│   ├── Dockerfile.dev  # Development Dockerfile
│   ├── package.json    # Зависимости и скрипты
│   └── .env.example    # Пример переменных окружения
├── infrastructure/      # Инфраструктурные файлы
│   ├── docker/         # Docker конфигурация
│   └── scripts/        # Утилитарные скрипты
├── docs/               # Документация проекта
├── docker-compose.yml  # Конфигурация для локальной разработки
├── .editorconfig       # Настройки редактора
├── .gitignore          # Игнорируемые файлы Git
└── .pre-commit-config.yaml  # Конфигурация pre-commit хуков

```

## 🚀 Быстрый старт

### Предварительные требования

- **Python 3.12+** с Poetry
- **Node.js 20+** с pnpm
- **Docker** и **Docker Compose**
- **Git**

### Установка

1. **Клонируйте репозиторий:**

```bash
git clone <repository-url>
cd <repository-name>
```

2. **Запустите скрипт установки:**

```bash
./infrastructure/scripts/setup.sh
```

Или выполните вручную:

```bash
# Установить pre-commit
pip3 install pre-commit
pre-commit install

# Установить зависимости бэкенда
cd backend
poetry install
cd ..

# Установить зависимости фронтенда
cd frontend
pnpm install
cd ..
```

3. **Настройте переменные окружения:**

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### Запуск в Docker

Самый простой способ запустить весь стек:

```bash
docker-compose up
```

Сервисы будут доступны по адресам:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **Backend API Docs:** http://localhost:8000/docs
- **MySQL:** localhost:3306

Для остановки:

```bash
docker-compose down
```

Для пересборки после изменений:

```bash
docker-compose up --build
```

### Локальная разработка (без Docker)

#### Backend

```bash
cd backend

# Запустить сервер разработки
poetry run uvicorn app.main:app --reload

# Запустить тесты
poetry run pytest

# Линтинг
poetry run ruff check app

# Форматирование
poetry run ruff format app

# Проверка типов
poetry run mypy app
```

Бэкенд будет доступен по адресу: http://localhost:8000

#### Frontend

```bash
cd frontend

# Запустить сервер разработки
pnpm dev

# Сборка для продакшна
pnpm build

# Линтинг
pnpm lint

# Форматирование
pnpm format

# Проверка форматирования
pnpm format:check

# Линтинг стилей
pnpm lint:style
```

Фронтенд будет доступен по адресу: http://localhost:5173

## 🔧 Технологический стек

### Backend
- **Framework:** FastAPI 0.120+
- **Server:** Uvicorn
- **Package Manager:** Poetry
- **Linter:** Ruff
- **Type Checker:** MyPy
- **Testing:** Pytest

### Frontend
- **Framework:** React 19+
- **Language:** TypeScript
- **Build Tool:** Vite 7+
- **Package Manager:** pnpm
- **Linter:** ESLint
- **Formatter:** Prettier
- **Style Linter:** Stylelint

### Infrastructure
- **Database:** MySQL 8.0
- **Containerization:** Docker + Docker Compose
- **Git Hooks:** pre-commit

## 📝 Переменные окружения

### Backend (.env)

```env
DATABASE_URL=mysql+aiomysql://user:password@mysql:3306/appdb
DEBUG=true
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## 🔍 Линтинг и форматирование

Проект использует pre-commit хуки для автоматической проверки кода перед коммитом.

### Запуск вручную

```bash
# Линтинг всего проекта
./infrastructure/scripts/lint.sh

# Только бэкенд
cd backend
poetry run ruff check app
poetry run mypy app

# Только фронтенд
cd frontend
pnpm lint
pnpm format:check
```

### Pre-commit хуки

Pre-commit хуки автоматически запускаются перед каждым коммитом. Они проверяют:

- Trailing whitespace
- End of file
- YAML синтаксис
- Большие файлы
- Конфликты слияния
- Python код (Ruff форматирование и линтинг)
- Python типы (MyPy)
- JavaScript/TypeScript код (ESLint)
- Форматирование фронтенда (Prettier)

Для ручного запуска:

```bash
pre-commit run --all-files
```

## 🧪 Тестирование

```bash
# Запустить все тесты
./infrastructure/scripts/test.sh

# Только тесты бэкенда
cd backend
poetry run pytest

# Тесты с покрытием
poetry run pytest --cov=app
```

## 🏗️ Workflow разработки

1. **Создайте новую ветку:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Внесите изменения** и убедитесь, что код соответствует стандартам:
   ```bash
   ./infrastructure/scripts/lint.sh
   ./infrastructure/scripts/test.sh
   ```

3. **Закоммитьте изменения:**
   ```bash
   git add .
   git commit -m "feat: описание изменений"
   ```
   Pre-commit хуки автоматически проверят ваш код.

4. **Отправьте изменения:**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Создайте Pull Request** в основную ветку.

## 📚 Дополнительные команды

### Docker

```bash
# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Перезапуск сервиса
docker-compose restart backend

# Выполнить команду в контейнере
docker-compose exec backend poetry run pytest

# Очистить volumes
docker-compose down -v
```

### База данных

```bash
# Подключиться к MySQL
docker-compose exec mysql mysql -u user -p appdb
# Пароль: password

# Создать бэкап
docker-compose exec mysql mysqldump -u user -p appdb > backup.sql

# Восстановить из бэкапа
docker-compose exec -T mysql mysql -u user -p appdb < backup.sql
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'feat: Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

### Стиль коммитов

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - новая функция
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование, пропущенные точки с запятой и т.д.
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление задач сборки, конфигураций и т.д.

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 📞 Поддержка

Если у вас возникли вопросы или проблемы, пожалуйста, создайте issue в репозитории.

---

**Приятной разработки! 🚀**
