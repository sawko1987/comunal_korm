import customtkinter as ctk
import messagebox

import users_db
from users_db import SqliteDB




# Изменение: Добавление нового класса MonthlyDataWindow
class MonthlyDataWindow:

    def __init__(self,parent, width, height,abonent_id, title= "Учет коммунальных услуг АО_Корммаш", resizable=(False,False),
                 icon='image/korm.ico', ):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)
        self.abonent_id = abonent_id

        self.montly_widget()



        self.grab_focus()


    def grab_focus(self):
        self.root.grab_set()  # фокус на окнe
        self.root.focus_set()  # фокус на окнe
        self.root.wait_window()  # ждем закрытия окна


    def montly_widget(self):
        # Поля для ввода данных
        self.month_label = ctk.CTkLabel(self.root, text="Месяц:")
        self.month_label.pack(pady=5)
        self.month_entry = ctk.CTkEntry(self.root)
        self.month_entry.pack(pady=5)

        self.year_label = ctk.CTkLabel(self.root, text="Год:")
        self.year_label.pack(pady=5)
        self.year_entry = ctk.CTkEntry(self.root)
        self.year_entry.pack(pady=5)

        self.electricity_label = ctk.CTkLabel(self.root, text="Электроэнергия:")
        self.electricity_label.pack(pady=5)
        self.electricity_entry = ctk.CTkEntry(self.root)
        self.electricity_entry.pack(pady=5)

        self.water_label = ctk.CTkLabel(self.root, text="Вода:")
        self.water_label.pack(pady=5)
        self.water_entry = ctk.CTkEntry(self.root)
        self.water_entry.pack(pady=5)

        self.wastewater_label = ctk.CTkLabel(self.root, text="Вотоотведение:")
        self.wastewater_label.pack(pady=5)
        self.wastewater_entry = ctk.CTkEntry(self.root)
        self.wastewater_entry.pack(pady=5)


        self.gas_label = ctk.CTkLabel(self.root, text="Газ:")
        self.gas_label.pack(pady=5)
        self.gas_entry = ctk.CTkEntry(self.root)
        self.gas_entry.pack(pady=5)

        # Кнопка сохранения
        self.save_button = ctk.CTkButton(self.root, text="Сохранить", command=self.save_data)
        self.save_button.pack(pady=20)

    # Метод для сохранения данных
    def save_data(self):
        try:
            # Проверка обязательных полей
            month = self.month_entry.get()
            year = self.year_entry.get()

            if not month or not year:
                messagebox.showerror("Ошибка", "Поля 'Месяц' и 'Год' обязательны для заполнения")
                return

            month = int(self.month_entry.get())
            year = int(self.year_entry.get())
            electricity = float(self.electricity_entry.get()) if self.electricity_entry.get() else None
            water = float(self.water_entry.get()) if self.water_entry.get() else None
            wastewater = float(self.wastewater_entry.get()) if self.wastewater_entry.get() else None
            gas = float(self.gas_entry.get()) if self.gas_entry.get() else None

            db = SqliteDB()
            db.insert_monthly_data(self.abonent_id, month, year, electricity, water,wastewater, gas)
            db.close_connection()
            self.root.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные. Убедитесь, что все поля заполнены числами.")
            return

        
