# Infrastructure

This directory contains infrastructure-related files and scripts.

## Structure

- `docker/` - Docker-related configurations
- `scripts/` - Utility scripts for development and deployment

## Scripts

### setup.sh
Initial project setup script. Installs pre-commit hooks and project dependencies.

```bash
./infrastructure/scripts/setup.sh
```

### lint.sh
Runs linting checks for both backend and frontend.

```bash
./infrastructure/scripts/lint.sh
```

### test.sh
Runs all tests for the project.

```bash
./infrastructure/scripts/test.sh
```

## Docker

The main `docker-compose.yml` is located in the project root. It includes:

- MySQL database
- FastAPI backend
- React frontend

See the main README for Docker usage instructions.
