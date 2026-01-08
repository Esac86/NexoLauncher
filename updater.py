import argparse
import requests
import subprocess
import sys
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--target", required=True)
args = parser.parse_args()

target = os.path.abspath(args.target)
temp = target + ".new"
exe_name = os.path.basename(target)

r = requests.get(args.url, stream=True)
r.raise_for_status()

with open(temp, "wb") as f:
    total = int(r.headers.get('content-length', 0))
    downloaded = 0
    for chunk in r.iter_content(8192):
        if chunk:
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                progress = (downloaded / total) * 100
                print(f"Progreso: {progress:.1f}%", end='\r')


time.sleep(1)

cmd = f'''
@echo off
echo Cerrando launcher...
taskkill /F /IM "{exe_name}" > nul 2>&1

echo Esperando cierre...
ping 127.0.0.1 -n 3 > nul

echo Reemplazando ejecutable...
if exist "{temp}" (
    del /f /q "{target}" 2>nul
    move /Y "{temp}" "{target}"
    if exist "{target}" (
        echo Actualización completada
        echo Iniciando launcher...
        start "" "{target}"
    ) else (
        echo Error: No se pudo reemplazar el ejecutable
        pause
    )
) else (
    echo Error: Archivo temporal no encontrado
    pause
)

rem Autodestrucción del script
del "%~f0"
'''

import tempfile
from pathlib import Path as PathLib

temp_dir = PathLib(tempfile.gettempdir())
batch_path = temp_dir / f"nexo_update_{os.getpid()}.bat"

with open(batch_path, 'w', encoding='utf-8') as f:
    f.write(cmd)

subprocess.Popen(
    ["cmd", "/c", str(batch_path)],
    creationflags=subprocess.CREATE_NO_WINDOW,
    cwd=os.path.dirname(target)
)
sys.exit(0)