# Основа этого файла взята из https://github.com/alexey-goloburdin/telegram-finance-bot/blob/master/db.py

import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()


def get_cursor():
    return cursor


def insert_or_update(user_id: int, youtube_hash: str, description: str):
    statement = "INSERT INTO youtube (user_id, youtube_hash, description) " \
                "VALUES (:user_id, :youtube_hash, :description) " \
                "ON CONFLICT(user_id, youtube_hash) " \
                "DO UPDATE SET description = :description"
    cursor.execute(statement, {
        "user_id": user_id,
        "youtube_hash": youtube_hash,
        "description": description
    })
    cursor.connection.commit()


def delete(user_id: int, youtube_hash: str):
    statement = "DELETE from youtube WHERE user_id = ? and youtube_hash = ?"
    cursor.execute(statement, (user_id, youtube_hash))
    cursor.connection.commit()


def get_links(user_id: int, search_query: str = None):
    statement = "SELECT youtube_hash, description from youtube WHERE user_id = ?"
    if search_query:
        statement += f" AND description LIKE ?"
        result = cursor.execute(statement, (user_id, f"%{search_query}%"))
    else:
        result = cursor.execute(statement, (user_id,))
    return result.fetchall()


def _init_db():
    """Инициализирует БД"""
    with open("create_database.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='youtube'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
