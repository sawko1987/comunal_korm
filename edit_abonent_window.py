from pprint import pprint
from tkinter import *
import customtkinter as ctk
from CustomTkinterMessagebox import CTkMessagebox
from users_db import SqliteDB


class EditAbonentWindow:
    def __init__(self, parent, width, height, abonent_data, title="Редактирование абонента",
                 resizable=(False, False), icon='image/korm.ico'):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)

        self.abonent_data = abonent_data  # Данные выбранного абонента
        self.abonent_id = abonent_data[0]  # ID абонента

        # Переменные для чекбоксов
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
        self.root.grab_set()
        self.root.focus_set()
        self.root.wait_window()

    def creat_frame(self):
        frame = ctk.CTkFrame(master=self.root, width=100, height=100)
        frame.pack(side=BOTTOM, fill=X, padx=0, pady=50)
        return frame

    def draw_abonent_widget(self):
        ctk.CTkLabel(master=self.root, text="Наименование организации абонента").pack()

        # Поле с текущим именем абонента
        self.name_entry = ctk.CTkEntry(master=self.root, width=250)
        self.name_entry.insert(0, self.abonent_data[1])
        self.name_entry.pack()

        ctk.CTkLabel(master=self.root,
                     text="Измените услуги и показания абонента:").pack()

        # Создаем CheckBox и Entry для каждого параметра
        for var, text, value in self.var_entry:
            # Создаем чекбокс
            ctk.CTkCheckBox(master=self.root, text=text, variable=var, onvalue=1, offvalue=0,
                            command=lambda v=var, t=text, val=value: self.chek_chek_box(v, t, val)).pack(anchor="w")

            # Если значение было, сразу создаем поле ввода
            if var.get():
                self.label = ctk.CTkLabel(master=self.root, text=f'{text}')
                self.label.pack()
                self.labels[text] = self.label

                entry = ctk.CTkEntry(master=self.root, width=250)
                if value is not None:
                    entry.insert(0, str(value))
                entry.pack()
                self.entries[text] = entry

        button_frame = self.creat_frame()
        ctk.CTkButton(button_frame, text="Сохранить", command=self.save_data).pack(side=LEFT, padx=30, pady=5)
        ctk.CTkButton(button_frame, text="Отмена", command=self.root.destroy).pack(side=LEFT, padx=30, pady=5)

    def chek_chek_box(self, var, text, default_value=None):
        if var.get():  # Если CheckBox отмечен
            if text not in self.entries:
                self.label = ctk.CTkLabel(master=self.root, text=f'{text}')
                self.label.pack()
                self.labels[text] = self.label

                entry = ctk.CTkEntry(master=self.root, width=250)
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
            fulname = self.name_entry.get()
            elect_value = self.entries.get("Электроэнергия", None)
            transformation_ratio_value = self.entries.get("Коэффициент трансформации", None)
            water_value = self.entries.get("Вода", None)
            wastewater_value = self.entries.get("Водоотведение", None)
            gaz_value = self.entries.get("Газ", None)

            # Преобразуем значения в числа, если они существуют
            elect_value = float(elect_value.get()) if elect_value and elect_value.get() else None
            transformation_ratio_value = int(
                transformation_ratio_value.get()) if transformation_ratio_value and transformation_ratio_value.get() else None
            water_value = int(water_value.get()) if water_value and water_value.get() else None
            wastewater_value = int(wastewater_value.get()) if wastewater_value and wastewater_value.get() else None
            gaz_value = int(gaz_value.get()) if gaz_value and gaz_value.get() else None

            # Обновляем данные в базе данных
            db = SqliteDB()
            query = """UPDATE abonents 
                      SET fulname = ?, 
                          elect_value = ?, 
                          transformation_ratio_value = ?, 
                          water_value = ?, 
                          wastewater_value = ?, 
                          gaz_value = ?
                      WHERE id = ?"""
            db.execute_query(query, (fulname, elect_value, transformation_ratio_value,
                                     water_value, wastewater_value, gaz_value, self.abonent_id), fetch_mode=None)
            db.close_connection()

            self.root.destroy()
        except Exception as e:
            CTkMessagebox(title="Ошибка", message=f"Ошибка при сохранении данных: {str(e)}", icon="cancel")