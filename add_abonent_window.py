from tkinter import *
import customtkinter as ctk
import sqlite3
from sqlite3 import Error
from CustomTkinterMessagebox import CTkMessagebox



class AddAbonentWindow:
    def __init__(self,parent, width, height, title="Учет коммунальных услуг АО_Корммаш", resizable=(False, False),
                 icon='image/korm.ico'):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)

        self.var_elect = BooleanVar(value=0)
        self.water_var = BooleanVar(value=0)
        self.wastewater_var = BooleanVar(value=0)
        self.gaz_var = BooleanVar(value=0)
        self.transformation_ratio_var = BooleanVar(value=0)

        self.var_entry = [
            (self.var_elect, "Электроэнергия"),
            (self.transformation_ratio_var, "Коэффициент трансформации"),
            (self.water_var, "Вода"),
            (self.wastewater_var, "Водоотведение"),
            (self.gaz_var, "Газ"),
                    ]
        self.labels = {}
        self.entries = {}
        self.name_entry = None

        self.draw_abonent_widget()
        self.grab_focus()


    # метод, который создает фокус на дочернем окне
    def grab_focus(self):
        self.root.grab_set() # фокус на окнe
        self.root.focus_set() # фокус на окнe
        self.root.wait_window() # ждем закрытия окна


    def creat_frame(self):
        frame = ctk.CTkFrame(master=self.root, width=100, height=100)
        frame.pack(side=BOTTOM, fill=X, padx=0, pady=50)
        return frame


    def draw_abonent_widget(self):
        ctk.CTkLabel(master=self.root, text="Введите наименование организации абонента").pack()
        self.name_entry =  ctk.CTkEntry(master=self.root, width=250)
        self.name_entry.pack()
        ctk.CTkLabel(master=self.root, text="Выберите услуги которыми пользуется абонент \nи внесите первоначальные показания:").pack()




        # Создаем CheckBox и связываем их с переменными
        for var, text in self.var_entry:
            ctk.CTkCheckBox(master=self.root, text=text, variable=var, onvalue=1, offvalue=0,
                            command=lambda v=var, t=text: self.chek_chek_box(v, t)).pack(anchor= "w")

        button_frame = self.creat_frame()

        button_save = ctk.CTkButton(button_frame, text="Сохранить", command=self.save_data).pack(side=LEFT, padx=5, pady=5)
        button_cancel = ctk.CTkButton(button_frame, text="Отмена").pack(side=LEFT, padx=5, pady=5)
        button_edit = ctk.CTkButton(button_frame, text="Редактировать").pack(side=RIGHT, padx=5, pady=5)

    def chek_chek_box(self, var, text):

        if var.get():  # Если CheckBox отмечен
            if text not in self.entries:

                self.label = ctk.CTkLabel(master=self.root, text=f'{text}')
                self.label.pack()
                self.labels[text] = self.label
                    # Если entry для этого CheckBox еще не создан
                entry = ctk.CTkEntry(master=self.root, width=250)
                entry.pack()
                self.entries[text] = entry  # Сохраняем entry в словаре
        else:  # Если CheckBox не отмечен
            if text in self.entries:  # Если entry для этого CheckBox существует
                self.entries[text].destroy()  # Удаляем entry
                del self.entries[text]  # Удаляем запись из словаря
                if text in self.labels:
                    self.labels[text].destroy()
                    del self.labels[text]

    def save_data(self): # Собираем данные из полей ввода
        fulname = self.name_entry.get()
        elect_value = self.entries.get("Электроэнергия", None)
        transformation_ratio_value = self.entries.get("Коэффициент трансформации", None)
        water_value = self.entries.get("Вода", None)
        wastewater_value = self.entries.get("Водоотведение", None)
        gaz_value = self.entries.get("Газ", None)

        # Преобразуем значения в числа, если они существуют
        elect_value = float(elect_value.get()) if elect_value else None
        transformation_ratio_value = int(transformation_ratio_value.get()) if transformation_ratio_value else None
        water_value = int(water_value.get()) if water_value else None
        wastewater_value = int(wastewater_value.get()) if wastewater_value else None
        gaz_value = int(gaz_value.get()) if gaz_value else None

        # Сохраняем данные в базу данных
        db = SqliteDB()
        db.create_table_abonent()
        db.insert_data((fulname, elect_value, transformation_ratio_value, water_value, wastewater_value, gaz_value))
        db.close_connection()

        # Закрываем окно после сохранения

        CTkMessagebox.messagebox(title='Уведомление!', text='Данные успешно сохранены', sound='on',
                                 button_text='OK')

        self.root.destroy()

class SqliteDB:
    def __init__(self):
        self.conn = sqlite3.connect('abonent.db')
        print("База данных успешно открыта.")
        self.cursor = self.conn.cursor()


    def create_table_abonent(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS abonents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fulname TEXT NOT NULL,
        elect_value INTEGER,
        transformation_ratio_value INTEGER,
        water_value INTEGER,
        wastewater_value INTEGER,
        gaz_value INTEGER)''')


    def insert_data(self, data):
        self.cursor.execute(
            'INSERT INTO abonents  (fulname, elect_value, transformation_ratio_value,water_value,wastewater_value,gaz_value) '
            'VALUES (?, ?, ?, ?, ?,?)', data)
        self.conn.commit() #сохраняем изменения


    def fetch_data(self):
        pass

    def update_data(self, data):
        pass

    def delete_data(self, id):
        pass

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто.")
















