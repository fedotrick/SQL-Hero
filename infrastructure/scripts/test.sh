#!/bin/bash
set -e

echo "🧪 Running backend tests..."
cd backend
export PATH="/home/engine/.local/bin:$PATH"
poetry run pytest
echo "✅ Backend tests passed"
cd ..

echo "✅ All tests passed!"
