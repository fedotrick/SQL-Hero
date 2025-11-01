# Sandbox Architecture - Technical Design Document

## Executive Summary

This document outlines the architecture for a per-user MySQL sandbox system that enables secure, isolated SQL query execution for educational purposes. The system allows users to practice SQL queries on lesson-specific datasets without affecting the main application database or other users' data.

## 1. Overview

### 1.1 Purpose

The sandbox service provides isolated MySQL environments for users to:
- Execute SQL queries safely during lessons
- Work with pre-seeded datasets specific to each lesson
- Practice SQL without risk to production data
- Learn in a controlled, monitored environment

### 1.2 Goals

- **Security**: Ensure complete isolation between users and from production data
- **Performance**: Minimize resource overhead while supporting concurrent users
- **Scalability**: Support growth from hundreds to thousands of concurrent users
- **Maintainability**: Simple operational model with automated lifecycle management
- **Reliability**: Automatic cleanup and resource recovery

## 2. Architecture Decision

### 2.1 Technology Choice: MySQL Multi-Schema

After evaluating multiple approaches, we've selected **MySQL multi-schema** as the primary implementation strategy.

#### Comparison Matrix

| Aspect | MySQL Multi-Schema | Docker Containers | Kubernetes Pods |
|--------|-------------------|-------------------|-----------------|
| **Resource Efficiency** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐ Moderate | ⭐ Heavy |
| **Setup Time** | ⭐⭐⭐⭐⭐ < 1s | ⭐⭐ 5-10s | ⭐ 15-30s |
| **Isolation Level** | ⭐⭐⭐ Database | ⭐⭐⭐⭐ Process | ⭐⭐⭐⭐⭐ Pod |
| **Operational Complexity** | ⭐⭐⭐⭐⭐ Low | ⭐⭐⭐ Medium | ⭐⭐ High |
| **Cost Efficiency** | ⭐⭐⭐⭐⭐ Best | ⭐⭐⭐ Good | ⭐⭐ Expensive |

#### Rationale

1. **Educational Context**: Database-level isolation is sufficient for SQL learning scenarios
2. **Resource Efficiency**: Can support 1000+ concurrent sandboxes on modest hardware
3. **Fast Provisioning**: Schema creation and seeding completes in milliseconds
4. **Cost-Effective**: Minimal infrastructure overhead
5. **Operational Simplicity**: Single MySQL instance to manage

### 2.2 Future Extensibility

The architecture is designed to support multiple backends:
- **Phase 1**: MySQL multi-schema (current)
- **Phase 2**: Optional Docker SDK integration for advanced isolation
- **Phase 3**: Cloud-native solutions (AWS RDS, Google Cloud SQL)

## 3. System Architecture

### 3.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Sandbox Service Layer                     │    │
│  │  - SandboxManager                                   │    │
│  │  - SchemaManager                                    │    │
│  │  - QueryExecutor                                    │    │
│  │  - CleanupScheduler                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Sandbox Connection Pool                      │    │
│  │  - Per-user connection management                   │    │
│  │  - Timeout handling                                 │    │
│  │  - Resource limiting                                │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │       MySQL Server 8.0              │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │  Main Application Database   │  │
        │  │  (users, courses, progress)  │  │
        │  └──────────────────────────────┘  │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │  Sandbox Schemas             │  │
        │  │  - sandbox_user_{user_id}_*  │  │
        │  │  - Isolated per user         │  │
        │  │  - Temporary lifecycle       │  │
        │  └──────────────────────────────┘  │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │  Lesson Dataset Templates    │  │
        │  │  - lesson_{lesson_id}_tmpl   │  │
        │  │  - Read-only reference data  │  │
        │  └──────────────────────────────┘  │
        └─────────────────────────────────────┘
