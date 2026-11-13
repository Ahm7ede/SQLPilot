
import sqlite3
import os

# Path to our database
DB_PATH = "database/sqlpilot.db"

def get_connection():
    """Create and return a SQLite database connection."""

    # Ensure database directory exists
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")

    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT
        )
    """)

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0)
        )
    """)

    # Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
    """)

    # Order items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),

            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),

            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        )
    """)

    conn.commit()
    conn.close()

    print("All tables created successfully!")

def insert_sample_data():
    conn = get_connection()
    cursor = conn.cursor()

    customers = [
        ("Ahmed", "ahmed@gmail.com", "Kochi"),
        ("Rahul", "rahul@gmail.com", "Trivandrum"),
        ("Anjali", "anjali@gmail.com", "Calicut"),
        ("Arjun", "arjun@gmail.com", "Kochi"),
        ("Sneha", "sneha@gmail.com", "Thrissur")
    ]

    products = [
        ("Laptop", 65000),
        ("Smartphone", 25000),
        ("Headphones", 2500),
        ("Keyboard", 1500),
        ("Mouse", 800)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (name, email, city)
        VALUES (?, ?, ?)
    """, customers)

    cursor.executemany("""
        INSERT OR IGNORE INTO products
        (product_name, price)
        VALUES (?, ?)
    """, products)

    orders = [
        (1, "2026-10-01"),
        (2, "2026-10-03"),
        (1, "2026-10-05"),
        (3, "2026-10-08"),
        (4, "2026-10-10"),
        (5, "2026-10-12")
    ]

    cursor.executemany("""
        INSERT INTO orders (customer_id, order_date)
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM orders
            WHERE customer_id = ? AND order_date = ?
        )
    """, [
        (customer_id, order_date, customer_id, order_date)
        for customer_id, order_date in orders
    ])

    order_items = [
        (1, 1, 1, 65000),
        (1, 3, 2, 2500),
        (2, 2, 1, 25000),
        (3, 5, 2, 800),
        (3, 4, 1, 1500),
        (4, 3, 1, 2500),
        (5, 1, 1, 65000),
        (6, 2, 1, 25000)
    ]

    cursor.executemany("""
        INSERT INTO order_items
        (order_id, product_id, quantity, unit_price)
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM order_items
            WHERE order_id = ?
            AND product_id = ?
        )
    """, [
        (*item, item[0], item[1])
        for item in order_items
    ])

    conn.commit()
    conn.close()

    print("Sample data inserted successfully!")

def inspect_database():
    conn = get_connection()
    cursor = conn.cursor()

    tables = ["customers", "products", "orders", "order_items"]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        print(f"{table}: {count} records")

    conn.close()


if __name__ == "__main__":
    create_tables()
    insert_sample_data()
    inspect_database()
