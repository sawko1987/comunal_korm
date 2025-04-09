import sqlite3
import customtkinter as ctk
from users_db import SqliteDB
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class ConsumptionHistoryWindow:
    def __init__(self, parent, width, height, abonent_id, title="Учет коммунальных услуг АО_Корммаш", resizable=(False, False), icon='image/korm.ico'):
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

        # Кнопка для расчета данных
        self.calc_button = ctk.CTkButton(self.root, text="Рассчитать потребление", command=self.calculate_consumption, state='disabled')
        self.calc_button.pack(pady=10)

        # Кнопка для генерации реестра
        self.generate_registry_button = ctk.CTkButton(self.root, text="Создать реестр", command=self.generate_registry, state='disabled')
        self.generate_registry_button.pack(pady=10)

        # Таблица для отображения данных
        self.table = ctk.CTkTextbox(self.root, width=550, height=200)
        self.table.pack(pady=10)

        # Поле для вывода расчетов
        self.calculation_result = ctk.CTkTextbox(self.root, width=550, height=200)
        self.calculation_result.pack(pady=10)

        self.root.grab_set()
        self.root.focus_set()

        # Устанавливаем фокус на окно
        self.root.grab_set()
        self.root.focus_set()

        # Добавляем placeholder'ы (подсказки)
        self.start_month_entry.insert(0, "1-12")
        self.start_year_entry.insert(0, "2025")
        self.end_month_entry.insert(0, "1-12")
        self.end_year_entry.insert(0, "2025")

        # Меняем цвет кнопки "Рассчитать" (чтобы она выглядела неактивной)
        self.calc_button.configure(fg_color="gray")

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

            print(f"Параметры запроса: abonent_id={self.abonent_id}, период: {start_month}/{start_year}-{end_month}/{end_year}")

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
        """Вычисляет общее потребление ресурсов за указанный период"""
        print("⚡ Запущен calculate_consumption()")  # Отладочный вывод
        try:
            # Проверяем, что все поля заполнены
            if not all([
                self.start_month_entry.get(),
                self.start_year_entry.get(),
                self.end_month_entry.get(),
                self.end_year_entry.get()
            ]):
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", "❌ Ошибка: заполните все поля периода!\n")
                return

            # Проверяем, что данные загружены (если таблица пуста)
            if not self.table.get("1.0", "end-1c"):  # Если текстовое поле пустое
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", "❌ Ошибка: сначала загрузите данные!\n")
                return

            start_month = int(self.start_month_entry.get())
            start_year = int(self.start_year_entry.get())
            end_month = int(self.end_month_entry.get())
            end_year = int(self.end_year_entry.get())

            db = SqliteDB()
            try:
                # Получаем данные за период
                data = db.get_consumption_data(self.abonent_id, start_month, start_year, end_month, end_year)
                print(f"📊 Данные из БД: {data}")  # Что пришло из БД?

                if not data:
                    print("❌ Нет данных для расчёта!")
                    self.calculation_result.delete("1.0", "end")
                    self.calculation_result.insert("end", "Нет данных для расчета\n")
                    return

                # Получаем коэффициент трансформации (если есть)
                transform_coeff = 1.0

                # Рассчитываем суммы по категориям
                total_electricity = 0.0
                total_water = 0.0
                total_wastewater = 0.0
                total_gas = 0.0

                for row in data:
                    if row[4]:  # Электроэнергия
                        total_electricity += float(row[4]) * transform_coeff
                    if row[5]:  # Вода
                        total_water += float(row[5])
                    if row[6]:  # Сточные воды
                        total_wastewater += float(row[6])
                    if len(row) > 7 and row[7]:  # Газ
                        total_gas += float(row[7])

                # Выводим результаты
                print(f"🔢 Результаты: Электричество={total_electricity}, Вода={total_water}")  # Проверяем числа
                self.calculation_result.delete("1.0", "end")
                result_text = (
                    f"Общее потребление за период {start_month}/{start_year}-{end_month}/{end_year}:\n"
                    f"Электроэнергия: {total_electricity:.2f} кВт·ч "
                    f"{'(с учетом коэффициента трансформации)' if transform_coeff != 1.0 else ''}\n"
                    f"Вода: {total_water:.2f} м³\n"
                    f"Сточные воды: {total_wastewater:.2f} м³\n"
                    f"Газ: {total_gas:.2f} м³\n"
                )

                # Очистка и вывод
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", result_text)
                self.calculation_result.see("end")  # Прокрутка к новому тексту
                self.calculation_result.update()  # Принудительное обновление

                print(f"✅ Результат в виджете: {self.calculation_result.get('1.0', 'end-1c')}")

                print("✅ Расчёт завершён и выведен на экран")

            finally:
                db.close_connection()

        except ValueError as ve:
            self.calculation_result.delete("1.0", "end")
            self.calculation_result.insert("end", f"Ошибка ввода: {str(ve)}\n")
        except Exception as e:
            self.calculation_result.delete("1.0", "end")
            self.calculation_result.insert("end", f"Ошибка расчета: {str(e)}\n")

    def generate_registry(self):
        """Генерирует реестр с показаниями и потреблением"""
        try:
            # Проверяем, что данные загружены и рассчитаны
            if not self.table.get("1.0", "end-1c") or not self.calculation_result.get("1.0", "end-1c"):
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", "❌ Ошибка: сначала загрузите и рассчитайте данные!\n")
                return

            start_month = int(self.start_month_entry.get())
            start_year = int(self.start_year_entry.get())
            end_month = int(self.end_month_entry.get())
            end_year = int(self.end_year_entry.get())

            db = SqliteDB()
            try:
                # 1. Проверяем существование таблицы abonents
                table_check = "SELECT name FROM sqlite_master WHERE type='table' AND name='abonents'"
                if not db.execute_query(table_check, fetch_mode='one'):
                    self.calculation_result.delete("1.0", "end")
                    self.calculation_result.insert("end", "Ошибка: таблица abonents не существует\n")
                    return

                # 2. Получаем полное имя абонента с дополнительной проверкой
                fulname_query = "SELECT fulname FROM abonents WHERE id = ?"
                fulname_data = db.execute_query(fulname_query, (self.abonent_id,), fetch_mode='one')

                if not fulname_data:
                    # Проверяем, есть ли вообще какие-либо абоненты в таблице
                    any_abonent_check = "SELECT 1 FROM abonents LIMIT 1"
                    if not db.execute_query(any_abonent_check, fetch_mode='one'):
                        self.calculation_result.delete("1.0", "end")
                        self.calculation_result.insert("end", "Ошибка: таблица abonents пуста\n")
                    else:
                        self.calculation_result.delete("1.0", "end")
                        self.calculation_result.insert("end", f"Ошибка: абонент с ID {self.abonent_id} не найден\n")
                    return

                fulname = fulname_data[0]
                print(f"Получено имя абонента: {fulname}")  # Отладочный вывод

                # Получаем данные за период
                data = db.get_consumption_data(self.abonent_id, start_month, start_year, end_month, end_year)
                print(f"📊 Данные из БД для реестра: {data}")

                if not data:
                    print("❌ Нет данных для создания реестра!")
                    self.calculation_result.delete("1.0", "end")
                    self.calculation_result.insert("end", "Нет данных для создания реестра\n")
                    return

                # Получаем полное имя абонента
                fulname_query = "SELECT fulname FROM abonents WHERE id = ?"
                fulname = db.execute_query(fulname_query, (self.abonent_id,), fetch_mode='one')
                if not fulname:
                    self.calculation_result.delete("1.0", "end")
                    self.calculation_result.insert("end", "Ошибка: не удалось получить имя абонента\n")
                    return

                fulname = fulname[0]

                # Получаем коэффициент трансформации (если есть)
                transform_coeff = 1.0  # Можно получить из БД или настроек

                # Создаем структуру данных для реестра
                registry_data = {
                    "Услуга": [],
                    "Предыдущие показания": [],
                    "Текущие показания": [],
                    "Потребление": [],
                    "Коэффициент трансформации": []
                }

                # Обрабатываем данные для каждой услуги
                for row in data:
                    month_year = f"{row[2]}/{row[3]}"

                    # Электроэнергия
                    if len(row) > 4 and row[4] is not None:
                        prev_value = float(row[8]) if len(row) > 8 and row[8] is not None else 0.0
                        curr_value = float(row[4])
                        consumption = (curr_value - prev_value) * transform_coeff

                        registry_data["Услуга"].append(f"Электроэнергия (кВт·ч) {month_year}")
                        registry_data["Предыдущие показания"].append(prev_value)
                        registry_data["Текущие показания"].append(curr_value)
                        registry_data["Потребление"].append(round(consumption, 2))
                        registry_data["Коэффициент трансформации"].append(transform_coeff)

                    # Вода
                    if len(row) > 5 and row[5] is not None:
                        prev_value = float(row[9]) if len(row) > 9 and row[9] is not None else 0.0
                        curr_value = float(row[5])
                        consumption = curr_value - prev_value

                        registry_data["Услуга"].append(f"Вода (м³) {month_year}")
                        registry_data["Предыдущие показания"].append(prev_value)
                        registry_data["Текущие показания"].append(curr_value)
                        registry_data["Потребление"].append(round(consumption, 2))
                        registry_data["Коэффициент трансформации"].append("")

                    # Сточные воды
                    if len(row) > 6 and row[6] is not None:
                        prev_value = float(row[10]) if len(row) > 10 and row[10] is not None else 0.0
                        curr_value = float(row[6])
                        consumption = curr_value - prev_value

                        registry_data["Услуга"].append(f"Сточные воды (м³) {month_year}")
                        registry_data["Предыдущие показания"].append(prev_value)
                        registry_data["Текущие показания"].append(curr_value)
                        registry_data["Потребление"].append(round(consumption, 2))
                        registry_data["Коэффициент трансформации"].append("")

                    # Газ
                    if len(row) > 7 and row[7] is not None:
                        prev_value = float(row[11]) if len(row) > 11 and row[11] is not None else 0.0
                        curr_value = float(row[7])
                        consumption = curr_value - prev_value

                        registry_data["Услуга"].append(f"Газ (м³) {month_year}")
                        registry_data["Предыдущие показания"].append(prev_value)
                        registry_data["Текущие показания"].append(curr_value)
                        registry_data["Потребление"].append(round(consumption, 2))
                        registry_data["Коэффициент трансформации"].append("")

                df = pd.DataFrame(registry_data)

                # Создаем папку для реестров
                org_name = f"{fulname}"  # Замените на реальное название
                folder_path = r"C:\Реестры по абонентам"
                os.makedirs(folder_path, exist_ok=True)

                # Формируем название файла
                period_str = f"{start_month}_{start_year}-{end_month}_{end_year}"
                file_prefix = f"{org_name}_{period_str}"

                # Сохраняем в Excel
                xls_file_path = os.path.join(folder_path, f"{file_prefix}.xlsx")
                with pd.ExcelWriter(xls_file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Реестр')

                    workbook = writer.book
                    worksheet = writer.sheets['Реестр']

                    # Устанавливаем ширину столбцов
                    worksheet.column_dimensions['A'].width = 30
                    worksheet.column_dimensions['B'].width = 20
                    worksheet.column_dimensions['C'].width = 20
                    worksheet.column_dimensions['D'].width = 15
                    worksheet.column_dimensions['E'].width = 25

                    # Добавляем заголовок
                    worksheet['F1'] = f"Реестр показаний за период {start_month}/{start_year}-{end_month}/{end_year}"
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
                c.drawString(100, height - 100,
                             f"Реестр показаний за период {start_month}/{start_year}-{end_month}/{end_year}")
                c.setFont(font_name, 12)
                c.drawString(100, height - 120, f"Абонент: {fulname}")

                # Таблица данных
                c.setFont(font_name, 10)
                y = height - 160
                c.drawString(100, y, "Услуга")
                c.drawString(250, y, "Пред.пок.")
                c.drawString(350, y, "Тек.пок.")
                c.drawString(450, y, "Потребление")
                c.drawString(550, y, "Коэф.транс.")
                y -= 20

                for index, row in df.iterrows():
                    c.drawString(100, y, str(row["Услуга"]))
                    c.drawString(250, y, str(row["Предыдущие показания"]))
                    c.drawString(350, y, str(row["Текущие показания"]))
                    c.drawString(450, y, str(row["Потребление"]))
                    c.drawString(550, y, str(row["Коэффициент трансформации"]))
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

                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end",
                                               f"Реестр успешно создан:\nExcel: {xls_file_path}\nPDF: {pdf_file_path}\n")
            except sqlite3.Error as e:
                self.calculation_result.delete("1.0", "end")
                self.calculation_result.insert("end", f"Ошибка базы данных: {str(e)}\n")
                import traceback
                traceback.print_exc()

            finally:
                db.close_connection()

        except ValueError as ve:
            self.calculation_result.delete("1.0", "end")
            self.calculation_result.insert("end", f"Ошибка ввода: {str(ve)}\n")
        except Exception as e:
            self.calculation_result.delete("1.0", "end")
            self.calculation_result.insert("end", f"Ошибка создания реестра: {str(e)}\n")
            import traceback
            traceback.print_exc()  # Печатаем полную трассировку ошибки


