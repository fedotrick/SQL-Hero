import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core.security import create_access_token
from app.main import app
from app.models.database import Lesson, Module, ProgressStatus, User, UserProgress


@pytest.fixture
async def test_engine():
    """Создание тестовой базы данных в памяти."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Создание тестовой сессии БД."""
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Создание тестового пользователя."""
    user = User(
        telegram_id=12345678,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="ru",
        is_active=True,
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_modules(test_db: AsyncSession) -> list[Module]:
    """Создание тестовых модулей."""
    modules = [
        Module(
            title="Введение в SQL",
            description="Основы работы с SQL",
            order=1,
            is_published=True,
        ),
        Module(
            title="Работа с таблицами",
            description="Создание и изменение таблиц",
            order=2,
            is_published=True,
        ),
        Module(
            title="Фильтрация данных",
            description="WHERE и ORDER BY",
            order=3,
            is_published=True,
        ),
    ]
    for module in modules:
        test_db.add(module)
    await test_db.commit()
    for module in modules:
        await test_db.refresh(module)
    return modules


@pytest.fixture
async def test_lessons(test_db: AsyncSession, test_modules: list[Module]) -> list[Lesson]:
    """Создание тестовых уроков."""
    lessons = [
        # Модуль 1
        Lesson(
            module_id=test_modules[0].id,
            title="Основы SELECT",
            content="Введение в SELECT",
            theory="SELECT - основной оператор SQL",
            sql_solution="SELECT * FROM users;",
            expected_result={"columns": ["id", "name"], "rows": [[1, "Иван"]]},
            order=1,
            estimated_duration=15,
            is_published=True,
        ),
        Lesson(
            module_id=test_modules[0].id,
            title="Выборка столбцов",
            content="Выбор конкретных столбцов",
            theory="SELECT column1, column2 FROM table",
            sql_solution="SELECT name FROM users;",
            expected_result={"columns": ["name"], "rows": [["Иван"]]},
            order=2,
            estimated_duration=10,
            is_published=True,
        ),
        # Модуль 2
        Lesson(
            module_id=test_modules[1].id,
            title="CREATE TABLE",
            content="Создание таблиц",
            theory="CREATE TABLE table_name (...)",
            sql_solution="CREATE TABLE users (id INT, name VARCHAR(100));",
            expected_result={"columns": [], "rows": []},
            order=1,
            estimated_duration=20,
            is_published=True,
        ),
        # Модуль 3
        Lesson(
            module_id=test_modules[2].id,
            title="WHERE условие",
            content="Фильтрация данных",
            theory="SELECT * FROM table WHERE condition",
            sql_solution="SELECT * FROM users WHERE id = 1;",
            expected_result={"columns": ["id", "name"], "rows": [[1, "Иван"]]},
            order=1,
            estimated_duration=15,
            is_published=True,
        ),
    ]
    for lesson in lessons:
        test_db.add(lesson)
    await test_db.commit()
    for lesson in lessons:
        await test_db.refresh(lesson)
    return lessons


@pytest.fixture
async def authenticated_client(test_db: AsyncSession, test_user: User):
    """Создание аутентифицированного HTTP клиента."""
    async def override_get_db():
        yield test_db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    access_token = create_access_token(data={"sub": str(test_user.id), "telegram_id": test_user.telegram_id})

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {access_token}"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


async def test_list_modules_unauthenticated(test_db: AsyncSession):
    """Тест: неаутентифицированный запрос должен вернуть 401."""
    async def override_get_db():
        yield test_db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/courses/modules")

    app.dependency_overrides.clear()

    assert response.status_code == 403


async def test_list_modules_empty(authenticated_client: httpx.AsyncClient):
    """Тест: список модулей пуст, если нет данных."""
    response = await authenticated_client.get("/courses/modules")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["page"] == 1
    assert data["page_size"] == 20


async def test_list_modules_basic(
    authenticated_client: httpx.AsyncClient,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: получение списка модулей с базовой информацией."""
    response = await authenticated_client.get("/courses/modules")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert data["total_pages"] == 1

    # Проверка первого модуля
    first_module = data["items"][0]
    assert first_module["title"] == "Введение в SQL"
    assert first_module["order"] == 1
    assert first_module["is_published"] is True
    assert first_module["is_locked"] is False  # Первый модуль всегда разблокирован
    assert first_module["lessons_count"] == 2
    assert first_module["completed_lessons_count"] == 0


