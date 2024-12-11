import sqlite3
from typing import Dict, List, Any
import os


class DatabaseManager:
    def __init__(self, db_path: str):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect(self):
        """Create or connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def create_tables(self, schema: Dict[str, Dict[str, str]]):
        """
        Create tables based on schema dictionary
        schema format: {
            'table_name': {
                'column_name': 'column_type [constraints]',
                ...
            }
        }
        """
        try:
            self.connect()
            for table_name, columns in schema.items():
                columns_def = ", ".join(
                    [f"{col} {dtype}" for col, dtype in columns.items()]
                )
                query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
                self.cursor.execute(query)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
        finally:
            self.close()

    def insert_record(self, table: str, data: Dict[str, Any]):
        """Insert a single record into a table"""
        try:
            self.connect()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(query, list(data.values()))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error inserting record: {e}")
        finally:
            self.close()

    def fetch_records(self, table: str, conditions: str = None) -> List[tuple]:
        """Fetch records from a table with optional WHERE clause"""
        try:
            self.connect()
            query = f"SELECT * FROM {table}"
            if conditions:
                query += f" WHERE {conditions}"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching records: {e}")
            return []
        finally:
            self.close()

    def maintain_database(self):
        """Perform database maintenance: VACUUM, integrity check, and analyze"""
        try:
            self.connect()
            # VACUUM to reclaim unused space and defragment
            self.cursor.execute("VACUUM")
            # Check database integrity
            self.cursor.execute("PRAGMA integrity_check")
            integrity_result = self.cursor.fetchone()[0]
            # Analyze to update statistics
            self.cursor.execute("ANALYZE")
            self.connection.commit()
            return integrity_result == "ok"
        except sqlite3.Error as e:
            print(f"Error during database maintenance: {e}")
            return False
        finally:
            self.close()


# Example usage:
if __name__ == "__main__":
    # Schema definition example
    schema = {
        "users": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "email": "TEXT UNIQUE",
        }
    }

    # Create database manager instance
    db = DatabaseManager("example.db")

    # Create tables
    db.create_tables(schema)

    # Insert a record
    db.insert_record("users", {"name": "John Doe", "email": "john@example.com"})

    # Fetch records
    records = db.fetch_records("users")
    print(records)
