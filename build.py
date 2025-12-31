import PyInstaller.__main__
import os
import shutil
import stat

def force_remove(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

for folder in ("build", "dist"):
    if os.path.exists(folder):
        shutil.rmtree(folder, onerror=force_remove)

PyInstaller.__main__.run([
    "main.py",
    "--name=Nexo Abierto Launcher",
    "--onefile",
    "--windowed",                  
    "--icon=img/favicon.ico",
    "--add-data=img/favicon.ico;img", 
    "--clean",
    "--noconfirm",
])