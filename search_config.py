import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config" / "search_config.json"


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def select_preset(preset_name=None):
    config = load_config()
    presets = config.get("presets", {})
    default = str(config.get("default_preset", "nb")).strip().lower()
    choices = "/".join(presets)

    while True:
        selected = preset_name
        if selected is None:
            selected = input(f"Select the config ({choices}) [{default}]: ").strip()
        selected = (selected or default).strip().lower()
        if selected in {"new balance", "new-balance"}:
            selected = "nb"
        if selected in presets:
            return selected, dict(presets[selected])
        if preset_name is not None:
            raise ValueError(f"Unknown config '{preset_name}'. Choose one of: {choices}.")
        print(f"Unknown config '{selected}'. Choose one of: {choices}.")