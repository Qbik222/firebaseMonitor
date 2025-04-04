import firebase_admin
from firebase_admin import credentials, db
import tkinter.messagebox as messagebox
from datetime import datetime
import json

class FirebaseManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.firebase_app = None
        self.log_file = "firebase_queries.log"  # Файл для зберігання логів

    def _log(self, action, details):
        """Логування дій у файл та консоль"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        log_entry = f"[{timestamp}] {action}: {details}\n"
        
        print(log_entry.strip())  # Вивід у консоль
        
        # Запис у файл
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def authenticate(self):
        try:
            if self.firebase_app is None:
                self._log("AUTH", f"Спроба підключення з файлом {self.config_manager.json_file}")
                cred = credentials.Certificate(self.config_manager.json_file)
                self.firebase_app = firebase_admin.initialize_app(
                    cred, 
                    {'databaseURL': self.config_manager.firebase_url}
                )
                self._log("AUTH", "Успішна автентифікація")
            return db
        except Exception as e:
            error_msg = f"Помилка автентифікації: {str(e)}"
            self._log("AUTH_ERROR", error_msg)
            messagebox.showerror("Помилка", error_msg)
            return None

    def load_data(self):
        try:
            self._log("QUERY", "Початок завантаження даних з кореня бази")
            start_time = datetime.now()
            
            ref = db.reference('/')
            data = ref.get()
            
            duration = (datetime.now() - start_time).total_seconds()
            data_size = len(json.dumps(data)) if data else 0
            
            self._log("QUERY_RESULT", (
                f"Отримано дані. "
                f"Час виконання: {duration:.3f} сек. "
                f"Розмір даних: {data_size} байт\n"
                f"Структура даних: {self._analyze_structure(data)}"
            ))
            
            return data if data else {}
        except Exception as e:
            error_msg = f"Помилка завантаження: {str(e)}"
            self._log("QUERY_ERROR", error_msg)
            messagebox.showerror("Помилка", error_msg)
            return {}

    def _analyze_structure(self, data):
        """Аналіз структури даних для логування"""
        if not data:
            return "Пусті дані"
            
        if isinstance(data, dict):
            structure = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    structure[key] = f"{type(value).__name__}({len(value)})"
                else:
                    structure[key] = type(value).__name__
            return structure
        return f"{type(data).__name__}({len(data)})"

    def cleanup(self):
        if self.firebase_app:
            try:
                self._log("CLEANUP", "Спроба закриття з'єднання")
                firebase_admin.delete_app(self.firebase_app)
                self._log("CLEANUP", "З'єднання успішно закрите")
            except Exception as e:
                self._log("CLEANUP_ERROR", f"Помилка закриття: {str(e)}")