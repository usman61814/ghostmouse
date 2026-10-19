
import tkinter as tk
import threading
import random
from human_like_mover import HumanLikeMover
from ui import GhostMouseUI
from tray import create_tray_icon
import config
import pyautogui
import time

class KeypresserThread(threading.Thread):
    def __init__(self, app, keys, interval):
        super().__init__()
        self.app = app
        self.keys = keys
        self.interval = interval
        self.running = threading.Event()
        self.daemon = True

    def run(self):
        self.running.set()
        while self.running.is_set():
            for key in self.keys:
                if not self.running.is_set():
                    break
                pyautogui.write(key.strip())
                time.sleep(self.interval)

    def stop(self):
        self.running.clear()

class RecordingThread(threading.Thread):
    def __init__(self, app, path_key):
        super().__init__()
        self.app = app
        self.path_key = path_key
        self.running = threading.Event()

    def run(self):
        self.app.settings['paths'][self.path_key] = []
        last_time = time.time()

        while self.running.is_set():
            pos = pyautogui.position()
            current_time = time.time()
            delta_t = current_time - last_time

            path = self.app.settings['paths'][self.path_key]
            if not path or pos != path[-1][:2]:
                path.append((pos.x, pos.y, delta_t))
                last_time = current_time
            
            time.sleep(0.005)

    def stop(self):
        self.running.clear()

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.settings = config.load_settings()
        if 'paths' not in self.settings or not isinstance(self.settings['paths'], dict):
            self.settings['paths'] = {
                "path_1": [],
                "path_2": [],
                "path_3": []
            }
        
        # Initialize new human-like behavior settings
        if 'human_like_enabled' not in self.settings:
            self.settings['human_like_enabled'] = True
        if 'click_enabled' not in self.settings:
            self.settings['click_enabled'] = False
        if 'click_interval' not in self.settings:
            self.settings['click_interval'] = 5
        if 'click_type' not in self.settings:
            self.settings['click_type'] = 'left'
        
        self.ui = GhostMouseUI(self.root, self)
        self.mover_thread = None
        self.recording_thread = None
        self.keypresser_thread = None
        self.click_thread = None

        self.root.withdraw()
        self.tray_icon = create_tray_icon(self)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
        
        self.ui.update_status(False)
        self.load_keypresser_settings()
        self.load_click_settings()

    def start_mover(self):
        try:
            interval = int(self.ui.interval_var.get())
            if interval < 5:
                self.ui.show_warning("Interval must be at least 5 seconds.")
                return
            self.settings['interval'] = interval
            config.save_settings(self.settings)
        except ValueError:
            self.ui.show_error("Invalid interval. Please enter a whole number.")
            return

        if self.mover_thread is None or not self.mover_thread.is_alive():
            self.mover_thread = HumanLikeMover(self)
            self.mover_thread.running.set()
            self.mover_thread.start()
            self.ui.update_status(True)
            
            # Start click automation if enabled
            if self.settings.get('click_enabled', False):
                self.start_click_automation()

    def stop_mover(self):
        if self.mover_thread and self.mover_thread.is_alive():
            self.mover_thread.stop()
            self.mover_thread.join()
        self.stop_click_automation()
        self.ui.update_status(False)

    def start_keypresser(self):
        keys_str = self.ui.keypress_keys_var.get()
        interval_str = self.ui.keypress_interval_var.get()

        if not keys_str:
            self.ui.show_error("No keys specified for key presser.")
            return

        try:
            interval = float(interval_str)
            if interval <= 0:
                raise ValueError()
        except ValueError:
            self.ui.show_error("Invalid interval. Please enter a positive number.")
            return

        keys = [k.strip() for k in keys_str.split(',')]
        self.settings["keypress_keys"] = keys_str
        self.settings["keypress_interval"] = interval
        self.save_settings()

        if self.keypresser_thread is None or not self.keypresser_thread.is_alive():
            self.keypresser_thread = KeypresserThread(self, keys, interval)
            self.keypresser_thread.start()
            self.ui.update_keypress_status(True)

    def stop_keypresser(self):
        if self.keypresser_thread and self.keypresser_thread.is_alive():
            self.keypresser_thread.stop()
            self.keypresser_thread.join()
        self.ui.update_keypress_status(False)

    def exit_app(self):
        self.stop_mover()
        if self.recording_thread:
            self.stop_recording()
        if self.keypresser_thread:
            self.stop_keypresser()
        self.stop_click_automation()
        self.tray_icon.stop()
        self.root.quit()

    def show_window(self):
        self.root.after(0, self.root.deiconify)

    def hide_window(self):
        self.root.withdraw()

    def get_interval(self):
        return self.settings.get('interval', 60)

    def get_movement_range(self):
        return self.settings.get('movement_range', 'Medium')

    def update_countdown(self, seconds):
        self.ui.update_countdown(seconds)

    def update_total_moves(self, count):
        self.ui.update_total_moves(count)

    def save_settings(self):
        config.save_settings(self.settings)

    def start_recording(self):
        selected_path = self.ui.path_selection_var.get()
        self.ui.show_info(f"Recording started for {selected_path.replace('_', ' ').title()}. Move your mouse.")
        self.ui.update_recording_status(True)

        self.recording_thread = RecordingThread(self, selected_path)
        self.recording_thread.running.set()
        self.recording_thread.start()

    def stop_recording(self):
        if self.recording_thread:
            self.recording_thread.stop()
            self.recording_thread.join()
            self.recording_thread = None
        
        self.save_settings()
        self.ui.update_recording_status(False)
        self.update_path_points()
        selected_path = self.ui.path_selection_var.get()
        point_count = len(self.settings['paths'].get(selected_path, []))
        self.ui.show_info(f"Path recording finished. {point_count} points saved.")

    def update_path_points(self):
        selected_path = self.ui.path_selection_var.get()
        count = len(self.settings['paths'].get(selected_path, []))
        self.ui.path_points_var.set(f"Recorded Points: {count}")

    def on_path_selection_change(self):
        self.update_path_points()

    def load_keypresser_settings(self):
        self.ui.keypress_keys_var.set(self.settings.get("keypress_keys", ""))
        self.ui.keypress_interval_var.set(str(self.settings.get("keypress_interval", 10)))

    def load_click_settings(self):
        self.ui.click_enabled_var.set(self.settings.get("click_enabled", False))
        self.ui.click_interval_var.set(str(self.settings.get("click_interval", 5)))
        self.ui.click_type_var.set(self.settings.get("click_type", "left"))

    def start_click_automation(self):
        """Start automated mouse clicking"""
        if self.click_thread is None or not self.click_thread.is_alive():
            self.click_thread = ClickAutomationThread(self)
            self.click_thread.running.set()
            self.click_thread.start()
            self.ui.update_click_status(True)

    def stop_click_automation(self):
        """Stop automated mouse clicking"""
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.stop()
            self.click_thread.join()
        self.ui.update_click_status(False)

    def run(self):
        self.root.mainloop()


