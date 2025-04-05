import tkinter as tk
from tkinter import Menu, messagebox
from config_manager import ConfigManager
from settings_window import SettingsWindow
from firebase_manager import FirebaseManager
from monitor import Monitor
from folder_window import FolderManager  # Changed from FolderWindowManager
from log_window import LogWindow

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.firebase_manager = FirebaseManager(self.config_manager)
        self.monitor = Monitor(self)
        self.folder_manager = FolderManager(self)  # Changed to FolderManager
        self.log_window = LogWindow(self)
        
        self._setup_main_window()
        self._initialize_data()

    def _initialize_data(self):
        if self.config_manager.read_config():
            try:
                data = self.firebase_manager.load_data()
                self.folder_manager.update_all_folders(data)  # Updated to use folder_manager
                self.status_bar.config(text="Підключено до Firebase")
            except Exception as e:
                self.status_bar.config(text=f"Помилка: {str(e)}")
                self.log_window.add_log(f"Помилка ініціалізації: {str(e)}")

    def _setup_main_window(self):
        self.root.title("Моніторинг частот Firebase")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main container with scroll
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for controls
        top_frame = tk.Frame(main_container)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self._create_menu()
        self._create_main_ui(top_frame)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Налаштуйте підключення до Firebase",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

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

    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
    
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
        self.folder_manager.close_all()  # Updated to use folder_manager
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()