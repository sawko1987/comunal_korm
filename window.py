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

    # метод запускает дочернее окно
    def create_child_window (self, width, height, title = None, resizable=(False,False), icon= 'image/korm.ico'):
        AddAbonentWindow(self.root, width, height, title = "Добавить абонента")

    # метод будет рисовать виджеты  и кнопки в основном окне
    def draw_widget(self):
        # Создание контейнера с вкладками
        self.tab_control = ctk.CTkTabview(self.root)
        self.tab_control.pack(padx=20, pady=20,fill="both", expand=True)

        # Добавление вкладок
        self.tab_control.add("Абоненты")  # Вкладка 1
        self.tab_control.add("Вкладка 2")  # Вкладка 2
        self.tab_control.add("Вкладка 3")  # Вкладка 3

        # Получаем фреймы для каждой вкладки
        tab1 = self.tab_control.tab("Абоненты")
        tab2 = self.tab_control.tab("Вкладка 2")
        tab3 = self.tab_control.tab("Вкладка 3")

        # Добавляем элементы на первую вкладку
        lb1 = ctk.CTkLabel(tab1, text="Это вкладка 'Абоненты'")
        lb1.pack(padx=20, pady=20)
        # Добавляем элементы на вторую вкладку
        lb2 = ctk.CTkLabel(tab2, text="Это вкладка 2")
        lb2.pack(padx=20, pady=20)
        # Добавляем элементы на вторую вкладку
        lb3 = ctk.CTkLabel(tab3, text="Это вкладка 3")
        lb3.pack(padx=20, pady=20)


        CTkButton(tab1, width=50,height=15, text= "Добавить абонента", command=self.run_child_window).pack()


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














