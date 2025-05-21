import customtkinter as ctk
import json
import os
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog

class SettingsWindow:
    def __init__(self, parent, width, height, title="Настройки", resizable=(False, False)):
        self.root = ctk.CTkToplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])
        
        # Загружаем настройки
        self.settings = self.load_settings()
        
        # Создаем и размещаем виджеты
        self.create_widgets()
        
        # Делаем окно модальным
        self.root.grab_set()
        self.root.focus_set()
        
    def create_widgets(self):
        """Создает и размещает виджеты в окне"""
        # Создаем основной фрейм с прокруткой
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Секция пути сохранения
        path_frame = ctk.CTkFrame(main_frame)
        path_frame.pack(padx=10, pady=5, fill="x")
        
        path_label = ctk.CTkLabel(path_frame, text="Папка для сохранения реестров:")
        path_label.pack(side="left", padx=5)
        
        self.path_entry = ctk.CTkEntry(path_frame)
        self.path_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.path_entry.insert(0, self.settings.get("save_path", r"C:\Реестры по абонентам"))
        
        # Кнопка 'Обзор' теперь под полем ввода
        browse_button = ctk.CTkButton(main_frame, text="Обзор",
                                    command=self.browse_save_path)
        browse_button.pack(padx=10, pady=(0, 10), anchor="w")
        
        # Секция подписей
        signatures_frame = ctk.CTkFrame(main_frame)
        signatures_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Заголовок секции подписей
        title_label = ctk.CTkLabel(signatures_frame, text="Подписи в реестре",
                                 font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Список подписантов
        self.signatures_list = []
        self.signatures_frames = []
        
        # Загружаем существующие подписи
        signatures = self.settings.get("signatures", [])
        for signature in signatures:
            self.add_signature_field(signatures_frame, signature)
        
        # Кнопка добавления подписи
        add_button = ctk.CTkButton(signatures_frame, text="Добавить подпись",
                                  command=lambda: self.add_signature_field(signatures_frame))
        add_button.pack(pady=10)
        
        # Кнопки внизу окна
        buttons_frame = ctk.CTkFrame(self.root)
        buttons_frame.pack(padx=20, pady=10, fill="x")
        save_button = ctk.CTkButton(buttons_frame, text="Сохранить",
                                  command=self.save_settings)
        save_button.pack(side="right", padx=5)
        cancel_button = ctk.CTkButton(buttons_frame, text="Отмена",
                                    command=self.root.destroy)
        cancel_button.pack(side="right", padx=5)
        
    def add_signature_field(self, parent, signature=None):
        """Добавляет поле для ввода подписи"""
        frame = ctk.CTkFrame(parent)
        frame.pack(padx=5, pady=5, fill="x")
        
        # Поле для должности
        position_entry = ctk.CTkEntry(frame, placeholder_text="Должность")
        position_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Поле для фамилии
        name_entry = ctk.CTkEntry(frame, placeholder_text="Фамилия И.О.")
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Кнопка удаления
        delete_button = ctk.CTkButton(frame, text="✕", width=30,
                                    command=lambda: self.remove_signature_field(frame))
        delete_button.pack(side="right", padx=5)
        
        # Если есть существующая подпись, заполняем поля
        if signature:
            position_entry.insert(0, signature.get("position", ""))
            name_entry.insert(0, signature.get("name", ""))
        
        self.signatures_frames.append((frame, position_entry, name_entry))
        
    def remove_signature_field(self, frame):
        """Удаляет поле подписи"""
        for i, (f, _, _) in enumerate(self.signatures_frames):
            if f == frame:
                self.signatures_frames.pop(i)
                frame.destroy()
                break
        
    def browse_save_path(self):
        """Открывает диалог выбора папки для сохранения"""
        folder_path = filedialog.askdirectory(
            title="Выберите папку для сохранения реестров",
            initialdir=self.path_entry.get()
        )
        if folder_path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_path)
        
    def load_settings(self):
        """Загружает настройки из файла"""
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            CTkMessagebox(title="Ошибка",
                         message=f"Ошибка при загрузке настроек: {str(e)}")
        return {}
        
    def save_settings(self):
        """Сохраняет настройки в файл"""
        # Собираем подписи
        signatures = []
        for _, position_entry, name_entry in self.signatures_frames:
            position = position_entry.get().strip()
            name = name_entry.get().strip()
            if position and name:  # Сохраняем только заполненные подписи
                signatures.append({
                    "position": position,
                    "name": name
                })
        
        settings = {
            "save_path": self.path_entry.get(),
            "signatures": signatures
        }
        
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'settings.json')
        try:
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            CTkMessagebox(title="Успех",
                         message="Настройки успешно сохранены")
            self.root.destroy()
        except Exception as e:
            CTkMessagebox(title="Ошибка",
                         message=f"Ошибка при сохранении настроек: {str(e)}") 