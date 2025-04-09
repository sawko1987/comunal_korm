import sqlite3
import customtkinter as ctk
from users_db import SqliteDB
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import subprocess


class ConsumptionHistoryWindow:
    def __init__(self, parent, width, height, abonent_id, title="Учет коммунальных услуг АО_Корммаш",
                 resizable=(False, False), icon='image/korm.ico'):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)

        self.abonent_id = abonent_id
        self.last_pdf_path = None  # Будем хранить путь к последнему созданному PDF
        print(f"Тип abonent_id: {type(self.abonent_id)}, значение: {self.abonent_id}")

        # Поля для выбора расчетного периода
        self.month_label = ctk.CTkLabel(self.root, text="Расчетный месяц:")
        self.month_label.pack(pady=5)

        # Выпадающий список для месяцев
        self.months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                       "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        self.month_var = ctk.StringVar(value=self.months[datetime.now().month - 1])
        self.month_combobox = ctk.CTkComboBox(self.root, values=self.months, variable=self.month_var)
        self.month_combobox.pack(pady=5)

        self.year_label = ctk.CTkLabel(self.root, text="Год:")
        self.year_label.pack(pady=5)
        self.year_entry = ctk.CTkEntry(self.root)
        self.year_entry.pack(pady=5)
        self.year_entry.insert(0, str(datetime.now().year))  # Текущий год по умолчанию

        # Кнопка для загрузки данных
        self.load_button = ctk.CTkButton(self.root, text="Загрузить данные", command=self.load_data)
        self.load_button.pack(pady=20)

        # Кнопка для расчета данных
        self.calc_button = ctk.CTkButton(self.root, text="Рассчитать потребление", command=self.calculate_consumption,
                                         state='disabled')
        self.calc_button.pack(pady=10)

        # Кнопка для генерации реестра
        self.generate_registry_button = ctk.CTkButton(self.root, text="Создать реестр", command=self.generate_registry,
                                                      state='disabled')
        self.generate_registry_button.pack(pady=10)

        # Кнопка для открытия PDF (изначально скрыта)
        self.open_pdf_button = ctk.CTkButton(self.root, text="Открыть PDF", command=self.open_pdf,
                                             state='disabled', fg_color='green')
        self.open_pdf_button.pack(pady=5)

        # Таблица для отображения данных
        self.table = ctk.CTkTextbox(self.root, width=550, height=200)
        self.table.pack(pady=10)

        # Поле для вывода расчетов
        self.calculation_result = ctk.CTkTextbox(self.root, width=550, height=200)
        self.calculation_result.pack(pady=10)

        self.root.grab_set()
        self.root.focus_set()

    def open_pdf(self):
        """Открывает созданный PDF файл в стандартном просмотрщике"""
        if self.last_pdf_path and os.path.exists(self.last_pdf_path):
            try:
                if os.name == 'nt':  # Для Windows
                    os.startfile(self.last_pdf_path)
                elif os.name == 'posix':  # Для Mac и Linux
                    subprocess.run(
                        ['open', self.last_pdf_path] if sys.platform == 'darwin' else ['xdg-open', self.last_pdf_path])
                self.calculation_result.insert("end", f"\nPDF файл открыт: {self.last_pdf_path}\n")
            except Exception as e:
                self.calculation_result.insert("end", f"\nОшибка при открытии PDF: {str(e)}\n")
        else:
            self.calculation_result.insert("end", "\nPDF файл не найден. Сначала создайте реестр.\n")

    def get_month_number(self, month_name):
        """Возвращает номер месяца по его названию"""
        return self.months.index(month_name) + 1

    def load_data(self):
        """Загружает данные о потреблении за указанный расчетный месяц и отображает их в интерфейсе"""
        try:
            # 1. Получаем и валидируем параметры периода
            month_name = self.month_var.get()
            month = self.get_month_number(month_name)
            year = int(self.year_entry.get())

            # Валидация введенных значений
            if year < 2000 or year > datetime.now().year + 1:
                raise ValueError("Год должен быть в диапазоне 2000-" + str(datetime.now().year + 1))

            print(f"Параметры запроса: abonent_id={self.abonent_id}, месяц: {month}/{year}")

            # 2. Подключаемся к базе данных
            db = SqliteDB()

            try:
                # Проверка существования таблицы abonents
                if not db.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='abonents'",
                                        fetch_mode='one'):
                    raise Exception("Таблица abonents не существует")

                # Получаем имя абонента
                fulname_data = db.execute_query(
                    "SELECT fulname FROM abonents WHERE id = ?",
                    (self.abonent_id,),
                    fetch_mode='one'
                )

                if not fulname_data:
                    raise Exception(f"Абонент с ID {self.abonent_id} не найден")

                fulname = fulname_data[0]
                print(f"Найден абонент: {fulname}")

                # 3. Проверяем существование таблицы monthly_data
                table_check = "SELECT name FROM sqlite_master WHERE type='table' AND name='monthly_data'"
                if not db.execute_query(table_check, fetch_mode='one'):
                    self.table.delete("1.0", "end")
                    self.table.insert("end", "Ошибка: таблица monthly_data не существует\n")
                    return

                # 4. Получаем данные за расчетный месяц и предыдущий месяц
                # Для расчета потребления нам нужны показания на начало и конец периода

                # Текущий расчетный месяц (конец периода)
                end_month_data = db.execute_query(
                    "SELECT * FROM monthly_data WHERE abonent_id = ? AND month = ? AND year = ?",
                    (self.abonent_id, month, year),
                    fetch_mode='one'
                )

                # Предыдущий месяц (начало периода)
                prev_month = month - 1 if month > 1 else 12
                prev_year = year if month > 1 else year - 1

                start_month_data = db.execute_query(
                    "SELECT * FROM monthly_data WHERE abonent_id = ? AND month = ? AND year = ?",
                    (self.abonent_id, prev_month, prev_year),
                    fetch_mode='one'
                )

                self.table.delete("1.0", "end")

                if not end_month_data:
                    self.table.insert("end", f"Нет данных за расчетный месяц {month}/{year}\n")
                    return

                if not start_month_data:
                    self.table.insert("end", f"Нет данных за предыдущий месяц {prev_month}/{prev_year}\n")
                    self.table.insert("end", "Расчет будет выполнен от нуля\n")

                # Формируем заголовки таблицы
                headers = ["Параметр", "Предыдущий месяц", "Текущий месяц", "Потребление"]
                self.table.insert("end", "\t".join(headers) + "\n")
                self.table.insert("end", "-" * 70 + "\n")

                # Электроэнергия
                if len(end_month_data) > 4 and end_month_data[4] is not None:
                    prev_value = float(start_month_data[4]) if start_month_data and len(start_month_data) > 4 and \
                                                               start_month_data[4] is not None else 0.0
                    curr_value = float(end_month_data[4])
                    consumption = curr_value - prev_value

                    row = [
                        "Электроэнергия (кВт·ч)",
                        f"{prev_value:.2f}" if start_month_data else "нет данных",
                        f"{curr_value:.2f}",
                        f"{consumption:.2f}"
                    ]
                    self.table.insert("end", "\t".join(row) + "\n")

                # Вода
                if len(end_month_data) > 5 and end_month_data[5] is not None:
                    prev_value = float(start_month_data[5]) if start_month_data and len(start_month_data) > 5 and \
                                                               start_month_data[5] is not None else 0.0
                    curr_value = float(end_month_data[5])
                    consumption = curr_value - prev_value

                    row = [
                        "Вода (м³)",
                        f"{prev_value:.2f}" if start_month_data else "нет данных",
                        f"{curr_value:.2f}",
                        f"{consumption:.2f}"
                    ]
                    self.table.insert("end", "\t".join(row) + "\n")

                # Сточные воды
                if len(end_month_data) > 6 and end_month_data[6] is not None:
                    prev_value = float(start_month_data[6]) if start_month_data and len(start_month_data) > 6 and \
                                                               start_month_data[6] is not None else 0.0
                    curr_value = float(end_month_data[6])
                    consumption = curr_value - prev_value

                    row = [
                        "Сточные воды (м³)",
                        f"{prev_value:.2f}" if start_month_data else "нет данных",
                        f"{curr_value:.2f}",
                        f"{consumption:.2f}"
                    ]
                    self.table.insert("end", "\t".join(row) + "\n")

                # Газ
                if len(end_month_data) > 7 and end_month_data[7] is not None:
                    prev_value = float(start_month_data[7]) if start_month_data and len(start_month_data) > 7 and \
                                                               start_month_data[7] is not None else 0.0
                    curr_value = float(end_month_data[7])
                    consumption = curr_value - prev_value

                    row = [
                        "Газ (м³)",
                        f"{prev_value:.2f}" if start_month_data else "нет данных",
                        f"{curr_value:.2f}",
                        f"{consumption:.2f}"
                    ]
                    self.table.insert("end", "\t".join(row) + "\n")

                # Активируем кнопки после успешной загрузки данных
                self.calc_button.configure(state="normal", fg_color="#1f6aa5")
                self.generate_registry_button.configure(state="normal", fg_color="#1f6aa5")

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

    def calculate_consumption(self):
        """Вычисляет общее потребление ресурсов за расчетный месяц"""
        try:
            # Проверяем, что данные загружены
            if not self.table.get("1.0", "end-1c"):
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", "❌ Ошибка: сначала загрузите данные!\n")
                return

            month_name = self.month_var.get()
            month = self.get_month_number(month_name)
            year = int(self.year_entry.get())

            db = SqliteDB()
            try:
                # Получаем имя абонента
                fulname = db.execute_query(
                    "SELECT fulname FROM abonents WHERE id = ?",
                    (self.abonent_id,),
                    fetch_mode='one'
                )[0]

                # Получаем данные за расчетный месяц и предыдущий месяц
                end_month_data = db.execute_query(
                    "SELECT * FROM monthly_data WHERE abonent_id = ? AND month = ? AND year = ?",
                    (self.abonent_id, month, year),
                    fetch_mode='one'
                )

                # Предыдущий месяц (начало периода)
                prev_month = month - 1 if month > 1 else 12
                prev_year = year if month > 1 else year - 1

                start_month_data = db.execute_query(
                    "SELECT * FROM monthly_data WHERE abonent_id = ? AND month = ? AND year = ?",
                    (self.abonent_id, prev_month, prev_year),
                    fetch_mode='one'
                )

                if not end_month_data:
                    self.calculation_result.delete("1.0", "end")
                    self.calculation_result.insert("end", f"Нет данных за расчетный месяц {month}/{year}\n")
                    return

                # Рассчитываем потребление по каждой услуге
                result_text = f"Расчет потребления за {month_name} {year} года\n"
                result_text += f"Абонент: {fulname}\n\n"

                # Электроэнергия
                if len(end_month_data) > 4 and end_month_data[4] is not None:
                    prev_value = float(start_month_data[4]) if start_month_data and len(start_month_data) > 4 and \
                                                               start_month_data[4] is not None else 0.0
                    curr_value = float(end_month_data[4])
                    consumption = curr_value - prev_value
                    result_text += f"Электроэнергия: {consumption:.2f} кВт·ч\n"

                # Вода
                if len(end_month_data) > 5 and end_month_data[5] is not None:
                    prev_value = float(start_month_data[5]) if start_month_data and len(start_month_data) > 5 and \
                                                               start_month_data[5] is not None else 0.0
                    curr_value = float(end_month_data[5])
                    consumption = curr_value - prev_value
                    result_text += f"Вода: {consumption:.2f} м³\n"

                # Сточные воды
                if len(end_month_data) > 6 and end_month_data[6] is not None:
                    prev_value = float(start_month_data[6]) if start_month_data and len(start_month_data) > 6 and \
                                                               start_month_data[6] is not None else 0.0
                    curr_value = float(end_month_data[6])
                    consumption = curr_value - prev_value
                    result_text += f"Сточные воды: {consumption:.2f} м³\n"

                # Газ
                if len(end_month_data) > 7 and end_month_data[7] is not None:
                    prev_value = float(start_month_data[7]) if start_month_data and len(start_month_data) > 7 and \
                                                               start_month_data[7] is not None else 0.0
                    curr_value = float(end_month_data[7])
                    consumption = curr_value - prev_value
                    result_text += f"Газ: {consumption:.2f} м³\n"

                # Выводим результат
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", result_text)

            finally:
                db.close_connection()

        except Exception as e:
            self.calculation_result.delete("1.0", "end")
            self.calculation_result.insert("end", f"Ошибка расчета: {str(e)}\n")

    def generate_registry(self):
        """Генерирует реестр с показаниями и потреблением за расчетный месяц"""
        try:
            # Проверяем, что данные загружены и рассчитаны
            if not self.table.get("1.0", "end-1c") or not self.calculation_result.get("1.0", "end-1c"):
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", "❌ Ошибка: сначала загрузите и рассчитайте данные!\n")
                return

            month_name = self.month_var.get()
            month = self.get_month_number(month_name)
            year = int(self.year_entry.get())

            db = SqliteDB()
            try:
                # Получаем имя абонента
                fulname = db.execute_query(
                    "SELECT fulname FROM abonents WHERE id = ?",
                    (self.abonent_id,),
                    fetch_mode='one'
                )[0]

                # Получаем данные за расчетный месяц и предыдущий месяц
                end_month_data = db.execute_query(
                    "SELECT * FROM monthly_data WHERE abonent_id = ? AND month = ? AND year = ?",
                    (self.abonent_id, month, year),
                    fetch_mode='one'
                )

                prev_month = month - 1 if month > 1 else 12
                prev_year = year if month > 1 else year - 1

                start_month_data = db.execute_query(
                    "SELECT * FROM monthly_data WHERE abonent_id = ? AND month = ? AND year = ?",
                    (self.abonent_id, prev_month, prev_year),
                    fetch_mode='one'
                )

                if not end_month_data:
                    self.calculation_result.delete("1.0", "end")
                    self.calculation_result.insert("end", f"Нет данных за расчетный месяц {month}/{year}\n")
                    return

                # Создаем структуру данных для реестра
                registry_data = {
                    "Услуга": [],
                    "Предыдущие показания": [],
                    "Текущие показания": [],
                    "Потребление": [],
                    "Единица измерения": []
                }

                # Обрабатываем данные для каждой услуги
                # Электроэнергия
                if len(end_month_data) > 4 and end_month_data[4] is not None:
                    prev_value = float(start_month_data[4]) if start_month_data and len(start_month_data) > 4 and \
                                                               start_month_data[4] is not None else 0.0
                    curr_value = float(end_month_data[4])
                    consumption = curr_value - prev_value

                    registry_data["Услуга"].append("Электроэнергия")
                    registry_data["Предыдущие показания"].append(f"{prev_value:.2f}")
                    registry_data["Текущие показания"].append(f"{curr_value:.2f}")
                    registry_data["Потребление"].append(f"{consumption:.2f}")
                    registry_data["Единица измерения"].append("кВт·ч")

                # Вода
                if len(end_month_data) > 5 and end_month_data[5] is not None:
                    prev_value = float(start_month_data[5]) if start_month_data and len(start_month_data) > 5 and \
                                                               start_month_data[5] is not None else 0.0
                    curr_value = float(end_month_data[5])
                    consumption = curr_value - prev_value

                    registry_data["Услуга"].append("Вода")
                    registry_data["Предыдущие показания"].append(f"{prev_value:.2f}")
                    registry_data["Текущие показания"].append(f"{curr_value:.2f}")
                    registry_data["Потребление"].append(f"{consumption:.2f}")
                    registry_data["Единица измерения"].append("м³")

                # Сточные воды
                if len(end_month_data) > 6 and end_month_data[6] is not None:
                    prev_value = float(start_month_data[6]) if start_month_data and len(start_month_data) > 6 and \
                                                               start_month_data[6] is not None else 0.0
                    curr_value = float(end_month_data[6])
                    consumption = curr_value - prev_value

                    registry_data["Услуга"].append("Сточные воды")
                    registry_data["Предыдущие показания"].append(f"{prev_value:.2f}")
                    registry_data["Текущие показания"].append(f"{curr_value:.2f}")
                    registry_data["Потребление"].append(f"{consumption:.2f}")
                    registry_data["Единица измерения"].append("м³")

                # Газ
                if len(end_month_data) > 7 and end_month_data[7] is not None:
                    prev_value = float(start_month_data[7]) if start_month_data and len(start_month_data) > 7 and \
                                                               start_month_data[7] is not None else 0.0
                    curr_value = float(end_month_data[7])
                    consumption = curr_value - prev_value

                    registry_data["Услуга"].append("Газ")
                    registry_data["Предыдущие показания"].append(f"{prev_value:.2f}")
                    registry_data["Текущие показания"].append(f"{curr_value:.2f}")
                    registry_data["Потребление"].append(f"{consumption:.2f}")
                    registry_data["Единица измерения"].append("м³")

                df = pd.DataFrame(registry_data)

                # Создаем папку для реестров
                folder_path = r"C:\Реестры по абонентам"
                os.makedirs(folder_path, exist_ok=True)

                # Формируем название файла
                file_prefix = f"{fulname}_{month_name}_{year}"

                # Сохраняем в Excel
                xls_file_path = os.path.join(folder_path, f"{file_prefix}.xlsx")
                with pd.ExcelWriter(xls_file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Реестр')

                    workbook = writer.book
                    worksheet = writer.sheets['Реестр']

                    # Устанавливаем ширину столбцов
                    worksheet.column_dimensions['A'].width = 20
                    worksheet.column_dimensions['B'].width = 20
                    worksheet.column_dimensions['C'].width = 20
                    worksheet.column_dimensions['D'].width = 15
                    worksheet.column_dimensions['E'].width = 20

                    # Добавляем заголовок
                    worksheet['F1'] = f"Реестр показаний за {month_name} {year} года"
                    worksheet['F2'] = f"Абонент: {fulname}"
                    worksheet['F4'] = "Подписи:"
                    worksheet['F5'] = "Бухгалтер: ____________________"
                    worksheet['F6'] = "Главный инженер: ____________________"
                    worksheet['F7'] = "Абонент: ____________________"

                print(f"✅ Excel-реестр сохранен в {xls_file_path}")

                # Создаем PDF
                pdf_file_path = os.path.join(folder_path, f"{file_prefix}.pdf")
                c = canvas.Canvas(pdf_file_path, pagesize=letter)
                width, height = letter

                # Устанавливаем шрифт с поддержкой кириллицы
                try:
                    from reportlab.pdfbase.ttfonts import TTFont
                    from reportlab.pdfbase import pdfmetrics
                    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                    font_name = 'Arial'
                except:
                    font_name = 'Helvetica'

                # Заголовок
                c.setFont(font_name, 14)
                c.drawString(100, height - 100, f"Реестр показаний за {month_name} {year} года")
                c.setFont(font_name, 12)
                c.drawString(100, height - 120, f"Абонент: {fulname}")

                # Таблица данных
                c.setFont(font_name, 10)
                y = height - 160
                headers = ["Услуга", "Пред.пок.", "Тек.пок.", "Потребление", "Ед.изм."]
                for i, header in enumerate(headers):
                    c.drawString(100 + i * 100, y, header)
                y -= 20

                for index, row in df.iterrows():
                    values = [row["Услуга"], row["Предыдущие показания"],
                              row["Текущие показания"], row["Потребление"],
                              row["Единица измерения"]]
                    for i, value in enumerate(values):
                        c.drawString(100 + i * 100, y, str(value))
                    y -= 15

                    if y < 100:  # Если место заканчивается, создаем новую страницу
                        c.showPage()
                        y = height - 100
                        c.setFont(font_name, 10)

                # Подписи
                c.setFont(font_name, 12)
                c.drawString(100, y - 20, "Подписи:")
                c.drawString(100, y - 40, "Бухгалтер: ____________________")
                c.drawString(100, y - 60, "Главный инженер: ____________________")
                c.drawString(100, y - 80, "Абонент: ____________________")

                c.save()
                print(f"✅ PDF-реестр сохранен в {pdf_file_path}")

                # Сохраняем путь к PDF для последующего открытия
                self.last_pdf_path = pdf_file_path

                # Активируем кнопку открытия PDF
                self.open_pdf_button.configure(state="normal", fg_color="green")

                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end",
                                               f"Реестр успешно создан:\nExcel: {xls_file_path}\nPDF: {pdf_file_path}\n")

                # Добавляем информацию о возможности открыть PDF
                self.calculation_result.insert("end", "\nНажмите кнопку 'Открыть PDF' для просмотра файла.\n")

            except Exception as e:
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", f"Ошибка создания реестра: {str(e)}\n")
                import traceback
                traceback.print_exc()

            finally:
                db.close_connection()

        except Exception as e:
            self.calculation_result.delete("1.0", "end")
            self.calculation_result.insert("end", f"Ошибка: {str(e)}\n")