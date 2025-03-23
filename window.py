import customtkinter as ctk
from customtkinter import CTkButton
from add_abonent_window import AddAbonentWindow
from add_abonent_window import AddAbonentWindow, SqliteDB


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

    # метод будет рисовать виджеты  и кнопки в основном окне
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


        CTkButton(tab1, width=50,height=15, text= "Добавить абонента", command=self.run_child_window).pack()

        # ComboBox для выбора абонента
        ctk.CTkLabel(master=tab1, text="Выберите абонента:").pack(pady=10)
        self.combobox = ctk.CTkComboBox(master=tab1, width=250)
        self.combobox.pack()

        # Инициализация поля для отображения данных выбранного абонента
        self.selected_abonent_info = ctk.CTkLabel(master=self.root, text="")
        self.selected_abonent_info.pack()

        # Заполнение ComboBox данными
        self.update_combobox()
        # Привязка события выбора абонента
        self.combobox.configure(command=self.on_combobox_select)







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
            # Создаем список для хранения непустых данных
            abonent_info_parts = []

            # Добавляем название (оно всегда есть)
            abonent_info_parts.append(f"Название: {selected_abonent[1]}\n")

            # Добавляем остальные данные, если они не None
            if selected_abonent[2] is not None:
                abonent_info_parts.append(f"Электроэнергия: {selected_abonent[2]}\n")
            if selected_abonent[3] is not None:
                abonent_info_parts.append(f"Коэффициент трансформации: {selected_abonent[3]}")
            if selected_abonent[4] is not None:
                abonent_info_parts.append(f"Вода: {selected_abonent[4]}\n")
            if selected_abonent[5] is not None:
                abonent_info_parts.append(f"Водоотведение: {selected_abonent[5]}\n")
            if selected_abonent[6] is not None:
                abonent_info_parts.append(f"Газ: {selected_abonent[6]}\n")

            # Объединяем все части в одну строку
            abonent_info = "".join(abonent_info_parts)
            self.selected_abonent_info.configure(text=abonent_info)
        else:
            self.selected_abonent_info.configure(text="Данные не найдены")

    # метод запускает дочернее окно добавление абонента
    def run_child_window(self):
        windows.create_child_window(450, 650)

    # метод будет запускать основное окно
    def run(self):
        self.draw_widget()
        self.root.mainloop()



if __name__ == "__main__":
    windows = Window(800,600)
    SqliteDB().create_table_abonent()
    windows.run()














