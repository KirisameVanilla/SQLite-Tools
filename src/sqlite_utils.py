import sqlite3
from typing import Optional, List, Dict, Any


class SQLiteUtils:
    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None
        self.current_db_path: Optional[str] = None

    def create_database(self, file_path: str):
        conn = sqlite3.connect(file_path)
        conn.close()
        self.open_database_file(file_path)

    def open_database_file(self, file_path: str):
        if self.conn:
            self.conn.close()
        self.conn = sqlite3.connect(file_path)
        self.current_db_path = file_path

    def import_database(self, source_file: str, target_file: str):
        import shutil

        shutil.copy2(source_file, target_file)
        self.open_database_file(target_file)

    def export_database(self, target_file: str):
        import shutil

        if not self.conn or not self.current_db_path:
            raise Exception("请先打开一个数据库")
        shutil.copy2(self.current_db_path, target_file)

    def get_tables(self) -> List[str]:
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row[0] for row in cursor.fetchall()]

    def get_table_structure(self, table_name: str) -> List[Dict[str, Any]]:
        if not self.conn:
            return []
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        return [
            {
                "cid": col[0],
                "name": col[1],
                "data_type": col[2],
                "not_null": col[3],
                "default_value": col[4],
                "pk": col[5],
            }
            for col in columns
        ]

    def get_table_data(self, table_name: str, limit: int = 100) -> Dict[str, Any]:
        if not self.conn:
            return {"columns": [], "rows": []}
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return {"columns": column_names, "rows": rows}

    def execute_query(self, table_name: str) -> Dict[str, Any]:
        if not self.conn:
            return {"columns": [], "rows": []}
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return {"columns": column_names, "rows": rows}

    def execute_sql(self, sql: str) -> Dict[str, Any]:
        if not self.conn:
            raise Exception("请先打开一个数据库")
        cursor = self.conn.cursor()
        cursor.execute(sql)
        if cursor.description:
            column_names = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return {"columns": column_names, "rows": rows}
        else:
            self.conn.commit()
            return {"affected_rows": cursor.rowcount}

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.current_db_path = None