async def test_list_modules_with_progress(
    authenticated_client: httpx.AsyncClient,
    test_db: AsyncSession,
    test_user: User,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: список модулей с информацией о прогрессе."""
    # Завершаем первый урок
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        score=100,
        attempts=1,
    )
    test_db.add(progress)
    await test_db.commit()

    response = await authenticated_client.get("/courses/modules")

    assert response.status_code == 200
    data = response.json()

    first_module = data["items"][0]
    assert first_module["completed_lessons_count"] == 1
    assert first_module["is_locked"] is False


async def test_list_modules_unlocking(
    authenticated_client: httpx.AsyncClient,
    test_db: AsyncSession,
    test_user: User,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: разблокировка модулей после завершения предыдущего."""
    response = await authenticated_client.get("/courses/modules")
    data = response.json()

    # Изначально только первый модуль разблокирован
    assert data["items"][0]["is_locked"] is False
    assert data["items"][1]["is_locked"] is True
    assert data["items"][2]["is_locked"] is True

    # Завершаем все уроки первого модуля
    for lesson in test_lessons[:2]:
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            status=ProgressStatus.COMPLETED,
            score=100,
            attempts=1,
        )
        test_db.add(progress)
    await test_db.commit()

    response = await authenticated_client.get("/courses/modules")
    data = response.json()

    # Теперь второй модуль разблокирован
    assert data["items"][0]["is_locked"] is False
    assert data["items"][1]["is_locked"] is False
    assert data["items"][2]["is_locked"] is True


