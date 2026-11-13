
from sqlalchemy import inspect

from db_engine import engine


# Create an Inspector object
inspector = inspect(engine)


def get_tables():
    """Return all table names in the database."""

    return inspector.get_table_names()


def get_table_schema(table_name):
    """Retrieve the schema of a specific table."""

    # Get column information
    columns = inspector.get_columns(table_name)

    # Get primary key information
    primary_key = inspector.get_pk_constraint(table_name)

    # Get foreign key information
    foreign_keys = inspector.get_foreign_keys(table_name)

    return {
        "table_name": table_name,
        "columns": [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": column["default"]
            }
            for column in columns
        ],
        "primary_key": primary_key.get("constrained_columns", []),
        "foreign_keys": [
            {
                "columns": fk["constrained_columns"],
                "references_table": fk["referred_table"],
                "references_columns": fk["referred_columns"]
            }
            for fk in foreign_keys
        ]
    }


def get_database_schema():
    """Retrieve the complete database schema."""

    schema = {}

    for table in get_tables():
        schema[table] = get_table_schema(table)

    return schema


if __name__ == "__main__":

    print("AVAILABLE TABLES")
    print("----------------")

    for table in get_tables():
        print(table)

    print("\nCOMPLETE DATABASE SCHEMA")
    print("------------------------")

    database_schema = get_database_schema()

    for table, details in database_schema.items():
        print(f"\nTable: {table}")
        print("Columns:")

        for column in details["columns"]:
            print(
                f"  {column['name']} "
                f"({column['type']})"
            )

        print("Primary Key:", details["primary_key"])
        print("Foreign Keys:", details["foreign_keys"])