```

### 3.2 Key Components

#### 3.2.1 SandboxManager

The primary orchestrator for sandbox lifecycle management.

**Responsibilities:**
- Create new sandboxes on-demand
- Track active sandboxes
- Coordinate cleanup operations
- Manage sandbox metadata

**Key Methods:**
```python
async def create_sandbox(user_id: int, lesson_id: int) -> Sandbox
async def get_sandbox(sandbox_id: str) -> Sandbox | None
async def destroy_sandbox(sandbox_id: str) -> None
async def cleanup_expired_sandboxes() -> int
```

#### 3.2.2 SchemaManager

Handles MySQL schema operations.

**Responsibilities:**
- Create isolated schemas
- Seed lesson-specific data
- Apply security constraints
- Drop schemas on cleanup

**Key Methods:**
```python
async def create_schema(schema_name: str) -> None
async def seed_data(schema_name: str, lesson_id: int) -> None
async def drop_schema(schema_name: str) -> None
async def verify_schema_isolation(schema_name: str) -> bool
```

#### 3.2.3 QueryExecutor

Executes user SQL queries with safety constraints.

**Responsibilities:**
- Execute queries with timeout
- Limit result set size
- Block dangerous operations
- Return formatted results

**Key Methods:**
```python
async def execute_query(sandbox_id: str, query: str) -> QueryResult
async def validate_query(query: str) -> ValidationResult
```

#### 3.2.4 CleanupScheduler

Background task for resource management.

**Responsibilities:**
- Identify expired sandboxes
- Perform automated cleanup
- Monitor resource usage
- Report metrics

## 4. Sandbox Lifecycle

### 4.1 State Diagram

```
┌──────────┐
│   INIT   │ User requests sandbox
└────┬─────┘
     │
     ▼
┌──────────┐ Schema creation
│ CREATING │ Data seeding
└────┬─────┘ User provisioning
     │
     ▼
┌──────────┐ User executes queries
│  ACTIVE  │ Timeout tracking
└────┬─────┘
     │
     ▼
┌──────────┐ Idle timeout OR
│ EXPIRED  │ Max lifetime reached
└────┬─────┘
     │
     ▼
┌──────────┐ Schema dropped
│ DESTROYED│ Resources released
└──────────┘
```

### 4.2 Lifecycle Phases

#### Phase 1: Creation (< 1 second)

1. **Generate unique schema name**: `sandbox_user_{user_id}_{timestamp}`
2. **Create schema**: `CREATE DATABASE IF NOT EXISTS ...`
3. **Create restricted user**: `CREATE USER ... IDENTIFIED BY ...`
4. **Grant limited privileges**: `GRANT SELECT, INSERT, UPDATE, DELETE ON schema.* TO ...`
5. **Clone lesson dataset**: Copy tables from lesson template
6. **Seed initial data**: Insert lesson-specific records
7. **Register sandbox metadata**: Store in main database

#### Phase 2: Active Usage (configurable duration)

1. **Query execution**: Users submit SQL queries via API
2. **Validation**: Parse and validate queries before execution
3. **Execution**: Run queries with timeout and result limits
4. **Activity tracking**: Update last_accessed_at timestamp
5. **Resource monitoring**: Track query count, execution time

#### Phase 3: Expiration (automatic)

Sandboxes expire when:
- **Idle timeout**: No activity for N minutes (default: 30)
- **Max lifetime**: Absolute maximum duration (default: 4 hours)
- **Manual termination**: User explicitly ends session

#### Phase 4: Cleanup (automatic)

1. **Mark for deletion**: Set status to EXPIRED
2. **Background cleanup**:
   - Drop database schema
   - Drop sandbox user
   - Delete sandbox metadata
   - Log cleanup metrics

## 5. Security Constraints

### 5.1 Database-Level Security

#### User Privileges

Sandbox users have restricted privileges:

```sql
-- Allowed operations
GRANT SELECT, INSERT, UPDATE, DELETE ON sandbox_schema.* TO sandbox_user;

