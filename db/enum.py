DB_NAME = 'wallpaperTool.db'

CONFIG_SQL = """
CREATE TABLE IF NOT EXISTS config (
    [key] TEXT PRIMARY KEY NOT NULL,
    [value] TEXT
);"""
WALLPAPER_DATA = """
CREATE TABLE IF NOT EXISTS wallpaper (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    json_path TEXT NOT NULL,
    file_path TEXT NOT NULL,
    name TEXT NOT NULL
);"""