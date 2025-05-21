# Кнопка для добавления абонента
self.add_abonent_button = ctk.CTkButton(self.abonents_frame, text="Добавить абонента",
                                       command=self.open_add_abonent_window)
self.add_abonent_button.pack(pady=10)

# Кнопка настроек
self.settings_button = ctk.CTkButton(self.abonents_frame, text="Настройки",
                                   command=self.open_settings_window)
self.settings_button.pack(pady=10)

# Комбобокс для выбора абонента

def open_settings_window(self):
    """Открывает окно настроек"""
    print("[DEBUG] open_settings_window вызван")
    try:
        from settings_window import SettingsWindow
        print("[DEBUG] SettingsWindow импортирован")
        settings_window = SettingsWindow(self.root, 400, 300)
        print("[DEBUG] SettingsWindow создан")
    except Exception as e:
        print(f"[DEBUG] Ошибка при открытии окна настроек: {e}") 