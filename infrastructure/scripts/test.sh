#!/bin/bash
set -e

echo "🧪 Running backend tests..."
cd backend
export PATH="/home/engine/.local/bin:$PATH"
poetry run pytest
echo "✅ Backend tests passed"
cd ..

echo "🧪 Running frontend tests..."
cd frontend
if command -v pnpm &> /dev/null; then
    pnpm test --run
    echo "✅ Frontend tests passed"
else
    echo "⚠️  pnpm not found, skipping frontend tests"
fi
cd ..

echo "✅ All tests passed!"
