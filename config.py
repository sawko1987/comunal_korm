import customtkinter as ctk

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Пример с вертикальными вкладками")
        self.root.geometry("600x400")
        self.draw_widgets()

    def draw_widgets(self):
        # Главный контейнер
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Контейнер для вкладок (вертикальный)
        tab_frame = ctk.CTkFrame(main_frame, width=150)
        tab_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)

        # Контейнер для контента
        self.content_frame = ctk.CTkFrame(main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Создание вкладок
        self.create_tab(tab_frame, "Абоненты", self.show_tab1)
        self.create_tab(tab_frame, "Вкладка 2", self.show_tab2)
        self.create_tab(tab_frame, "Вкладка 3", self.show_tab3)

        # Показываем первую вкладку по умолчанию
        self.show_tab1()

    def create_tab(self, parent, text, command):
        # Создание кнопки для вкладки
        button = ctk.CTkButton(parent, text=text, command=command)
        button.pack(fill="x", pady=5)

    def show_tab1(self):
        # Очистка контента
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Добавление контента для вкладки "Абоненты"
        lb1 = ctk.CTkLabel(self.content_frame, text="Это вкладка 'Абоненты'")
        lb1.pack(padx=20, pady=20)

        btn = ctk.CTkButton(self.content_frame, text="Добавить абонента", command=self.run_child_window)
        btn.pack(pady=10)

    def show_tab2(self):
        # Очистка контента
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Добавление контента для вкладки 2
        lb2 = ctk.CTkLabel(self.content_frame, text="Это вкладка 2")
        lb2.pack(padx=20, pady=20)

    def show_tab3(self):
        # Очистка контента
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Добавление контента для вкладки 3
        lb3 = ctk.CTkLabel(self.content_frame, text="Это вкладка 3")
        lb3.pack(padx=20, pady=20)

    def run_child_window(self):
        # Пример функции для открытия дочернего окна
        child_window = ctk.CTkToplevel(self.root)
        child_window.title("Дочернее окно")
        child_window.geometry("300x200")
        label = ctk.CTkLabel(child_window, text="Это дочернее окно")
        label.pack(padx=20, pady=20)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()