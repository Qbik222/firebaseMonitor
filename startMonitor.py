import tkinter as tk
from tkinter import messagebox, scrolledtext
import firebase_admin
from firebase_admin import credentials, db
import threading
import time
import re
import pyperclip
from datetime import datetime, timedelta

# Глобальні змінні
json_file = ""
firebase_url = ""
audio_save_path = ""
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

def read_config():
    global json_file, firebase_url, audio_save_path
    try:
        with open('config.txt', 'r') as config_file:
            lines = config_file.readlines()
            for line in lines:
                if line.startswith('json_file_path='):
                    json_file = line.strip().split('=')[1]
                elif line.startswith('audio_save_path='):
                    audio_save_path = line.strip().split('=')[1]
                elif line.startswith('firebase_url='):
                    firebase_url = line.strip().split('=')[1]
    except Exception as e:
        messagebox.showerror("Помилка", f"Помилка при читанні конфігураційного файлу: {e}")

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

    # Вивід у консоль
    print(log_line, end='')

    # Вивід у вікно логу, якщо воно відкрите
    if log_text and log_text.winfo_exists():
        log_text.config(state='normal')
        log_text.insert('end', log_line)
        log_text.see('end')
        log_text.config(state='disabled')

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

        # Кнопка закриття
        close_btn = tk.Button(log_window, text="Закрити лог", command=toggle_log_window)
        close_btn.pack(pady=5)

        # Текстове поле для логу
        log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, state='disabled')
        log_text.pack(expand=True, fill='both', padx=5, pady=5)

        # Захист від закриття через хрестик
        log_window.protocol("WM_DELETE_WINDOW", toggle_log_window)

def on_flag_button_click(i):
    global last_button, last_frequency
    if last_button:
        last_button.config(bg="SystemButtonFace")
    last_button = flag_buttons[i]
    flag_buttons[i].config(bg="yellow")
    print(f"Кнопка {i+1} була натиснута.")
    button_data = flag_buttons[i].cget('text')
    frequency_match = re.search(r'(\d+\.\d+)', button_data)
    if frequency_match:
        current_frequency = frequency_match.group(1)
        pyperclip.copy(current_frequency)
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = f"[{timestamp}] Частота {current_frequency} скопійована до буферу обміну"
        print(message)
        log_message(message)  # Додано логування копіювання частоти
        status_label = tk.Label(root, text=message, fg="green", font=('Arial', 14))
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
            # Логуємо нову частоту
            log_message(f"Нова частота в базі: {freq_value}")

    sorted_entries = sorted(unique_entries.values(),
                          key=lambda x: x.get('timestamp', 0),
                          reverse=True)

    latest_entries = sorted_entries[:6]

    for index in range(len(flag_buttons)):
        if index < len(latest_entries):
            entry = latest_entries[index]
            timestamp = entry.get('timestamp', 'Немає timestamp')
            value = entry.get('value', entry.get('name', 'Немає значення'))

            if isinstance(timestamp, (int, float)):
                try:
                    timestamp_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    timestamp_str = "Невірний timestamp"
            else:
                timestamp_str = str(timestamp)

            new_button_text = f"{value} - {timestamp_str}"

            if index < len(current_buttons_data) and current_buttons_data[index] != new_button_text:
                old_value = current_buttons_data[index].split(' - ')[0] if current_buttons_data[index] else None

                # Логуємо зміну частоти
                if old_value and old_value != "Немає значення":
                    log_message(f"Частота змінилась: {old_value} -> {value}")

                flag_buttons[index].config(text=new_button_text, state="normal")

                if last_frequency != value and value != "Немає значення":
                    flag_buttons[index].config(bg="lightgreen")
                    last_frequency = value
                else:
                    flag_buttons[index].config(bg="SystemButtonFace")
        else:
            # Логуємо видалення частоти
            old_value = current_buttons_data[index].split(' - ')[0] if index < len(current_buttons_data) and current_buttons_data[index] else None
            if old_value and old_value != "Немає значення":
                log_message(f"Частота видалена: {old_value}")

            flag_buttons[index].config(text="", state="disabled", bg="SystemButtonFace")

def refresh_data():
    global last_frequency, monitoring_active
    monitoring_active = True
    next_restart_time = datetime.now() + timedelta(minutes=10)
    last_data = None

    while monitoring_event.is_set():
        try:
            log_message(f"Перевірка оновлень... Наступна перевірка через 5 сек")
            current_data = load_data_from_firebase()

            if current_data and current_data != last_data:
                root.after(0, lambda: update_data_display(root, current_data))
                last_data = current_data

            if datetime.now() >= next_restart_time:
                log_message("Автоматичний перезапуск моніторингу")
                stop_monitoring()
                time.sleep(2)
                start_processing()
                break

            time.sleep(5)

        except Exception as e:
            log_message(f"Помилка при оновленні: {e}", "ERROR")
            time.sleep(10)

def start_processing():
    global monitoring_event, data_thread, monitoring_active
    if monitoring_active:
        log_message("Моніторинг вже активний")
        return
    if not json_file or not audio_save_path or not firebase_url:
        messagebox.showerror("Помилка", "Будь ласка, перевірте налаштування у конфігураційному файлі.")
        return
    firebase_db = authenticate_with_firebase()
    if firebase_db:
        monitoring_event.set()
        data_thread = threading.Thread(target=refresh_data)
        data_thread.daemon = True
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

def create_gui():
    global flag_buttons, data_thread, root

    root = tk.Tk()
    root.title("Відображення даних з Firebase")
    root.geometry("500x500")

    # Фрейм для кнопок керування
    control_frame = tk.Frame(root)
    control_frame.pack(pady=10)

    start_button = tk.Button(control_frame, text="Запуск", command=start_processing)
    start_button.pack(side='left', padx=5)

    stop_button = tk.Button(control_frame, text="Зупинити", command=stop_monitoring)
    stop_button.pack(side='left', padx=5)

    log_button = tk.Button(control_frame, text="Показати лог", command=toggle_log_window)
    log_button.pack(side='left', padx=5)

    # Фрейм для кнопок частот
    freq_frame = tk.Frame(root)
    freq_frame.pack(pady=10, fill='both', expand=True)

    flag_buttons = []
    for i in range(6):
        flag_button = tk.Button(freq_frame, text=f"Частота {i+1}", width=25, height=2,
                              command=lambda i=i: on_flag_button_click(i))
        flag_button.pack(pady=5)
        flag_buttons.append(flag_button)

    root.mainloop()

if __name__ == "__main__":
    read_config()
    create_gui()