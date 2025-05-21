import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            # Защита от множественных срабатываний
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                print(f"\nИзменен файл: {event.src_path}")
                print("Запускаю проверку...")
                try:
                    # Запускаем main.py
                    result = subprocess.run(['py', 'main.py'], 
                                         capture_output=True, 
                                         text=True)
                    
                    # Выводим результат
                    if result.returncode == 0:
                        print("\n✅ Программа запущена успешно")
                    else:
                        print("\n❌ Ошибка при запуске программы:")
                        print(result.stderr)
                        
                except Exception as e:
                    print(f"\n❌ Ошибка при запуске проверки: {e}")
                
                print("\nОжидаю изменений...")

def main():
    # Путь к директории проекта
    path = "."
    
    # Создаем обработчик событий
    event_handler = CodeChangeHandler()
    
    # Создаем наблюдателя
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    print("Мониторинг изменений запущен...")
    print("Для остановки нажмите Ctrl+C")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nМониторинг остановлен")
    
    observer.join()

if __name__ == "__main__":
    main() 