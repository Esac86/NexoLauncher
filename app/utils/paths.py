import os
from pathlib import Path
DIR = Path(os.getenv("APPDATA")) / ".minecraft"
DIR.mkdir(exist_ok=True)
CONFIG_FILE = DIR / "nexoLauncher.json"