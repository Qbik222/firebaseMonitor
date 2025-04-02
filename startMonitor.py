import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import firebase_admin
from firebase_admin import credentials, db
import threading
import time
import re
import pyperclip
from datetime import datetime, timedelta
import os
import json
import sys

# Глобальні змінні
json_file = ""
firebase_url = ""
last_button = None
last_frequency = None
data_thread = None
monitoring_event = threading.Event()
firebase_app = None
restart_timer = None
monitoring_active = False
flag_buttons = []
root = None
log_window = None
log_text = None
show_log = False
settings_window = None

def read_config():
    global json_file, firebase_url
    try:
        if not os.path.exists('config.json'):
            show_settings_window()
            return False

        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
            json_file = config_data.get('json_file_path', "")
            firebase_url = config_data.get('firebase_url', "")

            if not all([json_file, firebase_url]):
                show_settings_window()
                return False

        return True
    except Exception as e:
        messagebox.showerror("Помилка", f"Помилка при читанні конфігураційного файлу: {e}")
        show_settings_window()
        return False

def save_config():
    config_data = {
        'json_file_path': json_file,
        'firebase_url': firebase_url
    }
    try:
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file, indent=4)
        log_message("Конфігурацію збережено")
        return True
    except Exception as e:
        messagebox.showerror("Помилка", f"Помилка при збереженні конфігурації: {e}")
        return False

def authenticate_with_firebase():
    global firebase_app
    try:
        if firebase_app is None:
            cred = credentials.Certificate(json_file)
            firebase_app = firebase_admin.initialize_app(cred, {'databaseURL': firebase_url})
            log_message("Успішне підключення до Firebase")
        else:
            log_message("Firebase вже ініціалізовано")
        return db
    except Exception as e:
        messagebox.showerror("Помилка", f"Помилка автентифікації з Firebase: {e}")
        return None

def load_data_from_firebase():
    try:
        ref = db.reference('/')
        data = ref.get()
        if data:
            log_message(f"Отримані дані з Firebase: {data}")
        else:
            log_message("Немає даних у базі")
        return data if data else []
    except Exception as e:
        messagebox.showerror("Помилка", f"Помилка завантаження даних з Firebase: {e}")
        return []

def log_message(message, level="INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] [{level}] {message}\n"
    print(log_line, end='')

    try:
        if log_text and log_text.winfo_exists():
            log_text.config(state='normal')
            log_text.insert('end', log_line)
            log_text.see('end')
            log_text.config(state='disabled')
    except tk.TclError:
        pass  # Ігноруємо помилки, пов'язані з закритим вікном

def toggle_log_window():
    global show_log, log_window, log_text

    if show_log:
        if log_window and log_window.winfo_exists():
            log_window.destroy()
        show_log = False
    else:
        show_log = True
        log_window = tk.Toplevel(root)
        log_window.title("Лог змін частот")
        log_window.geometry("800x500")

        close_btn = tk.Button(log_window, text="Закрити лог", command=toggle_log_window)
        close_btn.pack(pady=5)

        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, state='disabled')
        log_text.pack(expand=True, fill='both', padx=5, pady=5)

        log_window.protocol("WM_DELETE_WINDOW", toggle_log_window)

