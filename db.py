import sqlite3
import pandas as pd
from typing import Dict, List, Any
import logging


class DatabaseHandler:
    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Create database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def create_schema(self, schema: Dict[str, List[str]]):
        """
        Create or update database schema.
        schema format: {
            'table_name': ['column1 type', 'column2 type', ...],
        }
        """
        try:
            with self.connection as conn:
                for table_name, columns in schema.items():
                    query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        {', '.join(columns)}
                    )
                    """
                    conn.execute(query)
            return True
        except sqlite3.Error as e:
            logging.error(f"Error creating schema: {e}")
            return False

    def bulk_insert(self, table_name: str, data: List[Dict[str, Any]]):
        """Insert multiple records into a table."""
        if not data:
            return False

        try:
            df = pd.DataFrame(data)
            with self.connection as conn:
                df.to_sql(table_name, conn, if_exists="append", index=False)
            return True
        except Exception as e:
            logging.error(f"Error during bulk insert: {e}")
            return False

    def read_query(self, query: str, params: tuple = None):
        """Execute a SELECT query and return results."""
        try:
            with self.connection as conn:
                if params:
                    results = pd.read_sql_query(query, conn, params=params)
                else:
                    results = pd.read_sql_query(query, conn)
                return results
        except Exception as e:
            logging.error(f"Error executing query: {e}")
            return None

    def execute_query(self, query: str, params: tuple = None):
        """Execute a non-SELECT query (INSERT, UPDATE, DELETE)."""
        try:
            with self.connection as conn:
                if params:
                    conn.execute(query, params)
                else:
                    conn.execute(query)
                return True
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return False