class ClickAutomationThread(threading.Thread):
    """Thread for human-like automated mouse clicking"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running = threading.Event()
        self.daemon = True
        
        # Human behavior patterns
        self.click_count = 0
        self.cluster_size = 0
        self.in_cluster = False
        self.distraction_chance = 0.15  # 15% chance to get distracted
        self.cluster_chance = 0.3       # 30% chance to start a click cluster
        self.min_interval = 2           # Minimum seconds between clicks
        
    def generate_human_interval(self, base_interval):
        """Generate a human-like interval with variation"""
        # Base variation: ±30%
        interval = base_interval * random.uniform(0.7, 1.3)
        
        # Occasionally take longer (distraction)
        if random.random() < self.distraction_chance:
            interval *= random.uniform(1.5, 3.0)
            print("[AutoClick] Got distracted...")
        
        # Ensure minimum interval
        return max(self.min_interval, interval)
    
    def decide_next_click_timing(self, base_interval):
        """Decide if we should cluster clicks or take a break"""
        if not self.in_cluster:
            # Maybe start a cluster (rapid clicks)
            if random.random() < self.cluster_chance:
                self.in_cluster = True
                self.cluster_size = random.randint(2, 5)
                self.click_count = 0
                print(f"[AutoClick] Starting cluster of {self.cluster_size} clicks")
                return random.uniform(0.3, 0.8)  # Fast clicks in cluster
            else:
                # Normal single click with human interval
                return self.generate_human_interval(base_interval)
        else:
            # In a cluster
            self.click_count += 1
            if self.click_count >= self.cluster_size:
                # Cluster finished, take a break
                self.in_cluster = False
                break_time = random.uniform(3, 8)
                print(f"[AutoClick] Cluster done, taking {break_time:.1f}s break")
                return break_time
            else:
                # Continue cluster with fast interval
                return random.uniform(0.3, 0.8)
    
    def add_position_variation(self, x, y):
        """Add human-like position variation (sometimes more, sometimes less precise)"""
        # Humans are sometimes precise, sometimes sloppy
        precision = random.choice(['high', 'medium', 'low'])
        
        if precision == 'high':
            # Very precise (±1 pixel)
            offset_x = random.gauss(0, 1)
            offset_y = random.gauss(0, 1)
        elif precision == 'medium':
            # Normal (±3 pixels)
            offset_x = random.gauss(0, 3)
            offset_y = random.gauss(0, 3)
        else:
            # Sloppy (±8 pixels) - human was careless
            offset_x = random.gauss(0, 8)
            offset_y = random.gauss(0, 8)
        
        return x + offset_x, y + offset_y
    
    def perform_click(self, click_type):
        """Perform click with human-like behavior"""
        # Sometimes hesitate before clicking (aiming)
        if random.random() < 0.2:
            time.sleep(random.uniform(0.1, 0.4))
        
        # Perform the click
        if click_type == 'left':
            # Sometimes do a quick double-click instead of single
            if random.random() < 0.05:
                pyautogui.doubleClick()
                print("[AutoClick] Double-click (accidental)")
            else:
                pyautogui.click()
        elif click_type == 'right':
            pyautogui.rightClick()
        elif click_type == 'double':
            pyautogui.doubleClick()
        
        # Sometimes click and hold briefly (drag intention that changed)
        if random.random() < 0.03:
            time.sleep(random.uniform(0.1, 0.3))
            print("[AutoClick] Brief hold after click")
    
    def run(self):
        self.running.set()
        base_interval = float(self.app.settings.get('click_interval', 5))
        click_type = self.app.settings.get('click_type', 'left')
        
        while self.running.is_set():
            try:
                # Decide next click timing (cluster or normal)
                wait_time = self.decide_next_click_timing(base_interval)
                
                # Wait with ability to interrupt
                elapsed = 0
                check_interval = 0.1
                while elapsed < wait_time and self.running.is_set():
                    time.sleep(check_interval)
                    elapsed += check_interval
                
                if not self.running.is_set():
                    break
                
                # Get current position with human-like variation
                current_pos = pyautogui.position()
                target_x, target_y = self.add_position_variation(current_pos.x, current_pos.y)
                
                # Move to position with slight delay (aiming)
                move_duration = random.uniform(0.05, 0.2)
                pyautogui.moveTo(target_x, target_y, duration=move_duration)
                
                # Perform the click
                self.perform_click(click_type)
                
                # Occasionally move mouse slightly after click (restless hand)
                if random.random() < 0.1:
                    rest_x = target_x + random.gauss(0, 5)
                    rest_y = target_y + random.gauss(0, 5)
                    pyautogui.moveTo(rest_x, rest_y, duration=0.1)
                    
            except Exception as e:
                print(f"[AutoClick] Error: {e}")
                time.sleep(1)
    
    def stop(self):
        self.running.clear()


if __name__ == "__main__":
    app = MainApp()
    app.run()

