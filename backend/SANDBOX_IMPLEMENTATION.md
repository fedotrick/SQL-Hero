# Sandbox Architecture Implementation

## Overview

This document provides an overview of the sandbox architecture implementation for per-user MySQL sandboxes. The sandbox system enables secure, isolated SQL query execution for educational purposes.

## Documentation

📖 **[Complete Technical Design Document](/docs/sandbox.md)**

The comprehensive technical design document is available at `/docs/sandbox.md` and includes:
- Architecture decisions and technology choices
- Component specifications and interfaces
- Security constraints and resource limits
- Lifecycle management and cleanup policies
- API design and configuration options
- Implementation roadmap and testing strategy

## Implementation Status

### Phase 1: Core Foundation ✅ COMPLETED

All Phase 1 deliverables have been completed:

- ✅ **Technical Design Document** - Comprehensive 500+ line architecture document
- ✅ **Configuration System** - Full validation and environment variable support
- ✅ **Service Interfaces** - Abstract base classes for all major components
- ✅ **Schema Models** - Pydantic models for requests/responses
- ✅ **Mock Implementations** - In-memory implementations for testing
- ✅ **Comprehensive Tests** - 68 passing tests with 100% coverage of config validation

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   └── sandbox_config.py        # Configuration with validation
│   ├── services/
│   │   └── sandbox.py                # Service interfaces and implementations
│   └── schemas/
│       └── sandbox.py                # Pydantic models
├── tests/
│   ├── test_sandbox_config.py        # Config validation tests (28 tests)
│   └── test_sandbox_service.py       # Service unit tests (40 tests)
└── docs/
    └── sandbox.md                    # Technical design document

```

## Key Components

### 1. Configuration (`app/core/sandbox_config.py`)

The `SandboxConfig` class provides comprehensive configuration management with validation:

```python
from app.core.sandbox_config import SandboxConfig, get_sandbox_config

config = SandboxConfig(
    enabled=True,
    mysql_admin_password="secure_password",
    max_active_sandboxes=1000,
    idle_timeout_minutes=30,
    query_timeout_seconds=30
)
```

**Features:**
- Environment variable support with `SANDBOX_` prefix
- Field validation (ranges, required fields, cross-field validation)
- Schema name generation utilities
- Configurable security patterns and limits

### 2. Service Interfaces (`app/services/sandbox.py`)

Abstract interfaces define contracts for all major components:

#### ISandboxManager
Manages sandbox lifecycle (create, retrieve, destroy, cleanup)

#### ISchemaManager
Handles MySQL schema operations (create, seed, drop)

#### IQueryExecutor
Executes and validates SQL queries with security constraints

### 3. Mock Implementations

In-memory implementations for testing and development:

- `InMemorySandboxManager` - Memory-based sandbox tracking
- `MockSchemaManager` - Schema operation simulation
- `MockQueryExecutor` - Query validation and execution

### 4. Data Models (`app/schemas/sandbox.py`)

Pydantic models for API contracts:

- `SandboxCreateRequest` / `SandboxCreateResponse`
- `QueryExecuteRequest` / `QueryExecuteResponse`
- `SandboxStatusResponse`
- `CleanupResult`
- `QueryValidationResult`

## Usage Examples

### Creating a Sandbox Service

```python
from app.core.sandbox_config import SandboxConfig
from app.services.sandbox import (
    SandboxService,
    InMemorySandboxManager,
    MockSchemaManager,
    MockQueryExecutor
)

# Initialize configuration
config = SandboxConfig(
    enabled=True,
    mysql_admin_password="password"
)

# Create service with implementations
service = SandboxService(
    config=config,
    sandbox_manager=InMemorySandboxManager(config),
    schema_manager=MockSchemaManager(config),
    query_executor=MockQueryExecutor(config)
)

# Create a sandbox
sandbox = await service.create_sandbox(user_id=123, lesson_id=5)

# Execute a query
result = await service.execute_query(
    sandbox.sandbox_id,
    "SELECT * FROM employees WHERE department = 'Engineering'"
)

# Cleanup
await service.destroy_sandbox(sandbox.sandbox_id)
```

### Configuration Validation

The configuration system includes extensive validation:

```python
from pydantic import ValidationError
from app.core.sandbox_config import SandboxConfig

# This will raise ValidationError - password required when enabled
try:
    config = SandboxConfig(enabled=True, mysql_admin_password="")
except ValidationError as e:
    print(e)

# This will raise ValidationError - idle timeout exceeds max lifetime
try:
    config = SandboxConfig(
        idle_timeout_minutes=300,
        max_lifetime_hours=4  # 240 minutes
    )
except ValidationError as e:
    print(e)
```

### Query Validation

Queries are validated against security patterns:

```python
from app.services.sandbox import QueryValidator
from app.core.sandbox_config import SandboxConfig

config = SandboxConfig()
validator = QueryValidator(config)

# Valid query
result = validator.validate("SELECT * FROM employees")
assert result.is_valid == True
assert result.query_type == "SELECT"

# Blocked query
result = validator.validate("DROP TABLE employees")
assert result.is_valid == False
assert len(result.errors) > 0
```

## Configuration Options

### Environment Variables

All configuration can be set via environment variables:

```bash
# Core settings
SANDBOX_ENABLED=true
SANDBOX_MYSQL_HOST=localhost
SANDBOX_MYSQL_PORT=3306
SANDBOX_MYSQL_ADMIN_USER=sandbox_admin
SANDBOX_MYSQL_ADMIN_PASSWORD=secure_password

