# Course API Endpoints Documentation

## Overview

This document describes the Course API endpoints implemented for fetching course structure with access control based on user progress.

## Implementation Summary

### Endpoints

1. **GET /courses/modules** - List all modules with pagination
2. **GET /courses/modules/{module_id}** - Get module detail with lessons summary
3. **GET /courses/lessons/{lesson_id}** - Get lesson detail (theory, task, expected result)

All endpoints require authentication via JWT Bearer token.

### Access Control Logic

#### Module Unlocking
- The first module is always unlocked for all users
- Subsequent modules are unlocked only after completing all lessons in the previous module
- A module is considered "locked" if the previous module is not fully completed

#### Lesson Unlocking
- Within a module, the first lesson is unlocked if the module is unlocked
- Subsequent lessons are unlocked only after completing the previous lesson
- A lesson is considered "completed" when `UserProgress.status == ProgressStatus.COMPLETED`

### Features

- **Pagination**: Module list supports pagination with `page` and `page_size` query parameters
- **Russian Content**: All user-facing content is in Russian
- **Progress Tracking**: Each endpoint returns progress status (not_started, in_progress, completed)
- **OpenAPI Documentation**: All endpoints are fully documented with Russian descriptions

## Files Created

### Core
- `app/core/auth.py` - Authentication dependency (`get_current_user`)

### Schemas
- `app/schemas/courses.py` - Pydantic models for course endpoints:
  - `ModuleListItem` - Module summary in list
  - `ModuleListResponse` - Paginated module list response
  - `ModuleDetail` - Detailed module with lessons
  - `LessonSummary` - Lesson summary in module detail
  - `LessonDetail` - Full lesson information

### Services
- `app/services/courses.py` - Business logic for course access:
  - `get_modules_with_progress()` - Fetch modules with unlock status
  - `get_module_detail_with_progress()` - Fetch module with lessons and unlock status
  - `get_lesson_detail_with_progress()` - Fetch lesson with unlock status

### Routers
- `app/routers/courses.py` - API route handlers for course endpoints

### Tests
- `tests/test_courses.py` - Comprehensive test suite (16 tests):
  - Authentication tests
  - Module list tests (empty, basic, with progress, pagination)
  - Module unlocking tests
  - Module detail tests
  - Lesson detail tests
  - Lesson unlocking tests
  - Schema validation tests

## API Examples

### List Modules

```http
GET /courses/modules?page=1&page_size=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Введение в SQL",
      "description": "Основы работы с SQL",
      "order": 1,
      "is_published": true,
      "is_locked": false,
      "lessons_count": 3,
      "completed_lessons_count": 2
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### Get Module Detail

```http
GET /courses/modules/1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "title": "Введение в SQL",
  "description": "Основы работы с SQL",
  "order": 1,
  "is_published": true,
  "is_locked": false,
  "lessons": [
    {
      "id": 1,
      "title": "Основы SELECT",
      "order": 1,
      "estimated_duration": 15,
      "is_published": true,
      "is_locked": false,
      "progress_status": "completed"
    }
  ],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Get Lesson Detail

```http
GET /courses/lessons/1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "module_id": 1,
  "title": "Основы SELECT",
  "content": "В этом уроке вы познакомитесь с основным оператором SQL - SELECT.",
  "theory": "SELECT - это основной оператор для запросов к базе данных...",
  "sql_solution": "SELECT * FROM users;",
  "expected_result": {
    "columns": ["id", "name", "email"],
    "rows": [[1, "Иван", "ivan@example.com"]]
  },
  "order": 1,
  "estimated_duration": 15,
  "is_published": true,
  "is_locked": false,
  "progress_status": "completed",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## Testing

Run the tests:
```bash
poetry run pytest tests/test_courses.py -v
```

All 16 tests cover:
- Unauthenticated access (401/403)
- Empty state
- Basic functionality
- Progress tracking
- Module/lesson unlocking logic
- Pagination
- Not found cases (404)
- Response schema validation

## OpenAPI Documentation

The API is fully documented with OpenAPI/Swagger. Visit `/docs` when running the server to see interactive documentation.

All endpoints include:
- Summary in Russian
- Detailed description
- Parameter descriptions
- Response schemas
- Security requirements (Bearer token)

## Notes

- All timestamps use UTC
- Pagination uses 1-based page numbers
- Default page size is 20, maximum is 100
- Russian text is used throughout for user-facing content
- Access control is based on sequential completion (no skipping)
