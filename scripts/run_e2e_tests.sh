#!/bin/bash
# E2E Test Runner Script for SQL Hero
# This script runs comprehensive E2E tests and generates reports

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REPORTS_DIR="$PROJECT_ROOT/test-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SQL Hero - Comprehensive E2E Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Function to print section header
print_header() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check dependencies
print_header "Checking dependencies"

if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi
print_success "Docker found"

if ! command -v poetry &> /dev/null; then
    print_warning "Poetry not found in PATH, trying local installation..."
    export PATH="/home/engine/.local/bin:$PATH"
fi

if command -v poetry &> /dev/null; then
    print_success "Poetry found"
else
    print_error "Poetry not found. Please install Poetry."
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    print_warning "pnpm not found. Installing..."
    npm install -g pnpm
fi

# Start Docker services if not running
print_header "Starting Docker services"

cd "$PROJECT_ROOT"
if ! docker compose ps | grep -q "Up"; then
    print_warning "Docker services not running. Starting..."
    docker compose up -d mysql
    echo "Waiting for MySQL to be healthy..."
    sleep 10
    print_success "Docker services started"
else
    print_success "Docker services already running"
fi

# Backend E2E Tests
print_header "Running Backend E2E Tests"

cd "$BACKEND_DIR"

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    print_warning "Installing backend dependencies..."
    poetry install --no-root
fi

# Run E2E tests with coverage
print_warning "Executing backend E2E test suite..."
export TEST_DATABASE_URL="sqlite+aiosqlite:///:memory:"

if poetry run pytest tests/e2e/ -v \
    --cov=app \
    --cov-report=html:../test-reports/backend-coverage-html \
    --cov-report=json:../test-reports/backend-coverage.json \
    --cov-report=term \
    --tb=short \
    2>&1 | tee "$REPORTS_DIR/backend-e2e-tests-$TIMESTAMP.log"; then
    print_success "Backend E2E tests passed"
    BACKEND_E2E_STATUS="PASS"
else
    print_error "Backend E2E tests failed"
    BACKEND_E2E_STATUS="FAIL"
fi

# Run all backend tests (regression)
print_header "Running Backend Regression Tests"

if poetry run pytest tests/ -v \
    --ignore=tests/e2e/ \
    --cov=app \
    --cov-append \
    --cov-report=html:../test-reports/backend-coverage-html \
    --cov-report=term-missing \
    2>&1 | tee -a "$REPORTS_DIR/backend-regression-tests-$TIMESTAMP.log"; then
    print_success "Backend regression tests passed"
    BACKEND_REGRESSION_STATUS="PASS"
else
    print_error "Backend regression tests failed"
    BACKEND_REGRESSION_STATUS="FAIL"
fi

# Backend lint checks
print_header "Running Backend Lint Checks"

if poetry run ruff check app 2>&1 | tee "$REPORTS_DIR/backend-lint-$TIMESTAMP.log"; then
    print_success "Ruff lint passed"
    BACKEND_LINT_STATUS="PASS"
else
    print_error "Ruff lint failed"
    BACKEND_LINT_STATUS="FAIL"
fi

# Backend type checks
print_header "Running Backend Type Checks"

if poetry run mypy app 2>&1 | tee "$REPORTS_DIR/backend-mypy-$TIMESTAMP.log"; then
    print_success "MyPy type check passed"
    BACKEND_MYPY_STATUS="PASS"
else
    print_error "MyPy type check failed"
    BACKEND_MYPY_STATUS="FAIL"
fi

# Frontend Tests
print_header "Running Frontend Tests"

cd "$FRONTEND_DIR"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    pnpm install
fi

# Run frontend tests with coverage
if pnpm test:coverage 2>&1 | tee "$REPORTS_DIR/frontend-tests-$TIMESTAMP.log"; then
    print_success "Frontend tests passed"
    FRONTEND_TEST_STATUS="PASS"
else
    print_error "Frontend tests failed"
    FRONTEND_TEST_STATUS="FAIL"
fi

# Frontend lint checks
print_header "Running Frontend Lint Checks"

if pnpm lint 2>&1 | tee "$REPORTS_DIR/frontend-lint-$TIMESTAMP.log"; then
    print_success "ESLint passed"
    FRONTEND_LINT_STATUS="PASS"
else
    print_error "ESLint failed"
    FRONTEND_LINT_STATUS="FAIL"
fi

# Frontend format checks
if pnpm format:check 2>&1 | tee -a "$REPORTS_DIR/frontend-lint-$TIMESTAMP.log"; then
    print_success "Prettier check passed"
    FRONTEND_FORMAT_STATUS="PASS"
else
    print_error "Prettier check failed"
    FRONTEND_FORMAT_STATUS="FAIL"
fi

# Generate Summary Report
print_header "Generating Test Summary Report"

SUMMARY_FILE="$REPORTS_DIR/test-summary-$TIMESTAMP.txt"

cat > "$SUMMARY_FILE" << EOF
═══════════════════════════════════════════════════════
  SQL Hero - E2E Test Summary Report
═══════════════════════════════════════════════════════

Timestamp: $(date +"%Y-%m-%d %H:%M:%S")

BACKEND TESTS
═════════════════════════════════════════════════════════
Backend E2E Tests:         $BACKEND_E2E_STATUS
Backend Regression Tests:  $BACKEND_REGRESSION_STATUS
Ruff Lint:                $BACKEND_LINT_STATUS
MyPy Type Check:          $BACKEND_MYPY_STATUS

FRONTEND TESTS
═════════════════════════════════════════════════════════
Frontend Unit Tests:      $FRONTEND_TEST_STATUS
ESLint:                   $FRONTEND_LINT_STATUS
Prettier Format:          $FRONTEND_FORMAT_STATUS

REPORTS
═════════════════════════════════════════════════════════
Backend Coverage: test-reports/backend-coverage-html/index.html
Frontend Coverage: frontend/coverage/index.html
Logs Directory: test-reports/

EOF

cat "$SUMMARY_FILE"

# Print final status
echo ""
print_header "Final Status"

ALL_PASS=true

if [ "$BACKEND_E2E_STATUS" != "PASS" ]; then ALL_PASS=false; fi
if [ "$BACKEND_REGRESSION_STATUS" != "PASS" ]; then ALL_PASS=false; fi
if [ "$BACKEND_LINT_STATUS" != "PASS" ]; then ALL_PASS=false; fi
if [ "$BACKEND_MYPY_STATUS" != "PASS" ]; then ALL_PASS=false; fi
if [ "$FRONTEND_TEST_STATUS" != "PASS" ]; then ALL_PASS=false; fi
if [ "$FRONTEND_LINT_STATUS" != "PASS" ]; then ALL_PASS=false; fi
if [ "$FRONTEND_FORMAT_STATUS" != "PASS" ]; then ALL_PASS=false; fi

if [ "$ALL_PASS" = true ]; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}   ✓ ALL TESTS PASSED - READY FOR DEPLOYMENT${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
    echo -e "${RED}   ✗ SOME TESTS FAILED - REVIEW REQUIRED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Check logs in: $REPORTS_DIR"
    echo "Summary: $SUMMARY_FILE"
    exit 1
fi
