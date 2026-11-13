
import json

from mcp.server.fastmcp import FastMCP
from sqlalchemy import MetaData, Table, select
from schema_inspector import (
    get_tables,
    get_table_schema,
    get_database_schema as inspect_database_schema
)
from sqlalchemy import text
from db_engine import engine
from security.sql_validator import (
    validate_read_only_sql,
    SQLValidationError
)
# Initialize MCP server
mcp = FastMCP("SQLPilot")


@mcp.tool()
def get_sample_data(table_name: str, limit: int = 5) -> dict:
    """
    Retrieve sample rows from a database table.

    Args:
        table_name: Name of the table.
        limit: Number of sample rows to retrieve.
    """

    from schema_inspector import get_tables

    # Validate table name
    if table_name not in get_tables():
        return {
            "success": False,
            "error": f"Table '{table_name}' does not exist."
        }

    # Validate limit
    if not 1 <= limit <= 50:
        return {
            "success": False,
            "error": "Limit must be between 1 and 50."
        }

    try:
        metadata = MetaData()

        # Dynamically retrieve the table structure
        table = Table(
            table_name,
            metadata,
            autoload_with=engine
        )

        # Build a SELECT query safely
        query = select(table).limit(limit)

        with engine.connect() as connection:
            result = connection.execute(query)

            rows = [
                dict(row)
                for row in result.mappings().all()
            ]

        return {
            "success": True,
            "table": table_name,
            "row_count": len(rows),
            "rows": rows
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def explain_query(query: str) -> dict:
    """
    Explain the SQLite execution plan of a read-only SQL query.

    Args:
        query: SQL SELECT query to analyze.
    """

    try:
        # Validate the original query first
        validate_read_only_sql(query)

        # Ask SQLite to explain its execution plan
        explain_sql = "EXPLAIN QUERY PLAN " + query

        with engine.connect() as connection:
            result = connection.execute(text(explain_sql))

            plan = [
                dict(row)
                for row in result.mappings().all()
            ]

        return {
            "success": True,
            "execution_plan": plan
        }

    except SQLValidationError as e:
        return {
            "success": False,
            "error": str(e)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def execute_query(query: str, max_rows: int = 100) -> dict:
    """
    Execute a safe, read-only SQL query.

    Args:
        query: SQL SELECT query to execute.
        max_rows: Maximum number of rows to return (1-100).
    """

    # Validate requested row limit
    if not 1 <= max_rows <= 100:
        return {
            "error": "max_rows must be between 1 and 100."
        }

    try:
        # Step 1: Validate SQL
        validate_read_only_sql(query)

        # Step 2: Execute validated SQL
        with engine.connect() as connection:

            result = connection.execute(text(query))

            # Step 3: Retrieve column names
            columns = list(result.keys())

            # Step 4: Fetch at most max_rows + 1
            fetched_rows = result.mappings().fetchmany(max_rows + 1)

            # Determine whether more rows exist
            truncated = len(fetched_rows) > max_rows

            # Keep only the requested number of rows
            rows = [
                dict(row)
                for row in fetched_rows[:max_rows]
            ]

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": truncated
            }

    except SQLValidationError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "SQLValidationError"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "ExecutionError"
        }


# -----------------------------
# MCP TOOL 1: LIST TABLES
# -----------------------------

@mcp.tool()
def list_tables() -> list[str]:
    """
    List all tables available in the connected database.
    """
    return get_tables()


# -----------------------------
# MCP TOOL 2: DESCRIBE TABLE
# -----------------------------

@mcp.tool()
def describe_table(table_name: str) -> dict:
    """
    Get the columns, data types, primary keys and foreign keys
    of a specific database table.

    Args:
        table_name: Name of the table to inspect.
    """

    available_tables = get_tables()

    if table_name not in available_tables:
        return {
            "error": f"Table '{table_name}' does not exist.",
            "available_tables": available_tables
        }

    return get_table_schema(table_name)


# -----------------------------
# MCP TOOL 3: COMPLETE SCHEMA
# -----------------------------

@mcp.tool()
def get_schema() -> dict:
    """
    Retrieve the complete schema of the connected database.
    """
    return inspect_database_schema()


# -----------------------------
# MCP RESOURCE 1: TABLES
# -----------------------------

@mcp.resource("db://tables")
def tables_resource() -> str:
    """
    Provides a list of available database tables.
    """
    return json.dumps(get_tables(), indent=2)


# -----------------------------
# MCP RESOURCE 2: SCHEMA
# -----------------------------

@mcp.resource("db://schema")
def schema_resource() -> str:
    """
    Provides the complete database schema.
    """
    return json.dumps(
        inspect_database_schema(),
        indent=2
    )


# -----------------------------
# MCP PROMPT: SQL ASSISTANT
# -----------------------------

@mcp.prompt()
def sql_query_assistant(question: str) -> str:
    """
    Generate a SQL query based on the database schema.

    Args:
        question: Natural language database question.
    """

    schema = inspect_database_schema()

    return f"""
    You are SQLPilot, an expert SQL assistant.

    DATABASE SCHEMA:
    {json.dumps(schema, indent=2)}

    USER QUESTION:
    {question}

    Instructions:
    1. Understand the database schema.
    2. Generate an appropriate SQLite SELECT query.
    3. Use correct table relationships and JOIN conditions.
    4. Do not generate INSERT, UPDATE or DELETE queries.
    5. Explain the generated SQL query.
    """


# -----------------------------
# START MCP SERVER
# -----------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
