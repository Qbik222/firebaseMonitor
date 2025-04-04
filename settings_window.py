import tkinter as tk
from tkinter import filedialog, messagebox

class SettingsWindow:
    def __init__(self, parent, config_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.window = None

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Налаштування підключення")
        self._setup_ui()

    def _setup_ui(self):
        self.window.geometry("500x300")
        self.window.resizable(False, False)

        # Заголовок
        tk.Label(
            self.window,
            text="Налаштування підключення до Firebase",
            font=('Arial', 12, 'bold')
        ).pack(pady=(10, 20))

        # JSON файл
        tk.Label(self.window, text="JSON файл з ключами Firebase:").pack(anchor='w', padx=20)
        json_file_frame = tk.Frame(self.window)
        json_file_frame.pack(fill='x', padx=20, pady=5)
        self.json_file_entry = tk.Entry(json_file_frame)
        self.json_file_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.json_file_entry.insert(0, self.config_manager.json_file)
        tk.Button(
            json_file_frame,
            text="Огляд...",
            command=self._browse_json_file,
            width=10
        ).pack(side='right')

        # Firebase URL
        tk.Label(self.window, text="URL бази даних Firebase:").pack(anchor='w', padx=20)
        self.firebase_url_entry = tk.Entry(self.window)
        self.firebase_url_entry.pack(fill='x', padx=20, pady=5)
        self.firebase_url_entry.insert(0, self.config_manager.firebase_url)
        tk.Label(
            self.window,
            text="Формат: https://ваш-проект.firebaseio.com/",
            font=('Arial', 8),
            fg='gray'
        ).pack(anchor='w', padx=20)

        # Кнопки
        buttons_frame = tk.Frame(self.window)
        buttons_frame.pack(pady=20)

        tk.Button(
            buttons_frame,
            text="Зберегти",
            command=self._save_settings,
            bg="#4CAF50",
            fg="black",
            padx=20
        ).pack(side='left', padx=10)

        tk.Button(
            buttons_frame,
            text="Скасувати",
            command=self.window.destroy,
            bg="#f44336",
            fg="black",
            padx=20
        ).pack(side='right', padx=10)

        self._center_window()

    def _browse_json_file(self):
        filename = filedialog.askopenfilename(
            title="Виберіть JSON файл з ключами Firebase",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.json_file_entry.delete(0, tk.END)
            self.json_file_entry.insert(0, filename)

    def _save_settings(self):
        json_file = self.json_file_entry.get()
        firebase_url = self.firebase_url_entry.get()

        if not firebase_url.startswith("https://") or not firebase_url.endswith(".firebaseio.com/"):
            messagebox.showerror("Помилка", "Будь ласка, введіть коректний URL Firebase у форматі:\nhttps://ваш-проект.firebaseio.com/")
            return

        if not os.path.exists(json_file):
            messagebox.showerror("Помилка", "Вказаний JSON файл не існує")
            return

        if self.config_manager.save_config(json_file, firebase_url):
            self.window.destroy()
            messagebox.showinfo("Успіх", "Налаштування збережено успішно!")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        self.window.grab_set()