-- Explicitly denied
REVOKE CREATE, DROP, ALTER, INDEX, REFERENCES ON *.* FROM sandbox_user;
REVOKE SUPER, PROCESS, FILE, RELOAD, SHUTDOWN ON *.* FROM sandbox_user;
```

#### Schema Isolation

- **Naming convention**: All sandbox schemas prefixed with `sandbox_user_`
- **No cross-schema access**: Users can only access their own schema
- **No system schema access**: Restricted from `mysql`, `information_schema`, `performance_schema`

### 5.2 Query-Level Security

#### Query Validation

Before execution, queries are validated for:

1. **Syntax validation**: Parse SQL to ensure it's valid
2. **Blocked commands**: Reject DDL operations (CREATE, DROP, ALTER)
3. **Transaction control**: Limit transaction size and duration
4. **System access**: Block queries accessing system tables

**Blocked Patterns:**
```python
BLOCKED_PATTERNS = [
    r'\bDROP\b',
    r'\bCREATE\s+(?:DATABASE|SCHEMA)\b',
    r'\bALTER\b',
    r'\bTRUNCATE\b',
    r'\bGRANT\b',
    r'\bREVOKE\b',
    r'information_schema',
    r'mysql\.',
    r'performance_schema',
]
```

#### Execution Limits

- **Query timeout**: 30 seconds (configurable)
- **Result limit**: 1000 rows maximum
- **Memory limit**: 100MB per query
- **Concurrent queries**: 3 per sandbox

### 5.3 Network Security

- **Internal only**: Sandbox MySQL not exposed externally
- **Backend-only access**: Users access via FastAPI, not directly
- **Rate limiting**: Maximum 60 queries per minute per user

### 5.4 Resource Limits

Per-sandbox limits:

```yaml
max_connections: 5
max_queries_per_minute: 60
max_query_duration: 30s
max_result_rows: 1000
max_schema_size: 100MB
max_lifetime: 4h
idle_timeout: 30m
```

## 6. Data Seeding Strategy

### 6.1 Lesson Dataset Templates

Each lesson has a template schema: `lesson_{lesson_id}_template`

**Structure:**
```sql
CREATE DATABASE lesson_1_template;

USE lesson_1_template;

-- Example: Basic SELECT lesson
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2)
);

INSERT INTO employees VALUES
(1, 'Alice Johnson', 'Engineering', 95000.00),
(2, 'Bob Smith', 'Sales', 75000.00),
...;
```

### 6.2 Seeding Process

When creating a sandbox:

1. **Identify lesson template**: Query database for lesson's template schema
2. **Clone structure**: Use `SHOW CREATE TABLE` to replicate schema
3. **Copy data**: Use `INSERT INTO ... SELECT * FROM` to copy data
4. **Verify integrity**: Check row counts and constraints

**Performance Optimization:**
- Templates are cached in memory
- Use bulk inserts for seeding
- Pre-generate common template variations

### 6.3 Dataset Management

**Template Creation Workflow:**
1. Course designers create SQL files: `/datasets/lesson_{id}.sql`
2. Migration scripts import templates during deployment
3. Templates are versioned with lesson updates
4. Old versions retained for compatibility

## 7. Interface Design

### 7.1 Internal Python API

```python
from app.services.sandbox import SandboxManager, QueryExecutor

# Initialize
sandbox_manager = SandboxManager(config)
query_executor = QueryExecutor(config)

# Create sandbox
sandbox = await sandbox_manager.create_sandbox(
    user_id=123,
    lesson_id=5
)

# Execute query
result = await query_executor.execute_query(
    sandbox_id=sandbox.id,
    query="SELECT * FROM employees WHERE department = 'Engineering'"
)

# Cleanup
await sandbox_manager.destroy_sandbox(sandbox.id)
```

### 7.2 REST API Endpoints

```
POST   /api/v1/sandbox/create
  Body: { "lesson_id": 5 }
  Response: { "sandbox_id": "uuid", "expires_at": "2024-01-01T12:00:00Z" }

POST   /api/v1/sandbox/{sandbox_id}/query
  Body: { "query": "SELECT * FROM employees" }
  Response: { "columns": [...], "rows": [...], "execution_time": 0.123 }

DELETE /api/v1/sandbox/{sandbox_id}
  Response: { "status": "destroyed" }

GET    /api/v1/sandbox/{sandbox_id}/status
  Response: { "status": "active", "expires_at": "...", "query_count": 42 }
```

### 7.3 WebSocket Interface (Future)

For real-time query execution and streaming results:

```
WS /api/v1/sandbox/{sandbox_id}/stream

Client -> Server:
  { "action": "execute", "query": "SELECT * FROM large_table" }

