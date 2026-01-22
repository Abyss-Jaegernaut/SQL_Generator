import json
import os


def _config_path() -> str:
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    app_dir = os.path.join(base, "SQL_GENERATOR")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "activation.json")


def is_activated() -> bool:
    try:
        path = _config_path()
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("activated"))
    except Exception:
        # If there's any error reading the activation file, assume not activated
        return False


def set_activated() -> None:
    try:
        path = _config_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"activated": True}, f)
    except Exception:
        # If we can't save to the activation file, activation fails silently
        pass