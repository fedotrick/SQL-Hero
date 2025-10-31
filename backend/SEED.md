# Database Seeding

This document describes how to use the database seeding functionality to populate the database with initial course data.

## Overview

The seed command populates the database with:
- **10 modules** covering SQL topics from basics to advanced
- **2-3 lessons per module** with Russian content, theory, SQL solutions, and expected results
- **Sample achievements** with codes and icon placeholders

The seeding process is **idempotent**, meaning you can run it multiple times safely. It will skip any data that already exists in the database.

## Quick Start

### Using the Management CLI

```bash
cd backend
python manage.py seed
```

### Using Poetry

```bash
cd backend
poetry run python manage.py seed
```

### Using Docker

```bash
docker compose exec backend python manage.py seed
```

## What Gets Seeded

### Modules

10 modules covering:
1. Введение в SQL (Introduction to SQL)
2. Работа с таблицами (Working with Tables)
3. Фильтрация и сортировка (Filtering and Sorting)
4. Агрегация данных (Data Aggregation)
5. Объединение таблиц (Table Joins)
6. Подзапросы (Subqueries)
7. Индексы и оптимизация (Indexes and Optimization)
8. Транзакции и блокировки (Transactions and Locks)
9. Хранимые процедуры (Stored Procedures)
10. Продвинутые техники (Advanced Techniques)

Each module includes:
- Title (in Russian)
- Description
- Sequential order number
- Published status

### Lessons

Each module contains 2-3 lessons with:
- **Title** - Lesson name in Russian
- **Content** - Main lesson content in Russian
- **Theory** - Theoretical explanation and syntax examples
- **sql_solution** - Example SQL query
- **expected_result** - JSON containing expected query results (columns and rows)
- **Order** - Sequential order within the module
- **Estimated duration** - Time in minutes
- **Published status**

Example lesson structure:
```python
{
    "title": "Основы SELECT",
    "content": "В этом уроке вы познакомитесь с основным оператором SQL...",
    "theory": "SELECT - это основной оператор для запросов к базе данных...",
    "sql_solution": "SELECT * FROM users;",
    "expected_result": {
        "columns": ["id", "name", "email"],
        "rows": [[1, "Иван", "ivan@example.com"]]
    },
    "order": 1,
    "estimated_duration": 15,
    "is_published": True
}
```

### Achievements

10 sample achievements including:
- **first_lesson** - Complete first lesson (10 points) 🎓
- **module_1_complete** - Complete Introduction to SQL module (50 points) 📚
- **ten_lessons** - Complete 10 lessons (100 points) 💪
- **streak_7** - 7-day learning streak (75 points) 🔥
- **streak_30** - 30-day learning streak (300 points) 🏆
- **challenge_master** - Solve 50 challenges (200 points) 🎯
- **perfect_score** - Get 100% score (25 points) ⭐
- **all_modules** - Complete all modules (500 points) 👑
- **speed_runner** - Complete lesson under estimated time (30 points) ⚡
- **night_owl** - Complete lesson after midnight (15 points) 🦉

Each achievement includes:
- Unique code
- Type (lesson_completed, module_completed, streak, challenges_solved, milestone)
- Title and description (in Russian)
- Icon (emoji placeholder)
- Points value
- Criteria description

## Idempotency

The seed command is designed to be idempotent. It checks for existing data before inserting:

- **Modules**: Checked by `order` field
- **Lessons**: Checked by combination of `module_id` and `order`
- **Achievements**: Checked by `code` field

If a record already exists, it will be skipped with a message. This allows you to:
- Run the seed command multiple times safely
- Add new seed data incrementally
- Re-run after partial failures

## Verification

After seeding, the command automatically verifies:
- Total number of modules (should be 10)
- Total number of lessons
- Total number of achievements
- Lesson count per module (2-3 per module)

Example output:
```
Starting database seeding...
============================================================
Seeding modules...
  Created module 'Введение в SQL' (order 1)
  ...
Modules seeding completed: 10 modules

Seeding lessons...
  Created lesson 'Основы SELECT' (module 1, order 1)
  ...
Lessons seeding completed: 25 new lessons created

Seeding achievements...
  Created achievement 'Первые шаги' (code: first_lesson)
  ...
Achievements seeding completed: 10 new achievements created
============================================================

Verifying seed data...
  Total modules: 10
  Total lessons: 25
  Total achievements: 10
  Lessons per module: {1: 3, 2: 2, 3: 3, 4: 2, 5: 3, 6: 2, 7: 3, 8: 2, 9: 2, 10: 3}

✅ Database seeding completed successfully!
```

## Testing

The seed functionality includes comprehensive tests:

```bash
# Run all seed tests
poetry run pytest tests/test_seed.py -v

# Run specific test
poetry run pytest tests/test_seed.py::test_seed_modules_is_idempotent -v
```

Tests verify:
- All modules are created correctly
- Lesson counts per module align with spec (2-3 lessons)
- All required fields are populated (content, theory, sql_solution, expected_result)
- Russian content is present in lessons
- Achievement codes are unique
- Idempotency works correctly
- Expected results are valid JSON

## Customizing Seed Data

To customize the seed data, edit the following file:

```
backend/app/cli/seed_data.py
```

This file contains:
- `MODULES_DATA` - List of module definitions
- `LESSONS_DATA` - List of lessons grouped by module
- `ACHIEVEMENTS_DATA` - List of achievement definitions

After modifying the seed data, run the seed command again to populate the database with the new data.

## Troubleshooting

### Database Connection Error

Make sure:
1. The database is running
2. The `DATABASE_URL` environment variable is set correctly
3. You can connect to the database

### Migration Not Applied

If you get errors about missing columns, make sure all migrations are applied:

```bash
poetry run alembic upgrade head
```

### Data Already Exists

If you see "already exists" messages, this is normal for idempotent operation. The command will skip existing records and only insert new ones.

### Foreign Key Errors

Make sure migrations are applied in the correct order, especially the migration that adds the new lesson fields.

## Related Documentation

- [ALEMBIC.md](./ALEMBIC.md) - Database migration guide
- [DATABASE.md](./DATABASE.md) - Database schema documentation
- [README.md](./README.md) - General backend documentation
