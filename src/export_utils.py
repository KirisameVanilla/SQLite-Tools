import os
import sqlite3
import pandas as pd
from typing import Optional


def export_db_to_csv(db_path: str, output_dir: Optional[str] = None):
    """
    将数据库中所有表导出为csv文件，输出到以数据库名为名的文件夹下。
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    db_name = os.path.splitext(os.path.basename(db_path))[0]
    output_dir = output_dir or db_name
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
            csv_path = os.path.join(output_dir, f"{table}.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    finally:
        conn.close()


def export_db_to_xlsx(db_path: str, output_path: Optional[str] = None):
    """
    将数据库中所有表导出为一个xlsx文件，每个表为一个sheet。
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    db_name = os.path.splitext(os.path.basename(db_path))[0]
    output_path = output_path or f"{db_name}.xlsx"
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for table in tables:
                df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
                df.to_excel(writer, sheet_name=table, index=False)
    finally:
        conn.close()
