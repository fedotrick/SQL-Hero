from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LessonSummary(BaseModel):
    """Краткая информация об уроке для отображения в списке модуля."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    order: int
    estimated_duration: int | None
    is_published: bool
    is_locked: bool
    progress_status: str | None = None


class ModuleListItem(BaseModel):
    """Элемент списка модулей."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    order: int
    is_published: bool
    is_locked: bool
    lessons_count: int
    completed_lessons_count: int


class ModuleListResponse(BaseModel):
    """Ответ со списком модулей с пагинацией."""

    items: list[ModuleListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ModuleDetail(BaseModel):
    """Детальная информация о модуле с уроками."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    order: int
    is_published: bool
    is_locked: bool
    lessons: list[LessonSummary]
    created_at: datetime
    updated_at: datetime


class LessonDetail(BaseModel):
    """Детальная информация об уроке."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    module_id: int
    title: str
    content: str | None
    theory: str | None
    sql_solution: str | None
    expected_result: dict[str, Any] | None
    order: int
    estimated_duration: int | None
    is_published: bool
    is_locked: bool
    progress_status: str | None = None
    attempts: int = 0
    created_at: datetime
    updated_at: datetime
