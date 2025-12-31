import json
from app.utils.paths import CONFIG_FILE

DEFAULT_CONFIG = {
    "username": "",
    "version": ""
}

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**DEFAULT_CONFIG, **data}
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print("Error cargando configuración:", e)
        return DEFAULT_CONFIG.copy()

def save_config(username=None, version=None):
    config = load_config()
    if username is not None:
        config["username"] = username
    if version is not None:
        config["version"] = version
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error guardando configuración:", e)
