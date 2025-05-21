from tkinter import *
import tkinter.messagebox as messagebox
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import statistics
from datetime import datetime
import users_db
from users_db import SqliteDB

class EditMonthlyDataWindow:
    def __init__(self, parent, abonent_id, month, year, data, on_save_callback):
        self.root = ctk.CTkToplevel(parent)
        self.root.title("Редактирование показаний")
        self.root.geometry("500x600")
        
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
            CTkMessagebox(title="Ошибка", 
                         message="Не удалось загрузить данные абонента",
                         icon="cancel")
            self.root.destroy()
            return
        
        # Создаем основной контейнер
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        self.draw_widgets()
        self.grab_focus()
        
    def grab_focus(self):
        self.root.grab_set()
        self.root.focus_set()
        self.root.wait_window()
        
    def draw_widgets(self):
        # Заголовок
        title_frame = ctk.CTkFrame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        ctk.CTkLabel(title_frame, 
                    text=f"Редактирование показаний за {self.month}/{self.year}",
                    font=("Roboto", 20, "bold")).pack(pady=10)
        
        # Поля для редактирования только выбранных услуг
        self.entries = {}
        
        if self.abonent_data[7]:  # uses_electricity
            self.entries['electricity'] = self.create_entry_field("⚡ Электроэнергия", self.data.get('electricity'))
            
        if self.abonent_data[8]:  # uses_water
            self.entries['water'] = self.create_entry_field("💧 Вода", self.data.get('water'))
            
        if self.abonent_data[9]:  # uses_wastewater
            self.entries['wastewater'] = self.create_entry_field("🚰 Водоотведение", self.data.get('wastewater'))
            
        if self.abonent_data[10]:  # uses_gas
            self.entries['gas'] = self.create_entry_field("🔥 Газ", self.data.get('gas'))
        
        # Кнопки
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(side=BOTTOM, fill=X, pady=20)
        
        ctk.CTkButton(button_frame, 
                     text="💾 Сохранить",
                     font=("Roboto", 12),
                     height=40,
                     command=self.save_data).pack(side=LEFT, padx=20, pady=5)
        
        ctk.CTkButton(button_frame, 
                     text="❌ Отмена",
                     font=("Roboto", 12),
                     height=40,
                     fg_color="transparent",
                     border_width=2,
                     command=self.root.destroy).pack(side=LEFT, padx=20, pady=5)
        
    def create_entry_field(self, label_text, value):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill=X, pady=10)
        
        ctk.CTkLabel(frame, 
                    text=label_text,
                    font=("Roboto", 14)).pack(side=LEFT, padx=10)
        
        entry = ctk.CTkEntry(frame,
                           width=200,
                           height=35,
                           font=("Roboto", 12))
        if value is not None:
            entry.insert(0, str(value))
        entry.pack(side=RIGHT, padx=10)
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
            CTkMessagebox(title="Успех", 
                         message="Данные успешно обновлены",
                         icon="check")
            
        except ValueError:
            CTkMessagebox(title="Ошибка", 
                         message="Некорректные данные. Убедитесь, что все поля заполнены числами.",
                         icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Ошибка", 
                         message=f"Ошибка при сохранении данных: {str(e)}",
                         icon="cancel")

class SelectMonthWindow:
    def __init__(self, parent, abonent_id, on_select_callback):
        self.root = ctk.CTkToplevel(parent)
        self.root.title("Выбор месяца для редактирования")
        self.root.geometry("500x600")
        
        self.abonent_id = abonent_id
        self.on_select_callback = on_select_callback
        
        # Создаем основной контейнер
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        self.draw_widgets()
        self.load_data()
        self.grab_focus()
        
    def grab_focus(self):
        self.root.grab_set()
        self.root.focus_set()
        self.root.wait_window()
        
    def draw_widgets(self):
        # Заголовок
        title_frame = ctk.CTkFrame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        ctk.CTkLabel(title_frame, 
                    text="Выберите месяц для редактирования",
                    font=("Roboto", 20, "bold")).pack(pady=10)
        
        # Создаем фрейм для списка
        self.list_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.list_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Кнопка закрытия
        ctk.CTkButton(self.main_frame, 
                     text="❌ Закрыть",
                     font=("Roboto", 12),
                     height=40,
                     fg_color="transparent",
                     border_width=2,
                     command=self.root.destroy).pack(pady=10)
        
    def load_data(self):
        try:
            db = SqliteDB()
            data = db.get_all_monthly_data(self.abonent_id)
            db.close_connection()
            
            if not data:
                ctk.CTkLabel(self.list_frame, 
                           text="Нет данных для редактирования",
                           font=("Roboto", 12)).pack(pady=10)
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
                
                button_text = f"📅 {month}/{year}"
                details = []
                if values['electricity'] is not None:
                    details.append(f"⚡ {values['electricity']}")
                if values['water'] is not None:
                    details.append(f"💧 {values['water']}")
                if values['wastewater'] is not None:
                    details.append(f"🚰 {values['wastewater']}")
                if values['gas'] is not None:
                    details.append(f"🔥 {values['gas']}")
                
                if details:
                    button_text += f" ({', '.join(details)})"
                
                button = ctk.CTkButton(
                    self.list_frame,
                    text=button_text,
                    font=("Roboto", 12),
                    height=40,
                    command=lambda m=month, y=year, v=values: self.select_month(m, y, v)
                )
                button.pack(fill=X, pady=5, padx=10)
                
        except Exception as e:
            CTkMessagebox(title="Ошибка", 
                         message=f"Ошибка при загрузке данных: {str(e)}",
                         icon="cancel")
            
    def select_month(self, month, year, values):
        self.on_select_callback(month, year, values)
        self.root.destroy()

