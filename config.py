
import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_SETTINGS = {
    'interval': 30,
    'move_only_when_idle': True,
    'idle_threshold': 60,
    'movement_range': 100,
    'debug_mode': False,
    'autostart': False,
    'paths': {
        'path_1': [],
        'path_2': [],
        'path_3': []
    },
    'keypress_keys': '',
    'keypress_interval': 10,
    'human_like_enabled': True,
    'click_enabled': False,
    'click_interval': 5,
    'click_type': 'left'
}

def load_settings():
    if not os.path.exists(CONFIG_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

    try:
        with open(CONFIG_FILE, 'r') as f:
            settings = json.load(f)
            # Merge with defaults to ensure all keys are present
            settings = {**DEFAULT_SETTINGS, **settings}
            return settings
    except (json.JSONDecodeError, FileNotFoundError):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

