import tkinter as tk
from tkinter import Menu, messagebox
from config_manager import ConfigManager
from settings_window import SettingsWindow
from firebase_manager import FirebaseManager
from monitor import Monitor
from folder_window import FolderWindowManager
from log_window import LogWindow

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.firebase_manager = FirebaseManager(self.config_manager)
        self.monitor = Monitor(self)
        self.folder_window_manager = FolderWindowManager(self)
        self.log_window = LogWindow(self)
        
        self._setup_main_window()

    def _initialize_data(self):
        if self.config_manager.read_config():
            try:
                data = self.firebase_manager.load_data()
                self.folder_window_manager.update_all_folders(data)
                self.status_bar.config(text="Підключено до Firebase")
            except Exception as e:
                self.status_bar.config(text=f"Помилка: {str(e)}")
                self.log_window.add_log(f"Помилка ініціалізації: {str(e)}")
    
    def _setup_main_window(self):
        self.root.title("Моніторинг частот Firebase")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._create_menu()
        self._create_main_ui()
        self._center_window()
        
        if not self.config_manager.read_config():
            self.status_bar.config(text="Потрібно налаштувати підключення")
    
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
    
    def _create_main_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(
            main_frame,
            text="Моніторинг частот Firebase",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        tk.Button(
            control_frame,
            text="Запуск",
            command=self.monitor.start,
            bg="#4CAF50",
            fg="black",
            width=15,
            height=2
        ).pack(side='left', padx=10)
        
        tk.Button(
            control_frame,
            text="Зупинити",
            command=self.monitor.stop,
            bg="#f44336",
            fg="black",
            width=15,
            height=2
        ).pack(side='left', padx=10)
        
        # Status bar
        self.status_bar = tk.Label(
            self.root,
            text="Налаштуйте підключення до Firebase",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
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
            "Моніторинг частот Firebase\nВерсія 1.0\n\nКожна папка у базі даних відкривається у окремому вікні."
        )
    
    def on_closing(self):
        self.monitor.stop()
        self.firebase_manager.cleanup()
        self.folder_window_manager.close_all()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()