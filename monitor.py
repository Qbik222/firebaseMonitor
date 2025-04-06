import threading
import time
from datetime import datetime, timedelta
import queue

class Monitor:
    def __init__(self, main_app):
        self.main_app = main_app
        self.event = threading.Event()
        self.thread = None
        self.is_active = False
        self.next_restart_time = None
        self.data_queue = queue.Queue()
        self.last_data = {}
        self.interval = 5  # Update interval in seconds

    def start(self):
        if self.is_active:
            self.main_app.log_window.add_log("Моніторинг вже активний", "INFO")
            return
            
        if not self.main_app.config_manager.read_config():
            self.main_app.show_settings()
            return

        if not self.main_app.config_manager.is_configured():
            self.main_app.log_window.add_log("Необхідно налаштувати підключення", "WARNING")
            self.main_app.show_settings()
            return

        if not self.main_app.firebase_manager.authenticate():
            self.main_app.log_window.add_log("Помилка автентифікації Firebase", "ERROR")
            return

        try:
            raw_data = self.main_app.firebase_manager.load_data()
            processed_data = self._process_firebase_data(raw_data)
            self._update_ui(processed_data)
            self.last_data = processed_data
        except Exception as e:
            self.main_app.log_window.add_log(f"Помилка первинного завантаження: {str(e)}", "ERROR")

        self.is_active = True
        self.event.set()
        self.next_restart_time = datetime.now() + timedelta(minutes=10)
        
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()

        self.main_app.root.after(100, self._process_updates)
        self.main_app.log_window.add_log("Моніторинг запущено", "INFO")
        self.main_app.status_bar.config(text="Моніторинг активний")

    def stop(self):
        if not self.is_active:
            return

        self.is_active = False
        self.event.clear()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        self._update_ui_on_stop()
        self.main_app.log_window.add_log("Моніторинг зупинено", "INFO")
        self.main_app.status_bar.config(text="Моніторинг зупинено")

    def _update_ui_on_stop(self):
        if hasattr(self.main_app, 'folder_manager'):
            self.main_app.folder_manager.close_all()

    def _process_firebase_data(self, raw_data):
        processed_data = {'frequency': {}}

        if not raw_data or 'frequency' not in raw_data:
            return processed_data

        for folder_name, folder_data in raw_data['frequency'].items():
            if not isinstance(folder_data, dict):
                continue

            frequencies = []
            for entry_id, entry_data in folder_data.items():
                try:
                    if not isinstance(entry_data, dict):
                        continue

                    freq = {
                        'name': entry_data.get('name', ''),
                        'name': entry_data.get('name', ''),
                        'timestamp': entry_data.get('timestamp', time.time()),
                        'status': entry_data.get('status', 'unknown')
                    }
                    frequencies.append(freq)
                except Exception as e:
                    self.main_app.log_window.add_log(
                        f"Помилка обробки частоти {entry_id}: {str(e)}",
                        "ERROR")
                    continue

            frequencies.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            processed_data['frequency'][folder_name] = frequencies[:2]

        return processed_data

    def _has_data_changed(self, new_data):
        """Check if the new data is different from the last data."""
        old_folders = set(self.last_data.get('frequency', {}).keys())
        new_folders = set(new_data.get('frequency', {}).keys())

        if old_folders != new_folders:
            return True

        for folder in new_folders:
            old_entries = self.last_data.get('frequency', {}).get(folder, [])
            new_entries = new_data.get('frequency', {}).get(folder, [])
            if old_entries != new_entries:
                return True

        return False

    def _update_ui(self, processed_data):
        if not hasattr(self.main_app, 'folder_manager'):
            return

        formatted_data = {}
        for folder_name, frequencies in processed_data.get('frequency', {}).items():
            formatted_data[folder_name] = [
                {
                    'frequency': f.get('name', ''),
                    'name': f.get('name', ''),
                    'timestamp': f.get('timestamp', 0)
                }
                for f in frequencies
            ]

        self.main_app.folder_manager.update_all_folders({'frequency': formatted_data})

    def _monitor_loop(self):
        while self.event.is_set():
            try:
                if datetime.now() >= self.next_restart_time:
                    self.data_queue.put(('restart', None))
                    break

                raw_data = self.main_app.firebase_manager.load_data()
                processed_data = self._process_firebase_data(raw_data)

                if not processed_data.get('frequency'):
                    self.main_app.log_window.add_log("Немає даних від Firebase", "WARNING")
                    time.sleep(self.interval)
                    continue

                if self._has_data_changed(processed_data):
                    self.data_queue.put(('update', processed_data))
                    self.last_data = processed_data

                time.sleep(self.interval)

            except Exception as e:
                self.main_app.log_window.add_log(
                    f"Критична помилка моніторингу: {str(e)}",
                    "ERROR")
                time.sleep(10)

    def _process_updates(self):
        try:
            while not self.data_queue.empty():
                action, data = self.data_queue.get_nowait()

                if action == 'update' and self.is_active:
                    self._update_ui(data)

                elif action == 'restart':
                    self.stop()
                    time.sleep(2)
                    self.start()

        except queue.Empty:
            pass

        if self.is_active:
            self.main_app.root.after(100, self._process_updates)
