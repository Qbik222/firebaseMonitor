# folder_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from firebase_manager import FirebaseManager
import pyperclip 

class FolderWindow:
    def __init__(self, master, folder_name):
        self.master = master
        self.folder_name = folder_name
        self.frequencies = []  # Зберігає повні дані про частоти
        self.cell_data = {}    # Швидкий доступ до даних комірок за їх індексом
        self.window = tk.Toplevel(master)
        self.window.title(f"Частоти: {folder_name}")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.last_folder_data = None
        self.MIN_CELLS = 12
        self.MAX_CELLS = 24
        
        self._setup_ui()
        self._center_window()
        
    def _setup_ui(self):
        self.cells = []
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(expand=True, fill='both')
        
        # Заголовок з інформацією про папку
        header_frame = tk.Frame(frame)
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text=f"Папка: {self.folder_name}", 
                font=('Arial', 12, 'bold')).pack(side='left')
        
        # Лічильник частот
        self.count_label = tk.Label(header_frame, text=f"(0/{self.MIN_CELLS} частот)", 
                                  font=('Arial', 10), fg='gray')
        self.count_label.pack(side='left', padx=10)
        
        # Основний фрейм для комірок
        self.cells_frame = tk.Frame(frame)
        self.cells_frame.pack(fill='both', expand=True)
        
        # Створюємо початкові комірки
        for i in range(self.MIN_CELLS):
            self._create_cell(i)
        
        # Статусний рядок
        self.status_label = tk.Label(frame, text="", fg="blue")
        self.status_label.pack(pady=5)
    
    def _create_cell(self, cell_id):
        """Створення однієї комірки"""
        row = cell_id // 3
        col = cell_id % 3
        
        cell_frame = tk.Frame(self.cells_frame, width=120, height=70, 
                            relief=tk.RAISED, borderwidth=1, background='white')
        cell_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        cell_frame.pack_propagate(False)
        
        # Заголовок комірки
        header = tk.Frame(cell_frame)
        header.pack(fill='x')
        
        tk.Label(header, text=f"Комірка {cell_id+1}", 
                font=('Arial', 8)).pack(side='left')
        
        # Вміст комірки
        freq_label = tk.Label(cell_frame, text="", font=('Arial', 10), bg="white")
        freq_label.pack(expand=True)

        time_label = tk.Label(cell_frame, text="", font=('Arial', 8), bg="white")
        time_label.pack()
        
        # Зберігаємо посилання на елементи UI
        self.cells.append({
            'id': cell_id,
            'frame': cell_frame,
            'freq_label': freq_label,
            'time_label': time_label
        })
        
        # Ініціалізуємо дані для комірки
        self.cell_data[cell_id] = {
            'frequency': '',
            'original_name': '',
            'timestamp': 0
        }
        
        # Додаємо обробники кліків до всіх елементів комірки
        for widget in [cell_frame, freq_label, time_label]:
            widget.bind("<Button-1>", self._create_click_handler(cell_id))
            
            # Зміна кольору на зелений при наведенні
            widget.bind("<Enter>", lambda e, w=widget, cf=cell_frame: (
                w.config(cursor="hand2"), 
                cf.config(bg="lightgreen"),
                freq_label.config(bg="lightgreen"),
                time_label.config(bg="lightgreen")
            ))
            
            # Відновлення кольору на білий при виході
            widget.bind("<Leave>", lambda e, w=widget, cf=cell_frame: (
                w.config(cursor=""), 
                cf.config(bg="white"),
                freq_label.config(bg="white"),
                time_label.config(bg="white")
            ))

    
    def _create_click_handler(self, cell_id):
        """Фабрика обробників кліку для уникнення замикань"""
        def handler(event):
            self._copy_to_clipboard(cell_id)
            return "break"  # Запобігаємо подальшому поширенню події
        return handler
    
    def _copy_to_clipboard(self, cell_index):
        """Оптимізоване копіювання в буфер обміну"""
        try:
            # Отримуємо дані безпосередньо з колекції cell_data
            cell_info = self.cell_data.get(cell_index, {})
            freq = cell_info.get('original_name') or cell_info.get('frequency', '')
            
            if freq:
                # Використовуємо обидва методи для надійності
                try:
                    self.window.clipboard_clear()
                    self.window.clipboard_append(str(freq))
                except:
                    pyperclip.copy(str(freq))
                
                self._show_status_message(f"Скопійовано: {freq}")
            else:
                self._show_status_message("Немає частоти для копіювання")
                
        except Exception as e:
            print(f"Помилка копіювання: {e}")
            self._show_status_message("Помилка при копіюванні")
    
    def _show_status_message(self, message):
        """Швидке оновлення статусу"""
        self.status_label.config(text=message)
        self.window.after(800, lambda: self.status_label.config(text=""))
    
    def _update_count_label(self):
        """Оновлення лічильника частот"""
        active_count = sum(1 for f in self.frequencies if f.get('name'))
        self.count_label.config(text=f"({active_count}/{len(self.cells)} частот)")
    
    def update_frequencies(self, folder_data):
        """Оновлення відображення частот"""
        self.last_folder_data = folder_data
        
        # Обробка вхідних даних
        if isinstance(folder_data, dict):
            entries = list(folder_data.values())
        elif isinstance(folder_data, list):
            entries = folder_data
        else:
            return

        # Оновлюємо основну колекцію даних
        self.frequencies = entries[-len(self.cells):] if entries else []
        
        # Оновлюємо дані для кожної комірки
        for i in range(len(self.frequencies)):
            freq_data = self.frequencies[i]
            
            # Оновлюємо колекцію cell_data
            self.cell_data[i] = {
                'frequency': freq_data.get('name', freq_data.get('frequency', '')),
                'original_name': freq_data.get('original_name', ''),
                'timestamp': freq_data.get('timestamp', 0)
            }
            
            # Оновлюємо відображення
            freq = self.cell_data[i]['frequency']
            timestamp = self.cell_data[i]['timestamp']
            
            time_str = ""
            if timestamp:
                try:
                    dt = datetime.fromtimestamp(timestamp)
                    time_str = dt.strftime("%H:%M")
                except Exception:
                    pass
                    
            self.cells[i]['freq_label'].config(text=freq)
            self.cells[i]['time_label'].config(text=time_str)
        
        # Очищаємо решту комірок
        for i in range(len(self.frequencies), len(self.cells)):
            self.cell_data[i] = {
                'frequency': '',
                'original_name': '',
                'timestamp': 0
            }
            self.cells[i]['freq_label'].config(text="")
            self.cells[i]['time_label'].config(text="")
        
        self._update_count_label()
    
    def on_close(self):
        """Обробка закриття вікна"""
        self.master.focus_set()
        self.window.destroy()
    
    def _center_window(self):
        """Центрування вікна на екрані"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')


class FolderWindowManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.windows = {}  # {folder_name: FolderWindow}
    
    def update_all_folders(self, frequencies_data):
        """Оновлення всіх вікон папок"""
        if not frequencies_data or 'frequency' not in frequencies_data:
            return
            
        folders_data = frequencies_data['frequency']
        
        for folder_name, folder_data in folders_data.items():
            self.update_folder(folder_name, folder_data)
    
    def update_folder(self, folder_name, folder_data):
        """Оновлення або створення вікна для папки"""
        if folder_name not in self.windows:
            self.windows[folder_name] = FolderWindow(self.main_app.root, folder_name)
        
        self.windows[folder_name].update_frequencies(folder_data)
    
    def close_all(self):
        """Закриття всіх вікон папок"""
        for window in self.windows.values():
            window.window.destroy()
        self.windows = {}