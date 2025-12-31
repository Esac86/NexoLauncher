import os

APP_DIR = os.path.join(os.getenv("APPDATA"), ".NexoAbiertoLauncher")
os.makedirs(APP_DIR, exist_ok=True)

MC_DIR = os.path.join(APP_DIR, ".minecraft")
os.makedirs(MC_DIR, exist_ok=True)

CONFIG_DIR = os.path.join(APP_DIR, ".config")
os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")