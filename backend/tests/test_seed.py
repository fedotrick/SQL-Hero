import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.cli.seed import run_seed, seed_achievements, seed_lessons, seed_modules
from app.cli.seed_data import ACHIEVEMENTS_DATA, LESSONS_DATA, MODULES_DATA
from app.core.config import get_settings
from app.core.database import Base
from app.models.database import Achievement, Lesson, Module


@pytest.fixture
async def test_db_session():
    settings = get_settings()
    
    engine = create_async_engine(settings.database_url, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_seed_modules_creates_all_modules(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    
    assert len(module_map) == len(MODULES_DATA)
    
    result = await test_db_session.execute(select(Module))
    modules = result.scalars().all()
    
    assert len(modules) == 10
    
    for module in modules:
        assert module.title is not None
        assert module.description is not None
        assert module.order > 0
        assert module.is_published is True


@pytest.mark.asyncio
async def test_seed_modules_is_idempotent(test_db_session: AsyncSession):
    module_map_1 = await seed_modules(test_db_session)
    
    module_map_2 = await seed_modules(test_db_session)
    
    assert len(module_map_1) == len(module_map_2)
    
    result = await test_db_session.execute(select(Module))
    modules = result.scalars().all()
    
    assert len(modules) == 10


@pytest.mark.asyncio
async def test_seed_lessons_creates_correct_count(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    
    await seed_lessons(test_db_session, module_map)
    
    result = await test_db_session.execute(select(Lesson))
    lessons = result.scalars().all()
    
    expected_lesson_count = sum(len(module["lessons"]) for module in LESSONS_DATA)
    assert len(lessons) == expected_lesson_count


@pytest.mark.asyncio
async def test_seed_lessons_has_required_fields(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    
    await seed_lessons(test_db_session, module_map)
    
    result = await test_db_session.execute(select(Lesson))
    lessons = result.scalars().all()
    
    for lesson in lessons:
        assert lesson.title is not None
        assert lesson.content is not None
        assert lesson.theory is not None
        assert lesson.sql_solution is not None
        assert lesson.expected_result is not None
        assert isinstance(lesson.expected_result, dict)
        assert lesson.order > 0
        assert lesson.module_id is not None


@pytest.mark.asyncio
async def test_lessons_per_module_align_with_spec(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    
    await seed_lessons(test_db_session, module_map)
    
    for module_lessons_data in LESSONS_DATA:
        module_order = module_lessons_data["module_order"]
        expected_lesson_count = len(module_lessons_data["lessons"])
        
        module = module_map[module_order]
        
        result = await test_db_session.execute(
            select(Lesson).where(Lesson.module_id == module.id)
        )
        lessons = result.scalars().all()
        
        assert len(lessons) == expected_lesson_count, f"Module {module_order} should have {expected_lesson_count} lessons"
        assert 2 <= len(lessons) <= 3, f"Module {module_order} should have 2-3 lessons per spec"


@pytest.mark.asyncio
async def test_seed_lessons_is_idempotent(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    
    await seed_lessons(test_db_session, module_map)
    first_count = (await test_db_session.execute(select(Lesson))).scalars().all()
    
    await seed_lessons(test_db_session, module_map)
    second_count = (await test_db_session.execute(select(Lesson))).scalars().all()
    
    assert len(first_count) == len(second_count)


@pytest.mark.asyncio
async def test_seed_achievements_creates_all_achievements(test_db_session: AsyncSession):
    await seed_achievements(test_db_session)
    
    result = await test_db_session.execute(select(Achievement))
    achievements = result.scalars().all()
    
    assert len(achievements) == len(ACHIEVEMENTS_DATA)
    
    for achievement in achievements:
        assert achievement.code is not None
        assert achievement.type is not None
        assert achievement.title is not None
        assert achievement.icon is not None
        assert achievement.points >= 0


@pytest.mark.asyncio
async def test_seed_achievements_has_unique_codes(test_db_session: AsyncSession):
    await seed_achievements(test_db_session)
    
    result = await test_db_session.execute(select(Achievement))
    achievements = result.scalars().all()
    
    codes = [a.code for a in achievements]
    assert len(codes) == len(set(codes)), "Achievement codes should be unique"


@pytest.mark.asyncio
async def test_seed_achievements_is_idempotent(test_db_session: AsyncSession):
    await seed_achievements(test_db_session)
    first_count = (await test_db_session.execute(select(Achievement))).scalars().all()
    
    await seed_achievements(test_db_session)
    second_count = (await test_db_session.execute(select(Achievement))).scalars().all()
    
    assert len(first_count) == len(second_count)


@pytest.mark.asyncio
async def test_run_seed_complete(test_db_session: AsyncSession):
    stats = await run_seed()
    
    assert stats["total_modules"] == 10
    assert stats["total_lessons"] > 0
    assert stats["total_achievements"] == len(ACHIEVEMENTS_DATA)
    
    for module_id, lesson_count in stats["lessons_per_module"].items():
        assert 2 <= lesson_count <= 3, f"Module {module_id} should have 2-3 lessons"


@pytest.mark.asyncio
async def test_lessons_have_russian_content(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    await seed_lessons(test_db_session, module_map)
    
    result = await test_db_session.execute(select(Lesson).limit(5))
    lessons = result.scalars().all()
    
    russian_chars = set("абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
    
    for lesson in lessons:
        content_has_russian = any(char in russian_chars for char in lesson.content or "")
        theory_has_russian = any(char in russian_chars for char in lesson.theory or "")
        
        assert content_has_russian or theory_has_russian, f"Lesson {lesson.title} should have Russian content"


@pytest.mark.asyncio
async def test_expected_result_is_valid_json(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    await seed_lessons(test_db_session, module_map)
    
    result = await test_db_session.execute(select(Lesson))
    lessons = result.scalars().all()
    
    for lesson in lessons:
        assert lesson.expected_result is not None
        assert isinstance(lesson.expected_result, dict)
        assert len(lesson.expected_result) > 0


@pytest.mark.asyncio
async def test_achievements_have_icon_placeholders(test_db_session: AsyncSession):
    await seed_achievements(test_db_session)
    
    result = await test_db_session.execute(select(Achievement))
    achievements = result.scalars().all()
    
    for achievement in achievements:
        assert achievement.icon is not None
        assert len(achievement.icon) > 0


@pytest.mark.asyncio
async def test_module_order_is_sequential(test_db_session: AsyncSession):
    module_map = await seed_modules(test_db_session)
    
    result = await test_db_session.execute(select(Module).order_by(Module.order))
    modules = result.scalars().all()
    
    for i, module in enumerate(modules, start=1):
        assert module.order == i, f"Module order should be sequential, expected {i}, got {module.order}"
