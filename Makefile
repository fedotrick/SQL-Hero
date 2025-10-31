.PHONY: help setup install lint format test docker-up docker-down docker-build clean db-migrate db-seed

help:
	@echo "Available commands:"
	@echo "  make setup        - Initial setup (install dependencies, pre-commit hooks)"
	@echo "  make install      - Install all dependencies"
	@echo "  make lint         - Run linting for backend and frontend"
	@echo "  make format       - Format code for backend and frontend"
	@echo "  make test         - Run all tests"
	@echo "  make docker-up    - Start all services with docker-compose"
	@echo "  make docker-down  - Stop all services"
	@echo "  make docker-build - Rebuild and start services"
	@echo "  make db-migrate   - Run database migrations"
	@echo "  make db-seed      - Seed database with initial data"
	@echo "  make clean        - Clean build artifacts"

setup:
	@./infrastructure/scripts/setup.sh

install:
	@echo "Installing backend dependencies..."
	@cd backend && poetry install
	@echo "Installing frontend dependencies..."
	@cd frontend && pnpm install

lint:
	@./infrastructure/scripts/lint.sh

format:
	@echo "Formatting backend..."
	@cd backend && poetry run ruff format app
	@echo "Formatting frontend..."
	@cd frontend && pnpm format

test:
	@./infrastructure/scripts/test.sh

docker-up:
	@docker-compose up

docker-down:
	@docker-compose down

docker-build:
	@docker-compose up --build

db-migrate:
	@echo "Running database migrations..."
	@cd backend && poetry run alembic upgrade head

db-seed:
	@echo "Seeding database with initial data..."
	@cd backend && python manage.py seed

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf backend/__pycache__ backend/.pytest_cache backend/.ruff_cache backend/.mypy_cache
	@rm -rf frontend/dist frontend/node_modules/.cache
	@echo "Clean complete!"
