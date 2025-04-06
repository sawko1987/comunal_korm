import sqlite3
from sqlite3 import Error

class SqliteDB:
    def __init__(self, db_name: str = 'abonent.db'):
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self._initialize_database()
            self.list_abonent = self.fetch_data()
        except Error as e:
            self._handle_error(f"Ошибка при подключении к базе данных: {e}")
            raise

    def _initialize_database(self) -> None:
        """Инициализирует структуру базы данных"""
        self.create_table_abonent()
        self.create_table_monthly_data()
        self._create_indexes()

    def _create_indexes(self) -> None:
        """Создает необходимые индексы"""
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_abonents_name ON abonents(fulname)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_monthly_data_abonent ON monthly_data(abonent_id)")
        self.conn.commit()

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
        print(f"Список абонентов:{list_abonents}")
        return list_abonents


    def update_data(self, data):
        pass

    def delete_data(self, name):

        try:
            self.cursor.execute("DELETE FROM abonents WHERE fulname = ?", (name,))
            self.conn.commit()
            print(f"Абонент '{name}' удален из базы данных.")
        except sqlite3.Error as e:
            print(f"Ошибка при удалении абонента: {e}")

    def close_connection(self):

        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто.")
    # Создание таблицы для ежемесячных данных
    def create_table_monthly_data(self):
        query = '''
                    CREATE TABLE IF NOT EXISTS monthly_data (                
                    id INTEGER PRIMARY KEY,                
                    abonent_id INTEGER NOT NULL,                
                    month INTEGER NOT NULL,                
                    year INTEGER NOT NULL,                
                    electricity REAL,                
                    water REAL,                
                    wastewater REAL,
                    gas REAL,                
                    FOREIGN KEY (abonent_id) REFERENCES abonents(id)                
                    );'''
        self.cursor.execute(query)
        print ('База данных monthly_data создана или открыта ')
        self.conn.commit()


    # Добавление ежемесячных данных в таблицу
    def insert_monthly_data(self, abonent_id, month, year, electricity=None, water=None, wastewater=None, gas=None):
        query = '''
                    INSERT INTO monthly_data (
                    abonent_id, month, year, electricity, water, wastewater, gas)    
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
        self.cursor.execute(query, (abonent_id, month, year, electricity, water, wastewater, gas))
        self.conn.commit()

        #  Получение последних показаний для абонента
    def get_last_reading(self, abonent_id):

        query = '''    
                    SELECT month, year, electricity, water, wastewater, gas                
                    FROM monthly_data                
                    WHERE abonent_id = ?                
                    ORDER BY year DESC, month DESC                
                    LIMIT 1                
                    '''
        self.cursor.execute(query, (abonent_id,))
        return self.cursor.fetchone()

    def get_consumption_data(self, abonent_id, start_month, start_year, end_month, end_year):
        """
        Получает данные о потреблении ресурсов за указанный период

        Args:
            abonent_id: ID абонента
            start_month: начальный месяц (1-12)
            start_year: начальный год (YYYY)
            end_month: конечный месяц (1-12)
            end_year: конечный год (YYYY)

        Returns:
            List[tuple]: список записей о потреблении или None при ошибке
        """
        try:
            # Валидация входных параметров
            if not isinstance(abonent_id, int) or abonent_id <= 0:
                raise ValueError("Некорректный ID абонента")

            if not all(isinstance(x, int) for x in [start_month, start_year, end_month, end_year]):
                raise ValueError("Все параметры периода должны быть целыми числами")

            if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
                raise ValueError("Месяц должен быть в диапазоне от 1 до 12")

            if start_year < 2000 or end_year < 2000 or start_year > 2100 or end_year > 2100:
                raise ValueError("Год должен быть между 2000 и 2100")

            if (start_year > end_year) or (start_year == end_year and start_month > end_month):
                raise ValueError("Начальная дата должна быть раньше конечной")

            query = """
                SELECT id, abonent_id, month, year, electricity, water, gas, 
                       strftime('%Y-%m', printf('%04d-%02d', year, month)) as period
                FROM monthly_data
                WHERE abonent_id = ? 
                  AND (year > ? OR (year = ? AND month >= ?))
                  AND (year < ? OR (year = ? AND month <= ?))
                ORDER BY year, month;
            """
            params = (abonent_id, start_year, start_year, start_month,
                      end_year, end_year, end_month)

            self.cursor.execute(query, params)
            result = self.cursor.fetchall()

            if not result:
                print(
                    f"Для абонента {abonent_id} нет данных за период {start_month}/{start_year}-{end_month}/{end_year}")

            return result

        except sqlite3.Error as e:
            print(f"Ошибка базы данных при получении данных о потреблении: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка при получении данных о потреблении: {e}")
            return None

    def get_abonent_id_by_name(self, name):
        query = "SELECT id FROM abonents WHERE fulname = ?"
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def execute_query(self, query, params=(), fetch_mode='one'):
        """
        Выполняет SQL-запрос и возвращает результат

        Параметры:
            query (str): SQL-запрос для выполнения
            params (tuple): параметры для запроса (по умолчанию пустой кортеж)
            fetch_mode (str): режим выборки:
                'one' - вернуть одну запись (по умолчанию)
                'all' - вернуть все записи
                None - не возвращать результат (для INSERT/UPDATE/DELETE)

        Возвращает:
            Результат запроса в зависимости от fetch_mode:
                - одна запись (для fetch_mode='one')
                - список всех записей (для fetch_mode='all')
                - None (для fetch_mode=None или при ошибке)
        """
        try:
            self.cursor.execute(query, params)

            if fetch_mode is None:
                return None
            elif fetch_mode == 'all':
                return self.cursor.fetchall()
            else:  # режим 'one' по умолчанию
                return self.cursor.fetchone()

        except sqlite3.Error as e:
            print(f"Ошибка при выполнении запроса '{query}': {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка при выполнении запроса: {e}")
            return None



