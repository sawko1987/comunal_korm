import customtkinter as ctk
from customtkinter import CTkButton
from add_abonent_window import AddAbonentWindow
from add_abonent_window import AddAbonentWindow


class Window (ctk.CTk):
    def __init__(self, width, height, title= "Учет коммунальных услуг АО_Корммаш", resizable=(False,False), icon='image/korm.ico'):
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[0])
        if icon:
            self.root.iconbitmap(icon)


    # метод будет запускать окно
    def run(self):
        self.draw_widget()
        self.root.mainloop()

    # метод запускает дочернее окно
    def create_child_window (self, width, height, title = None, resizable=(False,False), icon= 'image/korm.ico'):
        AddAbonentWindow(self.root, width, height, title = "Добавить абонента")

    # метод будет рисовать виджеты в окне
    def draw_widget(self):
        CTkButton(self.root, width=50,height=15, text= "Добавить абонента", command=self.run_child_window).place(relx= 0.4, rely = 0.4)
    # метод запускает дочернее окно добавление абонента
    def run_child_window(self):
        windows.create_child_window(300, 500)





    #добавление абонента
    def add_abonent(self):
        print('Эта кнопка потом будет добавлять абонента')











if __name__ == "__main__":
    windows = Window(800,600)


    windows.run()













