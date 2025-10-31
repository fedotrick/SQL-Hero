# Архитектура проекта

## Обзор

Проект представляет собой monorepo с четко разделенными слоями:

- **Backend (FastAPI)** - RESTful API сервер
- **Frontend (React)** - Веб-приложение
- **Infrastructure** - Docker, скрипты и конфигурация
- **Docs** - Документация

## Backend

### Технологии
- FastAPI - современный, быстрый веб-фреймворк
- Uvicorn - ASGI сервер
- Pydantic - валидация данных
- Poetry - управление зависимостями

### Структура
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Точка входа приложения
│   ├── api/             # API эндпоинты (будущее)
│   ├── models/          # Модели данных (будущее)
│   ├── services/        # Бизнес-логика (будущее)
│   └── config.py        # Конфигурация (будущее)
└── tests/               # Тесты
```

### Принципы
- Чистая архитектура
- Разделение ответственности
- Dependency Injection
- Тестируемость

## Frontend

### Технологии
- React 19 - UI библиотека
- TypeScript - типизированный JavaScript
- Vite - быстрый сборщик
- pnpm - эффективный менеджер пакетов

### Структура
```
frontend/
├── src/
│   ├── components/      # React компоненты (будущее)
│   ├── pages/           # Страницы (будущее)
│   ├── hooks/           # Кастомные хуки (будущее)
│   ├── services/        # API клиенты (будущее)
│   ├── types/           # TypeScript типы (будущее)
│   └── App.tsx          # Главный компонент
└── public/              # Статические файлы
```

### Принципы
- Компонентный подход
- Функциональное программирование
- Type-safe API взаимодействие
- Responsive дизайн

## Инфраструктура

### Docker
- Изолированные контейнеры для каждого сервиса
- Docker Compose для локальной разработки
- Hot reload в development режиме

### База данных
- MySQL 8.0
- Volumes для персистентности данных
- Health checks

## Взаимодействие между сервисами

```
Frontend (React) <--HTTP--> Backend (FastAPI) <--SQL--> MySQL
     :5173                       :8000                  :3306
```

## Инструменты разработки

### Backend
- **Ruff** - быстрый линтер и форматтер
- **MyPy** - статическая проверка типов
- **Pytest** - тестирование

### Frontend
- **ESLint** - линтер JavaScript/TypeScript
- **Prettier** - форматтер кода
- **Stylelint** - линтер CSS

### Общие
- **pre-commit** - Git хуки для проверки кода
- **EditorConfig** - единообразие стиля кода

## Развертывание

### Development
```bash
docker-compose up
```

### Production
Для production требуется:
1. Сборка Docker образов
2. Настройка переменных окружения
3. Настройка reverse proxy (nginx)
4. SSL сертификаты
5. Мониторинг и логирование

## Безопасность

- CORS настроен для development
- Переменные окружения для чувствительных данных
- TypeScript для type safety
- Валидация данных с Pydantic

## Будущие улучшения

- [ ] Аутентификация и авторизация (JWT)
- [ ] ORM интеграция (SQLAlchemy)
- [ ] Миграции базы данных (Alembic)
- [ ] Redis для кэширования
- [ ] State management (Zustand/Redux)
- [ ] E2E тесты (Playwright)
- [ ] CI/CD pipeline
- [ ] Kubernetes deployment
