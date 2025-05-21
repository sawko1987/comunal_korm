from pprint import pprint
from tkinter import *
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox



import tkinter.messagebox as messagebox
import customtkinter as ctk
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
            (self.var_elect, "Электроэнергия", abonent_data[2]),
            (self.transformation_ratio_var, "Коэффициент трансформации", abonent_data[3]),
            (self.water_var, "Вода", abonent_data[4]),
            (self.wastewater_var, "Водоотведение", abonent_data[5]),
            (self.gaz_var, "Газ", abonent_data[6]),
        ]

        self.labels = {}
        self.entries = {}
        self.name_entry = None

        self.draw_abonent_widget()
        self.grab_focus()



    def grab_focus(self):
        self.top.grab_set()
        self.top.focus_set()
        self.top.wait_window()

    def creat_frame(self):
        frame = ctk.CTkFrame(master=self.top, width=100, height=100)
        frame.pack(side=BOTTOM, fill=X, padx=0, pady=50)
        return frame

    def draw_abonent_widget(self):
        ctk.CTkLabel(master=self.top, text="Наименование организации абонента").pack()

        # Поле с текущим именем абонента
        self.name_entry = ctk.CTkEntry(master=self.top, width=250)
        self.name_entry.insert(0, self.abonent_data[1])
        self.name_entry.pack()

        ctk.CTkLabel(master=self.top,
                     text="Измените услуги и показания абонента:").pack()

        # Создаем CheckBox и Entry для каждого параметра
        for var, text, value in self.var_entry:
            # Создаем чекбокс
            ctk.CTkCheckBox(master=self.top, text=text, variable=var, onvalue=1, offvalue=0,
                            command=lambda v=var, t=text, val=value: self.chek_chek_box(v, t, val)).pack(anchor="w")

            # Если значение было, сразу создаем поле ввода
            if var.get():
                self.label = ctk.CTkLabel(master=self.top, text=f'{text}')
                self.label.pack()
                self.labels[text] = self.label

                entry = ctk.CTkEntry(master=self.top, width=250)
                if value is not None:
                    entry.insert(0, str(value))
                entry.pack()
                self.entries[text] = entry

        button_frame = self.creat_frame()
        ctk.CTkButton(button_frame, text="Сохранить", command=self.save_data).pack(side=LEFT, padx=30, pady=5)
        ctk.CTkButton(button_frame, text="Отмена", command=self.top.destroy).pack(side=LEFT, padx=30, pady=5)

    def chek_chek_box(self, var, text, default_value=None):
        if var.get():  # Если CheckBox отмечен
            if text not in self.entries:
                self.label = ctk.CTkLabel(master=self.top, text=f'{text}')
                self.label.pack()
                self.labels[text] = self.label

                entry = ctk.CTkEntry(master=self.top, width=250)
                if default_value is not None:
                    entry.insert(0, str(default_value))
                entry.pack()
                self.entries[text] = entry
        else:  # Если CheckBox не отмечен
            if text in self.entries:
                self.entries[text].destroy()
                del self.entries[text]
                if text in self.labels:
                    self.labels[text].destroy()
                    del self.labels[text]

    def save_data(self):
        """Сохраняет измененные данные абонента"""
        try:
            # Собираем данные из полей ввода
            fulname = self.name_entry.get().strip()
            if not fulname:
                messagebox.showwarning("Предупреждение", "Название организации не может быть пустым")
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
                messagebox.showerror("Ошибка", f"Некорректные числовые значения: {str(e)}")
                return

            # Обновляем данные в базе данных
            db = SqliteDB()
            try:
                if db.update_data(self.abonent_id, fulname, elect_value, transformation_ratio_value,
                                  water_value, wastewater_value, gaz_value):
                    messagebox.showinfo("Успех", "Данные успешно сохранены")
                    self.top.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить данные")
            except Exception as db_error:
                messagebox.showerror("Ошибка базы данных", f"Ошибка при сохранении: {str(db_error)}")
            finally:
                db.close_connection()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {str(e)}")