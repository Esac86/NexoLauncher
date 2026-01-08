import sys
import shutil
import subprocess
import os
import winreg
import tempfile
from pathlib import Path
from app.utils.paths import BASE_DIR, APP_EXE
import win32com.client


def create_shortcut():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                        r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    desktop = Path(winreg.QueryValueEx(key, 'Desktop')[0])
    winreg.CloseKey(key)
    
    desktop_shortcut = desktop / "Nexo Launcher.lnk"
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(desktop_shortcut))
    shortcut.TargetPath = str(APP_EXE)
    shortcut.WorkingDirectory = str(BASE_DIR)
    shortcut.IconLocation = str(APP_EXE)
    shortcut.Description = "Nexo Launcher"
    shortcut.Save()


def register_in_start_menu():
    start_menu = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
    start_menu.mkdir(parents=True, exist_ok=True)
    
    shortcut_path = start_menu / "Nexo Launcher.lnk"
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(APP_EXE)
    shortcut.WorkingDirectory = str(BASE_DIR)
    shortcut.IconLocation = str(APP_EXE)
    shortcut.Description = "Nexo Launcher"
    shortcut.Save()


def ensure_running_from_appdata():
    if not getattr(sys, "frozen", False):
        return

    current_exe = Path(sys.executable)

    if str(current_exe).startswith(str(BASE_DIR)):
        return
    
    shutil.copy2(current_exe, APP_EXE)
    
    updater_bundled = Path(sys._MEIPASS) / "Updater.exe"
    updater_target = BASE_DIR / "Updater.exe"
    if updater_bundled.exists():
        shutil.copy2(updater_bundled, updater_target)
    
    create_shortcut()
    register_in_start_menu()
    
    batch_script = f'''@echo off
timeout /t 2 /nobreak > nul
del /f /q "{current_exe}"
if exist "{current_exe.parent / '*.new'}" del /f /q "{current_exe.parent}\\*.new"
del /f /q "%~f0"
'''
    temp_dir = Path(tempfile.gettempdir())
    batch_path = temp_dir / f"nexo_cleanup_{os.getpid()}.bat"
    batch_path.write_text(batch_script, encoding="utf-8")
    
    subprocess.Popen(
        ["cmd", "/c", str(batch_path)],
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    subprocess.Popen([str(APP_EXE)])
    sys.exit(0)