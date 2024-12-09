import sqlite3


class Database:
    def __init__(self, db_path):
        """
        Initialize the database connection.

        :param db_path: The path to the SQLite database file
        :type db_path: str
        """
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def create_or_update_schema(self, schema_dict):
        """
        Create or update the database schema from a dictionary definition.

        :param schema_dict: A dictionary with table names as keys and
            dictionaries of column names and types as values.
        :type schema_dict: dict[str, dict[str, str]]
        """
        
        for table_name, columns in schema_dict.items():
            columns_def = ", ".join(
                [f"{name} {type}" for name, type in columns.items()]
            )
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
            self.cursor.execute(sql)
        self.connection.commit()

    def read_data(self, query, params=None):
        """
        Execute a SELECT query and return the results.

        :param query: The SQL query string
        :type query: str
        :param params: Optional parameters for the query
        :type params: tuple or list
        :return: The list of rows returned by the query
        :rtype: list of tuples
        """
        self.cursor.execute(query, params or [])
        return self.cursor.fetchall()

    def write_data(self, table_name, data):
        """
        Insert multiple records into the database.

        :param table_name: The name of the table to insert into
        :type table_name: str
        :param data: A list of dictionaries where each dictionary represents
            a record to be inserted. The keys of the dictionary should match
            the column names of the table.
        :type data: list of dict
        :return: None
        """
        if not data:
            return
        columns = data[0].keys()
        placeholders = ", ".join(["?"] * len(columns))
        columns_str = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        values = [tuple(item[col] for col in columns) for item in data]
        self.cursor.executemany(sql, values)
        self.connection.commit()

    def close(self):
        """
        Close the database connection.

        This method ensures that the connection to the database is properly closed, 
        releasing any resources or locks held by the connection.
        """
        self.connection.close()
