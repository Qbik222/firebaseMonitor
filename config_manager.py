import os
import json
import tkinter.messagebox as messagebox

class ConfigManager:
    def __init__(self):
        self.json_file = ""
        self.firebase_url = ""

    def read_config(self):
        try:
            if not os.path.exists('config.json'):
                return False

            with open('config.json', 'r') as config_file:
                config_data = json.load(config_file)
                self.json_file = config_data.get('json_file_path', "")
                self.firebase_url = config_data.get('firebase_url', "")

                if not all([self.json_file, self.firebase_url]):
                    return False

            return True
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при читанні конфігураційного файлу: {e}")
            return False

    def save_config(self, json_file, firebase_url):
        config_data = {
            'json_file_path': json_file,
            'firebase_url': firebase_url
        }
        try:
            with open('config.json', 'w') as config_file:
                json.dump(config_data, config_file, indent=4)
            self.json_file = json_file
            self.firebase_url = firebase_url
            return True
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при збереженні конфігурації: {e}")
            return False

    def is_configured(self):
        """Check if configuration is valid and loaded"""
        return bool(self.json_file and self.firebase_url)