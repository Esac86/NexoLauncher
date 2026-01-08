import PyInstaller.__main__
import shutil
import os
import stat
import subprocess

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
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
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
        StringStruct(u'FileDescription', u'Nexo Launcher - Game Management Tool'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'NexoLauncher'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 Nexo Development'),
        StringStruct(u'OriginalFilename', u'Nexo.Launcher.exe'),
        StringStruct(u'ProductName', u'Nexo Launcher'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
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
        exe_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

clean()
create_version_file()

common_options = [
    "--noconfirm",
    "--clean",
    "--noupx", 
    "--debug=imports",  
    "--version-file=version_info.txt", 
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
    "--add-binary=dist/Updater.exe;.",
    "--add-data=assets/favicon.ico;assets",
    "--hidden-import=win32com.client",
    "--hidden-import=win32timezone",
    *common_options
])

sign_with_signtool("dist/Updater.exe")
sign_with_signtool("dist/Nexo Launcher.exe")

shutil.rmtree("build", onerror=force_remove)
for spec in ("Updater.spec", "Nexo Launcher.spec"):
    if os.path.exists(spec):
        os.remove(spec)
if os.path.exists("version_info.txt"):
    os.remove("version_info.txt")