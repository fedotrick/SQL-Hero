# Руководство по внесению изменений в SQL Hero

Спасибо за интерес к проекту SQL Hero! Это руководство поможет вам внести свой вклад в развитие проекта.

---

## Начало работы

### 1. Fork репозитория

Создайте свою копию репозитория на GitHub:

1. Перейдите на [github.com/fedotrick/SQL-Hero](https://github.com/fedotrick/SQL-Hero)
2. Нажмите кнопку "Fork" в правом верхнем углу
3. Fork будет создан в вашем аккаунте

### 2. Клонирование

```bash
# Клонируйте ваш fork
git clone https://github.com/YOUR-USERNAME/SQL-Hero.git
cd SQL-Hero

# Добавьте upstream remote
git remote add upstream https://github.com/fedotrick/SQL-Hero.git

# Проверьте remotes
git remote -v
```

### 3. Установка окружения

Следуйте инструкциям в [SETUP.md](SETUP.md) для установки всех зависимостей.

```bash
# Backend
cd backend
poetry install

# Frontend
cd frontend
pnpm install
```

---

## Workflow разработки

### 1. Создание новой ветки

```bash
# Обновите main ветку
git checkout main
git pull upstream main

# Создайте новую ветку для вашей фичи
git checkout -b feature/your-feature-name
```

**Префиксы веток:**
- `feature/` — новая функциональность
- `fix/` — исправление бага
- `docs/` — изменения в документации
- `refactor/` — рефакторинг без изменения функциональности
- `test/` — добавление/изменение тестов
- `chore/` — рутинные задачи (обновление зависимостей и т.д.)

**Примеры:**
```bash
git checkout -b feature/add-new-achievement
git checkout -b fix/sandbox-timeout-error
git checkout -b docs/update-setup-guide
```

### 2. Внесение изменений

#### Следуйте стилю кода проекта

**Backend (Python):**
- PEP 8 стандарт
- Type hints обязательны
- Docstrings для публичных функций
- Async/await где возможно

**Frontend (TypeScript):**
- TypeScript strict mode
- Функциональные компоненты с hooks
- Props типизированы
- Избегайте `any` type

#### Пишите тесты

**Backend:**
```python
# tests/e2e/test_e2e_new_feature.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_new_feature(test_client: AsyncClient, test_user_token: str):
    response = await test_client.get(
        "/api/new-endpoint",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
```

**Frontend:**
```typescript
// src/components/NewComponent.test.tsx
import { render, screen } from '@testing-library/react';
import NewComponent from './NewComponent';

test('renders NewComponent', () => {
  render(<NewComponent />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

#### Обновите документацию

Если ваши изменения влияют на:
- API endpoints → обновите ARCHITECTURE.md
- Установку → обновите SETUP.md
- Новые фичи → обновите README.md

### 3. Проверка кода

Перед коммитом запустите все проверки:

```bash
# Backend
cd backend
poetry run ruff check app            # Linting
poetry run ruff format app --check   # Format check
poetry run mypy app                  # Type checking
poetry run pytest tests/e2e/ -v      # E2E tests

# Frontend
cd frontend
pnpm lint                            # ESLint
pnpm type-check                      # TypeScript
pnpm format:check                    # Prettier
pnpm test                            # Tests (если есть)
```

### 4. Коммит изменений

Используйте [Conventional Commits](https://www.conventionalcommits.org/ru/) формат:

```bash
git add .
git commit -m "feat: add new achievement for completing 10 lessons"
```

**Типы коммитов:**
- `feat:` — новая функция
- `fix:` — исправление бага
- `docs:` — изменения в документации
- `style:` — форматирование, пропущенные точки с запятой и т.д.
- `refactor:` — рефакторинг кода
- `test:` — добавление/изменение тестов
- `chore:` — обновление зависимостей, конфигураций и т.д.
- `perf:` — улучшение производительности

**Примеры хороших коммитов:**
```bash
git commit -m "feat: add leaderboard friends filter"
git commit -m "fix: resolve sandbox timeout on complex queries"
git commit -m "docs: update DEPLOYMENT.md with Railway instructions"
git commit -m "test: add E2E tests for achievement unlock"
git commit -m "refactor: extract XP calculation to separate service"
```

**Примеры плохих коммитов:**
```bash
git commit -m "fix"                    # Что именно исправлено?
git commit -m "update"                 # Что обновлено?
git commit -m "работает!!!"            # Нет контекста
```

### 5. Push в ваш fork

```bash
git push origin feature/your-feature-name
```

### 6. Создание Pull Request

1. Перейдите на GitHub в ваш fork
2. Нажмите "Compare & pull request"
3. Заполните описание PR:

**Шаблон PR:**
```markdown
## Описание
Краткое описание изменений и их цель.

## Тип изменений
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Чеклист
- [ ] Код следует стилю проекта
- [ ] Добавлены/обновлены тесты
- [ ] Все тесты проходят
- [ ] Документация обновлена
- [ ] Нет breaking changes (или они задокументированы)

## Как тестировать
1. Шаг 1
2. Шаг 2
3. Ожидаемый результат

## Скриншоты (если применимо)
[Добавьте скриншоты для UI изменений]
```

4. Дождитесь review от мейнтейнеров

---

## Стандарты кода

### Backend (Python/FastAPI)

#### Code Style

```python
# ✅ ХОРОШО: Type hints, docstring, async
async def get_user_by_telegram_id(
    db: AsyncSession,
    telegram_id: int
) -> User | None:
    """
    Получить пользователя по Telegram ID.
    
    Args:
        db: Database session
        telegram_id: Telegram user ID
        
    Returns:
        User объект или None если не найден
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()

# ❌ ПЛОХО: Нет type hints, нет docstring
def get_user(db, id):
    result = db.execute(select(User).where(User.telegram_id == id))
    return result.scalar_one_or_none()
```

#### Error Handling

```python
# ✅ ХОРОШО: Кастомные исключения, понятные сообщения
from app.core.exceptions import ResourceNotFoundError

async def get_lesson(db: AsyncSession, lesson_id: int) -> Lesson:
    lesson = await db.get(Lesson, lesson_id)
    if not lesson:
        raise ResourceNotFoundError(f"Lesson {lesson_id} not found")
    return lesson

# ❌ ПЛОХО: Generic exception
async def get_lesson(db, id):
    lesson = await db.get(Lesson, id)
    if not lesson:
        raise Exception("Not found")
    return lesson
```

#### Database Queries

```python
# ✅ ХОРОШО: Эффективный запрос с joinedload
from sqlalchemy.orm import selectinload

async def get_module_with_lessons(db: AsyncSession, module_id: int) -> Module:
    result = await db.execute(
        select(Module)
        .where(Module.id == module_id)
        .options(selectinload(Module.lessons))
    )
    return result.scalar_one()

# ❌ ПЛОХО: N+1 проблема
async def get_module_with_lessons(db, id):
    module = await db.get(Module, id)
    lessons = await db.execute(select(Lesson).where(Lesson.module_id == id))
    module.lessons = lessons.scalars().all()
    return module
```

### Frontend (TypeScript/React)

#### Component Style

```typescript
// ✅ ХОРОШО: Типизация props, функциональный компонент
interface UserStatsProps {
  xp: number;
  level: number;
  onLevelUp?: () => void;
}

export const UserStats: React.FC<UserStatsProps> = ({ xp, level, onLevelUp }) => {
  const progress = useMemo(() => calculateProgress(xp, level), [xp, level]);
  
  useEffect(() => {
    if (progress >= 100 && onLevelUp) {
      onLevelUp();
    }
  }, [progress, onLevelUp]);

  return (
    <div className="user-stats">
      <span>Level {level}</span>
      <ProgressBar value={progress} />
      <span>{xp} XP</span>
    </div>
  );
};

// ❌ ПЛОХО: Нет типов, any everywhere
export const UserStats = ({ xp, level }: any) => {
  return <div>{level} - {xp}</div>;
};
```

#### Hooks Usage

```typescript
// ✅ ХОРОШО: Кастомные хуки, мемоизация
export const useUser = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await userService.getMe();
        setUser(data);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUser();
  }, []);
  
  return { user, loading };
};

// В компоненте
const { user, loading } = useUser();

// ❌ ПЛОХО: Fetch в компоненте, нет обработки ошибок
const Component = () => {
  const [user, setUser] = useState(null);
  
  fetch('/api/user').then(res => setUser(res.data));
  
  return <div>{user?.name}</div>;
};
```

---

## Тестирование

### Backend тесты

Каждая новая функция должна иметь E2E тесты:

```python
# tests/e2e/test_e2e_achievements.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_unlock_achievement(
    test_client: AsyncClient,
    test_user_token: str
):
    # Arrange: создать условия для достижения
    # ...
    
    # Act: выполнить действие
    response = await test_client.post(
        "/api/progress/complete",
        json={"lesson_id": 10},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Assert: проверить результат
    assert response.status_code == 200
    
    achievements_response = await test_client.get(
        "/api/achievements/user",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    achievements = achievements_response.json()
    assert any(a["title"] == "First Steps" for a in achievements)
```

**Security тесты обязательны** для sandbox:

```python
@pytest.mark.asyncio
async def test_sandbox_blocks_dangerous_queries(test_client: AsyncClient, test_user_token: str):
    dangerous_queries = [
        "DROP TABLE users",
        "DELETE FROM users",
        "ALTER TABLE users ADD admin BOOLEAN",
        "SELECT * FROM mysql.user",
    ]
    
    for query in dangerous_queries:
        response = await test_client.post(
            "/api/sandbox/execute",
            json={"query": query, "lesson_id": 1},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 400
        assert "dangerous" in response.json()["detail"].lower()
```

---

## Areas для вклада

### 🐛 Bug Fixes

Проверьте [Issues с label "bug"](https://github.com/fedotrick/SQL-Hero/issues?q=is%3Aissue+is%3Aopen+label%3Abug).

### ✨ New Features

Идеи для новых фич:
- Новые модули и уроки SQL
- Дополнительные достижения
- Улучшения UI/UX
- Интеграции с другими сервисами
- Персонализация обучения

### 📚 Documentation

- Улучшение существующих guides
- Добавление примеров кода
- Перевод на другие языки
- Создание туториалов
- Запись видео-гайдов

### 🧪 Testing

- Добавление E2E тестов
- Улучшение покрытия кода
- Performance тесты
- UI тесты

### 🎨 Design

- Улучшение UI компонентов
- Темная тема
- Анимации и transitions
- Адаптивный дизайн

---

## Code Review Process

### Для Contributors

1. **Будьте терпеливы** — review может занять время
2. **Отвечайте на комментарии** — обсуждайте предложенные изменения
3. **Делайте requested changes** — вносите исправления по feedback
4. **Не обижайтесь** — критика конструктивна и направлена на улучшение кода

### Для Reviewers

1. **Будьте конструктивны** — предлагайте решения, не только критикуйте
2. **Будьте уважительны** — помните, что за кодом живой человек
3. **Объясняйте почему** — давайте контекст для ваших комментариев
4. **Хвалите хорошие решения** — позитивный feedback тоже важен

---

## Reporting Bugs

### Перед созданием Issue

1. **Поищите существующие Issues** — возможно, баг уже reported
2. **Проверьте документацию** — возможно, это expected behavior
3. **Попробуйте последнюю версию** — баг может быть уже исправлен

### Создание Bug Report

Используйте шаблон:

```markdown
## Описание бага
Чёткое и краткое описание проблемы.

## Шаги для воспроизведения
1. Перейти на '...'
2. Нажать на '....'
3. Scroll down to '....'
4. See error

## Ожидаемое поведение
Что должно было произойти.

## Актуальное поведение
Что произошло на самом деле.

## Скриншоты
Если применимо, добавьте скриншоты.

## Окружение
- OS: [e.g. macOS 14.0]
- Browser: [e.g. Chrome 120]
- Backend version: [e.g. 1.2.3]
- Frontend version: [e.g. 1.2.3]

## Дополнительный контекст
Логи, error messages и т.д.
```

---

## Feature Requests

Хотите предложить новую функцию?

1. **Создайте Issue с label "enhancement"**
2. **Опишите проблему**, которую решает фича
3. **Опишите предлагаемое решение**
4. **Предложите альтернативы**, если есть
5. **Дождитесь обсуждения** перед началом работы

---

## Community Guidelines

### Код поведения

- ✅ Будьте уважительны и инклюзивны
- ✅ Конструктивная критика приветствуется
- ✅ Помогайте новичкам
- ✅ Делитесь знаниями
- ❌ Оскорбления и токсичность недопустимы
- ❌ Спам и реклама запрещены

### Коммуникация

- **GitHub Issues** — для bugs и feature requests
- **Pull Requests** — для code review и обсуждения изменений
- **Telegram** — для быстрых вопросов и неформального общения
- **Email** — для приватных вопросов

---

## Лицензия

Делая вклад в SQL Hero, вы соглашаетесь, что ваш код будет распространяться под [MIT License](../LICENSE).

---

## Вопросы?

Если у вас есть вопросы по процессу contributing:

1. Проверьте [SETUP.md](SETUP.md) и [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Создайте Issue с label "question"
3. Свяжитесь с мейнтейнерами: [@fedotrick](https://t.me/fedotrick)

---

**Спасибо за ваш вклад в SQL Hero! 🎉**
