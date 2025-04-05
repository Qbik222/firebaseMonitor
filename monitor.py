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
            self.main_app.log_window.log("Моніторинг вже активний", "INFO")
            return
            
        if not self.main_app.config_manager.read_config():
            self.main_app.show_settings()
            return

        if not self.main_app.config_manager.is_configured():
            self.main_app.log_window.log("Необхідно налаштувати підключення", "WARNING")
            self.main_app.show_settings()
            return

        if not self.main_app.firebase_manager.authenticate():
            self.main_app.log_window.log("Помилка автентифікації Firebase", "ERROR")
            return

        # Initial data load
        try:
            raw_data = self.main_app.firebase_manager.load_data()
            processed_data = self._process_firebase_data(raw_data)
            self._update_all_folders(processed_data)
        except Exception as e:
            self.main_app.log_window.log(f"Помилка первинного завантаження: {str(e)}", "ERROR")

        self.is_active = True
        self.event.set()
        self.next_restart_time = datetime.now() + timedelta(minutes=10)
        
        self.thread = threading.Thread(target=self._monitor_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Start processing updates in main thread
        self.main_app.root.after(100, self.process_updates)
        
        self.main_app.log_window.log("Моніторинг запущено", "INFO")
        self.main_app.status_bar.config(text="Моніторинг активний")

    def stop(self):
        if not self.is_active:
            return
            
        self.is_active = False
        self.event.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
            
        self._update_ui_on_stop()
        self.main_app.log_window.log("Моніторинг зупинено", "INFO")
        self.main_app.status_bar.config(text="Моніторинг зупинено")

    def _update_ui_on_stop(self):
        """Update UI when monitoring stops"""
        if hasattr(self.main_app, 'folder_manager'):
            for frame in self.main_app.folder_manager.frames.values():
                for cell in frame.cells:
                    cell['frame'].config(bg='white')
                    cell['freq_label'].config(text="--", bg="white")
                    cell['time_label'].config(text="Сканування зупинено", bg="white")

    def _process_firebase_data(self, raw_data):
        """Process Firebase data into internal format"""
        processed_data = {}
        
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
                        'original_name': entry_data.get('original_name', ''),
                        'timestamp': entry_data.get('timestamp', time.time()),
                        'status': entry_data.get('status', 'unknown')
                    }
                    frequencies.append(freq)
                except Exception as e:
                    self.main_app.log_window.log(
                        f"Помилка обробки частоти {entry_id}: {str(e)}", 
                        "ERROR")
                    continue
            
            # Sort by timestamp (newest first) and limit to 2 entries
            frequencies.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            processed_data[folder_name] = frequencies[:2]
            
        return processed_data

    def _update_all_folders(self, processed_data):
        """Update all folder displays"""
        if not hasattr(self.main_app, 'folder_manager'):
            return
            
        for folder_name, frequencies in processed_data.items():
            self.main_app.folder_manager.update_folder(
                folder_name, 
                [{'name': f['name'], 
                  'timestamp': f['timestamp'],
                  'original_name': f['original_name']} 
                 for f in frequencies]
            )

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.event.is_set():
            try:
                # Check restart time
                if datetime.now() >= self.next_restart_time:
                    self.data_queue.put(('restart', None))
                    break
                
                # Get data
                raw_data = self.main_app.firebase_manager.load_data()
                processed_data = self._process_firebase_data(raw_data)
                
                if not processed_data:
                    self.main_app.log_window.log("Немає даних від Firebase", "WARNING")
                    time.sleep(self.interval)
                    continue
                
                # Detect updated folders
                updated_folders = []
                for folder_name, frequencies in processed_data.items():
                    if (folder_name not in self.last_data or 
                        frequencies != self.last_data.get(folder_name, [])):
                        updated_folders.append((folder_name, frequencies))
                
                if updated_folders:
                    self.data_queue.put(('update', processed_data))
                    self.last_data = processed_data
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.main_app.log_window.log(
                    f"Критична помилка моніторингу: {str(e)}", 
                    "ERROR")
                time.sleep(10)

    def process_updates(self):
        """Process updates in main thread"""
        try:
            while not self.data_queue.empty():
                action, data = self.data_queue.get_nowait()
                
                if action == 'update' and self.is_active:
                    self._update_all_folders(data)
                        
                elif action == 'restart':
                    self.stop()
                    time.sleep(2)
                    self.start()
                    
        except queue.Empty:
            pass
            
        if self.is_active:
            self.main_app.root.after(100, self.process_updates)