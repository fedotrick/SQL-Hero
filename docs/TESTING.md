# Тестирование SQL Hero

Полное руководство по запуску тестов и проверке качества кода.

---

## Обзор

SQL Hero использует комплексный подход к тестированию:

- **Backend:** Pytest с E2E тестами (SQLite) и интеграционными тестами (MySQL)
- **Frontend:** Jest + React Testing Library (планируется)
- **E2E:** Playwright (планируется)
- **Linting:** Ruff (Python), ESLint (TypeScript)
- **Type Checking:** MyPy (Python), TypeScript compiler
- **Code Coverage:** pytest-cov, jest coverage

---

## Backend тесты

### Быстрый старт

```bash
cd backend

# Запустить все тесты
poetry run pytest

# Запустить с verbose output
poetry run pytest -v

# Запустить с покрытием
poetry run pytest --cov=app --cov-report=html
```

### Типы тестов

#### E2E тесты (рекомендуется для разработки)

E2E тесты используют SQLite in-memory базу данных и не требуют MySQL.

```bash
# Запустить только E2E тесты
poetry run pytest tests/e2e/ -v

# Конкретный E2E тест файл
poetry run pytest tests/e2e/test_e2e_auth.py -v

# Конкретный тест
poetry run pytest tests/e2e/test_e2e_auth.py::test_register_new_user -v
```

**Преимущества E2E тестов:**
- ⚡ Быстрые (SQLite in-memory)
- 🔒 Изолированные (каждый тест со свежей БД)
- 🚀 Не требуют внешних зависимостей
- ✅ Покрывают полный flow приложения

**E2E тест файлы:**
```
tests/e2e/
├── test_e2e_auth.py              # Аутентификация
├── test_e2e_course.py            # Модули и уроки
├── test_e2e_progress.py          # Прогресс пользователя
├── test_e2e_achievements.py      # Достижения
├── test_e2e_leaderboard.py       # Таблица лидеров
├── test_e2e_dashboard.py         # Дашборд
└── test_e2e_sandbox_security.py  # Безопасность песочницы
```

#### Integration тесты

Integration тесты используют реальную MySQL базу данных.

```bash
# Запустить MySQL (если ещё не запущена)
docker-compose up mysql -d

# Запустить интеграционные тесты
poetry run pytest tests/ -v --ignore=tests/e2e/

# Или запустить все тесты (E2E + Integration)
poetry run pytest tests/ -v
```

**Когда использовать:**
- Тестирование специфичных MySQL функций
- Проверка производительности с реальной БД
- Integration с внешними сервисами

### Запуск тестов с покрытием

```bash
# HTML отчёт (рекомендуется)
poetry run pytest --cov=app --cov-report=html

# Открыть отчёт
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal отчёт
poetry run pytest --cov=app --cov-report=term

# Только покрытие без тестов
poetry run pytest --cov=app --cov-report=term-missing
```

### Фильтрация тестов

```bash
# По имени теста
poetry run pytest -k "test_auth" -v

# По маркерам (markers)
poetry run pytest -m "slow" -v
poetry run pytest -m "not slow" -v

# Первый провалившийся тест
poetry run pytest -x

# Повторить провалившиеся тесты
poetry run pytest --lf

# N последних провалившихся
poetry run pytest --lf --ff
```

### Parallel execution

```bash
# Установить pytest-xdist
poetry add --group dev pytest-xdist

# Запустить тесты параллельно
poetry run pytest -n auto

# С конкретным числом процессов
poetry run pytest -n 4
```

### Важные тесты безопасности

**⚠️ КРИТИЧЕСКИ ВАЖНО:** Всегда запускайте security тесты перед деплоем!

```bash
# Тесты безопасности песочницы
poetry run pytest tests/e2e/test_e2e_sandbox_security.py -v

# Должны пройти 100% тестов
# Проверяют защиту от:
# - SQL injection
# - DROP/ALTER операций
# - Доступа к system tables
# - Denial of Service атак
```

