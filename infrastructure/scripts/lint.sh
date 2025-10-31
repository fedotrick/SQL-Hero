#!/bin/bash
set -e

echo "🔍 Linting backend..."
cd backend
export PATH="/home/engine/.local/bin:$PATH"
poetry run ruff check app
poetry run mypy app
echo "✅ Backend linting passed"
cd ..

echo "🔍 Linting frontend..."
cd frontend
pnpm lint
pnpm format:check
echo "✅ Frontend linting passed"
cd ..

echo "✅ All linting checks passed!"