Server -> Client:
  { "type": "progress", "rows_processed": 100 }
  { "type": "row", "data": [...] }
  { "type": "complete", "total_rows": 500 }
```

## 8. Monitoring and Observability

### 8.1 Metrics

Key metrics to track:

**Performance Metrics:**
- `sandbox.creation.duration` - Time to create sandbox
- `sandbox.query.duration` - Query execution time
- `sandbox.query.count` - Total queries executed
- `sandbox.active.count` - Current active sandboxes

**Resource Metrics:**
- `sandbox.schema.size` - Total size per sandbox
- `sandbox.connection.pool.size` - Connection pool utilization
- `mysql.connection.count` - Total DB connections

**Business Metrics:**
- `sandbox.created.total` - Total sandboxes created
- `sandbox.expired.total` - Total expired sandboxes
- `sandbox.error.count` - Failed operations
- `user.sandbox.session.duration` - Average session time

### 8.2 Logging

Structured logging with context:

```python
logger.info(
    "Sandbox created",
    extra={
        "sandbox_id": sandbox.id,
        "user_id": user.id,
        "lesson_id": lesson.id,
        "schema_name": sandbox.schema_name,
        "duration_ms": elapsed_time
    }
)
```

**Log Levels:**
- **INFO**: Lifecycle events (create, destroy)
- **WARNING**: Approaching limits, slow queries
- **ERROR**: Failed operations, security violations
- **DEBUG**: Query details (development only)

### 8.3 Alerting

Alert conditions:

1. **High error rate**: > 5% of operations failing
2. **Resource exhaustion**: > 80% of max sandboxes
3. **Slow operations**: P95 > 2 seconds
4. **Security violations**: Blocked query attempts
5. **Cleanup failures**: Schemas not being cleaned up

## 9. Configuration

### 9.1 Configuration Schema

```python
class SandboxConfig(BaseModel):
    # Database connection
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_admin_user: str = "sandbox_admin"
    mysql_admin_password: str
    
    # Sandbox limits
    max_active_sandboxes: int = 1000
    max_sandboxes_per_user: int = 3
    idle_timeout_minutes: int = 30
    max_lifetime_hours: int = 4
    
    # Query limits
    query_timeout_seconds: int = 30
    max_result_rows: int = 1000
    max_query_memory_mb: int = 100
    rate_limit_queries_per_minute: int = 60
    
    # Resource limits
    max_schema_size_mb: int = 100
    max_connections_per_sandbox: int = 5
    
    # Cleanup
    cleanup_interval_minutes: int = 5
    cleanup_batch_size: int = 10
    
    # Security
    allowed_query_types: list[str] = ["SELECT", "INSERT", "UPDATE", "DELETE"]
    blocked_patterns: list[str] = [...]
    
    # Monitoring
    enable_metrics: bool = True
    enable_query_logging: bool = False  # Privacy consideration
```

### 9.2 Environment Variables

```bash
# Core
SANDBOX_ENABLED=true
SANDBOX_MYSQL_HOST=localhost
SANDBOX_MYSQL_PORT=3306
SANDBOX_MYSQL_ADMIN_USER=sandbox_admin
SANDBOX_MYSQL_ADMIN_PASSWORD=secure_password

# Limits
SANDBOX_MAX_ACTIVE=1000
SANDBOX_IDLE_TIMEOUT_MIN=30
SANDBOX_MAX_LIFETIME_HOURS=4
SANDBOX_QUERY_TIMEOUT_SEC=30

# Features
SANDBOX_ENABLE_METRICS=true
SANDBOX_ENABLE_QUERY_LOG=false
```

## 10. Implementation Roadmap

### 10.1 Phase 1: Core Foundation (Current)

**Deliverables:**
- ✅ Technical design document (this document)
- ✅ Configuration schema and validation
- ✅ Service interfaces and base classes
- ✅ Basic schema management operations
- ✅ Unit tests for config and validation

**Code Structure:**
```
backend/app/
  ├── core/
  │   └── sandbox_config.py        # Configuration classes
  ├── services/
  │   └── sandbox.py                # Core service implementation
  ├── schemas/
  │   └── sandbox.py                # Pydantic models
  └── routers/
      └── sandbox.py                # API endpoints (future)

