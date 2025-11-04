# SQL Hero - Known Issues Log

**Last Updated:** 2024-11-04  
**Version:** 1.0.0

---

## Active Issues

### None Currently

All critical and high-priority issues have been resolved.

---

## Resolved Issues

### Issue #1: SQLAlchemy Metadata Attribute Conflict

**Discovered:** 2024-11-04  
**Resolved:** 2024-11-04  
**Severity:** 🔴 CRITICAL

#### Description
The `PendingNotification` model in `app/models/database.py` had a field named `metadata` which conflicts with SQLAlchemy's reserved `metadata` attribute used by the Declarative API. This caused all tests that imported models to fail with:

```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

#### Impact
- All backend tests failed to import models
- Unable to run test suite
- Blocking issue for deployment

#### Root Cause
Using a reserved SQLAlchemy attribute name (`metadata`) as a model field without proper mapping.

#### Resolution
1. Renamed the Python attribute from `metadata` to `notification_metadata`
2. Used mapped_column with explicit column name: `mapped_column("metadata", JSON, nullable=True)`
3. Updated all references in codebase:
   - `app/services/telegram_notifications.py` - Parameter assignment
   - `app/schemas/notifications.py` - Schema field name
   - `tests/test_notifications.py` - Test assertions (3 locations)

#### Files Changed
```
app/models/database.py
app/services/telegram_notifications.py
app/schemas/notifications.py
tests/test_notifications.py
```

#### Prevention
- Add linting rule to check for SQLAlchemy reserved attributes
- Document reserved attribute names in coding standards
- Review all model fields against SQLAlchemy reserved names

#### Status
✅ **RESOLVED** - All tests now import models successfully

---

## Limitations (Not Bugs)

### L1: Database Connection Required for Integration Tests

**Severity:** 🟡 LOW  
**Type:** Infrastructure Dependency

#### Description
168 tests require a running MySQL database connection. These tests fail with "Can't connect to MySQL server" when database is not available.

#### Impact
- Cannot run full test suite without starting database
- CI/CD requires database service
- Local development requires docker-compose

#### Workaround
```bash
# Start MySQL with docker-compose
docker-compose up mysql

# Then run tests
cd backend
poetry run pytest tests/
```

#### E2E Tests Solution
E2E tests use SQLite in-memory database for isolation and don't require MySQL:
```bash
cd backend
poetry run pytest tests/e2e/ -v
```

#### Recommendation
- Keep current design (proper integration testing requires real database)
- Use E2E SQLite tests for CI/CD quick checks
- Use full MySQL tests for pre-deployment verification

### L2: Sandbox Requires Admin Password When Enabled

**Severity:** 🟡 LOW  
**Type:** Security Feature

#### Description
The sandbox configuration validates that `mysql_admin_password` is provided when `SANDBOX_ENABLED=true`. Tests fail if sandbox is enabled without password.

#### Impact
- Must configure sandbox properly in .env
- Tests fail with validation error if misconfigured

#### Workaround
Option 1 - Disable sandbox for testing:
```bash
SANDBOX_ENABLED=false
```

Option 2 - Provide password:
```bash
SANDBOX_ENABLED=true
SANDBOX_MYSQL_ADMIN_PASSWORD=your_password_here
```

#### Recommendation
- This is correct security behavior - keep as is
- Document in setup guide
- Provide clear .env.example with both options

### L3: Frontend Tests Not Automated in Current Session

**Severity:** 🟢 MINIMAL  
**Type:** Testing Coverage

#### Description
Frontend tests were not executed in this testing session, though they were previously implemented and verified (85% coverage documented).

#### Impact
- Frontend coverage not re-verified in final testing
- Relying on previous test results

#### Workaround
```bash
cd frontend
pnpm install
pnpm test
```

#### Recommendation
- Include frontend tests in automated CI/CD
- Document frontend test execution in deployment checklist
- Verify frontend tests before each deployment

---

## Testing Recommendations

### For Development
1. Run E2E tests locally (no DB required):
   ```bash
   cd backend
   poetry run pytest tests/e2e/ -v
   ```

2. Run unit tests (no DB required):
   ```bash
   poetry run pytest tests/test_config.py tests/test_main.py tests/test_database.py -v
   ```

### For CI/CD
1. Use SQLite E2E tests for fast feedback
2. Run full MySQL integration tests in staging
3. Include security tests in every build
4. Monitor test execution time

### For Pre-Deployment
1. Start full stack with docker-compose
2. Run complete test suite with coverage
3. Verify all 468 backend tests pass
4. Run frontend test suite
5. Execute manual smoke tests

---

## Issue Reporting Guidelines

When reporting new issues, include:

1. **Title:** Brief description
2. **Severity:** Critical / High / Medium / Low
3. **Environment:** Development / Staging / Production
4. **Steps to Reproduce:** Clear steps
5. **Expected vs Actual:** What should happen vs what happens
6. **Logs/Errors:** Relevant error messages
7. **Impact:** How it affects users/system
8. **Workaround:** Temporary solution (if any)

---

## Change Log

### 2024-11-04
- ✅ Fixed: SQLAlchemy metadata attribute conflict (Critical)
- ✅ Verified: All E2E tests passing
- ✅ Verified: Security tests at 100%
- ✅ Created: Comprehensive test documentation

---

**End of Known Issues Log**
