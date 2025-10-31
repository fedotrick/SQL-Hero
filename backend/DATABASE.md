# Database Schema Documentation

This document describes the database schema and models for the application.

## Overview

The application uses MySQL 8.0 with SQLAlchemy 2.0 (async) and Alembic for migrations.

## Tables

### Users Table
Stores user account information, primarily from Telegram.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `telegram_id` (BigInteger, Unique, Not Null, Indexed) - Telegram user ID
- `username` (String(100), Nullable) - Telegram username
- `first_name` (String(100), Nullable)
- `last_name` (String(100), Nullable)
- `language_code` (String(10), Nullable)
- `is_active` (Boolean, Not Null, Default: True)
- `created_at` (DateTime, Not Null)
- `updated_at` (DateTime, Not Null)

**Indexes:**
- Unique index on `telegram_id`

**Relationships:**
- One-to-many with `user_progress`
- One-to-many with `user_achievements`
- One-to-many with `activity_log`

### Modules Table
Represents learning modules or courses.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `title` (String(200), Not Null)
- `description` (Text, Nullable)
- `order` (Integer, Not Null, Indexed) - Display order
- `is_published` (Boolean, Not Null, Default: False)
- `created_at` (DateTime, Not Null)
- `updated_at` (DateTime, Not Null)

**Indexes:**
- Index on `order`

**Relationships:**
- One-to-many with `lessons`

### Lessons Table
Individual lessons within modules.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `module_id` (Integer, Foreign Key → modules.id, Not Null, Indexed)
- `title` (String(200), Not Null)
- `content` (Text, Nullable)
- `order` (Integer, Not Null) - Order within module
- `estimated_duration` (Integer, Nullable) - Duration in minutes
- `is_published` (Boolean, Not Null, Default: False)
- `created_at` (DateTime, Not Null)
- `updated_at` (DateTime, Not Null)

**Indexes:**
- Composite index on `(module_id, order)`
- Index on `module_id`

**Relationships:**
- Many-to-one with `modules`
- One-to-many with `user_progress`

### User Progress Table
Tracks user progress through lessons.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `user_id` (Integer, Foreign Key → users.id, Not Null)
- `lesson_id` (Integer, Foreign Key → lessons.id, Not Null)
- `status` (Enum: NOT_STARTED, IN_PROGRESS, COMPLETED, Not Null)
- `score` (Integer, Nullable)
- `attempts` (Integer, Not Null, Default: 0)
- `started_at` (DateTime, Nullable)
- `completed_at` (DateTime, Nullable)
- `created_at` (DateTime, Not Null)
- `updated_at` (DateTime, Not Null)

**Constraints:**
- Unique constraint on `(user_id, lesson_id)`

**Indexes:**
- Composite index on `(user_id, status)`
- Composite index on `(lesson_id, status)`

**Relationships:**
- Many-to-one with `users`
- Many-to-one with `lessons`

### Achievements Table
Defines available achievements that users can earn.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `type` (Enum: LESSON_COMPLETED, MODULE_COMPLETED, STREAK, CHALLENGES_SOLVED, MILESTONE, Not Null, Indexed)
- `title` (String(200), Not Null)
- `description` (Text, Nullable)
- `icon` (String(100), Nullable)
- `points` (Integer, Not Null, Default: 0)
- `criteria` (Text, Nullable) - JSON or text describing criteria
- `created_at` (DateTime, Not Null)

**Indexes:**
- Index on `type`

**Relationships:**
- One-to-many with `user_achievements`

### User Achievements Table
Junction table linking users with earned achievements.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `user_id` (Integer, Foreign Key → users.id, Not Null)
- `achievement_id` (Integer, Foreign Key → achievements.id, Not Null)
- `earned_at` (DateTime, Not Null)

**Constraints:**
- Unique constraint on `(user_id, achievement_id)`

**Indexes:**
- Composite index on `(user_id, earned_at)`

**Relationships:**
- Many-to-one with `users`
- Many-to-one with `achievements`

### Leaderboard Cache Table
Cached leaderboard data for performance.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `user_id` (Integer, Foreign Key → users.id, Not Null, Unique)
- `rank` (Integer, Not Null, Indexed)
- `total_score` (Integer, Not Null, Default: 0)
- `lessons_completed` (Integer, Not Null, Default: 0)
- `achievements_count` (Integer, Not Null, Default: 0)
- `updated_at` (DateTime, Not Null)

**Indexes:**
- Composite index on `(rank, total_score)`
- Index on `rank`

### Activity Log Table
Tracks user activity for analytics and monitoring.

**Columns:**
- `id` (Primary Key, Auto-increment)
- `user_id` (Integer, Foreign Key → users.id, Not Null, Indexed)
- `activity_type` (Enum: LESSON_STARTED, LESSON_COMPLETED, CHALLENGE_ATTEMPTED, CHALLENGE_SOLVED, ACHIEVEMENT_EARNED, LOGIN, Not Null, Indexed)
- `entity_id` (Integer, Nullable) - ID of related entity
- `entity_type` (String(50), Nullable) - Type of related entity
- `details` (Text, Nullable) - JSON or text with additional details
- `created_at` (DateTime, Not Null, Indexed)

**Indexes:**
- Composite index on `(user_id, activity_type, created_at)`
- Index on `created_at`
- Index on `activity_type`
- Index on `user_id`

**Relationships:**
- Many-to-one with `users`

## Enums

### ProgressStatus
- `NOT_STARTED` - Lesson not yet started
- `IN_PROGRESS` - Lesson in progress
- `COMPLETED` - Lesson completed

### AchievementType
- `LESSON_COMPLETED` - Achievement for completing a lesson
- `MODULE_COMPLETED` - Achievement for completing a module
- `STREAK` - Achievement for maintaining a learning streak
- `CHALLENGES_SOLVED` - Achievement for solving challenges
- `MILESTONE` - Achievement for reaching a milestone

### ActivityType
- `LESSON_STARTED` - User started a lesson
- `LESSON_COMPLETED` - User completed a lesson
- `CHALLENGE_ATTEMPTED` - User attempted a challenge
- `CHALLENGE_SOLVED` - User solved a challenge
- `ACHIEVEMENT_EARNED` - User earned an achievement
- `LOGIN` - User logged in

## Migration Commands

```bash
# Generate a new migration after model changes
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback last migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# Check current revision
poetry run alembic current
```

## Testing

The database schema is thoroughly tested with:
- Model structure tests (table names, columns, relationships)
- Constraint tests (NOT NULL, UNIQUE)
- Index tests (single and composite indexes)
- Foreign key tests
- Migration upgrade/downgrade cycle tests

Run tests with:
```bash
export DATABASE_URL="mysql+aiomysql://user:password@localhost:3306/appdb"
poetry run pytest tests/test_models.py tests/test_migrations.py -v
```
