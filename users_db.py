import os
import sqlite3
from sqlite3 import Error
from typing import Optional


class SqliteDB:
    def __init__(self, db_name: str = 'abonent.db'):
        # Определяем путь к папке `data`
        self.db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        self.db_path = os.path.join(self.db_dir, db_name)

        # Создаём папку, если её нет
        os.makedirs(self.db_dir, exist_ok=True)

        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

        try:
            # Подключаемся к базе данных по правильному пути
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self._initialize_database()
            self.list_abonent = self.fetch_data()
        except Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            raise

    def _handle_error(self, message: str):
        """Обработчик ошибок"""
        print(message)
        if self.conn:
            self.conn.rollback()

    def _initialize_database(self) -> None:
        """Инициализирует структуру базы данных"""
        self.create_table_abonent()
        self._update_table_structure()
        self.create_table_monthly_data()
        self._create_indexes()
        self.update_abonent_services()  # Обновляем флаги услуг
        self.conn.commit()

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
                            gaz_value INTEGER,
                            uses_electricity BOOLEAN DEFAULT 0,
                            uses_water BOOLEAN DEFAULT 0,
                            uses_wastewater BOOLEAN DEFAULT 0,
                            uses_gas BOOLEAN DEFAULT 0)''')
        self.conn.commit()

    def insert_data(self, data):
        try:
            self.cursor.execute(
                '''INSERT INTO abonents (
                    fulname, 
                    elect_value, 
                    transformation_ratio_value, 
                    water_value, 
                    wastewater_value, 
                    gaz_value,
                    uses_electricity,
                    uses_water,
                    uses_wastewater,
                    uses_gas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            self.conn.commit()
        except sqlite3.Error as e:
            self._handle_error(f"Ошибка при вставке данных: {e}")
            raise

    def fetch_data(self):
        try:
            self.cursor.execute('SELECT * FROM abonents')
            list_abonents = self.cursor.fetchall()
            print(f"Список абонентов:{list_abonents}")
            return list_abonents
        except sqlite3.Error as e:
            self._handle_error(f"Ошибка при получении данных: {e}")
            return []

    def update_data(self, abonent_id, fulname, elect_value=None, transformation_ratio_value=None,
                    water_value=None, wastewater_value=None, gaz_value=None,
                    uses_electricity=None, uses_water=None, uses_wastewater=None, uses_gas=None):
        """Обновляет данные абонента"""
        try:
            query = """UPDATE abonents 
                      SET fulname = ?, 
                          elect_value = ?, 
                          transformation_ratio_value = ?, 
                          water_value = ?, 
                          wastewater_value = ?, 
                          gaz_value = ?,
                          uses_electricity = ?,
                          uses_water = ?,
                          uses_wastewater = ?,
                          uses_gas = ?
                      WHERE id = ?"""
            self.cursor.execute(query, (
                fulname, 
                elect_value, 
                transformation_ratio_value,
                water_value, 
                wastewater_value, 
                gaz_value,
                uses_electricity,
                uses_water,
                uses_wastewater,
                uses_gas,
                abonent_id
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self._handle_error(f"Ошибка при обновлении данных: {e}")
            return False

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

    def get_abonent_by_id(self, abonent_id):
        """Получает данные абонента по ID"""
        print(f"\n=== Получение данных абонента по ID {abonent_id} ===")
        try:
            self.cursor.execute("SELECT * FROM abonents WHERE id = ?", (abonent_id,))
            result = self.cursor.fetchone()
            print(f"Результат запроса: {result}")
            if result:
                print("Данные абонента успешно получены")
            else:
                print("Абонент не найден")
            return result
        except sqlite3.Error as e:
            print(f"ОШИБКА при получении данных абонента: {e}")
            self._handle_error(f"Ошибка при получении данных абонента: {e}")
            return None


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

    def get_monthly_data_for_period(self, abonent_id, start_date, end_date):
        """Получает данные за указанный период для абонента"""
        query = """
        SELECT * FROM monthly_data 
        WHERE abonent_id = ? AND date BETWEEN ? AND ?
        ORDER BY date DESC
        """
        return self.execute_query(query, (abonent_id, start_date.strftime('%Y-%m-%d'),
                                          end_date.strftime('%Y-%m-%d')))


    def get_table_columns(self, table_name):
        """Возвращает список столбцов указанной таблицы"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            return columns
        except Exception as e:
            print(f"Ошибка при получении столбцов таблицы {table_name}: {e}")
            return None

    def print_table_structure(self, table_name):
        """Выводит структуру указанной таблицы"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"Структура таблицы {table_name}:")
            for column in columns:
                print(column)
        except Exception as e:
            print(f"Ошибка при получении структуры таблицы {table_name}: {e}")

    def get_last_months_with_data(self, abonent_id, limit=3):
        """Возвращает последние месяцы, по которым есть данные"""
        query = """
        SELECT DISTINCT month, year 
        FROM monthly_data 
        WHERE abonent_id = ?
        ORDER BY year DESC, month DESC
        LIMIT ?
        """
        return self.execute_query(query, (abonent_id, limit), fetch_mode='all')

    def get_last_months_data(self, abonent_id, limit=3):
        """Получает данные за последние месяцы"""
        try:
            query = """
                SELECT month, year, electricity, water, wastewater, gas
                FROM monthly_data
                WHERE abonent_id = ?
                ORDER BY year DESC, month DESC
                LIMIT ?
            """
            self.cursor.execute(query, (abonent_id, limit))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных за последние месяцы: {e}")
            return None

    def get_last_months_consumption(self, abonent_id, utility_type, limit=3):
        """
        Получает данные о потреблении конкретной услуги за последние месяцы
        
        Args:
            abonent_id: ID абонента
            utility_type: тип услуги ('electricity', 'water', 'wastewater', 'gas')
            limit: количество последних месяцев
            
        Returns:
            list: список значений потребления
        """
        try:
            # Маппинг названий услуг на названия столбцов в БД
            utility_mapping = {
                'electricity': 'electricity',
                'water': 'water',
                'wastewater': 'wastewater',
                'gas': 'gas'
            }
            
            if utility_type not in utility_mapping:
                raise ValueError(f"Неизвестный тип услуги: {utility_type}")
                
            column = utility_mapping[utility_type]
            
            query = f"""
                SELECT {column}
                FROM monthly_data
                WHERE abonent_id = ? AND {column} IS NOT NULL
                ORDER BY year DESC, month DESC
                LIMIT ?
            """
            
            self.cursor.execute(query, (abonent_id, limit))
            results = self.cursor.fetchall()
            
            # Извлекаем значения из кортежей
            return [row[0] for row in results]
            
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных о потреблении: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None

    def get_monthly_data_by_date(self, abonent_id, month, year):
        """Получает данные за конкретный месяц и год"""
        try:
            query = """
                SELECT electricity, water, wastewater, gas
                FROM monthly_data
                WHERE abonent_id = ? AND month = ? AND year = ?
            """
            self.cursor.execute(query, (abonent_id, month, year))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'electricity': result[0],
                    'water': result[1],
                    'wastewater': result[2],
                    'gas': result[3]
                }
            return None
            
        except sqlite3.Error as e:
            print(f"Ошибка при получении данных за месяц: {e}")
            return None

    def update_monthly_data(self, abonent_id, month, year, electricity=None, water=None, wastewater=None, gas=None):
        """Обновляет месячные данные"""
        try:
            query = """
                UPDATE monthly_data
                SET electricity = ?,
                    water = ?,
                    wastewater = ?,
                    gas = ?
                WHERE abonent_id = ? AND month = ? AND year = ?
            """
            self.cursor.execute(query, (electricity, water, wastewater, gas, abonent_id, month, year))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении месячных данных: {e}")
            return False

    def get_all_monthly_data(self, abonent_id):
        """Получает все месячные данные для абонента"""
        try:
            query = """
                SELECT id, abonent_id, month, year, electricity, water, wastewater, gas
                FROM monthly_data
                WHERE abonent_id = ?
                ORDER BY year DESC, month DESC
            """
            self.cursor.execute(query, (abonent_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка при получении месячных данных: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None

    def _update_table_structure(self):
        """Обновляет структуру таблицы, добавляя новые столбцы"""
        try:
            # Проверяем наличие столбцов
            self.cursor.execute("PRAGMA table_info(abonents)")
            columns = {column[1] for column in self.cursor.fetchall()}
            
            # Список необходимых столбцов и их типов
            required_columns = {
                'uses_electricity': 'BOOLEAN DEFAULT 0',
                'uses_water': 'BOOLEAN DEFAULT 0',
                'uses_wastewater': 'BOOLEAN DEFAULT 0',
                'uses_gas': 'BOOLEAN DEFAULT 0'
            }
            
            # Добавляем отсутствующие столбцы
            for column, type_def in required_columns.items():
                if column not in columns:
                    print(f"Добавляем столбец {column}")
                    self.cursor.execute(f"ALTER TABLE abonents ADD COLUMN {column} {type_def}")
            
            self.conn.commit()
            print("Структура таблицы успешно обновлена")
            
        except Error as e:
            print(f"Ошибка при обновлении структуры таблицы: {e}")
            self.conn.rollback()

    def update_abonent_services(self):
        """Обновляет флаги услуг для существующих абонентов на основе их показаний"""
        try:
            print("\n=== Обновление флагов услуг для абонентов ===")
            # Получаем всех абонентов
            self.cursor.execute("SELECT id, elect_value, water_value, wastewater_value, gaz_value FROM abonents")
            abonents = self.cursor.fetchall()
            
            for abonent in abonents:
                abonent_id = abonent[0]
                uses_electricity = 1 if abonent[1] is not None else 0
                uses_water = 1 if abonent[2] is not None else 0
                uses_wastewater = 1 if abonent[3] is not None else 0
                uses_gas = 1 if abonent[4] is not None else 0
                
                print(f"\nАбонент ID {abonent_id}:")
                print(f"Электроэнергия: {uses_electricity}")
                print(f"Вода: {uses_water}")
                print(f"Водоотведение: {uses_wastewater}")
                print(f"Газ: {uses_gas}")
                
                # Обновляем флаги
                self.cursor.execute("""
                    UPDATE abonents 
                    SET uses_electricity = ?,
                        uses_water = ?,
                        uses_wastewater = ?,
                        uses_gas = ?
                    WHERE id = ?
                """, (uses_electricity, uses_water, uses_wastewater, uses_gas, abonent_id))
            
            self.conn.commit()
            print("\nФлаги услуг успешно обновлены")
            
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении флагов услуг: {e}")
            self._handle_error(f"Ошибка при обновлении флагов услуг: {e}")
            return False