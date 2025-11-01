"""
MySQL Schema Manager for sandbox database operations.
"""

from typing import Any

import aiomysql

from app.core.sandbox_config import SandboxConfig
from app.services.sandbox import ISchemaManager


class MySQLSchemaManager(ISchemaManager):
    """
    Production MySQL schema manager for:
    - Creating/dropping schemas
    - Seeding fixture data for lessons
    - Managing sandbox users
    """

    def __init__(self, config: SandboxConfig):
        self.config = config

    async def create_schema(self, schema_name: str) -> None:
        """Create a new sandbox schema."""
        conn = await self._get_admin_connection()
        try:
            async with conn.cursor() as cursor:
                # Create schema
                await cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{schema_name}`")
        finally:
            conn.close()

    async def seed_data(self, schema_name: str, lesson_id: int) -> None:
        """
        Seed fixture data for a specific lesson.
        Looks for fixture SQL in lesson_fixtures table or uses template schemas.
        """
        conn = await self._get_admin_connection(database=schema_name)
        try:
            # Get fixture data for the lesson
            fixture_sql = await self._get_lesson_fixture(lesson_id)

            if fixture_sql:
                async with conn.cursor() as cursor:
                    # Execute fixture SQL (can contain multiple statements)
                    statements = self._split_sql_statements(fixture_sql)
                    for statement in statements:
                        if statement.strip():
                            await cursor.execute(statement)
        finally:
            conn.close()

    async def drop_schema(self, schema_name: str) -> None:
        """Drop a sandbox schema."""
        conn = await self._get_admin_connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f"DROP DATABASE IF EXISTS `{schema_name}`")
        finally:
            conn.close()

    async def schema_exists(self, schema_name: str) -> bool:
        """Check if a schema exists."""
        conn = await self._get_admin_connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
                    (schema_name,),
                )
                result = await cursor.fetchone()
                return result is not None
        finally:
            conn.close()

    async def get_schema_size(self, schema_name: str) -> int:
        """Get the size of a schema in bytes."""
        conn = await self._get_admin_connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """
                    SELECT SUM(DATA_LENGTH + INDEX_LENGTH) as size
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_SCHEMA = %s
                    """,
                    (schema_name,),
                )
                result = await cursor.fetchone()
                return int(result[0]) if result and result[0] else 0
        finally:
            conn.close()

    async def create_sandbox_user(
        self, username: str, password: str, schema_name: str
    ) -> None:
        """Create a sandbox user with limited privileges."""
        conn = await self._get_admin_connection()
        try:
            async with conn.cursor() as cursor:
                # Create user
                await cursor.execute(
                    f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY %s", (password,)
                )

                # Grant privileges only on the sandbox schema
                await cursor.execute(
                    f"GRANT SELECT, INSERT, UPDATE, DELETE ON `{schema_name}`.* TO '{username}'@'%'"
                )

                await cursor.execute("FLUSH PRIVILEGES")
        finally:
            conn.close()

    async def drop_sandbox_user(self, username: str) -> None:
        """Drop a sandbox user."""
        conn = await self._get_admin_connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f"DROP USER IF EXISTS '{username}'@'%'")
                await cursor.execute("FLUSH PRIVILEGES")
        finally:
            conn.close()

    async def _get_admin_connection(
        self, database: str | None = None
    ) -> aiomysql.Connection:
        """Get admin connection to MySQL."""
        return await aiomysql.connect(
            host=self.config.mysql_host,
            port=self.config.mysql_port,
            user=self.config.mysql_admin_user,
            password=self.config.mysql_admin_password,
            db=database,
            autocommit=True,
        )

    async def _get_lesson_fixture(self, lesson_id: int) -> str | None:
        """
        Get fixture SQL for a lesson.
        This connects to the main database to retrieve fixture data.
        """
        # For now, return basic fixture data
        # In production, this would query a lesson_fixtures table
        fixtures = {
            1: """
                CREATE TABLE IF NOT EXISTS employees (
                    id INT PRIMARY KEY,
                    name VARCHAR(100),
                    department VARCHAR(50),
                    salary DECIMAL(10, 2)
                );

                INSERT INTO employees (id, name, department, salary) VALUES
                (1, 'John Doe', 'Engineering', 75000.00),
                (2, 'Jane Smith', 'Marketing', 65000.00),
                (3, 'Bob Johnson', 'Engineering', 80000.00),
                (4, 'Alice Brown', 'HR', 60000.00),
                (5, 'Charlie Wilson', 'Engineering', 90000.00);
            """,
            2: """
                CREATE TABLE IF NOT EXISTS products (
                    id INT PRIMARY KEY,
                    name VARCHAR(100),
                    category VARCHAR(50),
                    price DECIMAL(10, 2),
                    stock INT
                );

                INSERT INTO products (id, name, category, price, stock) VALUES
                (1, 'Laptop', 'Electronics', 999.99, 50),
                (2, 'Mouse', 'Electronics', 29.99, 200),
                (3, 'Desk', 'Furniture', 299.99, 30),
                (4, 'Chair', 'Furniture', 199.99, 45),
                (5, 'Monitor', 'Electronics', 399.99, 75);
            """,
        }

        return fixtures.get(lesson_id)

    def _split_sql_statements(self, sql: str) -> list[str]:
        """Split SQL into individual statements."""
        # Simple split by semicolon (doesn't handle all edge cases)
        # For production, use a proper SQL parser
        statements = []
        current = []

        for line in sql.split("\n"):
            line = line.strip()
            if not line or line.startswith("--"):
                continue

            current.append(line)

            if line.endswith(";"):
                statements.append(" ".join(current))
                current = []

        if current:
            statements.append(" ".join(current))

        return statements
