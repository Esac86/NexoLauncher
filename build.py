import PyInstaller.__main__
import shutil
import stat
import os

def force_remove(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

for folder in ("build", "dist"):
    if os.path.exists(folder):
        shutil.rmtree(folder, onerror=force_remove)

spec_file = "Nexo Abierto Launcher.spec"
if os.path.exists(spec_file):
    os.remove(spec_file)

PyInstaller.__main__.run([
    "main.py",
    "--name=Nexo Abierto Launcher",
    "--onefile",
    "--windowed",
    "--icon=assets/favicon.ico",
    "--add-data=assets/favicon.ico;assets",
    "--upx-dir=C:\\upx-5.0.2-win64",
    "--noconfirm"
])

if os.path.exists("build"):
    shutil.rmtree("build", onerror=force_remove)

if os.path.exists(spec_file):
    os.remove(spec_file)