backend/tests/
  ├── test_sandbox_config.py        # Config validation tests
  └── test_sandbox_service.py       # Service unit tests (future)
```

### 10.2 Phase 2: Implementation (Next)

**Tasks:**
1. Implement SchemaManager with MySQL operations
2. Implement SandboxManager lifecycle
3. Create QueryExecutor with security validation
4. Add REST API endpoints
5. Integration tests with test MySQL

**Estimated Duration:** 2 weeks

### 10.3 Phase 3: Production Hardening

**Tasks:**
1. Implement CleanupScheduler background task
2. Add comprehensive monitoring and metrics
3. Performance testing and optimization
4. Security audit and penetration testing
5. Documentation and runbooks

**Estimated Duration:** 1 week

### 10.4 Phase 4: Advanced Features

**Tasks:**
1. WebSocket support for streaming results
2. Query result caching
3. Docker SDK alternative backend
4. Query history and replay
5. Dataset versioning

**Estimated Duration:** 2-3 weeks

## 11. Testing Strategy

### 11.1 Unit Tests

- Configuration validation
- Query parsing and validation
- Schema name generation
- Security constraint checks

### 11.2 Integration Tests

- End-to-end sandbox lifecycle
- Query execution with real MySQL
- Cleanup operations
- Concurrent sandbox creation

### 11.3 Performance Tests

- Load testing: 1000 concurrent sandboxes
- Query throughput benchmarks
- Memory and connection pool usage
- Cleanup efficiency

### 11.4 Security Tests

- Privilege escalation attempts
- Cross-schema access attempts
- SQL injection scenarios
- Resource exhaustion attacks

## 12. Operational Considerations

### 12.1 Deployment

**Prerequisites:**
- MySQL 8.0+ with administrative access
- Sufficient connection pool size (1000+ connections)
- Adequate disk space for schemas (estimate: 100MB × max_sandboxes)

**Deployment Steps:**
1. Create sandbox administrative user in MySQL
2. Deploy backend with sandbox configuration
3. Initialize lesson template schemas
4. Start cleanup scheduler as background task
5. Monitor metrics dashboard

### 12.2 Backup and Recovery

- **Main database**: Regular backups with point-in-time recovery
- **Sandbox schemas**: Ephemeral, no backup needed
- **Lesson templates**: Versioned in Git, backed up with main DB

### 12.3 Scaling Strategies

**Vertical Scaling:**
- Increase MySQL instance size
- Add more CPU and memory for query processing

**Horizontal Scaling:**
- Multiple MySQL instances with user sharding
- Geographic distribution for global users
- Read replicas for template schemas

### 12.4 Disaster Recovery

**Failure Scenarios:**

1. **MySQL instance failure**:
   - Automatic failover to replica
   - All active sandboxes lost (acceptable for ephemeral data)
   - Users notified to retry

2. **Backend service failure**:
   - Load balancer redirects to healthy instances
   - Active sandboxes continue (stateless service)

3. **Storage exhaustion**:
   - Aggressive cleanup triggered
   - New sandbox creation temporarily blocked
   - Alert operators

## 13. Cost Analysis

### 13.1 Infrastructure Costs

**MySQL Instance (Example: AWS RDS):**
- Instance type: db.r5.large (2 vCPU, 16GB RAM)
- Storage: 500GB SSD
- Estimated cost: $250-300/month
- Capacity: ~1000 concurrent sandboxes

**Compute (Backend):**
- Minimal overhead, existing FastAPI instances
- No additional infrastructure needed

### 13.2 Operational Costs

- **Monitoring**: ~$20/month (CloudWatch/Datadog)
- **Logging**: ~$30/month (ELK/Splunk)
- **Development time**: Initial 3-4 weeks, then maintenance

### 13.3 ROI

For a learning platform:
- Enables interactive SQL lessons
- Increases user engagement
- Reduces support burden (safe experimentation)
- Competitive advantage over static tutorials

## 14. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Resource exhaustion | Medium | High | Rate limiting, cleanup automation, monitoring |
| Security breach | Low | Critical | Multi-layer security, privilege restrictions, audit logging |
| Data leakage | Low | High | Complete schema isolation, no shared data |
| Performance degradation | Medium | Medium | Connection pooling, query limits, caching |
| MySQL failure | Low | High | HA setup, automatic failover, quick recovery |

## 15. Future Considerations

### 15.1 Advanced Isolation

- Transition to Docker containers for stronger isolation
- Kubernetes-based orchestration for cloud-native deployments
- Support for other databases (PostgreSQL, SQLite)

### 15.2 Enhanced Features

- **Collaborative sandboxes**: Multiple users in same sandbox
- **Sandbox persistence**: Optional save/restore functionality
- **Query optimization hints**: Suggest better queries
- **Visual query builder**: Generate SQL from UI
- **Sandbox templates**: Pre-configured environments for lessons

### 15.3 Analytics

- Query pattern analysis for lesson improvement
- Common error tracking for better UX
- Performance analytics for optimization
- User learning path insights

## 16. Conclusion

The MySQL multi-schema approach provides an optimal balance of:
- **Security**: Adequate isolation for educational use cases
- **Performance**: Fast provisioning and low overhead
- **Cost**: Minimal infrastructure requirements
- **Simplicity**: Easy to operate and maintain

This architecture is production-ready for launch, with clear paths for scaling and feature enhancement as the platform grows.

## Appendix A: Example SQL Queries

### Creating Sandbox Schema

```sql
-- Create schema
CREATE DATABASE IF NOT EXISTS sandbox_user_123_1704096000;

