import tkinter as tk
from datetime import datetime
import pyperclip

class FolderFrame:
    def __init__(self, master, folder_name):
        self.master = master
        self.folder_name = folder_name
        self.frequencies = []
        self.cell_data = {}
        self.NUM_CELLS = 2
        self.CELL_WIDTH = 150
        
        self.main_frame = tk.Frame(master, padx=10, pady=5, bd=2, relief=tk.GROOVE)
        # self.main_frame.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5, anchor='nw')
        self.main_frame.grid(sticky='w', padx=5, pady=5)

        self._setup_ui()

    def _setup_ui(self):
        self.cells = []
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text=f"Папка: {self.folder_name}", 
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        cells_frame = tk.Frame(self.main_frame)
        cells_frame.pack(fill=tk.X, pady=5)
        
        for i in range(self.NUM_CELLS):
            self._create_cell(cells_frame, i)
        
        self.status_label = tk.Label(self.main_frame, text="", fg="blue")
        self.status_label.pack()

    def _create_cell(self, parent, cell_id):
        cell_frame = tk.Frame(
            parent, 
            width=self.CELL_WIDTH, 
            height=70, 
            relief=tk.RAISED, 
            borderwidth=1, 
            bg='white'
        )
        cell_frame.pack_propagate(False)
        cell_frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)
        
        header = tk.Frame(cell_frame)
        header.pack(fill=tk.X)
        
        tk.Label(header, text=f"Комірка {cell_id+1}", font=('Arial', 8)).pack(side=tk.LEFT)
        
        freq_label = tk.Label(cell_frame, text="", font=('Arial', 10), bg="white")
        freq_label.pack(expand=True)

        time_label = tk.Label(cell_frame, text="", font=('Arial', 8), bg="white")
        time_label.pack()
        
        self.cells.append({
            'id': cell_id,
            'frame': cell_frame,
            'freq_label': freq_label,
            'time_label': time_label
        })
        
        self.cell_data[cell_id] = {
            'frequency': '',
            'original_name': '',
            'timestamp': 0
        }
        
        for widget in [cell_frame, freq_label, time_label]:
            widget.bind("<Button-1>", self._create_click_handler(cell_id))
            widget.bind("<Enter>", lambda e, cf=cell_frame, fl=freq_label, tl=time_label: 
                self._on_enter(cf, fl, tl))
            widget.bind("<Leave>", lambda e, cf=cell_frame, fl=freq_label, tl=time_label: 
                self._on_leave(cf, fl, tl))
            

    def _on_enter(self, cell_frame, freq_label, time_label):
        cell_frame.config(bg="lightgreen", cursor="hand2")
        freq_label.config(bg="lightgreen")
        time_label.config(bg="lightgreen")

    def _on_leave(self, cell_frame, freq_label, time_label):
        cell_frame.config(bg="white", cursor="")
        freq_label.config(bg="white")
        time_label.config(bg="white")

    def _create_click_handler(self, cell_id):
        def handler(event):
            self._copy_to_clipboard(cell_id)
            return "break"
        return handler

    def _copy_to_clipboard(self, cell_index):
        try:
            cell_info = self.cell_data.get(cell_index, {})
            freq = cell_info.get('original_name') or cell_info.get('frequency', '')
            
            if freq:
                pyperclip.copy(str(freq))
                self._show_status(f"Скопійовано: {freq}")
            else:
                self._show_status("Немає частоти для копіювання")
        except Exception as e:
            self._show_status("Помилка при копіюванні")

    def _show_status(self, message):
        self.status_label.config(text=message)
        self.master.after(1500, lambda: self.status_label.config(text=""))

    def _highlight_cell(self, i):
        cell = self.cells[0]
        cell['frame'].config(bg='green')
        cell['freq_label'].config(bg='green')
        cell['time_label'].config(bg='green')

        def restore():
            cell['frame'].config(bg='white')
            cell['freq_label'].config(bg='white')
            cell['time_label'].config(bg='white')

        cell['frame'].after(2000, restore)

    def update_frequencies(self, folder_data):
        entries = list(folder_data.values()) if isinstance(folder_data, dict) else folder_data
        self.frequencies = entries[:self.NUM_CELLS] if entries else []

        for i, freq_data in enumerate(self.frequencies):
            new_frequency = freq_data.get('frequency', freq_data.get('name', ''))
            new_original_name = freq_data.get('original_name', '')
            new_timestamp = freq_data.get('timestamp', 0)

            # Перевірка, чи змінились дані
            prev_data = self.cell_data.get(i, {})
            is_new = (
                new_frequency != prev_data.get('frequency') or
                new_original_name != prev_data.get('original_name') or
                new_timestamp != prev_data.get('timestamp')
            )

            # Оновлення cell_data
            self.cell_data[i] = {
                'frequency': new_frequency,
                'original_name': new_original_name,
                'timestamp': new_timestamp
            }

            # Відображення
            freq = new_original_name or new_frequency
            time_str = datetime.fromtimestamp(new_timestamp).strftime("%H:%M") if new_timestamp else ""

            self.cells[i]['freq_label'].config(text=freq)
            self.cells[i]['time_label'].config(text=time_str)

            # Якщо нові дані — фарбуємо
            if is_new:
                self._highlight_cell(i)

        # Очищення порожніх комірок
        for i in range(len(self.frequencies), self.NUM_CELLS):
            self.cell_data[i] = {'frequency': '', 'original_name': '', 'timestamp': 0}
            self.cells[i]['freq_label'].config(text="")
            self.cells[i]['time_label'].config(text="") 

    def destroy(self):
        self.main_frame.destroy()


class FolderManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.frames = {}
        
        self.container = tk.Frame(main_app.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind("<Configure>", self._handle_canvas_resize)
        self.last_width = 0

    def _handle_canvas_resize(self, event):
        if event.width == self.last_width:
            return
        self.last_width = event.width
        self._arrange_frames()

    def _arrange_frames(self):
        if not self.frames:
            return
            
        frames = [frame for frame in self.frames.values()]
        frame_width = frames[0].main_frame.winfo_reqwidth() if frames else 200
        frames_per_row = max(1, self.last_width // frame_width)
        
        for frame in frames:
            frame.main_frame.pack_forget()
            frame.main_frame.grid_forget()
        
        for i, frame in enumerate(frames):
            row = i // frames_per_row
            col = i % frames_per_row
            frame.main_frame.grid(row=row, column=col, sticky='nw', padx=5, pady=5)
        
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def update_all_folders(self, frequencies_data):
        # if not frequencies_data or 'frequency' not in frequencies_data:
        #     self.close_all()
        #     return
            
        folders_data = frequencies_data['frequency']
        current_folders = set(self.frames.keys())
        new_folders = set(folders_data.keys())
        
        for folder_name in current_folders - new_folders:
            self.frames[folder_name].destroy()
            del self.frames[folder_name]
        
        for folder_name in new_folders - current_folders:
            self.frames[folder_name] = FolderFrame(self.scrollable_frame, folder_name)
        
        for folder_name, folder_data in folders_data.items():
            if folder_name in self.frames:
                self.frames[folder_name].update_frequencies(folder_data)
        
        self._arrange_frames()

    def close_all(self):
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}