
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text

# Load environment variables from .env
load_dotenv()

# Read database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///database/sqlpilot.db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def configure_sqlite(dbapi_connection, connection_record):

        cursor = dbapi_connection.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=ON")

        # Make this connection read-only
        cursor.execute("PRAGMA query_only=ON")

        cursor.close()



def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            print("Test query result:", result.scalar())

    except Exception as e:
        print("Database connection failed:", e)


if __name__ == "__main__":
    test_connection()
