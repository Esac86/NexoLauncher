import json
from pathlib import Path
from app.utils.paths import CONFIG_FILE

DEFAULT_CONFIG = {
    "username": "",
    "version": "",
    "mode": "simple",
    "ms_account": False,
    "refresh_token": None,
    "mod_type": "vanilla",
    "launcher_version": ""
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULT_CONFIG, **data}
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(**kwargs) -> None:
    config = load_config()

    for key, value in kwargs.items():
        config[key] = value

    tmp: Path = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(config, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    tmp.replace(CONFIG_FILE)