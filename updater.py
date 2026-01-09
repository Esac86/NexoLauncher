import argparse
import requests
import subprocess
import sys
import os
from pathlib import Path
import time

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--target", required=True)
args = parser.parse_args()

target = Path(args.target).resolve()
temp = target.with_suffix(".new")

try:
    r = requests.get(args.url, stream=True, timeout=30)
    r.raise_for_status()

    with open(temp, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)

    max_retries = 5
    for i in range(max_retries):
        try:
            if target.exists():
                target.unlink()
            temp.rename(target)
            break
        except PermissionError:
            if i < max_retries - 1:
                time.sleep(2)
            else:
                raise

    subprocess.Popen(
        [str(target)],
        cwd=str(target.parent),
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    )

except Exception as e:
    log_path = Path(target.parent) / "updater_error.log"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{e}\n")
    sys.exit(1)

sys.exit(0)
