import customtkinter as ctk

from add_abonent_window import AddAbonentWindow, SqliteDB
from users_db import SqliteDB
from monthly_data_window import MonthlyDataWindow
from HistoryWindow import ConsumptionHistoryWindow



class Window (ctk.CTk):
    def __init__(self, width, height, title= "Учет коммунальных услуг АО_Корммаш", resizable=(False,False), icon='image/korm.ico'):
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[0])
        if icon:
            self.root.iconbitmap(icon)

        db = SqliteDB()
        self.list_abonent = db.fetch_data()
        db.close_connection()



    # метод запускает дочернее окно
    def create_child_window (self, width, height, title = None, resizable=(False,False), icon= 'image/korm.ico'):
        AddAbonentWindow(self.root, width, height, title = "Добавить абонента")
        self.refresh_data()

    # метод запускает дочернее окно
    def create_monthly_data_window(self, width, height, abonent_id, title = None, resizable=(False, False),
                                   icon='image/korm.ico'):
        MonthlyDataWindow(self.root, width, height, abonent_id, title=title)

    def create_consumption_history_window(self, width, height, abonent_id, title = None, resizable=(False, False),
                                          icon= 'image/korm.ico'):
        ConsumptionHistoryWindow(self.root, width, height, abonent_id, title = "История потребления")

    # метод будет рисовать виджеты и кнопки в основном окне
    def draw_widget(self):
        # Создание контейнера с вкладками
        self.tab_control = ctk.CTkTabview(self.root, width=150)
        self.tab_control.pack(side='left',fill='y', padx=(0,10), pady=10)

        # Добавление вкладок
        self.tab_control.add("Абоненты")  # Вкладка 1
        self.tab_control.add("Вкладка 2")  # Вкладка 2
        self.tab_control.add("Вкладка 3")  # Вкладка 3

        # Получаем фреймы для каждой вкладки
        tab1 = self.tab_control.tab("Абоненты")
        tab2 = self.tab_control.tab("Вкладка 2")
        tab3 = self.tab_control.tab("Вкладка 3")

        # Добавляем элементы на первую вкладку
        lb1 = ctk.CTkLabel(tab1, text="Вкладка 'Абоненты'")
        lb1.pack(padx=20, pady=20)


        # Добавляем элементы на вторую вкладку
        lb2 = ctk.CTkLabel(tab2, text="Это вкладка 2")
        lb2.pack(padx=20, pady=20)
        # Добавляем элементы на вторую вкладку
        lb3 = ctk.CTkLabel(tab3, text="Это вкладка 3")
        lb3.pack(padx=20, pady=20)


        ctk.CTkButton(tab1, width=50,height=15, text= "Добавить абонента", command=self.run_child_window).pack()

        # ComboBox для выбора абонента
        ctk.CTkLabel(master=tab1, text="Выберите абонента:").pack(pady=10)
        self.combobox = ctk.CTkComboBox(master=tab1, width=250)
        self.combobox.pack()

        # Инициализация поля для отображения данных выбранного абонента
        self.selected_abonent_info = ctk.CTkLabel(master=self.root, text="", width= 150, height= 150, anchor = 'w', font=("Arial", 16))
        self.selected_abonent_info.pack()

        # Заполнение ComboBox данными
        self.update_combobox()
        # Привязка события выбора абонента
        self.combobox.configure(command=self.on_combobox_select)



        ctk.CTkButton(tab1, width=50, height=15, text="Удалить абонента", command=self.delete_abonent).pack(pady=20)
        ctk.CTkButton(tab1,width=50, height=15, text="Редактировать абонента").pack(pady=20)

        # Добавление новых кнопок
        ctk.CTkButton(tab1, width=50, height=15, text="Внести показания", command=self.run_monthly_data_window).pack(
            pady=10)
        ctk.CTkButton(tab1, width=50, height=15, text="История потребления",
                      command=self.run_consumption_history_window).pack(pady=10)

    def update_combobox(self):
        # Извлекаем названия организаций из list_abonent
        abonent_names = [abonent[1] for abonent in self.list_abonent]  # Индекс 1 - это название организации
        self.combobox.configure(values=abonent_names)  # Заполняем ComboBox
        if abonent_names:  # Если есть данные, выбираем первый элемент по умолчанию
            self.combobox.set(abonent_names[0])
            self.on_combobox_select(abonent_names[0])  # Обновляем данные для первого абонента

    def on_combobox_select(self, choice):
        # Находим выбранного абонента в list_abonent
        selected_abonent = None
        for abonent in self.list_abonent:
            if abonent[1] == choice:  # Сравниваем по названию организации
                selected_abonent = abonent
                break

        # Отображаем данные выбранного абонента
        if selected_abonent:
            abonent_info_parts = [f"Название: {selected_abonent[1]}\n \n"]
            if selected_abonent[2] is not None:
                abonent_info_parts.append(f"Электроэнергия:----- {selected_abonent[2]}\n")
            if selected_abonent[3] is not None:
                abonent_info_parts.append(f"Коэффициент трансформации:------ {selected_abonent[3]}\n")
            if selected_abonent[4] is not None:
                abonent_info_parts.append(f"Вода:------ {selected_abonent[4]}\n")
            if selected_abonent[5] is not None:
                abonent_info_parts.append(f"Водоотведение:----- {selected_abonent[5]}\n")
            if selected_abonent[6] is not None:
                abonent_info_parts.append(f"Газ:----- {selected_abonent[6]}\n")

            abonent_info = "".join(abonent_info_parts)
            self.selected_abonent_info.configure(text=abonent_info)
        else:
            self.selected_abonent_info.configure(text="Данные не найдены")

    def delete_abonent(self):
        # Получаем выбранное название абонента из ComboBox
        selected_fulname = self.combobox.get()

        if selected_fulname:
            # Подключаемся к базе данных
            db = SqliteDB()

            # Удаляем абонента из базы данных
            db.delete_data(selected_fulname)

            # Закрываем соединение с базой данных
            db.close_connection()

            # Обновляем список абонентов
            db = SqliteDB()
            self.list_abonent = db.fetch_data()
            db.close_connection()

            # Обновляем ComboBox
            self.update_combobox()

            # Очищаем поле с информацией об абоненте
            self.selected_abonent_info.configure(text="")

            # Уведомляем пользователя
            print(f"Абонент '{selected_fulname}' удален.")
        else:
            print("Не выбран абонент для удаления.")

    def refresh_data(self):
        db = SqliteDB()
        self.list_abonent = db.fetch_data()  # Обновляем список абонентов
        db.close_connection()
        self.update_combobox()  # Обновляем ComboBox



        # Метод для открытия окна внесения показаний

    def run_monthly_data_window(self):
        selected_abonent_name = self.combobox.get()
        if selected_abonent_name:
            db = SqliteDB()
            abonent_id = db.get_abonent_id_by_name(selected_abonent_name)
            db.close_connection()
            self.create_monthly_data_window(400, 600, abonent_id, title="Внесение данных за месяц")

        # Метод для открытия окна истории потребления

    def run_consumption_history_window(self):
        selected_abonent_name = self.combobox.get()
        if selected_abonent_name:
            db = SqliteDB()
            abonent_id = db.get_abonent_id_by_name(selected_abonent_name)
            db.close_connection()
            self.create_consumption_history_window(900, 1200, abonent_id)

    # метод запускает дочернее окно добавление абонента
    def run_child_window(self):
        windows.create_child_window(400, 650)








    # метод будет запускать основное окно
    def run(self):
        self.draw_widget()
        self.root.mainloop()



if __name__ == "__main__":
    windows = Window(800,600)
    SqliteDB().create_table_abonent()
    windows.run()














