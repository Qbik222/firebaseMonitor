import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pyperclip 

class FolderFrame:
    def __init__(self, master, folder_name):
        self.master = master
        self.folder_name = folder_name
        self.frequencies = []
        self.cell_data = {}
        self.NUM_CELLS = 2  # Only 2 cells
        self.CELL_WIDTH = 150  # Increased cell width
        
        # Main frame for the folder
        self.main_frame = tk.Frame(master, padx=10, pady=5, bd=2, relief=tk.GROOVE)
        self.main_frame.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5, anchor='nw')
        
        self._setup_ui()

    def _setup_ui(self):
        self.cells = []
        
        # Folder name label
        header_frame = tk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text=f"Папка: {self.folder_name}", 
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Cells frame
        cells_frame = tk.Frame(self.main_frame)
        cells_frame.pack(fill=tk.X, pady=5)
        
        # Create exactly 2 cells
        for i in range(self.NUM_CELLS):
            self._create_cell(cells_frame, i)
        
        # Status label
        self.status_label = tk.Label(self.main_frame, text="", fg="blue")
        self.status_label.pack()

    def _create_cell(self, parent, cell_id):
        """Create a single cell with increased width"""
        cell_frame = tk.Frame(
            parent, 
            width=self.CELL_WIDTH, 
            height=70, 
            relief=tk.RAISED, 
            borderwidth=1, 
            bg='white'
        )
        cell_frame.pack_propagate(False)  # Prevent cell from resizing
        cell_frame.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)
        
        # Cell header
        header = tk.Frame(cell_frame)
        header.pack(fill=tk.X)
        
        tk.Label(
            header, 
            text=f"Комірка {cell_id+1}", 
            font=('Arial', 8)
        ).pack(side=tk.LEFT)
        
        # Cell content
        freq_label = tk.Label(
            cell_frame, 
            text="", 
            font=('Arial', 10), 
            bg="white"
        )
        freq_label.pack(expand=True)

        time_label = tk.Label(
            cell_frame, 
            text="", 
            font=('Arial', 8), 
            bg="white"
        )
        time_label.pack()
        
        # Store references
        self.cells.append({
            'id': cell_id,
            'frame': cell_frame,
            'freq_label': freq_label,
            'time_label': time_label
        })
        
        # Initialize data
        self.cell_data[cell_id] = {
            'frequency': '',
            'original_name': '',
            'timestamp': 0
        }
        
        # Bind events with hover effects
        for widget in [cell_frame, freq_label, time_label]:
            widget.bind("<Button-1>", self._create_click_handler(cell_id))
            widget.bind("<Enter>", lambda e, cf=cell_frame, fl=freq_label, tl=time_label: 
                self._on_enter(cf, fl, tl))
            widget.bind("<Leave>", lambda e, cf=cell_frame, fl=freq_label, tl=time_label: 
                self._on_leave(cf, fl, tl))

    def _on_enter(self, cell_frame, freq_label, time_label):
        """Handle mouse enter - green background and pointer cursor"""
        cell_frame.config(bg="lightgreen", cursor="hand2")
        freq_label.config(bg="lightgreen")
        time_label.config(bg="lightgreen")

    def _on_leave(self, cell_frame, freq_label, time_label):
        """Handle mouse leave - restore original style"""
        cell_frame.config(bg="white", cursor="")
        freq_label.config(bg="white")
        time_label.config(bg="white")

    def _create_click_handler(self, cell_id):
        """Create click handler"""
        def handler(event):
            self._copy_to_clipboard(cell_id)
            return "break"
        return handler

    def _copy_to_clipboard(self, cell_index):
        """Copy frequency to clipboard"""
        try:
            cell_info = self.cell_data.get(cell_index, {})
            freq = cell_info.get('original_name') or cell_info.get('frequency', '')
            
            if freq:
                pyperclip.copy(str(freq))
                self._show_status(f"Скопійовано: {freq}")
            else:
                self._show_status("Немає частоти для копіювання")
        except Exception as e:
            print(f"Помилка копіювання: {e}")
            self._show_status("Помилка при копіюванні")

    def _show_status(self, message):
        """Show status message"""
        self.status_label.config(text=message)
        self.master.after(1500, lambda: self.status_label.config(text=""))

    def update_frequencies(self, folder_data):
        """Update frequencies display"""
        entries = list(folder_data.values()) if isinstance(folder_data, dict) else folder_data
        
        self.frequencies = entries[-self.NUM_CELLS:] if entries else []
        
        for i, freq_data in enumerate(self.frequencies):
            # Update data
            self.cell_data[i] = {
                'frequency': freq_data.get('name', freq_data.get('frequency', '')),
                'original_name': freq_data.get('original_name', ''),
                'timestamp': freq_data.get('timestamp', 0)
            }
            
            # Update display
            freq = self.cell_data[i]['frequency']
            timestamp = self.cell_data[i]['timestamp']
            
            time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M") if timestamp else ""
            
            self.cells[i]['freq_label'].config(text=freq)
            self.cells[i]['time_label'].config(text=time_str)
        
        # Clear remaining cells
        for i in range(len(self.frequencies), self.NUM_CELLS):
            self.cell_data[i] = {'frequency': '', 'original_name': '', 'timestamp': 0}
            self.cells[i]['freq_label'].config(text="")
            self.cells[i]['time_label'].config(text="")

    def destroy(self):
        """Destroy the frame"""
        self.main_frame.destroy()


class FolderManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.frames = {}  # {folder_name: FolderFrame}
        
        # Create scrollable container
        self.container = tk.Frame(main_app.root)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = tk.Scrollbar(
            self.container, 
            orient="vertical", 
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize to handle wrapping
        self.canvas.bind("<Configure>", self._handle_canvas_resize)
        self.last_width = 0

    def _handle_canvas_resize(self, event):
        """Handle canvas resize to adjust wrapping of frames"""
        if event.width == self.last_width:
            return
            
        self.last_width = event.width
        self._arrange_frames()

    def _arrange_frames(self):
        """Arrange frames in rows with wrapping"""
        if not self.frames:
            return
            
        # Get all folder frames in order
        frames = [frame for frame in self.frames.values()]
        
        # Calculate how many fit in a row
        frame_width = frames[0].main_frame.winfo_reqwidth()
        frames_per_row = max(1, self.last_width // frame_width)
        
        # Clear current packing
        for frame in frames:
            frame.main_frame.pack_forget()
        
        # Repack in grid-like fashion
        for i, frame in enumerate(frames):
            row = i // frames_per_row
            col = i % frames_per_row
            frame.main_frame.grid(row=row, column=col, sticky='nw', padx=5, pady=5)
        
        # Update the scrollable frame's size
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def update_all_folders(self, frequencies_data):
        """Update all folders"""
        if not frequencies_data or 'frequency' not in frequencies_data:
            return
            
        folders_data = frequencies_data['frequency']
        
        # First update existing folders with your custom names
        for folder_name in list(self.frames.keys()):
            if folder_name in folders_data:
                self.frames[folder_name].update_frequencies(folders_data[folder_name])
        
        # Then add any new folders that appeared in the database
        for folder_name, folder_data in folders_data.items():
            if folder_name not in self.frames:
                self.frames[folder_name] = FolderFrame(self.scrollable_frame, folder_name)
                self.frames[folder_name].update_frequencies(folder_data)
        
        # Remove folders that are no longer in the database
        for folder_name in list(self.frames.keys()):
            if folder_name not in folders_data:
                self.frames[folder_name].destroy()
                del self.frames[folder_name]
        
        # Rearrange frames after update
        self._arrange_frames()

    def update_folder(self, folder_name, folder_data):
        """Update single folder"""
        if folder_name not in self.frames:
            self.frames[folder_name] = FolderFrame(self.scrollable_frame, folder_name)
        self.frames[folder_name].update_frequencies(folder_data)

    def close_all(self):
        """Close all folders"""
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}