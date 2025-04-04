import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class LogWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = None
        self.text_widget = None
        self.is_visible = False
    
    def toggle(self):
        if self.is_visible:
            self._hide()
        else:
            self._show()
    
    def _show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.is_visible = True
        self.window = tk.Toplevel(self.main_app.root)
        self.window.title("Лог змін частот")
        self._setup_window()
    
    def _setup_window(self):
        self.window.geometry("800x500")
        
        tk.Button(
            self.window,
            text="Закрити лог",
            command=self.toggle,
        ).pack(pady=5)
        
        self.text_widget = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            state='disabled'
        )
        self.text_widget.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.window.protocol("WM_DELETE_WINDOW", self.toggle)
    
    def _hide(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        self.is_visible = False
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line, end='')

        if self.text_widget and self.text_widget.winfo_exists():
            self.text_widget.config(state='normal')
            self.text_widget.insert('end', log_line)
            self.text_widget.see('end')
            self.text_widget.config(state='disabled')