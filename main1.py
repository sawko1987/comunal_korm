

import customtkinter as ctk
from database import create_connection


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_subscriber = None

        # Настройки окна
        self.title("Учёт коммунальных услуг АО 'Корммаш' v0.1")
        self.geometry("10000x700")
        self.minsize(800, 600)

        # Конфигурация сетки
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Стилизация
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # Создание виджетов
        self.create_widgets()

        # Загрузка данных
        self.load_subscribers()
        self.load_subscribers_combobox()

    def create_widgets(self):
        """Создаём основные элементы интерфейса"""
        # Вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.add("Абоненты")  # Вкладка 1
        self.tabview.add("Показания")  # Вкладка 2
        self.tabview.add("Реестры")  # Вкладка 3
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Вызов методов для наполнения вкладок
        self.setup_readings_tab()
        self.setup_subscribers_tab()
        self.setup_reports_tab()

    def setup_subscribers_tab(self):
        """Вкладка для работы с абонентами"""
        tab = self.tabview.tab("Абоненты")

        # Поля ввода
        self.name_entry = ctk.CTkEntry(tab, placeholder_text="ФИО абонента")
        self.name_entry.pack(pady=10)

        # Чекбоксы услуг
        self.electric_var = ctk.BooleanVar()
        self.gas_var = ctk.BooleanVar()
        self.water_var = ctk.BooleanVar()

        self.electric_cb = ctk.CTkCheckBox(tab, text="Электричество", variable=self.electric_var)
        self.gas_cb = ctk.CTkCheckBox(tab, text="Газ", variable=self.gas_var)
        self.water_cb = ctk.CTkCheckBox(tab, text="Вода", variable=self.water_var)

        for cb in [self.electric_cb, self.gas_cb, self.water_cb]:
            cb.pack(pady=5, anchor="w")

        # Кнопка добавления
        self.add_btn = ctk.CTkButton(tab, text="Добавить абонента", command=self.add_subscriber)
        self.add_btn.pack(pady=20)

        # Список абонентов
        self.subscribers_listbox = ctk.CTkTextbox(tab, state="disabled")
        self.subscribers_listbox.pack(fill="both", expand=True, padx=20, pady=10)

    def add_subscriber(self):
        """Добавление абонента в БД"""
        name = self.name_entry.get().strip()
        if not name:
            self.show_error("Введите ФИО абонента!")
            return

        # Получаем значения чекбоксов
        electricity = self.electric_var.get()
        gas = self.gas_var.get()
        water = self.water_var.get()

        # Сохранение в БД
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO subscribers (full_name, electricity, gas, water)
                    VALUES (?, ?, ?, ?)
                ''', (name, electricity, gas, water))
                conn.commit()
                self.clear_fields()
                self.load_subscribers()
                self.load_subscribers_combobox()
            except Exception as e:
                self.show_error(f"Ошибка БД: {str(e)}")
            finally:
                conn.close()

    def load_subscribers(self):
        """Загрузка списка абонентов из БД"""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, full_name FROM subscribers")
                rows = cursor.fetchall()

                # Формируем текст для отображения
                text = "Список абонентов:\n\n"
                for row in rows:
                    text += f"{row[0]}. {row[1]}\n"

                # Обновляем Textbox
                self.subscribers_listbox.configure(state="normal")
                self.subscribers_listbox.delete("1.0", "end")
                self.subscribers_listbox.insert("end", text)
                self.subscribers_listbox.configure(state="disabled")

            except Exception as e:
                self.show_error(f"Ошибка загрузки: {str(e)}")
            finally:
                conn.close()
        self.load_subscribers_combobox()

    def clear_fields(self):
        """Очистка полей ввода"""
        self.name_entry.delete(0, "end")
        self.electric_var.set(False)
        self.gas_var.set(False)
        self.water_var.set(False)

    def show_error(self, message):
        """Показ сообщения об ошибке"""
        error_window = ctk.CTkToplevel(self)
        error_window.title("Ошибка!")
        error_window.geometry("300x100")
        label = ctk.CTkLabel(error_window, text=message, text_color="red")
        label.pack(pady=20)

    def setup_readings_tab(self):
        """Вкладка для ввода показаний"""
        tab = self.tabview.tab("Показания")

        # Выбор абонента
        self.sub_combobox = ctk.CTkComboBox(tab, state="readonly")
        self.sub_combobox.pack(pady=10)
        self.sub_combobox.bind("<<ComboboxSelected>>", self.on_sub_select)

        # Поля для ввода
        self.electric_entry = ctk.CTkEntry(tab, placeholder_text="Электроэнергия, кВт·ч")
        self.coeff_entry = ctk.CTkEntry(tab, placeholder_text="Коэффициент трансформации (по умолчанию 1)")
        self.gas_entry = ctk.CTkEntry(tab, placeholder_text="Газ, м³")
        self.water_entry = ctk.CTkEntry(tab, placeholder_text="Вода, м³")

        for entry in [self.electric_entry, self.coeff_entry, self.gas_entry, self.water_entry]:
            entry.pack(pady=5)

        # Кнопка сохранения
        self.save_btn = ctk.CTkButton(tab, text="Сохранить показания", command=self.save_reading)
        self.save_btn.pack(pady=20)

    def on_sub_select(self, event):
        """Обработчик выбора абонента"""
        selected = self.sub_combobox.get()
        if selected:
            sub_id = int(selected.split(".")[0])
            conn = create_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM subscribers WHERE id=?", (sub_id,))
                    self.current_subscriber = cursor.fetchone()

                    # Блокировка неиспользуемых полей
                    self.toggle_fields()

                except Exception as e:
                    self.show_error(str(e))
                finally:
                    conn.close()

    def toggle_fields(self):
        """Активация/деактивация полей ввода"""
        # Электричество
        if self.current_subscriber[2]:  # electricity=True
            self.electric_entry.configure(state="normal")
            self.coeff_entry.configure(state="normal")
        else:
            self.electric_entry.configure(state="disabled")
            self.coeff_entry.configure(state="disabled")

        # Газ
        self.gas_entry.configure(state="normal" if self.current_subscriber[3] else "disabled")

        # Вода
        self.water_entry.configure(state="normal" if self.current_subscriber[4] else "disabled")

    def save_reading(self):
        """Сохранение показаний в БД"""
        if not self.current_subscriber:
            self.show_error("Выберите абонента!")
            return

        # Получаем период (предыдущий месяц)
        today = datetime.date.today()
        if today.month == 1:
            period = f"{today.year - 1}-12"
        else:
            period = f"{today.year}-{today.month - 1:02d}"

        # Парсим ввод
        try:
            electricity = float(self.electric_entry.get()) if self.electric_entry.get() else 0
            coeff = float(self.coeff_entry.get()) if self.coeff_entry.get() else 1
            gas = float(self.gas_entry.get()) if self.gas_entry.get() else 0
            water = float(self.water_entry.get()) if self.water_entry.get() else 0
            drainage = water * 0.9  # Пример расчёта водоотведения

        except ValueError:
            self.show_error("Некорректные числовые значения!")
            return

        # Сохранение в БД
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO readings 
                    (subscriber_id, period, electricity, coeff, gas, water, drainage)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.current_subscriber[0], period, electricity, coeff, gas, water, drainage))

                conn.commit()
                self.clear_entries()
                self.show_success("Данные успешно сохранены!")

            except Exception as e:
                self.show_error(str(e))
            finally:
                conn.close()

    def clear_entries(self):
        """Очистка полей ввода"""
        for entry in [self.electric_entry, self.coeff_entry, self.gas_entry, self.water_entry]:
            entry.delete(0, "end")

    def setup_reports_tab(self):
        """Вкладка для формирования реестра"""
        tab = self.tabview.tab("Реестры")

        # Выбор периода
        self.period_combobox = ctk.CTkComboBox(tab)
        self.period_combobox.pack(pady=10)

        # Кнопка генерации
        self.gen_btn = ctk.CTkButton(tab, text="Сформировать реестр", command=self.generate_report)
        self.gen_btn.pack(pady=10)

        # Область для отображения
        self.report_text = ctk.CTkTextbox(tab, state="disabled")
        self.report_text.pack(fill="both", expand=True, padx=20, pady=10)

    def generate_report(self):
        """Формирование реестра"""
        period = self.period_combobox.get()
        if not period:
            self.show_error("Выберите период!")
            return

        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.full_name, r.* 
                    FROM readings r
                    JOIN subscribers s ON r.subscriber_id = s.id
                    WHERE r.period = ?
                ''', (period,))

                rows = cursor.fetchall()
                if not rows:
                    self.show_error("Нет данных за выбранный период")
                    return

                # Формируем текст отчёта
                report = f"Реестр за {period}\n\n"
                report += "№ | Абонент | Эл-во (кВт·ч) | Газ (м³) | Вода (м³) | Водоотв.\n"
                report += "-" * 70 + "\n"

                for idx, row in enumerate(rows, 1):
                    report += f"{idx} | {row[0]} | {row[4]} | {row[6]} | {row[7]} | {row[8]}\n"

                # Поля для подписей
                report += "\n\nПодпись бухгалтера: ___________________\n"
                report += "Подпись исполнителя: ___________________\n"
                report += "Подпись абонента:    ___________________\n"

                # Выводим в Textbox
                self.report_text.configure(state="normal")
                self.report_text.delete("1.0", "end")
                self.report_text.insert("end", report)
                self.report_text.configure(state="disabled")

            except Exception as e:
                self.show_error(str(e))
            finally:
                conn.close()

    def load_subscribers_combobox(self):
        """Загрузка списка абонентов в выпадающий список"""
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, full_name FROM subscribers")
                rows = cursor.fetchall()

                # Формируем список в формате "ID. ФИО"
                values = [f"{row[0]}. {row[1]}" for row in rows]

                # Обновляем ComboBox, если он существует
                if hasattr(self, 'sub_combobox'):
                    self.sub_combobox.configure(values=values)
                    if values:
                        self.sub_combobox.set(values[0])
                    else:
                        self.sub_combobox.set("")

            except Exception as e:
                self.show_error(f"Ошибка загрузки: {str(e)}")
            finally:
                conn.close()  # Закрываем соединение



if __name__ == "__main__":
    app = App()
    app.mainloop()




