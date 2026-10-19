
import tkinter as tk
from tkinter import ttk, messagebox

class GhostMouseUI:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("Ghost Mouse 👻")
        self.root.geometry("350x450")
        self.root.configure(bg='#2E2E2E')

        self.root.protocol("WM_DELETE_WINDOW", self.app.hide_window)

        self.create_styles()
        self.create_widgets()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#2E2E2E', foreground='white', font=('Segoe UI', 10))
        style.configure('TFrame', background='#2E2E2E')
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('TButton', background=[('active', '#4F4F4F')])
        style.configure('green.TButton', background='#27AE60', foreground='white')
        style.map('green.TButton', background=[('active', '#2ECC71')])
        style.configure('red.TButton', background='#C0392B', foreground='white')
        style.map('red.TButton', background=[('active', '#E74C3C')])
        style.configure('Horizontal.TScale', background='#2E2E2E')

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Ghost Mouse 👻", font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 10))

        self.status_var = tk.StringVar(value="Status: Stopped 🔴")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=('Segoe UI', 12, 'italic'))
        status_label.pack()

        self.countdown_var = tk.StringVar(value="Next move in: -- seconds")
        countdown_label = ttk.Label(main_frame, textvariable=self.countdown_var)
        countdown_label.pack()

        self.moves_var = tk.StringVar(value="Total Moves: 0")
        moves_label = ttk.Label(main_frame, textvariable=self.moves_var)
        moves_label.pack(pady=(0, 10))

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Controls ---
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(pady=5)

        ttk.Label(controls_frame, text="Interval (s):").grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.interval_var = tk.StringVar(value=str(self.app.settings['interval']))
        self.interval_entry = ttk.Entry(controls_frame, textvariable=self.interval_var, width=5)
        self.interval_entry.grid(row=0, column=1, padx=5)

        self.start_button = ttk.Button(controls_frame, text="START", style='green.TButton', command=self.app.start_mover)
        self.start_button.grid(row=0, column=2, padx=5)

        self.stop_button = ttk.Button(controls_frame, text="STOP", style='red.TButton', command=self.app.stop_mover, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=5)

        self.start_record_button = ttk.Button(controls_frame, text="Start Recording", command=self.app.start_recording)
        self.start_record_button.grid(row=1, column=0, columnspan=2, pady=5)

        self.stop_record_button = ttk.Button(controls_frame, text="Stop Recording", command=self.app.stop_recording, style='red.TButton')
        self.stop_record_button.grid(row=1, column=2, columnspan=2, pady=5)
        self.stop_record_button.grid_remove() # Hide it initially

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Path Info ---
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(pady=5)
        self.path_points_var = tk.StringVar(value="Recorded Points: 0")
        ttk.Label(path_frame, textvariable=self.path_points_var).pack()

        # --- Settings ---
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill='x', pady=5)
        ttk.Label(settings_frame, text="Path Selection", font=('Segoe UI', 12, 'bold')).pack()

        path_selection_frame = ttk.Frame(settings_frame)
        path_selection_frame.pack(pady=5)

        self.path_selection_var = tk.StringVar(value="path_1")
        
        ttk.Radiobutton(path_selection_frame, text="Path 1", variable=self.path_selection_var, value="path_1", command=self.app.on_path_selection_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(path_selection_frame, text="Path 2", variable=self.path_selection_var, value="path_2", command=self.app.on_path_selection_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(path_selection_frame, text="Path 3", variable=self.path_selection_var, value="path_3", command=self.app.on_path_selection_change).pack(side=tk.LEFT, padx=5)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Auto Key Presser ---
        keypress_frame = ttk.LabelFrame(main_frame, text="Auto Key Presser")
        keypress_frame.pack(fill="x", pady=5)

        keypress_controls_frame = ttk.Frame(keypress_frame)
        keypress_controls_frame.pack(padx=10, pady=5, fill='x')
        keypress_controls_frame.columnconfigure(1, weight=1)

        ttk.Label(keypress_controls_frame, text="Text to Type (comma-sep):").grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")
        self.keypress_keys_var = tk.StringVar()
        self.keypress_keys_entry = ttk.Entry(keypress_controls_frame, textvariable=self.keypress_keys_var)
        self.keypress_keys_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        ttk.Label(keypress_controls_frame, text="Interval (s):").grid(row=1, column=0, padx=(0, 5), pady=2, sticky="w")
        self.keypress_interval_var = tk.StringVar()
        self.keypress_interval_entry = ttk.Entry(keypress_controls_frame, textvariable=self.keypress_interval_var)
        self.keypress_interval_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        self.start_keypress_button = ttk.Button(keypress_controls_frame, text="Start Key Pressing", command=self.app.start_keypresser)
        self.start_keypress_button.grid(row=2, column=0, padx=5, pady=5)

        self.stop_keypress_button = ttk.Button(keypress_controls_frame, text="Stop Key Pressing", command=self.app.stop_keypresser, state=tk.DISABLED)
        self.stop_keypress_button.grid(row=2, column=1, padx=5, pady=5)

        self.keypress_status_label = ttk.Label(keypress_controls_frame, text="Status: Stopped", foreground="red")
        self.keypress_status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=2)

        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # --- Auto Clicker ---
        click_frame = ttk.LabelFrame(main_frame, text="Auto Clicker")
        click_frame.pack(fill="x", pady=5)

        click_controls_frame = ttk.Frame(click_frame)
        click_controls_frame.pack(padx=10, pady=5, fill='x')
        click_controls_frame.columnconfigure(1, weight=1)

        # Enable checkbox
        self.click_enabled_var = tk.BooleanVar(value=False)
        self.click_enabled_check = ttk.Checkbutton(
            click_controls_frame, 
            text="Enable Auto-Click with Mover",
            variable=self.click_enabled_var,
            command=self.on_click_enabled_change
        )
        self.click_enabled_check.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        ttk.Label(click_controls_frame, text="Click Interval (s):").grid(row=1, column=0, padx=(0, 5), pady=2, sticky="w")
        self.click_interval_var = tk.StringVar(value="5")
        self.click_interval_entry = ttk.Entry(click_controls_frame, textvariable=self.click_interval_var, width=8)
        self.click_interval_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(click_controls_frame, text="Click Type:").grid(row=2, column=0, padx=(0, 5), pady=2, sticky="w")
        self.click_type_var = tk.StringVar(value="left")
        click_type_frame = ttk.Frame(click_controls_frame)
        click_type_frame.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Radiobutton(click_type_frame, text="Left", variable=self.click_type_var, value="left").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(click_type_frame, text="Right", variable=self.click_type_var, value="right").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(click_type_frame, text="Double", variable=self.click_type_var, value="double").pack(side=tk.LEFT, padx=2)

        self.click_status_label = ttk.Label(click_controls_frame, text="Status: Stopped", foreground="red")
        self.click_status_label.grid(row=3, column=0, columnspan=2, padx=5, pady=2)



    def on_slider_change(self, value):
        self.interval_var.set(str(int(float(value))))
        self.on_settings_change()

    def on_settings_change(self, event=None):
        try:
            interval = int(self.interval_var.get())
            if interval < 5:
                self.show_warning("Interval should not be less than 5 seconds.")
            
            self.app.settings['interval'] = interval
            self.app.settings['movement_range'] = self.movement_var.get()
            self.app.save_settings()
        except ValueError:
            self.show_error("Invalid interval. Please enter a number.")

    def update_status(self, running):
        if running:
            self.status_var.set("Status: Running ✅")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.interval_entry.config(state=tk.DISABLED)
        else:
            self.status_var.set("Status: Stopped 🔴")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.interval_entry.config(state=tk.NORMAL)
            self.update_countdown("--")

    def update_countdown(self, seconds):
        self.root.after(0, lambda: self.countdown_var.set(f"Next move in: {seconds} seconds"))

    def update_total_moves(self, count):
        self.root.after(0, lambda: self.moves_var.set(f"Total Moves: {count}"))

    def update_recording_status(self, recording):
        if recording:
            self.start_record_button.grid_remove()
            self.stop_record_button.grid()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
        else:
            self.start_record_button.grid()
            self.stop_record_button.grid_remove()
            self.update_status(self.app.mover_thread and self.app.mover_thread.is_alive())

    def update_keypress_status(self, running):
        if running:
            self.keypress_status_label.config(text="Status: Running", foreground="green")
            self.start_keypress_button.config(state=tk.DISABLED)
            self.stop_keypress_button.config(state=tk.NORMAL)
            self.keypress_keys_entry.config(state=tk.DISABLED)
            self.keypress_interval_entry.config(state=tk.DISABLED)
        else:
            self.keypress_status_label.config(text="Status: Stopped", foreground="red")
            self.start_keypress_button.config(state=tk.NORMAL)
            self.stop_keypress_button.config(state=tk.DISABLED)
            self.keypress_keys_entry.config(state=tk.NORMAL)
            self.keypress_interval_entry.config(state=tk.NORMAL)

    def update_click_status(self, running):
        """Update the click automation status display"""
        if running:
            self.click_status_label.config(text="Status: Running", foreground="green")
        else:
            self.click_status_label.config(text="Status: Stopped", foreground="red")

    def on_click_enabled_change(self):
        """Handle click enabled checkbox change"""
        enabled = self.click_enabled_var.get()
        self.app.settings['click_enabled'] = enabled
        self.app.settings['click_interval'] = float(self.click_interval_var.get())
        self.app.settings['click_type'] = self.click_type_var.get()
        self.app.save_settings()

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_warning(self, message):
        messagebox.showwarning("Warning", message)

    def show_info(self, message):
        messagebox.showinfo("Info", message)
