# Архитектура SQL Hero

Подробное описание архитектуры проекта SQL Hero.

---

## Обзор системы

SQL Hero — это Telegram WebApp для интерактивного изучения MySQL с геймификацией.

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram Users                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Telegram Bot API                          │
│              (BotFather, WebApp API)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│   Frontend       │    │   Backend        │
│   (React + TS)   │◄───┤   (FastAPI)      │
│   Port 5173      │    │   Port 8000      │
└──────────────────┘    └────┬─────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
        ┌─────────────────┐    ┌─────────────────┐
        │  Main Database  │    │  Sandbox MySQL  │
        │  (User data)    │    │  (User schemas) │
        │  MySQL 8.0      │    │  MySQL 8.0      │
        └─────────────────┘    └─────────────────┘
```

---

## Backend архитектура

### Технологии

- **FastAPI** — асинхронный веб-фреймворк
- **SQLAlchemy 2.0** — async ORM
- **Alembic** — миграции БД
- **Pydantic** — валидация данных
- **PyJWT** — JWT токены для аутентификации
- **aiomysql** — асинхронный драйвер MySQL
- **Uvicorn** — ASGI сервер

### Структура приложения

```
backend/
├── app/
│   ├── core/                   # Ядро приложения
│   │   ├── config.py           # Настройки из .env
│   │   ├── database.py         # Database engine и session
│   │   ├── security.py         # JWT, Telegram auth, password
│   │   └── exceptions.py       # Кастомные исключения
│   │
│   ├── models/                 # SQLAlchemy модели
│   │   ├── database.py         # Все модели БД
│   │   └── __init__.py
│   │
│   ├── schemas/                # Pydantic схемы
│   │   ├── user.py             # User schemas
│   │   ├── course.py           # Module, Lesson schemas
│   │   ├── progress.py         # Progress schemas
│   │   ├── achievement.py      # Achievement schemas
│   │   └── sandbox.py          # Sandbox schemas
│   │
│   ├── routers/                # API endpoints
│   │   ├── auth.py             # /api/auth/*
│   │   ├── course.py           # /api/modules/*, /api/lessons/*
│   │   ├── progress.py         # /api/progress/*
│   │   ├── achievements.py     # /api/achievements/*
│   │   ├── leaderboard.py      # /api/leaderboard/*
│   │   ├── dashboard.py        # /api/dashboard/*
│   │   └── sandbox.py          # /api/sandbox/*
│   │
│   ├── services/               # Бизнес-логика
│   │   ├── user_service.py     # Управление пользователями
│   │   ├── course_service.py   # Модули и уроки
│   │   ├── progress_service.py # Прогресс и XP
│   │   ├── achievement_service.py # Достижения
│   │   ├── sandbox_service.py  # SQL песочница
│   │   ├── leaderboard_service.py # Таблица лидеров
│   │   └── notification_service.py # Уведомления (future)
│   │
│   ├── cli/                    # CLI команды
│   │   ├── seed_data.py        # Загрузка начальных данных
│   │   ├── check_db.py         # Проверка БД
│   │   └── clear_db.py         # Очистка БД (dev)
│   │
│   └── main.py                 # Точка входа FastAPI app
│
├── tests/                      # Тесты
│   ├── e2e/                    # E2E тесты (SQLite)
│   │   ├── conftest.py         # Fixtures для E2E
│   │   ├── test_e2e_auth.py
│   │   ├── test_e2e_course.py
│   │   ├── test_e2e_progress.py
│   │   ├── test_e2e_achievements.py
│   │   ├── test_e2e_leaderboard.py
│   │   ├── test_e2e_dashboard.py
│   │   └── test_e2e_sandbox_security.py
│   │
│   └── conftest.py             # Общие fixtures
│
├── alembic/                    # Миграции
│   ├── versions/               # Файлы миграций
│   ├── env.py                  # Alembic environment
│   └── script.py.mako          # Шаблон миграций
│
├── pyproject.toml              # Poetry конфигурация
├── alembic.ini                 # Alembic конфигурация
├── Dockerfile                  # Production образ
└── .env.example                # Пример переменных окружения
```

### Слои приложения

#### 1. Routers (API Layer)

Определяют HTTP endpoints и обрабатывают request/response.

```python
# app/routers/auth.py
@router.post("/register", response_model=UserResponse)
async def register(
    data: TelegramInitData,
    db: AsyncSession = Depends(get_session)
):
    user = await user_service.register_user(db, data)
    return user