def show_settings_window():
    global settings_window, json_file, firebase_url

    def browse_json_file():
        filename = filedialog.askopenfilename(
            title="Виберіть JSON файл з ключами Firebase",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            json_file_entry.delete(0, tk.END)
            json_file_entry.insert(0, filename)

    def save_settings():
        global json_file, firebase_url
        json_file = json_file_entry.get()
        firebase_url = firebase_url_entry.get()

        if not firebase_url.startswith("https://") or not firebase_url.endswith(".firebaseio.com/"):
            messagebox.showerror("Помилка", "Будь ласка, введіть коректний URL Firebase у форматі:\nhttps://ваш-проект.firebaseio.com/")
            return

        if not os.path.exists(json_file):
            messagebox.showerror("Помилка", "Вказаний JSON файл не існує")
            return

        if save_config():
            settings_window.destroy()
            messagebox.showinfo("Успіх", "Налаштування збережено успішно!")

    settings_window = tk.Toplevel(root)
    settings_window.title("Налаштування підключення")
    settings_window.geometry("500x300")
    settings_window.resizable(False, False)

    # Заголовок
    tk.Label(
        settings_window,
        text="Налаштування підключення до Firebase",
        font=('Arial', 12, 'bold')
    ).pack(pady=(10, 20))

    # JSON файл
    tk.Label(settings_window, text="JSON файл з ключами Firebase:").pack(anchor='w', padx=20)
    json_file_frame = tk.Frame(settings_window)
    json_file_frame.pack(fill='x', padx=20, pady=5)
    json_file_entry = tk.Entry(json_file_frame)
    json_file_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
    json_file_entry.insert(0, json_file)
    tk.Button(
        json_file_frame,
        text="Огляд...",
        command=browse_json_file,
        width=10
    ).pack(side='right')

    # Firebase URL
    tk.Label(settings_window, text="URL бази даних Firebase:").pack(anchor='w', padx=20)
    firebase_url_entry = tk.Entry(settings_window)
    firebase_url_entry.pack(fill='x', padx=20, pady=5)
    firebase_url_entry.insert(0, firebase_url)
    tk.Label(
        settings_window,
        text="Формат: https://ваш-проект.firebaseio.com/",
        font=('Arial', 8),
        fg='gray'
    ).pack(anchor='w', padx=20)

    # Кнопки
    buttons_frame = tk.Frame(settings_window)
    buttons_frame.pack(pady=20)

    tk.Button(
        buttons_frame,
        text="Зберегти",
        command=save_settings,
        bg="#4CAF50",
        fg="black",
        padx=20
    ).pack(side='left', padx=10)

    tk.Button(
        buttons_frame,
        text="Скасувати",
        command=settings_window.destroy,
        bg="#f44336",
        fg="black",
        padx=20
    ).pack(side='right', padx=10)

    # Центрування
    settings_window.update_idletasks()
    width = settings_window.winfo_width()
    height = settings_window.winfo_height()
    x = (settings_window.winfo_screenwidth() // 2) - (width // 2)
    y = (settings_window.winfo_screenheight() // 2) - (height // 2)
    settings_window.geometry(f'{width}x{height}+{x}+{y}')

    settings_window.grab_set()

def on_flag_button_click(i):
    global last_button, last_frequency
    if last_button:
        last_button.config(bg="SystemButtonFace")
    last_button = flag_buttons[i]
    flag_buttons[i].config(bg="yellow")

    button_data = flag_buttons[i].cget('text')
    frequency_match = re.search(r'(\d+\.\d+)', button_data)
    if frequency_match:
        current_frequency = frequency_match.group(1)
        pyperclip.copy(current_frequency)
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = f"[{timestamp}] Частота {current_frequency} скопійована"
        log_message(message)
        status_label = tk.Label(root, text=message, fg="green", font=('Arial', 12))
        status_label.pack(pady=5)
        root.after(3000, status_label.destroy)

def update_data_display(root, data):
    global flag_buttons, last_frequency

    if not data or not isinstance(data, dict):
        return

    frequencies = data.get('frequency', data.get('text_entries', {}))
    if not frequencies:
        return

    current_buttons_data = [btn.cget('text') for btn in flag_buttons]
    unique_entries = {}

    for key, value in frequencies.items():
        freq_value = value.get('value', value.get('name', ''))
        if freq_value and freq_value not in unique_entries:
            unique_entries[freq_value] = value
            log_message(f"Нова частота: {freq_value}")

    sorted_entries = sorted(unique_entries.values(),
                          key=lambda x: x.get('timestamp', 0),
                          reverse=True)

    latest_entries = sorted_entries[:6]

    for index in range(len(flag_buttons)):
        if index < len(latest_entries):
            entry = latest_entries[index]
            timestamp = entry.get('timestamp', '')
            value = entry.get('value', entry.get('name', ''))

            if isinstance(timestamp, (int, float)):
                try:
                    timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp_str = ""
            else:
                timestamp_str = str(timestamp)

            new_button_text = f"{value} - {timestamp_str}" if timestamp_str else str(value)

            if index < len(current_buttons_data) and current_buttons_data[index] != new_button_text:
                old_value = current_buttons_data[index].split(' - ')[0] if current_buttons_data[index] else None

                if old_value and old_value != "":
                    log_message(f"Зміна частоти: {old_value} -> {value}")

                flag_buttons[index].config(text=new_button_text, state="normal")

                if last_frequency != value and value != "":
                    flag_buttons[index].config(bg="lightgreen")
                    last_frequency = value
                else:
                    flag_buttons[index].config(bg="SystemButtonFace")
        else:
            old_value = current_buttons_data[index].split(' - ')[0] if index < len(current_buttons_data) and current_buttons_data[index] else None
            if old_value and old_value != "":
                log_message(f"Видалено частоту: {old_value}")

            flag_buttons[index].config(text="", state="disabled", bg="SystemButtonFace")

def refresh_data():
    global last_frequency, monitoring_active
    monitoring_active = True
    next_restart_time = datetime.now() + timedelta(minutes=10)
    last_data = None

    while monitoring_event.is_set():
        try:
            log_message("Перевірка оновлень...")
            current_data = load_data_from_firebase()

            if current_data and current_data != last_data:
                try:
                    root.after(0, lambda: update_data_display(root, current_data))
                except tk.TclError:
                    break  # Вихід, якщо головне вікно закрите
                last_data = current_data

            if datetime.now() >= next_restart_time:
                log_message("Автоматичний перезапуск")
                stop_monitoring()
                time.sleep(2)
                start_processing()
                break

            time.sleep(5)

        except Exception as e:
            log_message(f"Помилка: {e}", "ERROR")
            time.sleep(10)

    monitoring_active = False

def start_processing():
    global monitoring_event, data_thread, monitoring_active
    if monitoring_active:
        log_message("Моніторинг вже активний")
        return
    if not json_file or not firebase_url:
        messagebox.showerror("Помилка", "Будь ласка, налаштуйте підключення")
        show_settings_window()
        return

    firebase_db = authenticate_with_firebase()
    if firebase_db:
        monitoring_event.set()
        data_thread = threading.Thread(target=refresh_data)
        data_thread.daemon = False  # Змінимо на не-daemon потік для кращого завершення
        data_thread.start()
        log_message("Моніторинг запущено")

def stop_monitoring():
    global monitoring_event, monitoring_active, restart_timer
    monitoring_active = False
    monitoring_event.clear()
    if restart_timer:
        restart_timer.cancel()
    log_message("Моніторинг зупинено")
    for button in flag_buttons:
        button.config(text="Сканування зупинено", state="disabled")

def on_closing():
    stop_monitoring()
    if firebase_app:
        try:
            firebase_admin.delete_app(firebase_app)
        except:
            pass
    root.destroy()
    sys.exit(0)

def create_gui():
    global flag_buttons, root

    root = tk.Tk()
    root.title("Моніторинг частот Firebase")
    root.geometry("500x500")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Центрування
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')

    # Меню
    menubar = tk.Menu(root)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Налаштування", command=show_settings_window)
    file_menu.add_separator()
    file_menu.add_command(label="Вийти", command=on_closing)
    menubar.add_cascade(label="Файл", menu=file_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="Про програму", command=lambda: messagebox.showinfo(
        "Про програму",
        "Моніторинг частот Firebase\nВерсія 1.0"
    ))
    menubar.add_cascade(label="Довідка", menu=help_menu)

    root.config(menu=menubar)

    # Керування
    control_frame = tk.Frame(root)
    control_frame.pack(pady=10)

    start_button = tk.Button(
        control_frame,
        text="Запуск",
        command=start_processing,
        bg="#4CAF50",
        fg="black",
        width=10
    )
    start_button.pack(side='left', padx=5)

    stop_button = tk.Button(
        control_frame,
        text="Зупинити",
        command=stop_monitoring,
        bg="#f44336",
        fg="black",
        width=10
    )
    stop_button.pack(side='left', padx=5)

    log_button = tk.Button(
        control_frame,
        text="Лог",
        command=toggle_log_window,
        width=10
    )
    log_button.pack(side='left', padx=5)

    # Частоти
    freq_frame = tk.Frame(root)
    freq_frame.pack(pady=10, fill='both', expand=True)

    flag_buttons = []
    for i in range(6):
        flag_button = tk.Button(
            freq_frame,
            text=f"Частота {i+1}",
            width=30,
            height=2,
            command=lambda i=i: on_flag_button_click(i)
        )
        flag_button.pack(pady=5)
        flag_buttons.append(flag_button)

    # Статус
    status_bar = tk.Label(
        root,
        text="Налаштуйте підключення до Firebase",
        bd=1,
        relief=tk.SUNKEN,
        anchor=tk.W
    )
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    if not read_config():
        status_bar.config(text="Потрібно налаштувати підключення")

    root.mainloop()

if __name__ == "__main__":
    create_gui()