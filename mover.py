
import threading
import time
import random
import pyautogui
from pynput import mouse

pyautogui.FAILSAFE = True

MOVEMENT_RANGES = {
    "Small": 10,
    "Medium": 30,
    "Large": 60
}

class MouseMover(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running = threading.Event()
        self.total_moves = 0
        self.last_user_activity = time.time()
        self.path_cycle_index = 0
        self.listener = mouse.Listener(on_move=self.on_move)

    def on_move(self, x, y):
        self.last_user_activity = time.time()

    def run(self):
        self.listener.start()
        
        # Get all non-empty paths
        available_paths = [p for p in self.app.settings['paths'].values() if p]

        if available_paths:
            self.playback_loop(available_paths)
        else:
            self.random_movement_loop()

    def playback_loop(self, available_paths):
        while self.running.is_set():
            # Select the next path in the cycle
            current_path = available_paths[self.path_cycle_index]

            interval = self.app.get_interval()
            time_since_activity = time.time() - self.last_user_activity

            if time_since_activity < interval:
                remaining_wait = interval - time_since_activity
                for i in range(int(remaining_wait), 0, -1):
                    if not self.running.is_set(): break
                    self.app.update_countdown(i)
                    time.sleep(1)
                continue

            self.app.update_countdown(0)

            for point in current_path:
                if not self.running.is_set():
                    break
                if time.time() - self.last_user_activity < 1:
                    break
                
                x, y, delta_t = point
                # Introduce human-like randomness to the timing
                random_factor = random.uniform(0.8, 1.2)
                time.sleep(delta_t * random_factor)
                pyautogui.moveTo(x, y, duration=0, _pause=False)
            
            if self.running.is_set() and time.time() - self.last_user_activity >= 1:
                self.total_moves += 1
                self.app.update_total_moves(self.total_moves)
                # Move to the next path for the next cycle
                self.path_cycle_index = (self.path_cycle_index + 1) % len(available_paths)

    def random_movement_loop(self):
        while self.running.is_set():
            interval = self.app.get_interval()
            
            time_since_activity = time.time() - self.last_user_activity
            if time_since_activity < interval:
                # User is active, wait for the full interval of inactivity
                remaining_wait = interval - time_since_activity
                for i in range(int(remaining_wait), 0, -1):
                    if not self.running.is_set():
                        break
                    self.app.update_countdown(i)
                    time.sleep(1)
                continue

            # Countdown
            for i in range(interval, 0, -1):
                if not self.running.is_set():
                    break
                # If user moves mouse during countdown, reset timer
                if time.time() - self.last_user_activity < 1:
                    break # Breaks countdown, will restart main loop
                self.app.update_countdown(i)
                time.sleep(1)
            else: # Only runs if countdown loop completes without break
                if self.running.is_set():
                    self.move_randomly()



    def move_randomly(self):
        try:
            original_pos = pyautogui.position()
            movement_range_str = self.app.get_movement_range()
            pixel_range = MOVEMENT_RANGES.get(movement_range_str, 30)

            offset_x = random.randint(-pixel_range, pixel_range)
            offset_y = random.randint(-pixel_range, pixel_range)
            
            new_x = original_pos.x + offset_x
            new_y = original_pos.y + offset_y

            # Ensure the new position is on screen
            width, height = pyautogui.size()
            new_x = max(0, min(width - 1, new_x))
            new_y = max(0, min(height - 1, new_y))

            pyautogui.moveTo(new_x, new_y, duration=0.25)
            time.sleep(0.5)
            pyautogui.moveTo(original_pos.x, original_pos.y, duration=0.25)

            self.total_moves += 1
            self.app.update_total_moves(self.total_moves)
        except Exception as e:
            print(f"Error moving mouse: {e}")

    def stop(self):
        self.running.clear()
        self.listener.stop()

