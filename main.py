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

        # Установим начальное значение и вызовем обработчик
        if self.list_abonent:
            self.combobox.set(self.list_abonent[0][1])
            self.on_combobox_select()

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
        print("Создание дочернего окна")  # Отладочный вывод
        try:
            # Create child window
            child_window = AddAbonentWindow(self.root, width, height, title="Добавить абонента")
            print("Дочернее окно создано")  # Отладочный вывод
            
            # Wait for child window to close
            self.root.wait_window(child_window.root)
            print("Ожидание закрытия дочернего окна завершено")  # Отладочный вывод
            
            # Refresh data after child window closes
            self.refresh_data()
            self.on_combobox_select()
            print("Данные обновлены")  # Отладочный вывод
            
        except Exception as e:
            print(f"Ошибка при создании окна: {e}")
            # Make sure main window is visible in case of error
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def create_monthly_data_window(self, width, height, abonent_id, title=None):
        """Создает окно внесения месячных данных"""
        # Disable main window interactions while child window is open
        self.root.withdraw()
        
        try:
            # Create and wait for child window
            monthly_window = MonthlyDataWindow(self.root, width, height, abonent_id, title=title)
            self.root.wait_window(monthly_window.root)
        finally:
            # Re-enable and show main window
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

    def create_consumption_history_window(self, width, height, abonent_id, title=None):
        """Создает окно истории потребления"""
        # Disable main window interactions while child window is open
        self.root.withdraw()
        
        try:
            # Create and wait for child window
            history_window = ConsumptionHistoryWindow(self.root, width, height, abonent_id, title=title)
            self.root.wait_window(history_window.root)
        finally:
            # Re-enable and show main window
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()

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
        self.combobox.configure(command=self.on_combobox_select_callback)

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
        print("Событие выбора абонента сработало!")  # Отладочный вывод
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                return

            # Очищаем поле перед загрузкой новых данных
            self.selected_abonent_info.delete("1.0", "end")

            # Загружаем свежие данные из БД
            self.list_abonent = self.load_abonents()  # Обновляем список абонентов

            # Находим выбранного абонента
            selected_abonent = next((abonent for abonent in self.list_abonent
                                     if abonent[1] == selected_name), None)

            if not selected_abonent:
                self.selected_abonent_info.insert("1.0", "Абонент не найден")
                return

            # Основная информация об абоненте
            info = (
                f"Название: {selected_abonent[1]}\n\n"
                f"Электроэнергия: {selected_abonent[2] or 'нет данных'}\n"
                f"Коэффициент трансформации: {selected_abonent[3] or 'нет данных'}\n"
                f"Вода: {selected_abonent[4] or 'нет данных'}\n"
                f"Водоотведение: {selected_abonent[5] or 'нет данных'}\n"
                f"Газ: {selected_abonent[6] or 'нет данных'}\n\n"
            )

            # Добавляем информацию о последних месяцах с данными
            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if abonent_id:
                try:
                    last_months_data = self.db.get_last_months_data(abonent_id)
                    if last_months_data:
                        info += "Последние внесенные данные:\n"
                        info += "-" * 30 + "\n"

                        for month_data in last_months_data:
                            month, year, electricity, water, wastewater, gas = month_data
                            info += (
                                    f"Месяц: {self.format_month(month)} {year}\n"
                                    f"Электричество: {electricity or 'нет данных'}\n"
                                    f"Вода: {water or 'нет данных'}\n"
                                    f"Водоотведение: {wastewater or 'нет данных'}\n"
                                    f"Газ: {gas or 'нет данных'}\n"
                                    + "-" * 30 + "\n"
                            )
                    else:
                        info += "Нет данных о потреблении\n"
                except Exception as db_error:
                    print(f"Ошибка при получении данных: {db_error}")
                    info += "Ошибка при загрузке данных\n"

            self.selected_abonent_info.insert("1.0", info)

        except Exception as e:
            print(f"Ошибка при обработке выбора абонента: {e}")
            self.selected_abonent_info.insert("1.0", f"Ошибка: {str(e)}")

    def on_combobox_select_callback(self, choice):
        """Обработчик выбора в комбобоксе"""
        self.on_combobox_select()

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
        self.on_combobox_select()

    def refresh_data(self):
        """Полностью обновляет данные в интерфейсе"""
        try:
            # Обновляем список абонентов
            self.list_abonent = self.load_abonents()

            # Обновляем комбобокс
            if self.list_abonent:
                current_selection = self.combobox.get()
                abonent_names = [abonent[1] for abonent in self.list_abonent]
                self.combobox.configure(values=abonent_names)

                # Восстанавливаем выбор, если абонент еще существует
                if current_selection in abonent_names:
                    self.combobox.set(current_selection)
                else:
                    self.combobox.set(abonent_names[0] if abonent_names else "")

                # Обновляем информацию
                self.on_combobox_select()
            else:
                self.combobox.configure(values=[])
                self.selected_abonent_info.delete("1.0", "end")
                self.selected_abonent_info.insert("1.0", "Нет доступных абонентов")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении данных: {str(e)}")

    def run_monthly_data_window(self):
        """Открывает окно внесения месячных данных"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                messagebox.showwarning("Предупреждение", "Сначала выберите абонента")
                return

            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if abonent_id:
                # Создаем окно (без ожидания закрытия)
                MonthlyDataWindow(self.root, 400, 600, abonent_id)

                # Обновляем данные
                self.refresh_data()
                self.on_combobox_select()
            else:
                messagebox.showerror("Ошибка", "Не удалось определить ID абонента")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при открытии окна данных: {str(e)}")

    def edit_abonent(self):
        """Открывает окно редактирования абонента"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                messagebox.showwarning("Предупреждение", "Не выбран абонент для редактирования")
                return

            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if not abonent_id:
                messagebox.showerror("Ошибка", "Не удалось определить ID абонента")
                return

            abonent_data = self.db.get_abonent_by_id(abonent_id)
            if not abonent_data:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные абонента")
                return

            # Создаем окно редактирования и ждем его закрытия
            edit_window = EditAbonentWindow(self.root, 400, 650, abonent_data)

            # После закрытия окна редактирования:
            self.refresh_data()  # Полностью обновляем данные
            self.combobox.set(selected_name)  # Восстанавливаем выбор абонента
            self.on_combobox_select()  # Обновляем информацию

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при редактировании абонента: {str(e)}")

    def run_consumption_history_window(self):
        """Открывает окно истории потребления"""
        try:
            selected_name = self.combobox.get()
            if not selected_name:
                messagebox.showwarning("Предупреждение", "Сначала выберите абонента")
                return

            abonent_id = self.db.get_abonent_id_by_name(selected_name)
            if abonent_id:
                self.create_consumption_history_window(900, 700, abonent_id)
            else:
                messagebox.showerror("Ошибка", "Не удалось определить ID абонента")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при открытии окна истории: {str(e)}")

    def run(self):
        """Запускает главное окно"""
        try:
            self.root.mainloop()
        finally:
            # Гарантированно закрываем соединение при выходе
            if hasattr(self, 'db') and self.db:
                self.db.close_connection()

    def format_month(self, month_num):
        """Форматирует номер месяца в название"""
        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        return months[month_num - 1] if 1 <= month_num <= 12 else f"Месяц {month_num}"


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
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {str(e)}")