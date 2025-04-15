import os
from edit_abonent_window import EditAbonentWindow
import customtkinter as ctk
import tkinter.messagebox as messagebox

from HistoryWindow import ConsumptionHistoryWindow
from add_abonent_window import AddAbonentWindow
from monthly_data_window import MonthlyDataWindow
from users_db import SqliteDB



class Window:
    def __init__(self, width, height, title="Учет коммунальных услуг АО_Корммаш",
                 resizable=(False, False), icon='image/korm.ico'):
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])

        # Проверяем существование файла иконки
        if icon and os.path.exists(icon):
            self.root.iconbitmap(icon)
        elif icon:
            print(f"Предупреждение: файл иконки '{icon}' не найден")

        # Инициализация базы данных
        self.db = SqliteDB()
        # Загружаем данные абонентов
        self.list_abonent = self.load_abonents()

        # Основные элементы интерфейса
        self.tab_control = None
        self.combobox = None
        self.selected_abonent_info = None

        # Инициализация интерфейса
        self.draw_widget()

    def load_abonents(self):
        """Загружает список абонентов из базы данных"""
        try:
            abonents = self.db.fetch_data()
            print(f"Загружено абонентов: {len(abonents)}")
            return abonents
        except Exception as e:
            print(f"Ошибка при загрузке абонентов: {e}")
            return []

    def create_child_window(self, width, height, title=None):
        """Создает окно добавления абонента"""
        AddAbonentWindow(self.root, width, height, title="Добавить абонента")
        self.refresh_data()

    def create_monthly_data_window(self, width, height, abonent_id, title=None):
        """Создает окно внесения месячных данных"""
        MonthlyDataWindow(self.root, width, height, abonent_id, title=title)

    def create_consumption_history_window(self, width, height, abonent_id, title=None):
        """Создает окно истории потребления"""
        ConsumptionHistoryWindow(self.root, width, height, abonent_id, title=title)

    def draw_widget(self):
        """Создает элементы интерфейса"""
        # Создание контейнера с вкладками
        self.tab_control = ctk.CTkTabview(self.root, width=150)
        self.tab_control.pack(side='left', fill='y', padx=(0, 10), pady=10)

        # Добавление вкладок
        self.tab_control.add("Абоненты")
        self.tab_control.add("Отчеты")
        self.tab_control.add("Настройки")

        # Получаем фреймы для каждой вкладки
        tab1 = self.tab_control.tab("Абоненты")
        tab2 = self.tab_control.tab("Отчеты")
        tab3 = self.tab_control.tab("Настройки")

        # Вкладка "Абоненты"
        ctk.CTkLabel(tab1, text="Управление абонентами").pack(pady=10)

        # Кнопки управления абонентами
        ctk.CTkButton(tab1, text="Добавить абонента",
                      command=lambda: self.create_child_window(400, 650)).pack(pady=5)
        ctk.CTkButton(tab1, text="Удалить абонента",
                      command=self.delete_abonent).pack(pady=5)
        # В методе draw_widget замените строку с кнопкой:

        ctk.CTkButton(tab1, text="Редактировать абонента", command=self.edit_abonent).pack(pady=5)

        # Выбор абонента
        ctk.CTkLabel(tab1, text="Выберите абонента:").pack(pady=5)
        self.combobox = ctk.CTkComboBox(tab1, width=250)
        self.combobox.pack()
        self.combobox.bind("<<ComboboxSelected>>", lambda e: self.on_combobox_select())

        # Кнопки работы с данными
        ctk.CTkButton(tab1, text="Внести показания",
                      command=self.run_monthly_data_window).pack(pady=10)
        ctk.CTkButton(tab1, text="История потребления",
                      command=self.run_consumption_history_window).pack(pady=10)

        # Поле для отображения информации об абоненте
        self.selected_abonent_info = ctk.CTkTextbox(self.root, width=400, height=200,
                                                    font=("Arial", 14), wrap="word")
        self.selected_abonent_info.pack(pady=20, padx=20, fill="both", expand=True)

        # Обновляем данные в интерфейсе
        self.update_combobox()

    def update_combobox(self):
        """Обновляет список абонентов в выпадающем меню"""
        try:
            # Обновляем список абонентов
            self.list_abonent = self.load_abonents()

            if not self.list_abonent:
                print("Список абонентов пуст")
                self.combobox.configure(values=[])
                self.selected_abonent_info.delete("1.0", "end")
                return

            abonent_names = [abonent[1] for abonent in self.list_abonent]
            self.combobox.configure(values=abonent_names)

            if abonent_names:
                self.combobox.set(abonent_names[0])
                self.on_combobox_select()
        except Exception as e:
            print(f"Ошибка при обновлении combobox: {e}")

    def on_combobox_select(self, event=None):
        """Обрабатывает выбор абонента из списка"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                return

            selected_abonent = next((abonent for abonent in self.list_abonent
                                     if abonent[1] == selected_name), None)

            if selected_abonent:
                info = (
                    f"Название: {selected_abonent[1]}\n\n"
                    f"Электроэнергия: {selected_abonent[2] or 'нет данных'}\n"
                    f"Коэффициент трансформации: {selected_abonent[3] or 'нет данных'}\n"
                    f"Вода: {selected_abonent[4] or 'нет данных'}\n"
                    f"Водоотведение: {selected_abonent[5] or 'нет данных'}\n"
                    f"Газ: {selected_abonent[6] or 'нет данных'}"
                )
                self.selected_abonent_info.delete("1.0", "end")
                self.selected_abonent_info.insert("1.0", info)
        except Exception as e:
            print(f"Ошибка при обработке выбора абонента: {e}")

    def delete_abonent(self):
        """Удаляет выбранного абонента"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                messagebox.showwarning("Предупреждение", "Не выбран абонент для удаления")
                return

            confirm = messagebox.askyesno(
                "Подтверждение",
                f"Вы уверены, что хотите удалить абонента '{selected_name}'?"
            )

            if confirm:
                self.db.delete_data(selected_name)
                self.refresh_data()
                messagebox.showinfo("Успех", f"Абонент '{selected_name}' удален")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении абонента: {str(e)}")

    def refresh_data(self):
        """Обновляет данные в интерфейсе"""
        try:
            self.list_abonent = self.load_abonents()
            self.update_combobox()
            self.selected_abonent_info.delete("1.0", "end")
        except Exception as e:
            print(f"Ошибка при обновлении данных: {e}")

    def run_monthly_data_window(self):
        """Открывает окно внесения месячных данных"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                ctk.CTkMessageBox.showwarning("Предупреждение", "Сначала выберите абонента")
                return

            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if abonent_id:
                self.create_monthly_data_window(400, 600, abonent_id)
            else:
                ctk.CTkMessageBox.showerror("Ошибка", "Не удалось определить ID абонента")
        except Exception as e:
            ctk.CTkMessageBox.showerror("Ошибка", f"Ошибка при открытии окна данных: {str(e)}")

    def edit_abonent(self):
        """Открывает окно редактирования абонента"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                import tkinter.messagebox as mb
                mb.showwarning("Предупреждение", "Не выбран абонент для редактирования")
                return

            # Получаем ID и данные выбранного абонента
            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if not abonent_id:
                import tkinter.messagebox as mb
                mb.showerror("Ошибка", "Не удалось определить ID абонента")
                return

            abonent_data = self.db.get_abonent_by_id(abonent_id)
            if not abonent_data:
                import tkinter.messagebox as mb
                mb.showerror("Ошибка", "Не удалось загрузить данные абонента")
                return

            # Создаем окно редактирования
            EditAbonentWindow(self.root, 400, 650, abonent_data)

            # Обновляем данные после закрытия окна редактирования
            self.refresh_data()
        except Exception as e:
            import tkinter.messagebox as mb
            mb.showerror("Ошибка", f"Ошибка при редактировании абонента: {str(e)}")

    def run_consumption_history_window(self):
        """Открывает окно истории потребления"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                ctk.CTkMessageBox.showwarning("Предупреждение", "Сначала выберите абонента")
                return

            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if abonent_id:
                self.create_consumption_history_window(900, 700, abonent_id)
            else:
                ctk.CTkMessageBox.showerror("Ошибка", "Не удалось определить ID абонента")
        except Exception as e:
            ctk.CTkMessageBox.showerror("Ошибка", f"Ошибка при открытии окна истории: {str(e)}")

    def run(self):
        """Запускает главное окно"""
        try:
            self.root.mainloop()
        finally:
            # Гарантированно закрываем соединение при выходе
            if hasattr(self, 'db') and self.db:
                self.db.close_connection()


if __name__ == "__main__":
    try:
        # Проверяем и создаем структуру базы данных
        db = SqliteDB()
        db.create_table_abonent()
        db.create_table_monthly_data()
        db.close_connection()

        # Запускаем приложение
        app = Window(800, 600)
        app.run()
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        ctk.CTkMessageBox.showerror("Ошибка", f"Не удалось запустить приложение: {str(e)}")