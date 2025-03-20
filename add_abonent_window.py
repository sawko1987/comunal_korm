
import customtkinter as ctk


class AddAbonentWindow:
    def __init__(self,parent, width, height, title="Учет коммунальных услуг АО_Корммаш", resizable=(False, False),
                 icon='image/korm.ico'):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        if icon:
            self.root.iconbitmap(icon)
        self.draw_abonent_widget()
        self.grab_focus()





    # метод который создает фокус на дочернем окне
    def grab_focus(self):
        self.root.grab_set() # фокус на окнe
        self.root.focus_set() # фокус на окнe
        self.root.wait_window() # ждем закрытия окна

    def draw_abonent_widget(self):
        ctk.CTkLabel(master=self.root, text="Введите наименование организации абонента").pack()
        ctk.CTkEntry(master=self.root, width=250).pack()






