from pprint import pprint
from tkinter import *
import customtkinter as ctk
#import sqlite
from sqlite3 import Error
from CTkMessagebox import CTkMessagebox
from users_db import SqliteDB


class AddAbonentWindow:

    def __init__(self, parent, width, height, title="Учет коммунальных услуг АО_Корммаш", resizable=(True, True),
                 icon='image/korm.ico'):
        print("Инициализация AddAbonentWindow")  # Отладочный вывод
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height+100}+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")  # Увеличиваем высоту окна
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)

        # Ensure this window stays on top and modal
        self.root.transient(parent)
        self.root.grab_set()
        print("Установлен grab_set()")  # Отладочный вывод
        
        # Create main frame with increased height
        self.main_frame = ctk.CTkScrollableFrame(self.root, height=height)  # Устанавливаем высоту скроллируемого фрейма
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)  # Увеличиваем отступы

        # Переменные для чекбоксов услуг
        self.uses_electricity = BooleanVar(value=False)
        self.uses_water = BooleanVar(value=False)
        self.uses_wastewater = BooleanVar(value=False)
        self.uses_gas = BooleanVar(value=False)
        self.has_transformation_ratio = BooleanVar(value=False)

        # Словарь для хранения полей ввода
        self.entries = {}
        self.labels = {}
        self.name_entry = None
        
        # Флаг, указывающий, активно ли окно
        self.is_active = True
        self.parent = parent

        # Draw widgets
        self.draw_abonent_widget()
        print("Виджеты отрисованы")  # Отладочный вывод
        
        # Set initial focus to name entry
        self.name_entry.focus_set()
        
        # Настройка обработчиков событий
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Destroy>', self.on_destroy)
        print("Обработчики событий установлены")  # Отладочный вывод

    def on_destroy(self, event):
        """Обработчик уничтожения окна"""
        print(f"on_destroy вызван для {event.widget}")  # Отладочный вывод
        if event.widget == self.root:
            print("Окно уничтожается")  # Отладочный вывод
            self.is_active = False
            try:
                self.root.grab_release()
                print("grab_release выполнен")  # Отладочный вывод
            except Exception as e:
                print(f"Ошибка при grab_release: {e}")  # Отладочный вывод

    def on_closing(self):
        """Обработчик закрытия окна"""
        print("on_closing вызван")  # Отладочный вывод
        if not self.is_active:
            print("Окно уже не активно")  # Отладочный вывод
            return
            
        self.is_active = False
        try:
            self.root.grab_release()
            print("grab_release выполнен")  # Отладочный вывод
        except Exception as e:
            print(f"Ошибка при grab_release: {e}")  # Отладочный вывод
            
        self.root.destroy()
        print("Окно уничтожено")  # Отладочный вывод
        
        # Восстанавливаем родительское окно
        if self.parent:
            self.parent.deiconify()
            self.parent.lift()
            self.parent.focus_force()
            print("Родительское окно восстановлено")  # Отладочный вывод

    def grab_focus(self):
        """Safely grab and manage window focus"""
        if not self.is_active:
            return
            
        try:
            # Ensure parent is updated
            self.parent.update_idletasks()
            
            # Try to grab focus
            self.root.grab_set()
            
            # Make sure window is on top
            self.root.lift()
            
            # Wait for window
            self.root.wait_window()
        except Exception as e:
            print(f"Ошибка при установке фокуса: {e}")
            # If focus grab fails, try to proceed normally
            self.root.wait_window()

    def create_frame(self):
        frame = ctk.CTkFrame(master=self.root, width=100, height=100)
        frame.pack(side=BOTTOM, fill=X, padx=10, pady=10)
        return frame

    def draw_abonent_widget(self):
        # Фрейм для названия организации
        name_frame = ctk.CTkFrame(self.main_frame)
        name_frame.pack(fill=X, pady=5)
        
        ctk.CTkLabel(name_frame, text="Введите наименование организации абонента").pack(pady=5)
        self.name_entry = ctk.CTkEntry(name_frame, width=250)
        self.name_entry.pack(pady=5)
        
        # Фрейм для выбора услуг
        services_label_frame = ctk.CTkFrame(self.main_frame)
        services_label_frame.pack(fill=X, pady=5)
        
        ctk.CTkLabel(services_label_frame, 
                    text="Выберите услуги, которыми пользуется абонент:").pack(pady=5)

        # Фрейм для чекбоксов услуг
        services_frame = ctk.CTkFrame(self.main_frame)
        services_frame.pack(fill=X, pady=5)

        # Чекбоксы для выбора услуг
        ctk.CTkCheckBox(services_frame, text="Электроэнергия", 
                       variable=self.uses_electricity,
                       command=lambda: self.toggle_service_entry("electricity")).pack(anchor=W, pady=2)
        
        ctk.CTkCheckBox(services_frame, text="Коэффициент трансформации", 
                       variable=self.has_transformation_ratio,
                       command=lambda: self.toggle_service_entry("transformation_ratio")).pack(anchor=W, pady=2)
        
        ctk.CTkCheckBox(services_frame, text="Вода", 
                       variable=self.uses_water,
                       command=lambda: self.toggle_service_entry("water")).pack(anchor=W, pady=2)
        
        ctk.CTkCheckBox(services_frame, text="Водоотведение", 
                       variable=self.uses_wastewater,
                       command=lambda: self.toggle_service_entry("wastewater")).pack(anchor=W, pady=2)
        
        ctk.CTkCheckBox(services_frame, text="Газ", 
                       variable=self.uses_gas,
                       command=lambda: self.toggle_service_entry("gas")).pack(anchor=W, pady=2)

        # Фрейм для полей ввода начальных показаний
        values_label_frame = ctk.CTkFrame(self.main_frame)
        values_label_frame.pack(fill=X, pady=5)
        
        ctk.CTkLabel(values_label_frame, text="Начальные показания:").pack(pady=5)

        self.values_frame = ctk.CTkFrame(self.main_frame)
        self.values_frame.pack(fill=X, pady=5)

        # Фрейм для кнопок
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(side=BOTTOM, fill=X, pady=10)
        
        ctk.CTkButton(button_frame, text="Сохранить", command=self.save_data).pack(side=LEFT, padx=30, pady=5)
        ctk.CTkButton(button_frame, text="Отмена", command=self.on_closing).pack(side=LEFT, padx=30, pady=5)

    def toggle_service_entry(self, service_type):
        """Показывает или скрывает поле ввода для выбранной услуги"""
        if not self.is_active:
            return

        service_labels = {
            "electricity": "Электроэнергия",
            "transformation_ratio": "Коэффициент трансформации",
            "water": "Вода",
            "wastewater": "Водоотведение",
            "gas": "Газ"
        }
        
        try:
            if service_type in self.entries:
                # Удаляем существующие поля
                if service_type in self.labels:
                    self.labels[service_type].destroy()
                    del self.labels[service_type]
                self.entries[service_type].destroy()
                del self.entries[service_type]
            else:
                # Создаем новые поля
                label = ctk.CTkLabel(self.values_frame, text=service_labels[service_type])
                label.pack(pady=2)
                self.labels[service_type] = label
                
                entry = ctk.CTkEntry(self.values_frame, width=250)
                entry.pack(pady=2)
                self.entries[service_type] = entry
        except Exception as e:
            print(f"Ошибка при переключении поля ввода: {e}")

    def get_entry_value(self, key, value_type=float):
        """Безопасное получение значения из поля ввода"""
        try:
            if not self.is_active or key not in self.entries:
                return None
                
            value = self.entries[key].get().strip()
            if not value:
                return None
                
            # Заменяем запятую на точку для корректной обработки чисел
            if value_type == float:
                value = value.replace(',', '.')
                
            return value_type(value)
        except ValueError:
            raise ValueError(f"Неверный формат данных в поле '{key}'. Ожидается число.")
        except Exception as e:
            print(f"Ошибка при получении значения поля: {e}")
            return None

    def save_data(self):
        if not self.is_active:
            return

        try:
            # Получаем название организации
            fulname = self.name_entry.get()
            if not fulname:
                CTkMessagebox(title="Ошибка", 
                            message="Введите название организации")
                return

            # Безопасное получение значений из полей ввода
            elect_value = self.get_entry_value("electricity") if self.uses_electricity.get() else None
            transformation_ratio = self.get_entry_value("transformation_ratio", int) if self.has_transformation_ratio.get() else None
            water_value = self.get_entry_value("water") if self.uses_water.get() else None
            wastewater_value = self.get_entry_value("wastewater") if self.uses_wastewater.get() else None
            gas_value = self.get_entry_value("gas") if self.uses_gas.get() else None

            # Получаем значения чекбоксов
            uses_electricity = self.uses_electricity.get()
            uses_water = self.uses_water.get()
            uses_wastewater = self.uses_wastewater.get()
            uses_gas = self.uses_gas.get()

            print("\n=== Сохранение данных абонента ===")
            print(f"Название: {fulname}")
            print(f"Электроэнергия: {elect_value} (использует: {uses_electricity})")
            print(f"Коэффициент трансформации: {transformation_ratio}")
            print(f"Вода: {water_value} (использует: {uses_water})")
            print(f"Водоотведение: {wastewater_value} (использует: {uses_wastewater})")
            print(f"Газ: {gas_value} (использует: {uses_gas})")

            # Проверяем, что хотя бы одна услуга выбрана
            if not any([uses_electricity, uses_water, uses_wastewater, uses_gas]):
                CTkMessagebox(title="Ошибка",
                            message="Выберите хотя бы одну услугу")
                return

            # Сохраняем данные в базу
            db = SqliteDB()
            db.create_table_abonent()
            data = (
                fulname,
                elect_value,
                transformation_ratio,
                water_value,
                wastewater_value,
                gas_value,
                uses_electricity,
                uses_water,
                uses_wastewater,
                uses_gas
            )
            print("\nДанные для сохранения:", data)
            db.insert_data(data)
            db.close_connection()

            CTkMessagebox(title="Успех", 
                         message="Данные успешно сохранены")
            self.on_closing()

        except ValueError as e:
            CTkMessagebox(title="Ошибка", 
                         message=f"Ошибка в введенных данных: {str(e)}")
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            CTkMessagebox(title="Ошибка", 
                         message=f"Произошла ошибка при сохранении данных: {str(e)}")





