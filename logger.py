from datetime import datetime

class Logger:
    def __init__(self, log_window):
        self.log_window = log_window
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line, end='')
        
        if self.log_window and self.log_window.text_widget and self.log_window.text_widget.winfo_exists():
            self.log_window.text_widget.config(state='normal')
            self.log_window.text_widget.insert('end', log_line)
            self.log_window.text_widget.see('end')
            self.log_window.text_widget.config(state='disabled')