-- Create restricted user
CREATE USER IF NOT EXISTS 'sandbox_user_123_1704096000'@'%' 
IDENTIFIED BY 'generated_secure_password';

-- Grant limited privileges
GRANT SELECT, INSERT, UPDATE, DELETE 
ON sandbox_user_123_1704096000.* 
TO 'sandbox_user_123_1704096000'@'%';

-- Set resource limits
ALTER USER 'sandbox_user_123_1704096000'@'%'
WITH MAX_QUERIES_PER_HOUR 360
     MAX_UPDATES_PER_HOUR 360
     MAX_CONNECTIONS_PER_HOUR 100
     MAX_USER_CONNECTIONS 5;

FLUSH PRIVILEGES;
```

### Seeding from Template

```sql
-- Clone table structure
CREATE TABLE sandbox_user_123_1704096000.employees 
LIKE lesson_5_template.employees;

-- Copy data
INSERT INTO sandbox_user_123_1704096000.employees 
SELECT * FROM lesson_5_template.employees;
```

### Cleanup

```sql
-- Drop user
DROP USER IF EXISTS 'sandbox_user_123_1704096000'@'%';

-- Drop schema
DROP DATABASE IF EXISTS sandbox_user_123_1704096000;
```

## Appendix B: Configuration Examples

### Development Configuration

```yaml
sandbox:
  mysql_host: localhost
  mysql_port: 3306
  max_active_sandboxes: 10
  idle_timeout_minutes: 15
  max_lifetime_hours: 2
  query_timeout_seconds: 10
  enable_query_logging: true
```

### Production Configuration

```yaml
sandbox:
  mysql_host: mysql.internal.prod
  mysql_port: 3306
  max_active_sandboxes: 1000
  idle_timeout_minutes: 30
  max_lifetime_hours: 4
  query_timeout_seconds: 30
  enable_query_logging: false
  enable_metrics: true
```

## Appendix C: API Examples

### Create Sandbox

```bash
curl -X POST http://localhost:8000/api/v1/sandbox/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lesson_id": 5}'

# Response
{
  "sandbox_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema_name": "sandbox_user_123_1704096000",
  "expires_at": "2024-01-01T16:00:00Z",
  "status": "active"
}
```

### Execute Query

```bash
curl -X POST http://localhost:8000/api/v1/sandbox/550e8400.../query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM employees LIMIT 10"}'

# Response
{
  "columns": ["id", "name", "department", "salary"],
  "rows": [
    [1, "Alice Johnson", "Engineering", 95000.00],
    [2, "Bob Smith", "Sales", 75000.00]
  ],
  "row_count": 2,
  "execution_time": 0.023
}
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-01  
**Author:** Platform Architecture Team  
**Status:** Approved for Implementation