```

#### 2. Services (Business Logic Layer)

Содержат бизнес-логику, независимую от HTTP.

```python
# app/services/user_service.py
async def register_user(db: AsyncSession, data: TelegramInitData) -> User:
    # Проверка подписи Telegram
    # Создание/обновление пользователя
    # Логирование активности
    return user
```

#### 3. Models (Data Layer)

SQLAlchemy модели, представляющие таблицы БД.

```python
# app/models/database.py
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None]
    xp: Mapped[int] = mapped_column(default=0)
    level: Mapped[int] = mapped_column(default=1)
```

#### 4. Schemas (Validation Layer)

Pydantic схемы для валидации и сериализации данных.

```python
# app/schemas/user.py
class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    xp: int
    level: int
    
    model_config = ConfigDict(from_attributes=True)
```

---

## Database схема

### Основные таблицы

#### users
Хранит информацию о пользователях.

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    xp INT DEFAULT 0,
    level INT DEFAULT 1,
    streak_days INT DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### modules
10 модулей курса SQL.

```sql
CREATE TABLE modules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INT NOT NULL,
    is_locked BOOLEAN DEFAULT FALSE,
    lessons_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### lessons
100+ уроков с теорией, задачами и тестами.

```sql
CREATE TABLE lessons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    module_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,  -- Теория урока
    lesson_type ENUM('theory', 'task', 'quiz') NOT NULL,
    order_index INT NOT NULL,
    xp_reward INT DEFAULT 10,
    
    -- Для типа 'task'
    task_description TEXT,
    initial_db_state JSON,  -- Начальное состояние БД
    expected_result JSON,   -- Ожидаемый результат
    solution_query TEXT,    -- Правильное решение (скрыто)
    hints JSON,             -- Подсказки
    
    -- Для типа 'quiz'
    quiz_question TEXT,
    quiz_options JSON,
    quiz_correct_answer VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);
```

#### user_progress
Прогресс пользователя по урокам.

```sql
CREATE TABLE user_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    lesson_id INT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    attempts INT DEFAULT 0,
    xp_earned INT DEFAULT 0,
    time_spent_seconds INT DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_user_lesson (user_id, lesson_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);
```

#### achievements
50+ достижений для мотивации.

```sql
CREATE TABLE achievements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    achievement_type ENUM('progress', 'streak', 'skill', 'special') NOT NULL,
    icon VARCHAR(50),  -- Emoji или иконка
    xp_reward INT DEFAULT 0,
    
    -- Условия для получения
    condition_type VARCHAR(50),  -- 'complete_lessons', 'reach_level', etc.
    condition_value JSON,
    
    is_hidden BOOLEAN DEFAULT FALSE,  -- Скрытое достижение
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### user_achievements
Достижения, открытые пользователями.

```sql
CREATE TABLE user_achievements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    achievement_id INT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_user_achievement (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);
```

#### activity_logs
Логи активности для тепловой карты.

```sql
CREATE TABLE activity_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    activity_date DATE NOT NULL,
    actions_count INT DEFAULT 1,
    xp_earned INT DEFAULT 0,
    
    UNIQUE KEY unique_user_date (user_id, activity_date),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Relationships

```
users
  ├─ user_progress (one-to-many)
  ├─ user_achievements (one-to-many)
  └─ activity_logs (one-to-many)

modules
  └─ lessons (one-to-many)

lessons
  └─ user_progress (one-to-many)

achievements
  └─ user_achievements (one-to-many)
```

---

## Frontend архитектура

### Технологии

- **React 19** — UI библиотека
- **TypeScript** — типизация
- **Vite 7** — build tool и dev server
- **React Router** — client-side routing
- **Axios** — HTTP клиент
- **Telegram WebApp API** — интеграция с Telegram
- **Monaco Editor** (или Code Mirror) — SQL редактор
- **Recharts** (или Chart.js) — графики и диаграммы

### Структура приложения

