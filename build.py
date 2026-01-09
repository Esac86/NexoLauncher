import PyInstaller.__main__
import shutil
import os
import stat
import subprocess
from pathlib import Path

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

def create_version_file():
    version_content = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 1, 0),
    prodvers=(1, 0, 1, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Nexo Development'),
        StringStruct(u'FileDescription', u'Nexo Launcher - Minecraft Game Launcher'),
        StringStruct(u'FileVersion', u'1.0.1.0'),
        StringStruct(u'InternalName', u'NexoLauncher'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 Nexo Development'),
        StringStruct(u'OriginalFilename', u'Nexo.Launcher.exe'),
        StringStruct(u'ProductName', u'Nexo Launcher'),
        StringStruct(u'ProductVersion', u'1.0.1.0'),
        StringStruct(u'Comments', u'Open source Minecraft launcher - https://github.com/Esac86/NexoLauncher'),
        StringStruct(u'LegalTrademarks', u'')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)"""
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(version_content)

def sign_with_signtool(exe_path):
    try:
        subprocess.run(["signtool"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    cmd = [
        "signtool", "sign",
        "/a", 
        "/fd", "SHA256",
        "/tr", "http://timestamp.digicert.com",
        "/td", "SHA256",
        "/v",
        exe_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def build_executables():
    common_options = [
        "--noconfirm",
        "--clean",
        "--version-file=version_info.txt",
        "--exclude-module=pytest",
        "--exclude-module=setuptools",
    ]
    PyInstaller.__main__.run([
        "updater.py",
        "--name=Updater",
        "--onefile",
        "--windowed",
        "--icon=assets/updater.ico",
        *common_options
    ])
    PyInstaller.__main__.run([
        "main.py",
        "--name=Nexo Launcher",
        "--onefile",
        "--windowed",
        "--icon=assets/favicon.ico",
        "--add-data=assets/favicon.ico;assets",
        "--hidden-import=win32com.client",
        "--hidden-import=win32timezone",
        *common_options
    ])

def sign_executables():
    sign_with_signtool("dist/Updater.exe")
    sign_with_signtool("dist/Nexo Launcher.exe")

def build_installer():
    iscc_exe = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(iscc_exe):
        return False
    iss_file = Path("installer/installer.iss")
    if not iss_file.exists():
        return False
    result = subprocess.run([iscc_exe, str(iss_file)], capture_output=True, text=True)
    return result.returncode == 0

def cleanup():
    if os.path.exists("build"):
        shutil.rmtree("build", onerror=force_remove)
    for spec in ("Updater.spec", "Nexo Launcher.spec"):
        if os.path.exists(spec):
            os.remove(spec)
    if os.path.exists("version_info.txt"):
        os.remove("version_info.txt")

def main():
    clean()
    create_version_file()
    build_executables()
    sign_executables()
    build_installer()
    cleanup()

if __name__ == "__main__":
    main()
