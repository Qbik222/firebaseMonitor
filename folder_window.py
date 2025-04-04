# folder_window.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from firebase_manager import FirebaseManager
import pyperclip 

class FolderWindow:
    def __init__(self, master, folder_name):
        self.master = master
        self.folder_name = folder_name
        self.frequencies = []  # Тут зберігатимемо дані для цієї папки
        self.window = tk.Toplevel(master)
        self.window.title(f"Частоти: {folder_name}")
        
        self._setup_ui()
        self._center_window()
        
    def _setup_ui(self):
        self.cells = []
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(expand=True, fill='both')
        
        tk.Label(frame, text=f"Папка: {self.folder_name}", 
                font=('Arial', 12, 'bold')).pack(pady=5)
        
        cells_frame = tk.Frame(frame)
        cells_frame.pack(pady=10)
        
        # Create 6 cells (2 rows x 3 columns)
        for i in range(6):
            cell_frame = tk.Frame(cells_frame, width=100, height=60, 
                                relief=tk.RAISED, borderwidth=1)
            cell_frame.grid(row=i//3, column=i%3, padx=5, pady=5)
            cell_frame.pack_propagate(False)
            
            freq_label = tk.Label(cell_frame, text="", font=('Arial', 10))
            freq_label.pack(expand=True)
            
            time_label = tk.Label(cell_frame, text="", font=('Arial', 8))
            time_label.pack()
            
            # Bind click event
            cell_frame.bind("<Button-1>", lambda e, idx=i: self._copy_to_clipboard(idx))
            
            self.cells.append({
                'frame': cell_frame,
                'freq_label': freq_label,
                'time_label': time_label
            })
        
        # Status label
        self.status_label = tk.Label(frame, text="", fg="blue")
        self.status_label.pack(pady=5)
    
    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
    
    def update_frequencies(self, folder_data):
        """Update the display with new frequencies with detailed logging"""
        print(f"\n{'='*50}")
        print(f"Оновлення даних для папки: {self.folder_name}")
        print("Отримані дані (folder_data):")
        print(f"Тип даних: {type(folder_data)}")
        
        # Детальний вивід вмісту folder_data
        if isinstance(folder_data, dict):
            print("Вміст словника:")
            for key, value in folder_data.items():
                print(f"Ключ: {key}")
                print(f"Тип значення: {type(value)}")
                if isinstance(value, dict):
                    print("Вміст запису:")
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key}: {sub_value} (тип: {type(sub_value)})")
                else:
                    print(f"Значення: {value}")
        else:
            print(f"Неочікуваний тип даних: {folder_data}")

        # Отримуємо всі записи для цієї папки
        try:
            entries = list(folder_data.values())
            print(f"\nЗнайдено записів: {len(entries)}")
            self.frequencies = entries[-6:]  # Беремо останні 6 записів
            print(f"Відображаємо останні {len(self.frequencies)} записів")
        except Exception as e:
            print(f"Помилка обробки даних: {e}")
            return

        for i, freq_data in enumerate(self.frequencies):
            print(f"\nОбробка комірки {i}:")
            if not isinstance(freq_data, dict):
                print(f"Невірний формат даних для комірки {i}: {freq_data}")
                continue

            freq = freq_data.get('name', '')
            timestamp = freq_data.get('timestamp', 0)
            original_freq = freq_data.get('original_name', '')

            print(f"Дані комірки {i}:")
            print(f"  name: {freq} (тип: {type(freq)})")
            print(f"  original_name: {original_freq} (тип: {type(original_freq)})")
            print(f"  timestamp: {timestamp} (тип: {type(timestamp)})")

            # Конвертація часу
            time_str = ""
            if timestamp:
                try:
                    print(f"Спроба конвертувати timestamp: {timestamp}")
                    dt = datetime.fromtimestamp(timestamp)
                    time_str = dt.strftime("%H:%M")
                    print(f"Конвертований час: {time_str}")
                except Exception as e:
                    print(f"Помилка конвертації часу: {e}")
                    time_str = ""
            
            # Оновлення інтерфейсу
            print(f"Встановлюємо значення для комірки {i}:")
            print(f"  Назва: {freq}")
            print(f"  Час: {time_str}")
            self.cells[i]['freq_label'].config(text=freq)
            self.cells[i]['time_label'].config(text=time_str)
        
        print(f"{'='*50}\n")
    
    def _copy_to_clipboard(self, cell_index):
        """Copy frequency to clipboard and show status"""
        if cell_index < len(self.frequencies):
            freq_data = self.frequencies[cell_index]
            # Використовуємо original_name якщо він є, інакше name
            freq = freq_data.get('original_name', freq_data.get('name', ''))
            if freq:
                pyperclip.copy(str(freq))
                self.status_label.config(text=f"Скопійовано: {freq}")
                self.window.after(2000, lambda: self.status_label.config(text=""))


class FolderWindowManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.windows = {}  # {folder_name: FolderWindow}
    
    def update_all_folders(self, frequencies_data):
        """Update or create windows for all folders"""
        if not frequencies_data or 'frequency' not in frequencies_data:
            return
            
        folders_data = frequencies_data['frequency']
        print(folder_data)
        
        for folder_name, folder_data in folders_data.items():
            self.update_folder(folder_name, folder_data)
    
    def update_folder(self, folder_name, folder_data):
        """Update or create a window for a specific folder"""
        if folder_name not in self.windows:
            self.windows[folder_name] = FolderWindow(self.main_app.root, folder_name)
        
        self.windows[folder_name].update_frequencies(folder_data)
    
    def close_all(self):
        """Close all folder windows"""
        for window in self.windows.values():
            window.window.destroy()
        self.windows = {}