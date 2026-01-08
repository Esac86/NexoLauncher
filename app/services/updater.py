import requests
import subprocess
import sys
import shutil
from pathlib import Path
from packaging import version
from app.utils.paths import APP_EXE, UPDATER_EXE
from app.services.config import load_config, save_config

CURRENT_VERSION = "1.0"
GITHUB_API_URL = "https://api.github.com/repos/Esac86/NexoLauncher/releases/latest"


def normalize_version(v):
    v = v.lstrip("v")
    parts = v.split(".")
    
    while len(parts) < 3:
        parts.append("0")
    
    return ".".join(parts[:3])


class UpdateService:

    @staticmethod
    def check_for_updates():
        config = load_config()
        if not config.get("launcher_version"):
            save_config(launcher_version=CURRENT_VERSION)
        
        r = requests.get(GITHUB_API_URL, timeout=5)
        r.raise_for_status()
        data = r.json()

        latest_raw = data["tag_name"].lstrip("v")
        latest = normalize_version(latest_raw)
        current = normalize_version(CURRENT_VERSION)
        
        if version.parse(latest) <= version.parse(current):
            return None

        asset = next(a for a in data["assets"] if a["name"].endswith(".exe"))
        return {
            "version": latest_raw, 
            "download_url": asset["browser_download_url"]
        }

    @staticmethod
    def start_update(download_url):
        updater_path = UpdateService._ensure_updater()

        subprocess.Popen([
            str(updater_path),
            "--url", download_url,
            "--target", str(APP_EXE)
        ])

        return True

    @staticmethod
    def _ensure_updater():
        if not UPDATER_EXE.exists():
            if not getattr(sys, "frozen", False):
                raise RuntimeError("Updater solo funciona en build")

            bundled = Path(sys._MEIPASS) / "Updater.exe"
            shutil.copy2(bundled, UPDATER_EXE)

        return UPDATER_EXE