async def test_list_modules_pagination(
    authenticated_client: httpx.AsyncClient,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: пагинация списка модулей."""
    # Страница 1 с размером 2
    response = await authenticated_client.get("/courses/modules?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 2
    assert data["items"][0]["order"] == 1
    assert data["items"][1]["order"] == 2

    # Страница 2 с размером 2
    response = await authenticated_client.get("/courses/modules?page=2&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["order"] == 3


async def test_get_module_detail(
    authenticated_client: httpx.AsyncClient,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: получение детальной информации о модуле."""
    module_id = test_modules[0].id
    response = await authenticated_client.get(f"/courses/modules/{module_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == module_id
    assert data["title"] == "Введение в SQL"
    assert data["description"] == "Основы работы с SQL"
    assert data["order"] == 1
    assert data["is_locked"] is False
    assert len(data["lessons"]) == 2

    # Проверка уроков
    assert data["lessons"][0]["title"] == "Основы SELECT"
    assert data["lessons"][0]["order"] == 1
    assert data["lessons"][0]["is_locked"] is False
    assert data["lessons"][0]["progress_status"] is None

    assert data["lessons"][1]["title"] == "Выборка столбцов"
    assert data["lessons"][1]["order"] == 2
    assert data["lessons"][1]["is_locked"] is True  # Второй урок заблокирован


async def test_get_module_detail_not_found(authenticated_client: httpx.AsyncClient):
    """Тест: модуль не найден."""
    response = await authenticated_client.get("/courses/modules/99999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


async def test_get_module_detail_with_progress(
    authenticated_client: httpx.AsyncClient,
    test_db: AsyncSession,
    test_user: User,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: детали модуля с прогрессом пользователя."""
    # Завершаем первый урок
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        score=100,
        attempts=1,
    )
    test_db.add(progress)
    await test_db.commit()

    module_id = test_modules[0].id
    response = await authenticated_client.get(f"/courses/modules/{module_id}")

    assert response.status_code == 200
    data = response.json()

    # Первый урок завершён и второй разблокирован
    assert data["lessons"][0]["progress_status"] == "completed"
    assert data["lessons"][0]["is_locked"] is False
    assert data["lessons"][1]["is_locked"] is False


async def test_get_lesson_detail(
    authenticated_client: httpx.AsyncClient,
    test_lessons: list[Lesson],
):
    """Тест: получение детальной информации об уроке."""
    lesson_id = test_lessons[0].id
    response = await authenticated_client.get(f"/courses/lessons/{lesson_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lesson_id
    assert data["title"] == "Основы SELECT"
    assert data["content"] == "Введение в SELECT"
    assert data["theory"] == "SELECT - основной оператор SQL"
    assert data["sql_solution"] == "SELECT * FROM users;"
    assert data["expected_result"]["columns"] == ["id", "name"]
    assert data["expected_result"]["rows"] == [[1, "Иван"]]
    assert data["order"] == 1
    assert data["estimated_duration"] == 15
    assert data["is_locked"] is False
    assert data["progress_status"] is None
    assert data["attempts"] == 0


async def test_get_lesson_detail_not_found(authenticated_client: httpx.AsyncClient):
    """Тест: урок не найден."""
    response = await authenticated_client.get("/courses/lessons/99999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


async def test_get_lesson_detail_locked(
    authenticated_client: httpx.AsyncClient,
    test_lessons: list[Lesson],
):
    """Тест: второй урок заблокирован без завершения первого."""
    lesson_id = test_lessons[1].id
    response = await authenticated_client.get(f"/courses/lessons/{lesson_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["is_locked"] is True
    assert data["progress_status"] is None


async def test_get_lesson_detail_with_progress(
    authenticated_client: httpx.AsyncClient,
    test_db: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
):
    """Тест: детали урока с прогрессом пользователя."""
    # Завершаем первый урок
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.IN_PROGRESS,
        score=50,
        attempts=2,
    )
    test_db.add(progress)
    await test_db.commit()

    lesson_id = test_lessons[0].id
    response = await authenticated_client.get(f"/courses/lessons/{lesson_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["progress_status"] == "in_progress"
    assert data["is_locked"] is False
    assert data["attempts"] == 2


async def test_lesson_unlocking_sequence(
    authenticated_client: httpx.AsyncClient,
    test_db: AsyncSession,
    test_user: User,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: последовательная разблокировка уроков."""
    # Проверяем начальное состояние
    response = await authenticated_client.get(f"/courses/lessons/{test_lessons[0].id}")
    assert response.json()["is_locked"] is False

    response = await authenticated_client.get(f"/courses/lessons/{test_lessons[1].id}")
    assert response.json()["is_locked"] is True

    # Завершаем первый урок
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        score=100,
        attempts=1,
    )
    test_db.add(progress)
    await test_db.commit()

    # Второй урок теперь разблокирован
    response = await authenticated_client.get(f"/courses/lessons/{test_lessons[1].id}")
    assert response.json()["is_locked"] is False


async def test_module_unlocking_after_completion(
    authenticated_client: httpx.AsyncClient,
    test_db: AsyncSession,
    test_user: User,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: разблокировка модуля после завершения всех уроков предыдущего."""
    # Второй модуль заблокирован
    response = await authenticated_client.get(f"/courses/modules/{test_modules[1].id}")
    assert response.json()["is_locked"] is True

    # Урок второго модуля тоже заблокирован
    response = await authenticated_client.get(f"/courses/lessons/{test_lessons[2].id}")
    assert response.json()["is_locked"] is True

    # Завершаем все уроки первого модуля
    for lesson in test_lessons[:2]:
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            status=ProgressStatus.COMPLETED,
            score=100,
            attempts=1,
        )
        test_db.add(progress)
    await test_db.commit()

    # Второй модуль разблокирован
    response = await authenticated_client.get(f"/courses/modules/{test_modules[1].id}")
    assert response.json()["is_locked"] is False

    # Первый урок второго модуля разблокирован
    response = await authenticated_client.get(f"/courses/lessons/{test_lessons[2].id}")
    assert response.json()["is_locked"] is False


async def test_response_schema_fields(
    authenticated_client: httpx.AsyncClient,
    test_modules: list[Module],
    test_lessons: list[Lesson],
):
    """Тест: проверка всех полей в схеме ответа."""
    # Проверка модулей
    response = await authenticated_client.get("/courses/modules")
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    module = data["items"][0]
    assert "id" in module
    assert "title" in module
    assert "description" in module
    assert "order" in module
    assert "is_published" in module
    assert "is_locked" in module
    assert "lessons_count" in module
    assert "completed_lessons_count" in module

    # Проверка детали модуля
    response = await authenticated_client.get(f"/courses/modules/{test_modules[0].id}")
    module_detail = response.json()
    assert "lessons" in module_detail
    assert "created_at" in module_detail
    assert "updated_at" in module_detail

    lesson_summary = module_detail["lessons"][0]
    assert "id" in lesson_summary
    assert "title" in lesson_summary
    assert "order" in lesson_summary
    assert "estimated_duration" in lesson_summary
    assert "is_locked" in lesson_summary
    assert "progress_status" in lesson_summary

    # Проверка детали урока
    response = await authenticated_client.get(f"/courses/lessons/{test_lessons[0].id}")
    lesson_detail = response.json()
    assert "module_id" in lesson_detail
    assert "content" in lesson_detail
    assert "theory" in lesson_detail
    assert "sql_solution" in lesson_detail
    assert "expected_result" in lesson_detail
    assert "created_at" in lesson_detail
    assert "updated_at" in lesson_detail
