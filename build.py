import PyInstaller.__main__
import shutil
import os
import stat

def force_remove(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clean():
    for f in ("build", "dist"):
        if os.path.exists(f):
            shutil.rmtree(f, onerror=force_remove)

    for spec in ("Updater.spec", "Nexo Launcher.spec"):
        if os.path.exists(spec):
            os.remove(spec)

clean()

PyInstaller.__main__.run([
    "updater.py",
    "--name=Updater",
    "--onefile",
    "--windowed",
    "--icon=assets/updater.ico",
    "--noconfirm",
    "--clean"
])

PyInstaller.__main__.run([
    "main.py",
    "--name=Nexo Launcher",
    "--onefile",
    "--windowed",
    "--icon=assets/favicon.ico",
    "--add-binary=dist/Updater.exe;.",
    "--add-data=assets/favicon.ico;assets",
    "--noconfirm",
    "--clean",
    "--hidden-import=win32com.client",
    "--hidden-import=win32timezone"
])

shutil.rmtree("build", onerror=force_remove)

for spec in ("Updater.spec", "Nexo Launcher.spec"):
    if os.path.exists(spec):
        os.remove(spec)