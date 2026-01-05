import requests
import os
import sys
import subprocess
import tempfile
from packaging import version

CURRENT_VERSION = "1.0.2"
GITHUB_API_URL = "https://api.github.com/repos/Esac86/NexoAbiertoLauncher/releases/latest"

class UpdateService:
    @staticmethod
    def check_for_updates():
        try:
            response = requests.get(GITHUB_API_URL, timeout=5)
            if response.status_code != 200:
                return None
            
            data = response.json()
            latest_version = data["tag_name"].replace("v", "")
            
            if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                download_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(".exe"):
                        download_url = asset["browser_download_url"]
                        break
                
                return {
                    "version": latest_version,
                    "download_url": download_url,
                    "release_notes": data.get("body", "")
                }
            return None
        except Exception as e:
            print(f"Error verificando actualizaciones: {e}")
            return None

    @staticmethod
    def download_and_install(download_url, latest_version, on_progress=None):
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            
            temp_file = os.path.join(tempfile.gettempdir(), "NexoAbiertoLauncher_update.exe")
            
            downloaded = 0
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress and total_size > 0:
                            on_progress(downloaded, total_size)
            
            from app.utils.paths import DIR
            flag_file = os.path.join(DIR, ".just_updated")
            with open(flag_file, 'w') as f:
                f.write(latest_version)
            
            current_exe = sys.executable if getattr(sys, 'frozen', False) else None
            if not current_exe:
                return False
            
            current_exe = os.path.abspath(current_exe)
            current_dir = os.path.dirname(current_exe)
            
            batch_script = f'''@echo off
cd /d "{current_dir}"
timeout /t 2 /nobreak >nul
taskkill /F /IM "{os.path.basename(current_exe)}" >nul 2>&1
timeout /t 2 /nobreak >nul
move /Y "{temp_file}" "{current_exe}"
timeout /t 1 /nobreak >nul
start "" "{current_exe}"
del "%~f0"
'''
        
            batch_file = os.path.join(tempfile.gettempdir(), "update_launcher.bat")
            with open(batch_file, 'w') as f:
                f.write(batch_script)
            
            subprocess.Popen(['cmd', '/c', batch_file], 
                           creationflags=subprocess.CREATE_NO_WINDOW,
                           cwd=current_dir)
            return True
            
        except Exception as e:
            print(f"Error descargando actualización: {e}")
            import traceback
            traceback.print_exc()
            return False