---

## Frontend тесты

### Быстрый старт

```bash
cd frontend

# Запустить тесты (когда будут добавлены)
pnpm test

# Watch режим
pnpm test:watch

# С покрытием
pnpm test:coverage

# Обновить snapshots
pnpm test -u
```

### Unit тесты компонентов

```bash
# Тестировать конкретный компонент
pnpm test Button.test.tsx

# Тестировать все компоненты
pnpm test --testPathPattern=components
```

### Integration тесты

```bash
# Тестировать страницы
pnpm test --testPathPattern=pages

# Тестировать API интеграцию
pnpm test --testPathPattern=services
```

---

## Linting

### Backend (Python)

```bash
cd backend

# Проверка кода
poetry run ruff check app

# Проверка с автофиксом
poetry run ruff check app --fix

# Форматирование кода
poetry run ruff format app

# Проверка форматирования (без изменений)
poetry run ruff format app --check
```

**Настройки Ruff** в `pyproject.toml`:
- Line length: 100
- Target version: Python 3.12
- Правила: pycodestyle, pyflakes, isort, flake8-bugbear

### Frontend (TypeScript)

```bash
cd frontend

# ESLint проверка
pnpm lint

# ESLint с автофиксом
pnpm lint:fix

# Prettier форматирование
pnpm format

# Проверка форматирования
pnpm format:check

# Stylelint для CSS
pnpm lint:style
pnpm lint:style:fix
```

---

## Type Checking

### Backend (MyPy)

```bash
cd backend

# Проверка типов
poetry run mypy app

# С детальным выводом
poetry run mypy app --show-error-codes

# Игнорировать конкретные ошибки
poetry run mypy app --ignore-missing-imports
```

**Настройки MyPy** в `pyproject.toml`:
- Strict mode
- No implicit optional
- Warn unused ignores

### Frontend (TypeScript)

```bash
cd frontend

# Проверка типов
pnpm type-check

# В watch режиме
pnpm type-check --watch
```

---

## Pre-commit хуки

Проект использует pre-commit для автоматической проверки перед коммитом.

### Установка

```bash
# Установить pre-commit
pip install pre-commit

# Установить git hooks
pre-commit install
```

### Использование

```bash
# Автоматически запускается при git commit
git add .
git commit -m "feat: new feature"
# Pre-commit хуки запустятся автоматически

# Запустить вручную на всех файлах
pre-commit run --all-files

# Запустить конкретный хук
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### Что проверяется

Pre-commit хуки проверяют:
- ✅ Trailing whitespace
- ✅ End of file newline
- ✅ YAML синтаксис
- ✅ Большие файлы (>500KB)
- ✅ Merge conflicts
- ✅ Ruff форматирование и линтинг (Python)
- ✅ MyPy type checking (Python)
- ✅ ESLint (TypeScript)
- ✅ Prettier (Frontend)

### Пропуск хуков (не рекомендуется)

```bash
# Пропустить pre-commit хуки
git commit --no-verify -m "message"

# Или
git commit -n -m "message"
```

---

## Coverage

### Целевые показатели

- **Backend:** 90%+ (текущее: 92%)
- **Frontend:** 85%+ (когда будут добавлены тесты)
- **Critical paths:** 100% (auth, security, payments)

### Backend Coverage

```bash
cd backend

# Генерация HTML отчёта
poetry run pytest --cov=app --cov-report=html

# Терминальный отчёт
poetry run pytest --cov=app --cov-report=term-missing

# XML для CI/CD
poetry run pytest --cov=app --cov-report=xml

# Fail если покрытие ниже порога
poetry run pytest --cov=app --cov-fail-under=90
```

### Frontend Coverage

```bash
cd frontend

# С генерацией отчёта
pnpm test:coverage

