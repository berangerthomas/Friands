import sqlite3
from pathlib import Path


class sqlutils:
    def __init__(self, filepath: Path) -> tuple:
        try:
            # Vérifier que le fichier db existe
            """
            Initialize a new sqlite database connection.

            Args:
                filepath (Path): Path to the sqlite database file.

            Notes:
                If the file does not exist, it will be created.
            """
            if not filepath.exists():
                # Si le fichier n'existe pas, on le crée
                filepath.touch()

            # initialiser la connexion à la base de données
            self.db = sqlite3.connect(filepath)
            self.cursor = self.db.cursor()
            return (True, "Initialization successful")
        except sqlite3.Error as e:
            return (False, str(e))

    def create_table(self, table_name: str, schema: dict) -> tuple:
        """
        Create a new table in the database.

        Args:
            table_name (str): The name of the table to create.
            schema (dict): A dictionary mapping column names to their data type.

        Returns:
            str: A message indicating whether the table was created successfully or already existed.

        Notes:
            If the table already exists, this method will return a message indicating that the table already exists.
        """
        self.cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
        )
        if self.cursor.fetchone():
            return (False, f"La table '{table_name}' existe déjà")
        else:
            schema_str = ", ".join(f"{k} {v}" for k, v in schema.items())
            self.cursor.execute(f"CREATE TABLE {table_name} ({schema_str})")
            return (True, f"Table '{table_name}' crée avec succès")

    def select(self, query: str) -> tuple:
        """
        Execute a complete SQL query.

        Args:
            query (str): The SQL query to execute.

        Returns:
            tuple: (True, result) if successful, (False, error message) otherwise.
        """
        try:
            result = self.cursor.execute(query).fetchall()
            return (True, result)
        except sqlite3.Error as e:
            return (False, str(e))

    def insert(
        self,
        table_name: str,
        rows: list,
        column_names: list = None,
        chk_duplicates: bool = False,
    ) -> tuple:
        """
        Insert one or more rows into the table.

        Args:
            table_name (str): The name of the table to insert into.
            rows (list): A list of tuples or lists, each containing the values to insert.
            column_names (list): A list of column names to insert into. If None, will use all columns from the table.
            chk_duplicates (bool): If True, will check if the row already exists in the table before inserting.

        Returns:
            tuple: A tuple containing a boolean indicating whether the insert was successful and a message describing the result of the insert.

        Notes:
            If `column_names` is specified, it must match the length of the first row in `rows`.
            If `chk_duplicates` is True, this method will check if the rows already exist in the table before inserting.
            If at least one row already exists, the method will return a tuple containing False and a message indicating that first duplicate row.
        """

        if column_names:
            # Vérifier que les colonnes passées en argument correspondent au schéma de la table
            if len(rows[0]) != len(column_names):
                return (
                    False,
                    f"Data length ({len(rows[0])}) does not match number of columns ({len(column_names)}) provided",
                )
        else:
            # Si aucune colonne fournie, utiliser toutes les colonnes de la table
            schema_info = self.cursor.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
            column_names = [col[1] for col in schema_info if not col[5]]

        if chk_duplicates:
            # Vérifier si des enregistrements existent déjà
            condition_placeholders = " AND ".join(
                [f"{col} = ?" for col in column_names]
            )
            for row in rows:
                if self.cursor.execute(
                    f"SELECT 1 FROM {table_name} WHERE {condition_placeholders}", row
                ).fetchone():
                    return (
                        False,
                        f"doublon trouvé dans la table '{table_name}' : {row}",
                    )

        try:
            placeholders = ", ".join(["?"] * len(column_names))
            query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
            self.cursor.executemany(query, rows)
            return (True, "Insert successful")
        except sqlite3.Error as error:
            return (False, str(error))

    def update(self, table_name: str, data: dict, where: list = None) -> tuple:
        """
        Update entries in the table.

        Args:
            table_name (str): The name of the table to update.
            data (dict): A dictionary containing the column names as keys and the values to update as values.
            where (list, optional): A list of condition strings (e.g. ["age > 20", "name = 'Alice'"]).

        Returns:
            tuple: A tuple containing a boolean indicating whether the update was successful and a message describing the result of the update.

        Notes:
            If `where` is specified, only rows matching all conditions will be updated.
            If an error occurs during the update, the method will return a tuple containing False and the error message.
        """
        set_clause = ", ".join(f"{col} = ?" for col in data)
        values = list(data.values())
        query = f"UPDATE {table_name} SET {set_clause}"
        if where:
            query += f" WHERE {' AND '.join(where)}"
        try:
            self.cursor.execute(query, values)
            return (True, "Update successful")
        except Exception as e:
            return (False, str(e))

    def delete(self, table_name: str, where: list) -> tuple:
        """
        Delete entries from the table.

        Args:
            table_name (str): The name of the table to delete entries from.
            where (list): A list of condition strings (e.g. ["age > 20", "name = 'Alice'"]).

        Returns:
            tuple: A tuple containing a boolean indicating whether the deletion was successful and a message describing the result of the deletion.

        Notes:
            The `where` parameter is used to specify which rows to delete.
            If an error occurs during the deletion, the method will return a tuple containing False and the error message.
        """
        try:
            query = f"DELETE FROM {table_name} WHERE {' AND '.join(where)}"
            self.cursor.execute(query)
            return (True, "Delete successful")
        except Exception as e:
            return (False, str(e))

    def commit(self) -> tuple:
        """
        Commit the current transaction.

        Notes:
            This method is used to explicitly commit a transaction.
            If you do not call this method, the database will automatically
            commit or rollback the transaction when the connection is closed.
        """
        try:
            self.db.commit()
            return (True, "Commit successful")
        except sqlite3.Error as e:
            return (False, str(e))

    def rollback(self) -> tuple:
        """
        Rollback the current transaction.

        Notes:
        This method is used to explicitly rollback a transaction.
        If you do not call this method, the database will automatically
        commit the transaction when the connection is closed.
        """
        try:
            self.db.rollback()
            return (True, "Rollback successful")
        except sqlite3.Error as e:
            return (False, str(e))

    def maintenance(self) -> tuple:
        """
        Perform database maintenance operations.

        Notes:
            This method is used to perform database maintenance operations : vacuuming, analyze, and optimize.
        """
        try:
            self.db.execute("ANALYZE")
            self.db.execute("PRAGMA optimize")
            return (True, "Maintenance successful")
        except Exception as e:
            return (False, str(e))

    def __del__(self):
        """
        Close the database connection and commit any pending changes when the object
        is garbage collected.

        Notes:
            This method is called when the object is garbage collected.
            It is used to ensure that the database connection is always closed,
            even if the object is not explicitly closed.
        """
        self.commit()
        self.db.close()
