
import threading
import time
import random
import math
import pyautogui
from pynput import mouse

pyautogui.FAILSAFE = True

MOVEMENT_RANGES = {
    "Small": 10,
    "Medium": 30,
    "Large": 60
}

class HumanLikeMover(threading.Thread):
    """
    Advanced human-like mouse movement simulator with:
    - Bézier curve paths
    - Variable speed (acceleration/deceleration)
    - Random pauses and distractions
    - Overshoot and correction behavior
    - Hand jitter simulation
    """
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running = threading.Event()
        self.total_moves = 0
        self.last_user_activity = time.time()
        self.path_cycle_index = 0
        self.listener = mouse.Listener(on_move=self.on_move)
        
        # Human behavior settings
        self.overshoot_chance = 0.15  # 15% chance to overshoot
        self.pause_chance = 0.1       # 10% chance to pause mid-movement
        self.distraction_chance = 0.05  # 5% chance to get distracted
        self.jitter_amount = 2        # Pixels of hand jitter
        
    def on_move(self, x, y):
        self.last_user_activity = time.time()
        
    def bezier_curve(self, p0, p1, p2, p3, t):
        """Calculate point on cubic Bézier curve at parameter t (0-1)"""
        x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
        return (x, y)
    
    def generate_control_points(self, start, end):
        """Generate random control points for Bézier curve to create natural arc"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Create perpendicular offset for curve
        offset_factor = random.uniform(0.2, 0.4)
        offset_x = -dy * offset_factor
        offset_y = dx * offset_factor
        
        # Add some randomness to control points
        jitter = distance * 0.1
        
        cp1 = (
            start[0] + dx * 0.3 + offset_x + random.uniform(-jitter, jitter),
            start[1] + dy * 0.3 + offset_y + random.uniform(-jitter, jitter)
        )
        cp2 = (
            start[0] + dx * 0.7 + offset_x + random.uniform(-jitter, jitter),
            start[1] + dy * 0.7 + offset_y + random.uniform(-jitter, jitter)
        )
        
        return cp1, cp2
    
    def ease_in_out(self, t):
        """Ease-in-out function for natural acceleration/deceleration"""
        return t * t * (3 - 2 * t)
    
    def ease_out(self, t):
        """Ease-out function for deceleration"""
        return 1 - (1 - t) ** 2
    
    def ease_in(self, t):
        """Ease-in function for acceleration"""
        return t ** 2
    
    def calculate_movement_speed(self, progress, base_speed):
        """Calculate variable speed based on progress through movement"""
        # Humans accelerate at start, maintain speed, decelerate at end
        if progress < 0.2:
            # Acceleration phase
            speed_factor = self.ease_in(progress / 0.2)
        elif progress > 0.8:
            # Deceleration phase
            speed_factor = self.ease_out((1 - progress) / 0.2)
        else:
            # Maintain speed in middle
            speed_factor = 1.0
            
        # Add some random variation
        speed_factor *= random.uniform(0.8, 1.2)
        
        return base_speed * speed_factor
    
    def add_hand_jitter(self, x, y):
        """Add slight random jitter to simulate hand shake"""
        jitter_x = random.gauss(0, self.jitter_amount * 0.5)
        jitter_y = random.gauss(0, self.jitter_amount * 0.5)
        return (x + jitter_x, y + jitter_y)
    
    def human_like_move(self, target_x, target_y, duration=None):
        """
        Move mouse to target with human-like behavior including:
        - Bézier curve path
        - Variable speed
        - Possible overshoot and correction
        - Possible mid-movement pause
        - Hand jitter
        """
        start_pos = pyautogui.position()
        start = (start_pos.x, start_pos.y)
        end = (target_x, target_y)
        
        # Calculate distance for timing
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        if duration is None:
            # Base duration on distance (humans move faster for short distances)
            base_duration = 0.1 + (distance / 2000)  # ~0.1s to 0.6s
            duration = base_duration * random.uniform(0.8, 1.3)
        
        # Decide if we should overshoot
        overshoot = random.random() < self.overshoot_chance and distance > 100
        
        if overshoot:
            # Calculate overshoot position
            overshoot_factor = random.uniform(1.05, 1.15)
            overshoot_x = start[0] + (end[0] - start[0]) * overshoot_factor
            overshoot_y = start[1] + (end[1] - start[1]) * overshoot_factor
            
            # Move to overshoot position first
            self._execute_move(overshoot_x, overshoot_y, duration * 0.7)
            
            # Small pause before correction (realization)
            time.sleep(random.uniform(0.1, 0.3))
            
            # Correct to actual target
            self._execute_move(end[0], end[1], duration * 0.4)
        else:
            # Normal move
            self._execute_move(end[0], end[1], duration)
    
    def _execute_move(self, target_x, target_y, duration):
        """Execute a single movement with Bézier curve and variable speed"""
        start_pos = pyautogui.position()
        start = (start_pos.x, start_pos.y)
        end = (target_x, target_y)
        
        # Generate control points for Bézier curve
        cp1, cp2 = self.generate_control_points(start, end)
        
        # Number of steps based on distance
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        steps = max(20, int(distance / 5))
        
        start_time = time.time()
        
        for i in range(steps + 1):
            if not self.running.is_set():
                break
            if time.time() - self.last_user_activity < 1:
                break
            
            # Calculate progress
            t = i / steps
            
            # Apply ease-in-out to progress for natural feel
            eased_t = self.ease_in_out(t)
            
            # Get position on Bézier curve
            x, y = self.bezier_curve(start, cp1, cp2, end, eased_t)
            
            # Add hand jitter
            x, y = self.add_hand_jitter(x, y)
            
            # Ensure on screen
            width, height = pyautogui.size()
            x = max(0, min(width - 1, x))
            y = max(0, min(height - 1, y))
            
            # Move to position
            pyautogui.moveTo(x, y, duration=0, _pause=False)
            
            # Calculate variable delay for this step
            base_step_time = duration / steps
            speed_factor = self.calculate_movement_speed(t, 1.0)
            # Prevent division by zero - ensure minimum speed factor
            speed_factor = max(0.1, speed_factor)
            step_delay = base_step_time / speed_factor
            step_delay *= random.uniform(0.9, 1.1)  # Add micro-variation
            
            # Random pause mid-movement (distraction)
            if random.random() < self.pause_chance and 0.3 < t < 0.7:
                time.sleep(random.uniform(0.3, 1.5))
            
            time.sleep(step_delay)
    
    def run(self):
        self.listener.start()
        
        # Get all non-empty paths
        available_paths = [p for p in self.app.settings['paths'].values() if p]
        
        if available_paths:
            self.playback_loop(available_paths)
        else:
            self.random_movement_loop()
    
    def playback_loop(self, available_paths):
        """Playback recorded paths with human-like variations"""
        while self.running.is_set():
            current_path = available_paths[self.path_cycle_index]
            
            interval = self.app.get_interval()
            time_since_activity = time.time() - self.last_user_activity
            
            if time_since_activity < interval:
                remaining_wait = interval - time_since_activity
                for i in range(int(remaining_wait), 0, -1):
                    if not self.running.is_set():
                        break
                    self.app.update_countdown(i)
                    # Randomize sleep slightly
                    time.sleep(random.uniform(0.95, 1.05))
                continue
            
            self.app.update_countdown(0)
            
            # Random distraction before starting (occasional)
            if random.random() < self.distraction_chance:
                time.sleep(random.uniform(2, 5))
            
            # Execute path with human-like movement
            for i, point in enumerate(current_path):
                if not self.running.is_set():
                    break
                if time.time() - self.last_user_activity < 1:
                    break
                
                x, y, _ = point
                
                # Add slight variation to target (humans aren't pixel-perfect)
                target_x = x + random.gauss(0, 3)
                target_y = y + random.gauss(0, 3)
                
                # Move with human-like behavior
                self.human_like_move(target_x, target_y)
                
                # Variable pause between points
                pause = random.uniform(0.05, 0.2)
                time.sleep(pause)
            
            if self.running.is_set() and time.time() - self.last_user_activity >= 1:
                self.total_moves += 1
                self.app.update_total_moves(self.total_moves)
                self.path_cycle_index = (self.path_cycle_index + 1) % len(available_paths)
    
    def random_movement_loop(self):
        """Random movement with human-like behavior"""
        while self.running.is_set():
            interval = self.app.get_interval()
            
            time_since_activity = time.time() - self.last_user_activity
            if time_since_activity < interval:
                remaining_wait = interval - time_since_activity
                for i in range(int(remaining_wait), 0, -1):
                    if not self.running.is_set():
                        break
                    self.app.update_countdown(i)
                    time.sleep(random.uniform(0.95, 1.05))
                continue
            
            # Countdown with randomization
            for i in range(interval, 0, -1):
                if not self.running.is_set():
                    break
                if time.time() - self.last_user_activity < 1:
                    break
                self.app.update_countdown(i)
                time.sleep(random.uniform(0.95, 1.05))
            else:
                if self.running.is_set():
                    self.move_randomly_human_like()
    
    def move_randomly_human_like(self):
        """Random movement with human-like behavior"""
        try:
            original_pos = pyautogui.position()
            movement_range_str = self.app.get_movement_range()
            pixel_range = MOVEMENT_RANGES.get(movement_range_str, 30)
            
            # Random target with some gaussian distribution (humans tend toward center)
            offset_x = random.gauss(0, pixel_range / 2)
            offset_y = random.gauss(0, pixel_range / 2)
            
            new_x = original_pos.x + offset_x
            new_y = original_pos.y + offset_y
            
            # Ensure on screen
            width, height = pyautogui.size()
            new_x = max(50, min(width - 50, new_x))
            new_y = max(50, min(height - 50, new_y))
            
            # Move to new position with human-like behavior
            self.human_like_move(new_x, new_y)
            
            # Pause at destination
            time.sleep(random.uniform(0.2, 0.5))
            
            # Sometimes do a small secondary movement (hesitation)
            if random.random() < 0.3:
                small_offset_x = random.uniform(-10, 10)
                small_offset_y = random.uniform(-10, 10)
                self.human_like_move(
                    pyautogui.position().x + small_offset_x,
                    pyautogui.position().y + small_offset_y,
                    duration=0.15
                )
                time.sleep(random.uniform(0.1, 0.3))
            
            # Return to original with human-like movement
            self.human_like_move(original_pos.x, original_pos.y)
            
            self.total_moves += 1
            self.app.update_total_moves(self.total_moves)
            
        except Exception as e:
            print(f"Error moving mouse: {e}")
    
    def stop(self):
        self.running.clear()
        self.listener.stop()
