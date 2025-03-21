import sqlite3
from sqlite3 import Error


def create_connection():
    """Создаём соединение с БД"""
    conn = None
    try:
        conn = sqlite3.connect('utilities.db')
        print(f"Подключение к SQLite успешно: sqlite3.version {sqlite3.version}")
        return conn
    except Error as e:
        print(f"Ошибка подключения: {e}")
    return conn


def create_tables(conn):
    """Создаём таблицы"""
    sql_subscribers = """
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        electricity REAL DEFAULT 0,
        transformation_ratio INTEGER DEFAULT 1,
        gas BOOLEAN DEFAULT 0,
        water BOOLEAN DEFAULT 0,
        wastewater BOOLEAN DEFAULT 0,
        
    );"""

    sql_readings = """
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscriber_id INTEGER NOT NULL,
        period DATE NOT NULL,  -- Формат: 'YYYY-MM'
        electricity REAL DEFAULT 0,
        coeff REAL DEFAULT 1,
        gas REAL DEFAULT 0,
        water REAL DEFAULT 0,
        drainage REAL DEFAULT 0,
        FOREIGN KEY (subscriber_id) REFERENCES subscribers (id)
    );"""

    try:
        c = conn.cursor()
        c.execute(sql_subscribers)
        c.execute(sql_readings)
        conn.commit()
        print("Таблицы созданы успешно")
    except Error as e:
        print(f"Ошибка создания таблиц: {e}")


if __name__ == "__main__":
    conn = create_connection()
    if conn:
        create_tables(conn)
        conn.close()