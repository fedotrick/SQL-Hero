# Alembic Database Migrations

This project uses Alembic for database migrations with SQLAlchemy async support.

## Prerequisites

Make sure the database is running (via docker-compose or locally) and the `DATABASE_URL` environment variable is set.

## Common Commands

### Generate a new migration

After making changes to your models, generate a migration:

```bash
poetry run alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

Apply all pending migrations to the database:

```bash
poetry run alembic upgrade head
```

### Rollback migrations

Rollback the last migration:

```bash
poetry run alembic downgrade -1
```

### View migration history

```bash
poetry run alembic history
```

### View current revision

```bash
poetry run alembic current
```

## Configuration

- **alembic.ini**: Main Alembic configuration file
- **alembic/env.py**: Migration environment setup, configured for async SQLAlchemy
- **alembic/versions/**: Directory containing migration scripts

The configuration automatically reads the `DATABASE_URL` from settings.
