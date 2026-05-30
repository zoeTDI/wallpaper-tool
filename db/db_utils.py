import sqlite3
from typing import Union
from db.enum import DB_NAME

def read_config(key: str) -> Union[str, None]:
    sql_query = "SELECT VALUE FROM config WHERE [KEY] = ?;"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(sql_query, (key,))

    result = cursor.fetchone()
    conn.close()

    return result

def write_config(key: str, value:str) -> bool:
    sql_upsert = "INSERT OR REPLACE INTO config ([KEY], VALUE) VALUES (?, ?);"
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(sql_upsert, (key, value))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"写入配置项 [{key}] 时出错: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_wallpaper_path():
    return read_config('wallpaper_dir_path')