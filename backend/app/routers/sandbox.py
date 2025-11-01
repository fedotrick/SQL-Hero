"""
Sandbox API endpoints for SQL query execution.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.sandbox_config import SandboxConfig
from app.models.database import Lesson
from app.schemas.sandbox import (
    QueryExecuteRequest,
    QueryExecuteResponse,
    QueryValidateResponse,
    SandboxCreateRequest,
    SandboxCreateResponse,
    SandboxDestroyResponse,
    SandboxStatus,
    SandboxStatusResponse,
)
from app.services.query_executor import MySQLQueryExecutor
from app.services.sandbox import InMemorySandboxManager, SandboxService
from app.services.schema_manager import MySQLSchemaManager

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

# Initialize services (in production, these would be dependency-injected)
sandbox_config = SandboxConfig()
sandbox_manager = InMemorySandboxManager(sandbox_config)
schema_manager = MySQLSchemaManager(sandbox_config)
query_executor = MySQLQueryExecutor(sandbox_config)
sandbox_service = SandboxService(
    config=sandbox_config,
    sandbox_manager=sandbox_manager,
    schema_manager=schema_manager,
    query_executor=query_executor,
)


@router.post("/create", response_model=SandboxCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_sandbox(
    request: SandboxCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> SandboxCreateResponse:
    """
    Create a new sandbox environment for a lesson.

    This endpoint:
    - Creates an isolated database schema
    - Seeds lesson-specific fixture data
    - Returns sandbox credentials and metadata
    """
    # For now, use a hardcoded user_id (in production, get from auth)
    user_id = 1

    # Verify lesson exists
    result = await db.execute(select(Lesson).where(Lesson.id == request.lesson_id))
    lesson = result.scalar_one_or_none()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson {request.lesson_id} not found",
        )

    try:
        sandbox = await sandbox_service.create_sandbox(user_id, request.lesson_id)

        return SandboxCreateResponse(
            sandbox_id=sandbox.sandbox_id,
            schema_name=sandbox.schema_name,
            status=sandbox.status,
            expires_at=sandbox.expires_at,
            created_at=sandbox.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sandbox: {str(e)}",
        )


@router.post("/{sandbox_id}/execute", response_model=QueryValidateResponse)
async def execute_query(
    sandbox_id: str,
    request: QueryExecuteRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryValidateResponse:
    """
    Execute a SQL query in a sandbox environment.

    This endpoint:
    - Validates the query syntax and permissions
    - Executes the query with timeout enforcement
    - Optionally compares results with expected output
    - Returns pass/fail status with result preview
    """
    try:
        # Get sandbox
        sandbox = await sandbox_manager.get_sandbox(sandbox_id)
        if not sandbox:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sandbox {sandbox_id} not found",
            )

        # Execute query
        try:
            result = await sandbox_service.execute_query(sandbox_id, request.query)
        except TimeoutError as e:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=str(e),
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # If validation requested, compare with expected result
        if request.validate_against_expected:
            # Get lesson expected result
            result_db = await db.execute(select(Lesson).where(Lesson.id == sandbox.lesson_id))
            lesson = result_db.scalar_one_or_none()

            if not lesson or not lesson.expected_result:
                return QueryValidateResponse(
                    passed=False,
                    result=result,
                    differences=["No expected result defined for this lesson"],
                    message="Cannot validate: no expected result available",
                )

            # Compare results
            matches, differences = query_executor.compare_results(
                result, lesson.expected_result, ordered=False
            )

            message = (
                "✓ Perfect! Your query result matches the expected output."
                if matches
                else "✗ Your query result doesn't match the expected output. Review the differences below."
            )

            return QueryValidateResponse(
                passed=matches,
                result=result,
                differences=differences,
                message=message,
            )
        else:
            # Just return the result without validation
            return QueryValidateResponse(
                passed=True,
                result=result,
                differences=[],
                message="Query executed successfully",
            )

    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}",
        )


@router.get("/{sandbox_id}/status", response_model=SandboxStatusResponse)
async def get_sandbox_status(sandbox_id: str) -> SandboxStatusResponse:
    """Get the status of a sandbox environment."""
    sandbox = await sandbox_manager.get_sandbox(sandbox_id)

    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sandbox {sandbox_id} not found",
        )

    return SandboxStatusResponse(
        sandbox_id=sandbox.sandbox_id,
        schema_name=sandbox.schema_name,
        status=sandbox.status,
        created_at=sandbox.created_at,
        expires_at=sandbox.expires_at,
        last_accessed_at=sandbox.last_accessed_at,
        query_count=sandbox.query_count,
        lesson_id=sandbox.lesson_id,
    )


@router.delete("/{sandbox_id}", response_model=SandboxDestroyResponse)
async def destroy_sandbox(sandbox_id: str) -> SandboxDestroyResponse:
    """Destroy a sandbox environment and clean up resources."""
    sandbox = await sandbox_manager.get_sandbox(sandbox_id)

    if not sandbox:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sandbox {sandbox_id} not found",
        )

    try:
        await sandbox_service.destroy_sandbox(sandbox_id)

        return SandboxDestroyResponse(
            sandbox_id=sandbox_id,
            status=SandboxStatus.DESTROYED,
            destroyed_at=datetime.now(UTC),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to destroy sandbox: {str(e)}",
        )
