import sqlite3
from sqlite3 import Error

class SqliteDB:
    def __init__(self):
        self.conn = sqlite3.connect('abonent.db')
        print("База данных успешно открыта.")
        self.cursor = self.conn.cursor()
        self.list_abonent = self.fetch_data()

    def create_table_abonent(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abonents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fulname TEXT NOT NULL,
        elect_value INTEGER,
        transformation_ratio_value INTEGER,
        water_value INTEGER,
        wastewater_value INTEGER,
        gaz_value INTEGER)''')

    def insert_data(self, data):
        self.cursor.execute(
            'INSERT INTO abonents  (fulname, elect_value, transformation_ratio_value,water_value,wastewater_value,gaz_value) '
            'VALUES (?, ?, ?, ?, ?,?)', data)
        self.conn.commit() #сохраняем изменения


    def fetch_data(self):
        self.cursor.execute('SELECT * FROM abonents')
        list_abonents = self.cursor.fetchall()
        print(list_abonents)
        return list_abonents


    def update_data(self, data):
        pass

    def delete_data(self, id):
        pass

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто.")