```
frontend/
├── src/
│   ├── pages/                  # Страницы приложения
│   │   ├── Dashboard.tsx       # Главная страница
│   │   ├── ModulesMap.tsx      # Карта модулей
│   │   ├── ModuleDetail.tsx    # Детали модуля
│   │   ├── Lesson.tsx          # Страница урока
│   │   ├── Leaderboard.tsx     # Таблица лидеров
│   │   ├── Achievements.tsx    # Достижения
│   │   └── Profile.tsx         # Профиль пользователя
│   │
│   ├── components/             # Переиспользуемые компоненты
│   │   ├── Layout/             # Layout компоненты
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── Footer.tsx
│   │   │
│   │   ├── Lesson/             # Компоненты урока
│   │   │   ├── TheoryContent.tsx
│   │   │   ├── TaskContent.tsx
│   │   │   ├── QuizContent.tsx
│   │   │   └── LessonProgress.tsx
│   │   │
│   │   ├── SQLEditor/          # SQL редактор
│   │   │   ├── Editor.tsx
│   │   │   ├── ResultTable.tsx
│   │   │   └── QueryHistory.tsx
│   │   │
│   │   ├── Dashboard/          # Компоненты дашборда
│   │   │   ├── StatsCard.tsx
│   │   │   ├── ProgressChart.tsx
│   │   │   ├── ActivityHeatmap.tsx
│   │   │   └── RecentAchievements.tsx
│   │   │
│   │   └── UI/                 # UI компоненты
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Modal.tsx
│   │       ├── Loading.tsx
│   │       └── ErrorBoundary.tsx
│   │
│   ├── services/               # API клиенты
│   │   ├── api.ts              # Axios instance
│   │   ├── authService.ts      # Authentication
│   │   ├── courseService.ts    # Modules and Lessons
│   │   ├── progressService.ts  # User progress
│   │   ├── sandboxService.ts   # SQL execution
│   │   ├── achievementService.ts
│   │   └── leaderboardService.ts
│   │
│   ├── hooks/                  # Custom hooks
│   │   ├── useAuth.ts          # Authentication state
│   │   ├── useUser.ts          # User data
│   │   ├── useLessons.ts       # Lessons data
│   │   ├── useTelegram.ts      # Telegram WebApp API
│   │   └── useLocalStorage.ts  # Local storage
│   │
│   ├── types/                  # TypeScript types
│   │   ├── user.ts
│   │   ├── course.ts
│   │   ├── progress.ts
│   │   ├── achievement.ts
│   │   └── telegram.ts
│   │
│   ├── utils/                  # Утилиты
│   │   ├── telegramAuth.ts     # Telegram init data parsing
│   │   ├── xpCalculator.ts     # XP and level calculations
│   │   ├── dateUtils.ts
│   │   └── validators.ts
│   │
│   ├── styles/                 # Стили
│   │   ├── globals.css
│   │   └── themes/
│   │
│   ├── App.tsx                 # Главный компонент
│   ├── main.tsx                # Точка входа
│   └── vite-env.d.ts           # Vite types
│
├── public/                     # Статические файлы
│   ├── images/
│   └── favicon.ico
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.example
```

### State Management

Проект использует React hooks и Context API для управления состоянием.

```typescript
// src/contexts/AuthContext.tsx
export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  
  // Authentication logic
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

## Sandbox архитектура

### Безопасная изоляция SQL запросов

SQL Hero использует изолированные MySQL схемы для каждого пользователя.

```
Main Database (sqlhero)
  ├─ users, modules, lessons, ... (app data)
  
