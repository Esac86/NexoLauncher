import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent.parent.parent

APP_EXE = APP_DIR / \
    "Nexo Launcher.exe" if getattr(
        sys, 'frozen', False) else APP_DIR / "main.py"
UPDATER_EXE = APP_DIR / "Updater.exe"
CONFIG_FILE = APP_DIR / "config.json"

DIR = Path(os.getenv("APPDATA")) / ".minecraft"
DIR.mkdir(exist_ok=True)