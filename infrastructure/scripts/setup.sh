#!/bin/bash
set -e

echo "🚀 Setting up monorepo..."

# Install pre-commit
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip3 install pre-commit --break-system-packages || pip3 install pre-commit --user
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Setup backend
echo "📦 Setting up backend..."
cd backend
if [ ! -f "poetry.lock" ]; then
    poetry install
else
    echo "Backend already initialized"
fi
cd ..

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    pnpm install
else
    echo "Frontend already initialized"
fi
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  • Copy .env.example files to .env in backend and frontend"
echo "  • Run 'docker-compose up' to start all services"
