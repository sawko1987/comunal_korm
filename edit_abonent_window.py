from pprint import pprint
from tkinter import *
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter.messagebox as messagebox
from users_db import SqliteDB
from tkinter import BooleanVar


class EditAbonentWindow:
    def __init__(self, parent, width, height, abonent_data, title="Редактирование абонента",
                 resizable=(False, False), icon='image/korm.ico'):
        self.top = ctk.CTkToplevel(parent)
        self.top.title(title)
        self.top.geometry(f"{width}x{height}")
        self.top.resizable(resizable[0], resizable[1])
        if icon:
            self.top.iconbitmap(icon)

        self.abonent_data = abonent_data
        self.abonent_id = abonent_data[0]

        # Инициализация переменных и виджетов
        self.var_elect = BooleanVar(value=abonent_data[2] is not None)
        self.water_var = BooleanVar(value=abonent_data[4] is not None)
        self.wastewater_var = BooleanVar(value=abonent_data[5] is not None)
        self.gaz_var = BooleanVar(value=abonent_data[6] is not None)
        self.transformation_ratio_var = BooleanVar(value=abonent_data[3] is not None)

        self.var_entry = [
            (self.var_elect, "⚡ Электроэнергия", abonent_data[2]),
            (self.transformation_ratio_var, "📊 Коэффициент трансформации", abonent_data[3]),
            (self.water_var, "💧 Вода", abonent_data[4]),
            (self.wastewater_var, "🚰 Водоотведение", abonent_data[5]),
            (self.gaz_var, "🔥 Газ", abonent_data[6]),
        ]

        self.labels = {}
        self.entries = {}
        self.name_entry = None

        # Создаем основной контейнер
        self.main_frame = ctk.CTkScrollableFrame(self.top)
        self.main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        self.draw_abonent_widget()
        self.grab_focus()

    def grab_focus(self):
        self.top.grab_set()
        self.top.focus_set()
        self.top.wait_window()

    def draw_abonent_widget(self):
        # Заголовок
        title_frame = ctk.CTkFrame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        ctk.CTkLabel(title_frame, 
                    text="Редактирование абонента",
                    font=("Roboto", 20, "bold")).pack(pady=10)

        # Фрейм для названия организации
        name_frame = ctk.CTkFrame(self.main_frame)
        name_frame.pack(fill=X, pady=10)
        
        ctk.CTkLabel(name_frame, 
                    text="Наименование организации",
                    font=("Roboto", 14)).pack(pady=5)
        
        self.name_entry = ctk.CTkEntry(name_frame, 
                                     width=300,
                                     height=35,
                                     font=("Roboto", 12))
        self.name_entry.insert(0, self.abonent_data[1])
        self.name_entry.pack(pady=5)

        # Фрейм для услуг
        services_frame = ctk.CTkFrame(self.main_frame)
        services_frame.pack(fill=X, pady=10)
        
        ctk.CTkLabel(services_frame, 
                    text="Услуги и показания",
                    font=("Roboto", 14)).pack(pady=5)

        # Создаем CheckBox и Entry для каждого параметра
        for var, text, value in self.var_entry:
            service_frame = ctk.CTkFrame(services_frame)
            service_frame.pack(fill=X, pady=5)
            
            # Создаем чекбокс
            ctk.CTkCheckBox(service_frame, 
                          text=text,
                          font=("Roboto", 12),
                          variable=var,
                          onvalue=1,
                          offvalue=0,
                          command=lambda v=var, t=text, val=value: self.chek_chek_box(v, t, val)).pack(side=LEFT, padx=5)

            # Если значение было, сразу создаем поле ввода
            if var.get():
                entry = ctk.CTkEntry(service_frame, 
                                   width=200,
                                   height=35,
                                   font=("Roboto", 12))
                if value is not None:
                    entry.insert(0, str(value))
                entry.pack(side=LEFT, padx=5)
                self.entries[text] = entry

        # Фрейм для кнопок
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(side=BOTTOM, fill=X, pady=20)
        
        # Кнопки с современным дизайном
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
                     command=self.top.destroy).pack(side=LEFT, padx=20, pady=5)

    def chek_chek_box(self, var, text, default_value=None):
        if var.get():  # Если CheckBox отмечен
            if text not in self.entries:
                entry = ctk.CTkEntry(self.main_frame, 
                                   width=200,
                                   height=35,
                                   font=("Roboto", 12))
                if default_value is not None:
                    entry.insert(0, str(default_value))
                entry.pack(pady=5)
                self.entries[text] = entry
        else:  # Если CheckBox не отмечен
            if text in self.entries:
                self.entries[text].destroy()
                del self.entries[text]

    def save_data(self):
        """Сохраняет измененные данные абонента"""
        try:
            # Собираем данные из полей ввода
            fulname = self.name_entry.get().strip()
            if not fulname:
                CTkMessagebox(title="Предупреждение", 
                            message="Название организации не может быть пустым",
                            icon="warning")
                return

            # Получаем значения из полей, если они существуют
            def get_entry_value(field_name):
                if field_name in self.entries:
                    value = self.entries[field_name].get().strip()
                    return value if value else None
                return None

            elect_value = get_entry_value("Электроэнергия")
            transformation_ratio_value = get_entry_value("Коэффициент трансформации")
            water_value = get_entry_value("Вода")
            wastewater_value = get_entry_value("Водоотведение")
            gaz_value = get_entry_value("Газ")

            # Преобразуем значения в числа
            try:
                elect_value = float(elect_value) if elect_value is not None else None
                transformation_ratio_value = int(
                    transformation_ratio_value) if transformation_ratio_value is not None else None
                water_value = int(water_value) if water_value is not None else None
                wastewater_value = int(wastewater_value) if wastewater_value is not None else None
                gaz_value = int(gaz_value) if gaz_value is not None else None
            except ValueError as e:
                CTkMessagebox(title="Ошибка", 
                            message=f"Некорректные числовые значения: {str(e)}",
                            icon="cancel")
                return

            # Обновляем данные в базе данных
            db = SqliteDB()
            try:
                if db.update_data(self.abonent_id, fulname, elect_value, transformation_ratio_value,
                                  water_value, wastewater_value, gaz_value):
                    CTkMessagebox(title="Успех", 
                                message="Данные успешно сохранены",
                                icon="check")
                    self.top.destroy()
                else:
                    CTkMessagebox(title="Ошибка", 
                                message="Не удалось сохранить данные",
                                icon="cancel")
            except Exception as db_error:
                CTkMessagebox(title="Ошибка базы данных", 
                            message=f"Ошибка при сохранении: {str(db_error)}",
                            icon="cancel")
            finally:
                db.close_connection()

        except Exception as e:
            CTkMessagebox(title="Ошибка", 
                         message=f"Ошибка при сохранении данных: {str(e)}",
                         icon="cancel")