User Sandboxes (per user)
  ├─ sandbox_user_123 (user 123's schema)
  ├─ sandbox_user_456 (user 456's schema)
  └─ sandbox_user_789 (user 789's schema)
```

### Query Execution Flow

```
1. User submits SQL query
   ↓
2. Frontend → Backend API (/api/sandbox/execute)
   ↓
3. Validate query (Query Validator)
   ├─ Block dangerous operations (DROP, ALTER, etc.)
   ├─ Block system tables (mysql.user, etc.)
   └─ Block excessive result sets
   ↓
4. Create/Use user sandbox schema (sandbox_user_{id})
   ↓
5. Setup lesson initial data (if first time)
   ↓
6. Execute query with timeout (5 seconds)
   ↓
7. Compare result with expected_result
   ↓
8. Return result to frontend
   ├─ Success: mark lesson complete, award XP
   └─ Failure: show error, give hints
```

### Security measures

1. **Query Validator** — блокирует опасные операции
2. **Schema Isolation** — каждый пользователь в своей схеме
3. **Timeout** — запросы ограничены по времени
4. **Result Limit** — максимум 1000 строк результата
5. **Read-Only User** (опционально) — пользователь без прав на изменение

---

## Authentication Flow

### Telegram WebApp Auth

```
1. User opens bot in Telegram
   ↓
2. User clicks "Начать обучение" button
   ↓
3. Telegram opens WebApp with initData
   ↓
4. Frontend extracts initData
   ↓
5. Frontend → Backend (/api/auth/telegram)
   ↓
6. Backend validates initData signature (HMAC SHA-256)
   ├─ Check hash matches
   ├─ Check auth_date is recent
   └─ Verify with TELEGRAM_BOT_TOKEN
   ↓
7. Create/Update user in database
   ↓
8. Generate JWT token
   ↓
9. Return token to frontend
   ↓
10. Frontend stores token in localStorage
    ↓
11. All subsequent requests include token in Authorization header
```

### JWT Token

```python
{
  "user_id": 123,
  "telegram_id": 987654321,
  "exp": 1234567890,  # Expiration (7 days)
  "iat": 1234567890   # Issued at
}
```

---

## API Design

### RESTful Endpoints

```
Authentication:
POST   /api/auth/telegram          # Telegram auth
GET    /api/auth/me                # Get current user

Course:
GET    /api/modules                # List modules
GET    /api/modules/{id}           # Module details
GET    /api/modules/{id}/lessons   # Module lessons
GET    /api/lessons/{id}           # Lesson details

Progress:
GET    /api/progress               # User progress
POST   /api/progress/complete      # Mark lesson complete
GET    /api/progress/stats         # User stats

Sandbox:
POST   /api/sandbox/execute        # Execute SQL query
POST   /api/sandbox/reset          # Reset sandbox

Achievements:
GET    /api/achievements           # List achievements
GET    /api/achievements/user      # User achievements

Leaderboard:
GET    /api/leaderboard            # Top users
GET    /api/leaderboard/friends    # Friends leaderboard

Dashboard:
GET    /api/dashboard/stats        # Dashboard stats
GET    /api/dashboard/activity     # Activity heatmap
```

---

## Performance Optimizations

### Backend

1. **Database Connection Pooling**
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
   )
   ```

2. **Caching** (future)
   - Redis для leaderboard и stats
   - Cache для module/lesson lists

3. **Indexes**
   ```sql
   CREATE INDEX idx_user_telegram_id ON users(telegram_id);
   CREATE INDEX idx_progress_user_lesson ON user_progress(user_id, lesson_id);
   CREATE INDEX idx_activity_user_date ON activity_logs(user_id, activity_date);
   ```

### Frontend

1. **Code Splitting**
   ```typescript
   const Dashboard = React.lazy(() => import('./pages/Dashboard'));
   ```

2. **Memoization**
   ```typescript
   const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
   ```

3. **Virtual Scrolling** (для длинных списков)

---

## Monitoring & Logging

### Backend Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"User {user_id} completed lesson {lesson_id}")
logger.error(f"SQL execution failed: {error}", exc_info=True)
```

### Error Tracking

- **Sentry** для production error tracking
- **Custom error handlers** в FastAPI

### Performance Monitoring

- **Response time logging**
- **Database query profiling**
- **Resource usage monitoring**

---

## Deployment Architecture

### Production Setup

```
[Users] → [Cloudflare CDN] → [Frontend (Vercel)]
                                      ↓ HTTPS
                                [Backend (Railway/VPS)]
                                      ↓
                                [MySQL (Managed DB)]
```

---

## Future Improvements

- [ ] Redis для кэширования
- [ ] WebSocket для real-time updates
- [ ] GraphQL API (опционально)
- [ ] Microservices (если нужно масштабирование)
- [ ] Kubernetes для orchestration
- [ ] CDN для статических файлов
- [ ] Message Queue (RabbitMQ/Celery) для async tasks

---

**Документация по архитектуре SQL Hero 🏗️**
