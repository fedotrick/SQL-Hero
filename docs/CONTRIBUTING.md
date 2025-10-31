# Руководство по внесению изменений

Спасибо за интерес к проекту! Это руководство поможет вам внести свой вклад.

## Начало работы

1. **Форкните репозиторий** на GitHub
2. **Клонируйте** свой форк локально:
   ```bash
   git clone https://github.com/your-username/project-name.git
   cd project-name
   ```
3. **Настройте окружение:**
   ```bash
   ./infrastructure/scripts/setup.sh
   ```

## Процесс разработки

### 1. Создайте новую ветку

```bash
git checkout -b feature/your-feature-name
```

Используйте префиксы:
- `feature/` - новая функциональность
- `fix/` - исправление ошибки
- `docs/` - изменения в документации
- `refactor/` - рефакторинг кода
- `test/` - добавление тестов
- `chore/` - рутинные задачи

### 2. Внесите изменения

- Следуйте стилю кода проекта
- Пишите понятный код
- Добавляйте тесты для новой функциональности
- Обновляйте документацию

### 3. Проверьте код

```bash
# Запустите линтинг
./infrastructure/scripts/lint.sh

# Запустите тесты
./infrastructure/scripts/test.sh

# Или используйте Makefile
make lint
make test
```

### 4. Закоммитьте изменения

```bash
git add .
git commit -m "feat: описание изменений"
```

Используйте [Conventional Commits](https://www.conventionalcommits.org/ru/):

- `feat:` - новая функция
- `fix:` - исправление бага
- `docs:` - изменения в документации
- `style:` - форматирование, пропущенные точки с запятой и т.д.
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление задач сборки, конфигураций и т.д.
- `perf:` - улучшение производительности

Примеры:
```bash
git commit -m "feat: добавить эндпоинт для аутентификации"
git commit -m "fix: исправить ошибку валидации email"
git commit -m "docs: обновить README с новыми инструкциями"
```

### 5. Отправьте изменения

```bash
git push origin feature/your-feature-name
```

### 6. Создайте Pull Request

1. Перейдите в оригинальный репозиторий на GitHub
2. Нажмите "New Pull Request"
3. Выберите вашу ветку
4. Заполните описание PR:
   - Что было изменено
   - Почему было изменено
   - Как протестировать изменения
5. Дождитесь review

## Стандарты кода

### Backend (Python)

- Следуйте PEP 8
- Используйте type hints
- Документируйте сложные функции
- Пишите тесты для новой функциональности
- Код должен проходить ruff и mypy

```python
# Хороший пример
def get_user_by_id(user_id: int) -> User | None:
    """
    Получить пользователя по ID.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Объект User или None, если не найден
    """
    return database.get_user(user_id)
```

### Frontend (TypeScript/React)

- Используйте TypeScript для type safety
- Следуйте React best practices
- Функциональные компоненты с хуками
- Именуйте компоненты в PascalCase
- Код должен проходить ESLint и Prettier

```tsx
// Хороший пример
interface UserProfileProps {
  userId: number;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  return <div>{user?.name}</div>;
};
```

## Git хуки

Проект использует pre-commit хуки. Они автоматически:

- Проверяют форматирование
- Запускают линтеры
- Проверяют типы
- Исправляют простые ошибки

Если хуки не проходят, коммит будет отклонен. Исправьте ошибки и попробуйте снова.

Чтобы пропустить хуки (не рекомендуется):
```bash
git commit --no-verify -m "message"
```

## Тестирование

### Backend тесты

```bash
cd backend
poetry run pytest

# С покрытием
poetry run pytest --cov=app

# Конкретный тест
poetry run pytest tests/test_main.py::test_root
```

### Frontend тесты

```bash
cd frontend
pnpm test  # Когда будут добавлены тесты
```

## Документация

- Обновляйте README.md при изменении функциональности
- Добавляйте комментарии к сложному коду
- Документируйте API изменения
- Обновляйте ARCHITECTURE.md при изменении структуры

## Вопросы?

Если у вас есть вопросы:

1. Проверьте существующие [Issues](https://github.com/your-repo/issues)
2. Создайте новый Issue с тегом "question"
3. Свяжитесь с мейнтейнерами

## Код поведения

- Будьте уважительны к другим разработчикам
- Конструктивная критика приветствуется
- Помогайте новичкам
- Создавайте инклюзивное сообщество

Спасибо за ваш вклад! 🎉
