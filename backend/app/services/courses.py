from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import Lesson, Module, ProgressStatus, User, UserProgress


async def get_modules_with_progress(
    db: AsyncSession,
    user: User,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Module], int]:
    """Получить список модулей с информацией о прогрессе пользователя."""
    # Подсчёт общего количества модулей
    count_query = select(func.count(Module.id)).where(Module.is_published == True)  # noqa: E712
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Получение модулей с уроками
    query = (
        select(Module)
        .where(Module.is_published == True)  # noqa: E712
        .options(selectinload(Module.lessons))
        .order_by(Module.order)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    modules = list(result.scalars().all())

    # Получение прогресса пользователя по всем урокам
    progress_query = select(UserProgress).where(UserProgress.user_id == user.id)
    progress_result = await db.execute(progress_query)
    progress_map = {p.lesson_id: p for p in progress_result.scalars().all()}

    # Добавление информации о прогрессе и блокировке к каждому модулю
    for i, module in enumerate(modules):
        # Подсчёт завершённых уроков в модуле
        completed_count = sum(
            1
            for lesson in module.lessons
            if progress_map.get(lesson.id)
            and progress_map[lesson.id].status == ProgressStatus.COMPLETED
        )
        module.completed_lessons_count = completed_count  # type: ignore
        module.lessons_count = len([lesson for lesson in module.lessons if lesson.is_published])  # type: ignore

        # Логика разблокировки: первый модуль всегда разблокирован
        # Последующие модули разблокируются после завершения всех уроков предыдущего модуля
        if i == 0:
            module.is_locked = False  # type: ignore
        else:
            prev_module = modules[i - 1]
            prev_lessons_count = len(
                [lesson for lesson in prev_module.lessons if lesson.is_published]
            )
            prev_completed = sum(
                1
                for lesson in prev_module.lessons
                if progress_map.get(lesson.id)
                and progress_map[lesson.id].status == ProgressStatus.COMPLETED
            )
            module.is_locked = prev_completed < prev_lessons_count  # type: ignore

    return modules, total


async def get_module_detail_with_progress(
    db: AsyncSession,
    user: User,
    module_id: int,
) -> Module | None:
    """Получить детальную информацию о модуле с уроками и прогрессом."""
    # Получение модуля с уроками
    query = (
        select(Module)
        .where(Module.id == module_id, Module.is_published == True)  # noqa: E712
        .options(selectinload(Module.lessons))
    )
    result = await db.execute(query)
    module = result.scalar_one_or_none()

    if not module:
        return None

    # Получение прогресса пользователя
    progress_query = select(UserProgress).where(UserProgress.user_id == user.id)
    progress_result = await db.execute(progress_query)
    progress_map = {p.lesson_id: p for p in progress_result.scalars().all()}

    # Определение, заблокирован ли модуль
    # Получение всех модулей до текущего
    prev_modules_query = (
        select(Module)
        .where(Module.is_published == True, Module.order < module.order)  # noqa: E712
        .options(selectinload(Module.lessons))
        .order_by(Module.order)
    )
    prev_modules_result = await db.execute(prev_modules_query)
    prev_modules = list(prev_modules_result.scalars().all())

    # Если это не первый модуль, проверяем прогресс предыдущих
    if prev_modules:
        # Берём последний предыдущий модуль
        prev_module = prev_modules[-1]
        prev_lessons_count = len(
            [lesson for lesson in prev_module.lessons if lesson.is_published]
        )
        prev_completed = sum(
            1
            for lesson in prev_module.lessons
            if progress_map.get(lesson.id)
            and progress_map[lesson.id].status == ProgressStatus.COMPLETED
        )
        module.is_locked = prev_completed < prev_lessons_count  # type: ignore
    else:
        module.is_locked = False  # type: ignore

    # Добавление информации о прогрессе и блокировке к урокам
    for i, lesson in enumerate(module.lessons):
        if not lesson.is_published:
            continue

        progress = progress_map.get(lesson.id)
        lesson.progress_status = progress.status.value if progress else None  # type: ignore

        # Логика разблокировки уроков: первый урок разблокирован
        # Последующие разблокируются после завершения предыдущего
        if i == 0:
            lesson.is_locked = False if not module.is_locked else True  # type: ignore
        else:
            prev_lesson_progress = progress_map.get(module.lessons[i - 1].id)
            if module.is_locked:  # type: ignore
                lesson.is_locked = True  # type: ignore
            elif prev_lesson_progress and prev_lesson_progress.status == ProgressStatus.COMPLETED:
                lesson.is_locked = False  # type: ignore
            else:
                lesson.is_locked = True  # type: ignore

    return module


async def get_lesson_detail_with_progress(
    db: AsyncSession,
    user: User,
    lesson_id: int,
) -> Lesson | None:
    """Получить детальную информацию об уроке с прогрессом."""
    # Получение урока
    query = (
        select(Lesson)
        .where(Lesson.id == lesson_id, Lesson.is_published == True)  # noqa: E712
        .options(selectinload(Lesson.module))
    )
    result = await db.execute(query)
    lesson = result.scalar_one_or_none()

    if not lesson:
        return None

    # Получение прогресса пользователя по этому уроку
    progress_query = select(UserProgress).where(
        UserProgress.user_id == user.id,
        UserProgress.lesson_id == lesson_id,
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    lesson.progress_status = progress.status.value if progress else None  # type: ignore

    # Определение, заблокирован ли урок
    # Получение всех уроков модуля до текущего
    prev_lessons_query = (
        select(Lesson)
        .where(
            Lesson.module_id == lesson.module_id,
            Lesson.is_published == True,  # noqa: E712
            Lesson.order < lesson.order,
        )
        .order_by(Lesson.order)
    )
    prev_lessons_result = await db.execute(prev_lessons_query)
    prev_lessons = list(prev_lessons_result.scalars().all())

    # Получение прогресса по всем предыдущим урокам
    if prev_lessons:
        prev_lesson_ids = [lesson.id for lesson in prev_lessons]
        prev_progress_query = select(UserProgress).where(
            UserProgress.user_id == user.id,
            UserProgress.lesson_id.in_(prev_lesson_ids),
        )
        prev_progress_result = await db.execute(prev_progress_query)
        prev_progress_map = {p.lesson_id: p for p in prev_progress_result.scalars().all()}

        # Проверяем, завершён ли предыдущий урок
        prev_lesson = prev_lessons[-1]
        prev_lesson_progress = prev_progress_map.get(prev_lesson.id)
        lesson.is_locked = (  # type: ignore
            not prev_lesson_progress
            or prev_lesson_progress.status != ProgressStatus.COMPLETED
        )
    else:
        # Первый урок модуля - проверяем, разблокирован ли модуль
        # Получение предыдущих модулей
        prev_modules_query = (
            select(Module)
            .where(Module.is_published == True, Module.order < lesson.module.order)  # noqa: E712
            .options(selectinload(Module.lessons))
            .order_by(Module.order)
        )
        prev_modules_result = await db.execute(prev_modules_query)
        prev_modules = list(prev_modules_result.scalars().all())

        if prev_modules:
            # Проверяем, завершены ли все уроки предыдущего модуля
            prev_module = prev_modules[-1]
            prev_module_lesson_ids = [
                lesson.id for lesson in prev_module.lessons if lesson.is_published
            ]
            prev_module_progress_query = select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.lesson_id.in_(prev_module_lesson_ids),
            )
            prev_module_progress_result = await db.execute(prev_module_progress_query)
            prev_module_progress = list(prev_module_progress_result.scalars().all())

            completed_count = sum(
                1 for p in prev_module_progress if p.status == ProgressStatus.COMPLETED
            )
            lesson.is_locked = completed_count < len(prev_module_lesson_ids)  # type: ignore
        else:
            # Первый урок первого модуля - всегда разблокирован
            lesson.is_locked = False  # type: ignore

    return lesson
