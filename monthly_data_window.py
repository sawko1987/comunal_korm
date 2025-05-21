from tkinter import *
import tkinter.messagebox as messagebox
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import statistics

import users_db
from users_db import SqliteDB

class EditMonthlyDataWindow:
    def __init__(self, parent, abonent_id, month, year, data, on_save_callback):
        self.root = ctk.CTkToplevel(parent)
        self.root.title("Редактирование показаний")
        self.root.geometry("400x500")
        
        self.abonent_id = abonent_id
        self.month = month
        self.year = year
        self.data = data
        self.on_save_callback = on_save_callback
        
        # Получаем информацию об услугах абонента
        db = SqliteDB()
        self.abonent_data = db.get_abonent_by_id(self.abonent_id)
        db.close_connection()
        
        if not self.abonent_data:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные абонента")
            self.root.destroy()
            return
        
        self.draw_widgets()
        self.grab_focus()
        
    def grab_focus(self):
        self.root.grab_set()
        self.root.focus_set()
        self.root.wait_window()
        
    def draw_widgets(self):
        # Заголовок
        ctk.CTkLabel(self.root, text=f"Редактирование показаний за {self.month}/{self.year}").pack(pady=10)
        
        # Поля для редактирования только выбранных услуг
        self.entries = {}
        
        if self.abonent_data[7]:  # uses_electricity
            self.entries['electricity'] = self.create_entry_field("Электроэнергия", self.data.get('electricity'))
            
        if self.abonent_data[8]:  # uses_water
            self.entries['water'] = self.create_entry_field("Вода", self.data.get('water'))
            
        if self.abonent_data[9]:  # uses_wastewater
            self.entries['wastewater'] = self.create_entry_field("Водоотведение", self.data.get('wastewater'))
            
        if self.abonent_data[10]:  # uses_gas
            self.entries['gas'] = self.create_entry_field("Газ", self.data.get('gas'))
        
        # Кнопки
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(side=BOTTOM, fill=X, padx=20, pady=20)
        
        ctk.CTkButton(button_frame, text="Сохранить", command=self.save_data).pack(side=LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Отмена", command=self.root.destroy).pack(side=RIGHT, padx=10)
        
    def create_entry_field(self, label_text, value):
        frame = ctk.CTkFrame(self.root)
        frame.pack(fill=X, padx=20, pady=5)
        
        ctk.CTkLabel(frame, text=label_text).pack(side=LEFT)
        entry = ctk.CTkEntry(frame)
        if value is not None:
            entry.insert(0, str(value))
        entry.pack(side=RIGHT)
        return entry
        
    def save_data(self):
        try:
            # Получаем значения только для выбранных услуг
            electricity = float(self.entries['electricity'].get()) if 'electricity' in self.entries and self.entries['electricity'].get() else None
            water = float(self.entries['water'].get()) if 'water' in self.entries and self.entries['water'].get() else None
            wastewater = float(self.entries['wastewater'].get()) if 'wastewater' in self.entries and self.entries['wastewater'].get() else None
            gas = float(self.entries['gas'].get()) if 'gas' in self.entries and self.entries['gas'].get() else None
            
            # Обновляем данные в БД
            db = SqliteDB()
            db.update_monthly_data(self.abonent_id, self.month, self.year,
                                 electricity, water, wastewater, gas)
            db.close_connection()
            
            # Вызываем callback для обновления основного окна
            if self.on_save_callback:
                self.on_save_callback()
                
            self.root.destroy()
            messagebox.showinfo("Успех", "Данные успешно обновлены")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные. Убедитесь, что все поля заполнены числами.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")

class SelectMonthWindow:
    def __init__(self, parent, abonent_id, on_select_callback):
        self.root = ctk.CTkToplevel(parent)
        self.root.title("Выбор месяца для редактирования")
        self.root.geometry("400x500")
        
        self.abonent_id = abonent_id
        self.on_select_callback = on_select_callback
        
        self.draw_widgets()
        self.load_data()
        self.grab_focus()
        
    def grab_focus(self):
        self.root.grab_set()
        self.root.focus_set()
        self.root.wait_window()
        
    def draw_widgets(self):
        # Заголовок
        ctk.CTkLabel(self.root, text="Выберите месяц для редактирования").pack(pady=10)
        
        # Создаем фрейм для списка
        self.list_frame = ctk.CTkScrollableFrame(self.root)
        self.list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Кнопка закрытия
        ctk.CTkButton(self.root, text="Закрыть", command=self.root.destroy).pack(pady=10)
        
    def load_data(self):
        try:
            db = SqliteDB()
            data = db.get_all_monthly_data(self.abonent_id)
            db.close_connection()
            
            if not data:
                ctk.CTkLabel(self.list_frame, text="Нет данных для редактирования").pack(pady=10)
                return
                
            # Сортируем данные по году и месяцу (в обратном порядке)
            data.sort(key=lambda x: (x[3], x[2]), reverse=True)
            
            # Создаем кнопки для каждого месяца
            for record in data:
                month, year = record[2], record[3]
                values = {
                    'electricity': record[4],
                    'water': record[5],
                    'wastewater': record[6],
                    'gas': record[7]
                }
                
                button_text = f"{month}/{year}"
                details = []
                if values['electricity'] is not None:
                    details.append(f"Э/э: {values['electricity']}")
                if values['water'] is not None:
                    details.append(f"Вода: {values['water']}")
                if values['wastewater'] is not None:
                    details.append(f"Водоотв.: {values['wastewater']}")
                if values['gas'] is not None:
                    details.append(f"Газ: {values['gas']}")
                
                if details:
                    button_text += f" ({', '.join(details)})"
                
                button = ctk.CTkButton(
                    self.list_frame,
                    text=button_text,
                    command=lambda m=month, y=year, v=values: self.select_month(m, y, v)
                )
                button.pack(fill=X, pady=5)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке данных: {str(e)}")
            
    def select_month(self, month, year, values):
        self.on_select_callback(month, year, values)
        self.root.destroy()

class MonthlyDataWindow:
    def __init__(self, parent, width, height, abonent_id, title="Учет коммунальных услуг АО_Корммаш",
                 resizable=(False, False), icon='image/korm.ico'):
        print("\n=== Инициализация окна ввода показаний ===")
        print(f"ID абонента: {abonent_id}")
        
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)
        self.abonent_id = abonent_id
        
        # Получаем информацию об услугах абонента
        print("\nПолучение данных абонента из БД...")
        db = SqliteDB()
        self.abonent_data = db.get_abonent_by_id(self.abonent_id)
        db.close_connection()
        
        print(f"Полученные данные абонента: {self.abonent_data}")
        
        if not self.abonent_data:
            print("ОШИБКА: Не удалось загрузить данные абонента")
            messagebox.showerror("Ошибка", "Не удалось загрузить данные абонента")
            self.root.destroy()
            return
            
        print("Данные абонента успешно загружены")
        self.montly_widget()
        self.grab_focus()
        print("=== Завершение инициализации окна ввода показаний ===\n")

    def grab_focus(self):
        self.root.grab_set()  # фокус на окнe
        self.root.focus_set()  # фокус на окнe
        self.root.wait_window()  # ждем закрытия окна

    def montly_widget(self):
        print("\n=== Начало создания виджетов для ввода показаний ===")
        # Поля для ввода данных
        input_frame = ctk.CTkScrollableFrame(self.root, height=400)  # Увеличиваем высоту фрейма
        input_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        print("\nДанные абонента:")
        print(f"ID абонента: {self.abonent_id}")
        print(f"Данные из БД: {self.abonent_data}")
        print("\nПроверка услуг абонента:")
        print(f"Электроэнергия: {self.abonent_data[7]}")
        print(f"Вода: {self.abonent_data[8]}")
        print(f"Водоотведение: {self.abonent_data[9]}")
        print(f"Газ: {self.abonent_data[10]}")
        
        # Общие поля (месяц и год)
        print("\nСоздание полей месяца и года")
        month_year_frame = ctk.CTkFrame(input_frame)
        month_year_frame.pack(fill=X, pady=5)
        
        month_frame = ctk.CTkFrame(month_year_frame)
        month_frame.pack(side=LEFT, padx=5, expand=True)
        self.month_label = ctk.CTkLabel(month_frame, text="Месяц:")
        self.month_label.pack(pady=5)
        self.month_entry = ctk.CTkEntry(month_frame)
        self.month_entry.pack(pady=5)

        year_frame = ctk.CTkFrame(month_year_frame)
        year_frame.pack(side=LEFT, padx=5, expand=True)
        self.year_label = ctk.CTkLabel(year_frame, text="Год:")
        self.year_label.pack(pady=5)
        self.year_entry = ctk.CTkEntry(year_frame)
        self.year_entry.pack(pady=5)

        # Разделитель
        separator = ctk.CTkFrame(input_frame, height=2)
        separator.pack(fill=X, pady=10)

        # Поля для услуг в зависимости от настроек абонента
        print("\nСоздание полей для услуг:")
        
        if self.abonent_data[7]:  # uses_electricity
            print("Создание поля для электроэнергии")
            electricity_frame = ctk.CTkFrame(input_frame)
            electricity_frame.pack(fill=X, pady=5)
            self.electricity_label = ctk.CTkLabel(electricity_frame, text="Электроэнергия:")
            self.electricity_label.pack(side=LEFT, padx=5)
            self.electricity_entry = ctk.CTkEntry(electricity_frame)
            self.electricity_entry.pack(side=RIGHT, padx=5)
        else:
            print("Электроэнергия не выбрана")
            self.electricity_entry = None

        if self.abonent_data[8]:  # uses_water
            print("Создание поля для воды")
            water_frame = ctk.CTkFrame(input_frame)
            water_frame.pack(fill=X, pady=5)
            self.water_label = ctk.CTkLabel(water_frame, text="Вода:")
            self.water_label.pack(side=LEFT, padx=5)
            self.water_entry = ctk.CTkEntry(water_frame)
            self.water_entry.pack(side=RIGHT, padx=5)
        else:
            print("Вода не выбрана")
            self.water_entry = None

        if self.abonent_data[9]:  # uses_wastewater
            print("Создание поля для водоотведения")
            wastewater_frame = ctk.CTkFrame(input_frame)
            wastewater_frame.pack(fill=X, pady=5)
            self.wastewater_label = ctk.CTkLabel(wastewater_frame, text="Водоотведение:")
            self.wastewater_label.pack(side=LEFT, padx=5)
            self.wastewater_entry = ctk.CTkEntry(wastewater_frame)
            self.wastewater_entry.pack(side=RIGHT, padx=5)
        else:
            print("Водоотведение не выбрано")
            self.wastewater_entry = None

        if self.abonent_data[10]:  # uses_gas
            print("Создание поля для газа")
            gas_frame = ctk.CTkFrame(input_frame)
            gas_frame.pack(fill=X, pady=5)
            self.gas_label = ctk.CTkLabel(gas_frame, text="Газ:")
            self.gas_label.pack(side=LEFT, padx=5)
            self.gas_entry = ctk.CTkEntry(gas_frame)
            self.gas_entry.pack(side=RIGHT, padx=5)
        else:
            print("Газ не выбран")
            self.gas_entry = None

        print("\nСоздание кнопок")
        # Кнопки
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(side=BOTTOM, fill=X, padx=20, pady=10)
        
        self.save_button = ctk.CTkButton(button_frame, text="Сохранить", command=self.save_data)
        self.save_button.pack(side=LEFT, padx=5)
        
        self.edit_button = ctk.CTkButton(button_frame, text="Редактировать показания", command=self.show_edit_window)
        self.edit_button.pack(side=RIGHT, padx=5)
        
        print("=== Завершение создания виджетов для ввода показаний ===\n")

    def get_average_consumption(self, utility_type):
        """Получает среднее потребление за последние 3 месяца для указанного типа услуги"""
        try:
            db = SqliteDB()
            # Получаем данные за последние 3 месяца
            data = db.get_last_months_consumption(self.abonent_id, utility_type, limit=3)
            db.close_connection()
            
            if not data:
                return None
                
            # Фильтруем None значения и вычисляем среднее
            valid_values = [x for x in data if x is not None]
            if not valid_values:
                return None
                
            return statistics.mean(valid_values)
        except Exception as e:
            print(f"Ошибка при получении среднего потребления: {e}")
            return None

    def check_consumption_difference(self, utility_type, current_value):
        """Проверяет, отличается ли текущее значение от среднего более чем в 10 раз"""
        if current_value is None:
            return True
            
        avg_consumption = self.get_average_consumption(utility_type)
        if avg_consumption is None or avg_consumption == 0:
            return True
            
        ratio = current_value / avg_consumption
        return 0.1 <= ratio <= 10

    def confirm_unusual_value(self, utility_name, current_value, avg_consumption):
        """Запрашивает подтверждение у пользователя при необычном значении"""
        message = (f"Внимание! Введенное значение для {utility_name} ({current_value}) "
                  f"сильно отличается от среднего потребления за последние месяцы ({avg_consumption:.2f}).\n\n"
                  f"Вы уверены, что данные введены правильно?")
        return messagebox.askyesno("Проверка данных", message)

    def check_previous_month_data(self, current_values):
        """Проверяет, что текущие показания не меньше предыдущих"""
        try:
            month = int(self.month_entry.get())
            year = int(self.year_entry.get())
            
            # Вычисляем предыдущий месяц и год
            prev_month = 12 if month == 1 else month - 1
            prev_year = year - 1 if month == 1 else year
            
            db = SqliteDB()
            prev_data = db.get_monthly_data_by_date(self.abonent_id, prev_month, prev_year)
            db.close_connection()
            
            if not prev_data:
                return True  # Нет данных за предыдущий месяц
                
            utilities = [
                ('electricity', 'Электроэнергия'),
                ('water', 'Вода'),
                ('wastewater', 'Водоотведение'),
                ('gas', 'Газ')
            ]
            
            errors = []
            for current_value, (field, name) in zip(current_values, utilities):
                if current_value is not None and prev_data[field] is not None:
                    if current_value < prev_data[field]:
                        errors.append(f"{name}: текущее показание ({current_value}) меньше предыдущего ({prev_data[field]})")
            
            if errors:
                message = "Обнаружены ошибки в показаниях:\n\n" + "\n".join(errors)
                if messagebox.askyesno("Ошибка в показаниях", 
                                     message + "\n\nХотите отредактировать предыдущие показания?"):
                    self.edit_previous_month_data(prev_month, prev_year, prev_data)
                    return False
                return False
            return True
            
        except Exception as e:
            print(f"Ошибка при проверке предыдущих показаний: {e}")
            return True

    def edit_previous_month_data(self, month, year, data):
        """Открывает окно редактирования предыдущих показаний"""
        EditMonthlyDataWindow(self.root, self.abonent_id, month, year, data, self.refresh_data)

    def refresh_data(self):
        """Обновляет данные после редактирования"""
        # Здесь можно добавить обновление отображаемых данных, если необходимо
        pass

    def show_edit_window(self):
        """Открывает окно выбора месяца для редактирования"""
        SelectMonthWindow(self.root, self.abonent_id, self.edit_selected_month)
        
    def edit_selected_month(self, month, year, values):
        """Callback для редактирования выбранного месяца"""
        EditMonthlyDataWindow(self.root, self.abonent_id, month, year, values, self.refresh_data)

    def save_data(self):
        """Сохраняет введенные данные"""
        try:
            # Проверяем обязательные поля
            month = int(self.month_entry.get())
            year = int(self.year_entry.get())
            
            if not (1 <= month <= 12):
                messagebox.showerror("Ошибка", "Месяц должен быть от 1 до 12")
                return
                
            if not (2000 <= year <= 2100):
                messagebox.showerror("Ошибка", "Год должен быть от 2000 до 2100")
                return
            
            # Получаем значения только для выбранных услуг
            electricity = float(self.electricity_entry.get()) if self.electricity_entry else None
            water = float(self.water_entry.get()) if self.water_entry else None
            wastewater = float(self.wastewater_entry.get()) if self.wastewater_entry else None
            gas = float(self.gas_entry.get()) if self.gas_entry else None
            
            # Проверяем введенные значения на необычные отклонения
            if electricity is not None:
                self.check_consumption_difference('electricity', electricity)
            if water is not None:
                self.check_consumption_difference('water', water)
            if wastewater is not None:
                self.check_consumption_difference('wastewater', wastewater)
            if gas is not None:
                self.check_consumption_difference('gas', gas)
            
            # Сохраняем данные
            db = SqliteDB()
            db.insert_monthly_data(self.abonent_id, month, year, electricity, water, wastewater, gas)
            db.close_connection()
            
            messagebox.showinfo("Успех", "Данные успешно сохранены")
            
            # Уничтожаем окно только после успешного сохранения
            self.root.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", "Проверьте правильность введенных данных. Все значения должны быть числами.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")

        
