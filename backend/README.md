# Backend (FastAPI)

FastAPI-based backend service with SQLAlchemy async, Alembic migrations, and modular architecture.

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core functionality (config, database)
│   ├── models/         # SQLAlchemy models
│   ├── routers/        # API route handlers
│   ├── services/       # Business logic
│   └── main.py         # FastAPI application entry point
├── alembic/            # Database migrations
├── tests/              # Test suite
└── pyproject.toml      # Dependencies and configuration
```

## Features

- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM with type hints
- **Alembic**: Database migration management
- **Pydantic Settings**: Environment-based configuration
- **pytest**: Async test suite with httpx

## Configuration

Settings are managed via environment variables (see `.env.example`):

- `DATABASE_URL`: MySQL connection string (async)
- `DEBUG`: Debug mode
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `TELEGRAM_WEBHOOK_URL`: Webhook URL for Telegram
- `SANDBOX_ENABLED`: Enable/disable sandbox mode
- `SANDBOX_API_URL`: Sandbox service URL

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Lint
poetry run ruff check .

# Format
poetry run ruff format .

# Type check
poetry run mypy app

# Run server
poetry run uvicorn app.main:app --reload
```

## Database Migrations

See [ALEMBIC.md](./ALEMBIC.md) for detailed migration instructions.

```bash
# Generate migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

## Database Seeding

See [SEED.md](./SEED.md) for detailed seeding instructions.

```bash
# Load initial course data and achievements
python manage.py seed
```

The seed command populates the database with:
- 10 modules covering SQL basics to advanced topics
- 2-3 lessons per module with Russian content
- Sample achievements with codes and icons

## API Endpoints

- `GET /`: Root endpoint with app info
- `GET /health`: Health check endpoint with version info
