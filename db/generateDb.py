import os.path
import sqlite3
from typing import List
from db.enum import DB_NAME, CONFIG_SQL, WALLPAPER_DATA


TABLE_SQLS = [CONFIG_SQL, WALLPAPER_DATA]

def safe_process_db_name(name:str)->str:
    if not name.endswith('.db'):
        return f"{name}.db"
    else:
        return name

def create_sqlite_databases(db_name: str) -> bool:
    """
    创建指定名称的 SQLite 数据库文件
    :param db_name: 数据库名字符串
    :return:数据库是否创建成功
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    db_name = safe_process_db_name(db_name)

    db_path = os.path.join(base_dir, db_name)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"创建数据库 [{db_name}] 失败，错误原因: {e}")
        return False

def create_sqlite_tables(tb_sqls: List[str]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for tb_sql in tb_sqls:
        cursor.execute(tb_sql)
        conn.commit()
    conn.close()

def init():
    is_create_success = create_sqlite_databases(DB_NAME)
    if not is_create_success:
        print(f"{DB_NAME} 创建失败")
        return None
    create_sqlite_tables(TABLE_SQLS)