# Открыть отчёт
open coverage/index.html
```

---

## CI/CD Integration

### GitHub Actions (пример)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Poetry
        run: curl -sSL https://install.python-poetry.org | python3 -
      
      - name: Install dependencies
        run: |
          cd backend
          poetry install
      
      - name: Run E2E tests
        run: |
          cd backend
          poetry run pytest tests/e2e/ -v --cov=app
      
      - name: Security tests
        run: |
          cd backend
          poetry run pytest tests/e2e/test_e2e_sandbox_security.py -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Install dependencies
        run: |
          cd frontend
          pnpm install
      
      - name: Lint
        run: |
          cd frontend
          pnpm lint
      
      - name: Type check
        run: |
          cd frontend
          pnpm type-check
```

---

## Performance Testing

### Backend

```bash
# Установить locust
poetry add --group dev locust

# Запустить load test
locust -f tests/performance/locustfile.py

# Headless mode
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 5m
```

### Frontend

```bash
# Lighthouse CI
npm install -g @lhci/cli

# Запустить Lighthouse
lhci autorun

# Для конкретного URL
lighthouse http://localhost:5173 --view
```

---

## Debugging тестов

### Backend

```bash
# Запустить с pdb debugger
poetry run pytest -s --pdb

# Остановиться на первой ошибке
poetry run pytest -x --pdb

# Детальный вывод
poetry run pytest -vv

# Показать print statements
poetry run pytest -s

# Показать locals при ошибке
poetry run pytest -l
```

### Логирование в тестах

```python
import logging

def test_something(caplog):
    caplog.set_level(logging.DEBUG)
    # Ваш код
    assert "Expected log message" in caplog.text
```

---

## Best Practices

### Backend тесты

1. **Используйте fixtures** для повторяющейся setup логики
2. **Используйте E2E тесты** для быстрой разработки
3. **Тестируйте happy path и edge cases**
4. **Используйте parametrize** для множественных сценариев
5. **Mock внешние сервисы** (Telegram API, email)
6. **Всегда проверяйте security тесты** перед деплоем

```python
# Хороший пример
import pytest

@pytest.mark.parametrize("xp,expected_level", [
    (0, 1),
    (100, 2),
    (1000, 5),
])
def test_calculate_level(xp, expected_level):
    assert calculate_level(xp) == expected_level
```

### Frontend тесты

1. **Тестируйте поведение, а не реализацию**
2. **Используйте Testing Library queries** (getByRole, getByText)
3. **Mock API calls** с MSW или jest.mock
4. **Тестируйте accessibility**
5. **Snapshot тесты для UI компонентов**

---

## Troubleshooting

### "Database connection failed"

```bash
# Убедитесь, что MySQL запущена (для integration тестов)
docker-compose up mysql -d

# Или используйте E2E тесты (SQLite)
poetry run pytest tests/e2e/ -v
```

### "Import errors"

```bash
# Переустановите зависимости
poetry install

# Проверьте PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "Tests are slow"

```bash
# Используйте E2E тесты вместо integration
poetry run pytest tests/e2e/ -v

# Или запустите параллельно
poetry run pytest -n auto
```

### "Coverage не генерируется"

```bash
# Убедитесь, что установлен pytest-cov
poetry add --group dev pytest-cov

# Проверьте .coveragerc или pyproject.toml настройки
```

---

## Полезные команды

### Makefile команды (если есть)

```bash
# Запустить все проверки
make test

# Только линтинг
make lint

# Только type checking
make typecheck

# Всё вместе (lint + typecheck + test)
make check
```

### Одной командой всё

```bash
# Backend: lint + typecheck + test
cd backend
poetry run ruff check app && \
poetry run ruff format app --check && \
poetry run mypy app && \
poetry run pytest tests/e2e/ -v

# Frontend: lint + typecheck + test
cd frontend
pnpm lint && pnpm type-check && pnpm test
```

---

## Дополнительные ресурсы

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)

---

**Следующие шаги:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production деплой
- [CONTRIBUTING.md](CONTRIBUTING.md) - Процесс разработки
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Решение проблем

---

**Happy Testing! ✅**
