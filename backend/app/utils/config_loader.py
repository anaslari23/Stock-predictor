import json
from pathlib import Path
from typing import Any, Dict

from loguru import logger


CONFIG_PATH = Path("config.json")


def load_config() -> Dict[str, Any]:
    """Load application config from config.json.

    Returns an empty dict if the file does not exist or is invalid.
    """
    if not CONFIG_PATH.exists():
        logger.warning(f"Config file not found at {CONFIG_PATH}, returning empty config")
        return {}

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config from {CONFIG_PATH}: {e}")
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Persist config back to config.json."""
    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4, sort_keys=False)
        logger.info(f"Saved config to {CONFIG_PATH}")
    except Exception as e:
        logger.error(f"Error saving config to {CONFIG_PATH}: {e}")


def get_ai_thresholds() -> Dict[str, float]:
    """Return AI prediction thresholds with sensible defaults.

    Ensures that the config contains an "ai" section with threshold keys.
    """
    config = load_config()
    ai_cfg = config.get("ai") or {}

    entry = float(ai_cfg.get("entry_threshold", 0.55))
    exit_ = float(ai_cfg.get("exit_threshold", 0.5))
    min_conf = float(ai_cfg.get("min_confidence", 0.6))

    ai_cfg = {
        "entry_threshold": entry,
        "exit_threshold": exit_,
        "min_confidence": min_conf,
    }

    config["ai"] = ai_cfg
    save_config(config)

    return ai_cfg


def update_config(partial: Dict[str, Any]) -> Dict[str, Any]:
    """Update config.json with provided partial keys.

    Performs a shallow merge at the top level; nested dicts like "ai" are also
    shallow-merged.
    """
    config = load_config()

    for key, value in partial.items():
        if isinstance(value, dict) and isinstance(config.get(key), dict):
            merged = dict(config[key])
            merged.update(value)
            config[key] = merged
        else:
            config[key] = value

    save_config(config)
    return config