# Resource limits
SANDBOX_MAX_ACTIVE_SANDBOXES=1000
SANDBOX_MAX_SANDBOXES_PER_USER=3
SANDBOX_IDLE_TIMEOUT_MINUTES=30
SANDBOX_MAX_LIFETIME_HOURS=4

# Query limits
SANDBOX_QUERY_TIMEOUT_SECONDS=30
SANDBOX_MAX_RESULT_ROWS=1000
SANDBOX_RATE_LIMIT_QUERIES_PER_MINUTE=60

# Features
SANDBOX_ENABLE_METRICS=true
SANDBOX_ENABLE_QUERY_LOGGING=false
```

### Default Values

See `app/core/sandbox_config.py` for all default values and valid ranges.

## Testing

### Running Tests

```bash
# All sandbox tests
poetry run pytest tests/test_sandbox_config.py tests/test_sandbox_service.py -v

# Config validation tests only
poetry run pytest tests/test_sandbox_config.py -v

# Service tests only
poetry run pytest tests/test_sandbox_service.py -v

# With coverage
poetry run pytest tests/test_sandbox*.py --cov=app.core.sandbox_config --cov=app.services.sandbox
```

### Test Coverage

- **Config Tests**: 28 tests covering all validation scenarios
- **Service Tests**: 40 tests covering all interfaces and mock implementations
- **Total**: 68 passing tests

### Test Categories

1. **Configuration Validation**
   - Default values
   - Field validation (ranges, types)
   - Cross-field validation
   - Password requirements
   - Schema name generation

2. **Query Validation**
   - SQL syntax detection
   - Blocked patterns (DROP, ALTER, etc.)
   - System schema access prevention
   - Query type detection

3. **Sandbox Management**
   - Lifecycle operations
   - User limits
   - Expiration and cleanup
   - Access tracking

4. **Schema Operations**
   - Schema creation/deletion
   - Data seeding
   - User management

5. **Query Execution**
   - Valid query execution
   - Security validation
   - Error handling

## Security Features

### Query-Level Security

- **Blocked Commands**: DROP, ALTER, TRUNCATE, CREATE DATABASE, GRANT, REVOKE
- **System Schema Protection**: Blocks access to `information_schema`, `mysql`, `performance_schema`
- **Query Validation**: Syntax and pattern matching before execution
- **Timeout Enforcement**: 30-second default query timeout
- **Result Limits**: Maximum 1000 rows per query

### Resource Limits

- **Per-User Limits**: Maximum 3 sandboxes per user
- **System Limits**: Maximum 1000 concurrent sandboxes
- **Rate Limiting**: 60 queries per minute per user
- **Memory Limits**: 100MB per query
- **Schema Size**: 100MB maximum

### Isolation

- **Schema-Level**: Each user gets isolated MySQL schema
- **User-Level**: Dedicated MySQL user per sandbox
- **Privilege Restriction**: Only SELECT, INSERT, UPDATE, DELETE allowed
- **Automatic Cleanup**: Expired sandboxes cleaned up automatically

## Next Steps (Phase 2)

### MySQL Integration

Implement production-ready MySQL schema manager:

1. Real MySQL connection using aiomysql
2. Schema creation with DDL operations
3. Template-based data seeding
4. User privilege management
5. Connection pooling

### API Endpoints

Implement REST API for sandbox operations:

```
POST   /api/v1/sandbox/create
POST   /api/v1/sandbox/{id}/query
DELETE /api/v1/sandbox/{id}
GET    /api/v1/sandbox/{id}/status
```

### Background Tasks

Implement cleanup scheduler:

1. Periodic expired sandbox cleanup
2. Resource monitoring and metrics
3. Automatic teardown on timeout
4. Logging and alerting

### Persistence Layer

Add database models for sandbox metadata:

1. Track active sandboxes
2. Store query history (optional)
3. Monitor resource usage
4. Support sandbox recovery

## Architecture Highlights

### Technology Choice: MySQL Multi-Schema

The design uses MySQL multi-schema approach for several reasons:

- **Resource Efficiency**: Minimal overhead compared to Docker containers
- **Fast Provisioning**: Schema creation in milliseconds
- **Cost-Effective**: Single MySQL instance supports 1000+ sandboxes
- **Operational Simplicity**: Easy to manage and monitor
- **Sufficient Isolation**: Database-level isolation adequate for educational use

### Design Patterns

- **Strategy Pattern**: Pluggable implementations via interfaces
- **Dependency Injection**: Services accept interface implementations
- **Configuration Object**: Centralized, validated configuration
- **Value Objects**: Immutable sandbox and query result models

### Code Quality

- **Type Safety**: Full type hints with strict mypy checking
- **Input Validation**: Pydantic models with comprehensive validation
- **Test Coverage**: 68 tests covering all scenarios
- **Code Style**: Ruff-compliant formatting and linting
- **Documentation**: Comprehensive inline and external docs

## Contributing

When extending the sandbox implementation:

1. **Follow Interfaces**: Implement abstract base classes
2. **Add Tests**: Maintain test coverage for new features
3. **Validate Configuration**: Add validation for new config fields
4. **Update Documentation**: Keep design doc in sync with implementation
5. **Type Hints**: Use strict type hints for all functions
6. **Security First**: Consider security implications of all changes

## References

- [Technical Design Document](/docs/sandbox.md) - Complete architecture specification
- [Configuration Reference](app/core/sandbox_config.py) - All configuration options
- [Service Interfaces](app/services/sandbox.py) - Implementation contracts
- [Test Suite](tests/) - Usage examples and test scenarios

---

**Implementation Date**: 2024  
**Status**: Phase 1 Complete, Ready for Phase 2  
**Test Coverage**: 68 passing tests