class MonthlyDataWindow:
    def __init__(self, parent, width, height, abonent_id, title="Учет коммунальных услуг АО_Корммаш",
                 resizable=(False, False), icon='image/korm.ico'):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)
        self.abonent_id = abonent_id
        
        # Получаем информацию об услугах абонента
        db = SqliteDB()
        self.abonent_data = db.get_abonent_by_id(self.abonent_id)
        db.close_connection()
        
        if not self.abonent_data:
            messagebox.showerror("Ошибка", "Не удалось загрузить данные абонента")
            self.root.destroy()
            return
            
        # Создаем основной контейнер
        self.main_frame = ctk.CTkScrollableFrame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        self.montly_widget()
        self.grab_focus()

    def grab_focus(self):
        self.root.grab_set()
        self.root.focus_set()
        self.root.wait_window()

    def montly_widget(self):
        # Заголовок
        title_frame = ctk.CTkFrame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        ctk.CTkLabel(title_frame, 
                    text="Ввод показаний",
                    font=("Roboto", 20, "bold")).pack(pady=10)
        
        # Общие поля (месяц и год)
        month_year_frame = ctk.CTkFrame(self.main_frame)
        month_year_frame.pack(fill=X, pady=10)
        
        month_frame = ctk.CTkFrame(month_year_frame)
        month_frame.pack(side=LEFT, padx=5, expand=True)
        self.month_label = ctk.CTkLabel(month_frame, 
                                      text="📅 Месяц:",
                                      font=("Roboto", 14))
        self.month_label.pack(pady=5)
        self.month_entry = ctk.CTkEntry(month_frame,
                                      width=100,
                                      height=35,
                                      font=("Roboto", 12))
        self.month_entry.pack(pady=5)

        year_frame = ctk.CTkFrame(month_year_frame)
        year_frame.pack(side=LEFT, padx=5, expand=True)
        self.year_label = ctk.CTkLabel(year_frame, 
                                     text="📅 Год:",
                                     font=("Roboto", 14))
        self.year_label.pack(pady=5)
        self.year_entry = ctk.CTkEntry(year_frame,
                                     width=100,
                                     height=35,
                                     font=("Roboto", 12))
        self.year_entry.pack(pady=5)

        # Поля для ввода показаний
        self.entries = {}
        
        if self.abonent_data[7]:  # uses_electricity
            self.entries['electricity'] = self.create_entry_field("⚡ Электроэнергия")
            
        if self.abonent_data[8]:  # uses_water
            self.entries['water'] = self.create_entry_field("💧 Вода")
            
        if self.abonent_data[9]:  # uses_wastewater
            self.entries['wastewater'] = self.create_entry_field("🚰 Водоотведение")
            
        if self.abonent_data[10]:  # uses_gas
            self.entries['gas'] = self.create_entry_field("🔥 Газ")

        # Кнопки
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(side=BOTTOM, fill=X, pady=20)
        
        ctk.CTkButton(button_frame, 
                     text="💾 Сохранить",
                     font=("Roboto", 12),
                     height=40,
                     command=self.save_data).pack(side=LEFT, padx=20, pady=5)
        
        ctk.CTkButton(button_frame, 
                     text="📝 Редактировать",
                     font=("Roboto", 12),
                     height=40,
                     command=self.show_edit_window).pack(side=LEFT, padx=20, pady=5)
        
        ctk.CTkButton(button_frame, 
                     text="❌ Отмена",
                     font=("Roboto", 12),
                     height=40,
                     fg_color="transparent",
                     border_width=2,
                     command=self.root.destroy).pack(side=LEFT, padx=20, pady=5)

    def create_entry_field(self, label_text):
        frame = ctk.CTkFrame(self.main_frame)
        frame.pack(fill=X, pady=10)
        
        ctk.CTkLabel(frame, 
                    text=label_text,
                    font=("Roboto", 14)).pack(side=LEFT, padx=10)
        
        entry = ctk.CTkEntry(frame,
                           width=200,
                           height=35,
                           font=("Roboto", 12))
        entry.pack(side=RIGHT, padx=10)
        return entry

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
                CTkMessagebox(title="Ошибка", 
                            message="Месяц должен быть от 1 до 12",
                            icon="cancel")
                return
                
            if not (2000 <= year <= 2100):
                CTkMessagebox(title="Ошибка", 
                            message="Год должен быть от 2000 до 2100",
                            icon="cancel")
                return
            
            # Получаем значения только для выбранных услуг
            electricity = float(self.entries['electricity'].get()) if 'electricity' in self.entries else None
            water = float(self.entries['water'].get()) if 'water' in self.entries else None
            wastewater = float(self.entries['wastewater'].get()) if 'wastewater' in self.entries else None
            gas = float(self.entries['gas'].get()) if 'gas' in self.entries else None
            
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
            
            CTkMessagebox(title="Успех", 
                         message="Данные успешно сохранены",
                         icon="check")
            
            # Уничтожаем окно только после успешного сохранения
            self.root.destroy()
            
        except ValueError as e:
            CTkMessagebox(title="Ошибка", 
                         message="Проверьте правильность введенных данных. Все значения должны быть числами.",
                         icon="cancel")
        except Exception as e:
            CTkMessagebox(title="Ошибка", 
                         message=f"Ошибка при сохранении данных: {str(e)}",
                         icon="cancel")

        
