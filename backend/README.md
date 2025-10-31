# Backend (FastAPI)

FastAPI-based backend service.

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
