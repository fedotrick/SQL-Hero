from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.database import User
from app.schemas.courses import (
    LessonDetail,
    LessonSummary,
    ModuleDetail,
    ModuleListItem,
    ModuleListResponse,
)
from app.services.courses import (
    get_lesson_detail_with_progress,
    get_module_detail_with_progress,
    get_modules_with_progress,
)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "/modules",
    response_model=ModuleListResponse,
    summary="Получить список модулей курса",
    description=(
        "Возвращает список всех опубликованных модулей с информацией о "
        "прогрессе пользователя и статусе блокировки"
    ),
)
async def list_modules(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Номер страницы (начиная с 1)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Количество элементов на странице")
    ] = 20,
) -> ModuleListResponse:
    """
    Получить список модулей с пагинацией.

    Модули разблокируются последовательно после завершения всех уроков предыдущего модуля.
    Первый модуль всегда разблокирован.
    """
    skip = (page - 1) * page_size
    modules, total = await get_modules_with_progress(db, current_user, skip=skip, limit=page_size)

    items = [
        ModuleListItem(
            id=module.id,
            title=module.title,
            description=module.description,
            order=module.order,
            is_published=module.is_published,
            is_locked=module.is_locked,  # type: ignore
            lessons_count=module.lessons_count,  # type: ignore
            completed_lessons_count=module.completed_lessons_count,  # type: ignore
        )
        for module in modules
    ]

    total_pages = (total + page_size - 1) // page_size

    return ModuleListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/modules/{module_id}",
    response_model=ModuleDetail,
    summary="Получить детальную информацию о модуле",
    description="Возвращает детальную информацию о модуле включая список уроков с их статусами",
)
async def get_module(
    module_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModuleDetail:
    """
    Получить детальную информацию о модуле с уроками.

    Каждый урок содержит информацию о статусе прогресса и блокировке.
    Уроки разблокируются последовательно после завершения предыдущего урока.
    """
    module = await get_module_detail_with_progress(db, current_user, module_id)

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Модуль не найден",
        )

    lessons = [
        LessonSummary(
            id=lesson.id,
            title=lesson.title,
            order=lesson.order,
            estimated_duration=lesson.estimated_duration,
            is_published=lesson.is_published,
            is_locked=lesson.is_locked,  # type: ignore
            progress_status=lesson.progress_status,  # type: ignore
        )
        for lesson in module.lessons
        if lesson.is_published
    ]

    return ModuleDetail(
        id=module.id,
        title=module.title,
        description=module.description,
        order=module.order,
        is_published=module.is_published,
        is_locked=module.is_locked,  # type: ignore
        lessons=lessons,
        created_at=module.created_at,
        updated_at=module.updated_at,
    )


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetail,
    summary="Получить детальную информацию об уроке",
    description=(
        "Возвращает полную информацию об уроке включая теорию, задание и ожидаемый результат"
    ),
)
async def get_lesson(
    lesson_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LessonDetail:
    """
    Получить детальную информацию об уроке.

    Содержит теоретический материал, SQL решение, ожидаемый результат и статус прогресса.
    Урок может быть заблокирован, если не завершён предыдущий урок или предыдущий модуль.
    """
    lesson = await get_lesson_detail_with_progress(db, current_user, lesson_id)

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Урок не найден",
        )

    return LessonDetail(
        id=lesson.id,
        module_id=lesson.module_id,
        title=lesson.title,
        content=lesson.content,
        theory=lesson.theory,
        sql_solution=lesson.sql_solution,
        expected_result=lesson.expected_result,
        order=lesson.order,
        estimated_duration=lesson.estimated_duration,
        is_published=lesson.is_published,
        is_locked=lesson.is_locked,  # type: ignore
        progress_status=lesson.progress_status,  # type: ignore
        attempts=lesson.attempts,  # type: ignore
        created_at=lesson.created_at,
        updated_at=lesson.updated_at,
    )
