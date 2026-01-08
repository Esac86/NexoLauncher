import os
from pathlib import Path

BASE_DIR = Path(os.getenv("APPDATA")) / ".nexoLauncher"
BASE_DIR.mkdir(exist_ok=True)

APP_EXE = BASE_DIR / "Launcher.exe"
UPDATER_EXE = BASE_DIR / "Updater.exe"

VERSION_FILE = BASE_DIR / "version.json"
CONFIG_FILE = BASE_DIR / "config.json"

DIR = Path(os.getenv("APPDATA")) / ".minecraft"
DIR.mkdir(exist_ok=True)
