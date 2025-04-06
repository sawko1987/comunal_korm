import sqlite3

import customtkinter as ctk
from users_db import SqliteDB



# Изменение: Добавление нового класса ConsumptionHistoryWindow
class ConsumptionHistoryWindow:
    def __init__(self, parent, width, height,abonent_id, title= "Учет коммунальных услуг АО_Корммаш", resizable=(False,False),
                 icon='image/korm.ico',):
        self.root = ctk.CTkToplevel(parent)

        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)

        self.abonent_id = abonent_id
        print(f"Тип abonent_id: {type(self.abonent_id)}, значение: {self.abonent_id}")


        # Поля для выбора периода
        self.start_month_label = ctk.CTkLabel(self.root, text="Начальный месяц:")
        self.start_month_label.pack(pady=5)
        self.start_month_entry = ctk.CTkEntry(self.root)
        self.start_month_entry.pack(pady=5)

        self.start_year_label = ctk.CTkLabel(self.root, text="Начальный год:")
        self.start_year_label.pack(pady=5)
        self.start_year_entry = ctk.CTkEntry(self.root)
        self.start_year_entry.pack(pady=5)

        self.end_month_label = ctk.CTkLabel(self.root, text="Конечный месяц:")
        self.end_month_label.pack(pady=5)
        self.end_month_entry = ctk.CTkEntry(self.root)
        self.end_month_entry.pack(pady=5)

        self.end_year_label = ctk.CTkLabel(self.root, text="Конечный год:")
        self.end_year_label.pack(pady=5)
        self.end_year_entry = ctk.CTkEntry(self.root)
        self.end_year_entry.pack(pady=5)

        # Кнопка для загрузки данных
        self.load_button = ctk.CTkButton(self.root, text="Загрузить данные", command=self.load_data)
        self.load_button.pack(pady=20)

        # Таблица для отображения данных
        self.table = ctk.CTkTextbox(self.root, width=550, height=200)
        self.table.pack(pady=10)

        # Устанавливаем фокус на окно
        self.root.grab_set()
        self.root.focus_set()

    # Метод для загрузки данных
    def load_data(self):
        """Загружает данные о потреблении за указанный период и отображает их в интерфейсе"""
        try:
            # 1. Получаем и валидируем параметры периода
            start_month = int(self.start_month_entry.get())
            start_year = int(self.start_year_entry.get())
            end_month = int(self.end_month_entry.get())
            end_year = int(self.end_year_entry.get())

            # Валидация введенных значений
            if not (1 <= start_month <= 12) or not (1 <= end_month <= 12):
                raise ValueError("Месяц должен быть от 1 до 12")
            if start_year < 2000 or end_year < 2000:
                raise ValueError("Год должен быть не менее 2000")
            if (start_year > end_year) or (start_year == end_year and start_month > end_month):
                raise ValueError("Начальная дата должна быть раньше конечной")

            print(
                f"Параметры запроса: abonent_id={self.abonent_id}, период: {start_month}/{start_year}-{end_month}/{end_year}")

            # 2. Подключаемся к базе данных
            db = SqliteDB()

            try:
                # 3. Проверяем существование таблицы monthly_data (бывшая consumption)
                table_check = "SELECT name FROM sqlite_master WHERE type='table' AND name='monthly_data'"
                if not db.execute_query(table_check, fetch_mode='one'):
                    self.table.delete("1.0", "end")
                    self.table.insert("end", "Ошибка: таблица monthly_data не существует\n")
                    return

                # 4. Проверяем наличие любых данных для абонента
                test_query = "SELECT 1 FROM monthly_data WHERE abonent_id = ? LIMIT 1"
                test_data = db.execute_query(test_query, (self.abonent_id,), fetch_mode='one')
                print(f"Тестовые данные (любые): {test_data}")

                if not test_data:
                    self.table.delete("1.0", "end")
                    self.table.insert("end", "Ошибка: нет никаких данных для этого абонента\n")
                    return

                # 5. Запрашиваем данные за указанный период
                data = db.get_consumption_data(self.abonent_id, start_month, start_year, end_month, end_year)
                print(f"Данные за период: {data}")

                self.table.delete("1.0", "end")

                if not data:
                    self.table.insert("end", "Нет данных за указанный период (но данные для абонента существуют)\n")
                    return

                # 6. Форматируем и выводим данные
                headers = ["Месяц/Год", "Электроэнергия (кВт·ч)", "Вода (м³)", "Сточные воды (м³)", "Газ (м³)"]
                self.table.insert("end", "\t".join(headers) + "\n")
                self.table.insert("end", "-" * 70 + "\n")

                for row in data:
                    month_year = f"{row[2]}/{row[3]}"
                    electricity = f"{row[4] or 'нет'}"
                    water = f"{row[5] or 'нет'}"
                    wastewater = f"{row[6] or 'нет'}"
                    gas = f"{row[7] or 'нет'}" if len(row) > 7 else 'нет'

                    values = [month_year, electricity, water, wastewater, gas]
                    self.table.insert("end", "\t".join(values) + "\n")

            finally:
                # Всегда закрываем соединение с БД
                db.close_connection()

        except ValueError as ve:
            self.table.delete("1.0", "end")
            self.table.insert("end", f"Ошибка ввода: {str(ve)}\n")
        except sqlite3.Error as dbe:
            self.table.delete("1.0", "end")
            self.table.insert("end", f"Ошибка базы данных: {str(dbe)}\n")
        except Exception as e:
            self.table.delete("1.0", "end")
            self.table.insert("end", f"Неожиданная ошибка: {str(e)}\n")
            import traceback
            traceback.print_exc()