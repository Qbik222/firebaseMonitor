import tkinter as tk
from tkinter import Menu, messagebox
from config_manager import ConfigManager
from settings_window import SettingsWindow
from firebase_manager import FirebaseManager
from monitor import Monitor
from folder_window import FolderManager
from log_window import LogWindow

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.firebase_manager = FirebaseManager(self.config_manager)
        self.monitor = Monitor(self)
        self.folder_manager = FolderManager(self)
        self.log_window = LogWindow(self)
        
        self._setup_main_window()
        self._initialize_data()

    def _initialize_data(self):
        if self.config_manager.read_config():
            try:
                data = self.firebase_manager.load_data()
                self.folder_manager.update_all_folders(data)
                self.status_bar.config(text="Підключено до Firebase")
            except Exception as e:
                self.status_bar.config(text=f"Помилка: {str(e)}")
                self.log_window.add_log(f"Помилка ініціалізації: {str(e)}")

    def _setup_main_window(self):
        self.root.title("Моніторинг частот Firebase")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Використовуємо grid для більш гнучкого розташування
        self.root.grid_rowconfigure(1, weight=1)  # Рядок для папок - розтягується
        self.root.grid_columnconfigure(0, weight=1)  # Колонка - розтягується
        
        # Верхня панель з заголовком і кнопками
        header_frame = tk.Frame(self.root, padx=5, pady=5)
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Заголовок
        tk.Label(
            header_frame,
            text="Моніторинг частот Firebase",
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Панель кнопок (права частина)
        button_frame = tk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Кнопки меншого розміру
        tk.Button(
            button_frame,
            text="Запуск",
            command=self.monitor.start,
            bg="#4CAF50",
            fg="black",
            width=10,
            height=1
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            button_frame,
            text="Зупинити",
            command=self.monitor.stop,
            bg="#f44336",
            fg="black",
            width=10,
            height=1
        ).pack(side=tk.LEFT, padx=2)
        
        # Контейнер для папок (займає весь доступний простір)
        self.folder_container = tk.Frame(self.root)
        self.folder_container.grid(row=1, column=0, sticky="nsew")
        
        # Передаємо новий контейнер у FolderManager
        self.folder_manager.set_container(self.folder_container)
        
        # Статус бар
        self.status_bar = tk.Label(
            self.root,
            text="Налаштуйте підключення до Firebase",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        self._create_menu()

    def _create_menu(self):
        menubar = Menu(self.root)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Налаштування", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Вийти", command=self.on_closing)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Показати лог", command=self.log_window.toggle)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Про програму", command=self.show_about)
        menubar.add_cascade(label="Довідка", menu=help_menu)
        
        self.root.config(menu=menubar)

    def show_settings(self):
        settings = SettingsWindow(self.root, self.config_manager)
        settings.show()
    
    def show_about(self):
        messagebox.showinfo(
            "Про програму",
            "Моніторинг частот Firebase\nВерсія 1.0\n\nВсі частоти відображаються у головному вікні."
        )
    
    def on_closing(self):
        self.monitor.stop()
        self.firebase_manager.cleanup()
        self.folder_manager.close_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.firebase_manager = FirebaseManager(self.config_manager)
        self.monitor = Monitor(self)
        self.folder_manager = FolderManager(self)
        self.log_window = LogWindow(self)
        
        self._setup_main_window()
        self._initialize_data()

    def _initialize_data(self):
        if self.config_manager.read_config():
            try:
                data = self.firebase_manager.load_data()
                self.folder_manager.update_all_folders(data)
                self.status_bar.config(text="Підключено до Firebase")
            except Exception as e:
                self.status_bar.config(text=f"Помилка: {str(e)}")
                self.log_window.add_log(f"Помилка ініціалізації: {str(e)}")

    def _setup_main_window(self):
        self.root.title("Моніторинг частот Firebase")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure grid for main window
        self.root.grid_rowconfigure(1, weight=1)  # Main content area
        self.root.grid_columnconfigure(0, weight=1)
        
        # Header frame (top)
        header_frame = tk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Title label
        tk.Label(
            header_frame,
            text="Моніторинг частот Firebase",
            font=('Arial', 12, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame (right side)
        button_frame = tk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT, padx=5)
        
        # Control buttons
        tk.Button(
            button_frame,
            text="Запуск",
            command=self.monitor.start,
            bg="#4CAF50",
            fg="black",
            width=10,
            height=1
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            button_frame,
            text="Зупинити",
            command=self.monitor.stop,
            bg="#f44336",
            fg="black",
            width=10,
            height=1
        ).pack(side=tk.LEFT, padx=2)
        
        # Folder manager container will use grid (already set in FolderManager)
        # Status bar at bottom
        self.status_bar = tk.Label(
            self.root,
            text="Налаштуйте підключення до Firebase",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        self._create_menu()
        
    def _create_main_ui(self, parent):
        """Create UI in the top part"""
        tk.Label(
            parent,
            text="Моніторинг частот Firebase",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))
        
        # Control buttons
        control_frame = tk.Frame(parent)
        control_frame.pack(pady=10)
        
        tk.Button(
            control_frame,
            text="Запуск",
            command=self.monitor.start,
            bg="#4CAF50",
            fg="black",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            control_frame,
            text="Зупинити",
            command=self.monitor.stop,
            bg="#f44336",
            fg="black",
            width=15,
            height=2
        ).pack(side=tk.LEFT, padx=10)

    def _create_menu(self):
        menubar = Menu(self.root)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Налаштування", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Вийти", command=self.on_closing)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # View menu
        view_menu = Menu(menubar, tearoff=0)
        view_menu.add_command(label="Показати лог", command=self.log_window.toggle)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Про програму", command=self.show_about)
        menubar.add_cascade(label="Довідка", menu=help_menu)
        
        self.root.config(menu=menubar)

    def show_settings(self):
        settings = SettingsWindow(self.root, self.config_manager)
        settings.show()
    
    def show_about(self):
        messagebox.showinfo(
            "Про програму",
            "Моніторинг частот Firebase\nВерсія 1.0\n\nВсі частоти відображаються у головному вікні."
        )
    
    def on_closing(self):
        self.monitor.stop()
        self.firebase_manager.cleanup()
        self.folder_manager.close_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()