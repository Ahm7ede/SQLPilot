
import sqlglot
from sqlglot import exp


class SQLValidationError(Exception):
    """Raised when a SQL query violates security rules."""
    pass


def validate_read_only_sql(query: str):
    """
    Validate SQL and allow only read-only queries.

    Supports SELECT, UNION, INTERSECT and EXCEPT.
    Rejects multiple statements and all write operations.
    """

    if not query or not query.strip():
        raise SQLValidationError("SQL query cannot be empty.")

    try:
        # Parse SQL using SQLite dialect
        statements = sqlglot.parse(query, read="sqlite")

    except sqlglot.errors.ParseError as e:
        raise SQLValidationError(
            f"Invalid SQL syntax: {str(e)}"
        )

    # Reject multiple SQL statements
    if len(statements) != 1:
        raise SQLValidationError(
            "Only one SQL statement is allowed."
        )

    parsed_query = statements[0]

    # Allow only read-only query types
    allowed_types = (
        exp.Select,
        exp.Union,
        exp.Intersect,
        exp.Except
    )

    if not isinstance(parsed_query, allowed_types):
        raise SQLValidationError(
            "Only SELECT queries are allowed."
        )

    return parsed_query
