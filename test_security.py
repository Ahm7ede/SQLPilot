
from security.sql_validator import (
    validate_read_only_sql,
    SQLValidationError
)

test_queries = [
    "SELECT * FROM customers",
    "SELECT COUNT(*) FROM orders",
    "DELETE FROM customers",
    "DROP TABLE customers",
    "UPDATE customers SET city = 'Kochi'",
    "SELECT * FROM customers; DROP TABLE customers"
]

for query in test_queries:

    print("\nTesting:", query)

    try:
        validate_read_only_sql(query)
        print("ALLOWED")

    except SQLValidationError as e:
        print("BLOCKED:", e)
