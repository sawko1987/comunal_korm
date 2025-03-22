import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter Example")
        self.geometry("800x600")

        # Создание бокового контейнера
        self.sidebar = ctk.CTkFrame(self, width=200, height=600, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        # Создание кнопок для вкладок
        self.tab1_button = ctk.CTkButton(self.sidebar, text="Tab 1", command=self.show_tab1)
        self.tab1_button.pack(pady=10, padx=10)

        self.tab2_button = ctk.CTkButton(self.sidebar, text="Tab 2", command=self.show_tab2)
        self.tab2_button.pack(pady=10, padx=10)

        # Создание фреймов для контента вкладок
        self.tab1_frame = ctk.CTkFrame(self, width=600, height=600, corner_radius=0)
        self.tab2_frame = ctk.CTkFrame(self, width=600, height=600, corner_radius=0)

        # Добавление контента в фреймы
        self.label1 = ctk.CTkLabel(self.tab1_frame, text="This is Tab 1", font=("Arial", 24))
        self.label1.pack(pady=50)

        self.label2 = ctk.CTkLabel(self.tab2_frame, text="This is Tab 2", font=("Arial", 24))
        self.label2.pack(pady=50)

        # Показ первой вкладки по умолчанию
        self.show_tab1()

    def show_tab1(self):
        self.tab2_frame.pack_forget()  # Скрыть вторую вкладку
        self.tab1_frame.pack(side="right", fill="both", expand=True)  # Показать первую вкладку

    def show_tab2(self):
        self.tab1_frame.pack_forget()  # Скрыть первую вкладку
        self.tab2_frame.pack(side="right", fill="both", expand=True)  # Показать вторую вкладку

if __name__ == "__main__":
    app = App()
    app.mainloop()