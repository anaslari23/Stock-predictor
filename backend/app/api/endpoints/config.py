"""Config API Endpoints"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger

from app.utils.config_loader import load_config, update_config, get_ai_thresholds

router = APIRouter()


class ConfigUpdateRequest(BaseModel):
    ai: Optional[Dict[str, Any]] = None


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Return the current application configuration.

    Includes indices, data, features, model, timezone, and ai thresholds.
    """
    try:
        cfg = load_config()
        # Ensure AI thresholds section is present
        cfg.setdefault("ai", get_ai_thresholds())
        return cfg
    except Exception as e:
        logger.error(f"Config read error: {e}")
        raise HTTPException(status_code=500, detail="Unable to load config")


@router.post("/config/update")
async def update_config_endpoint(payload: ConfigUpdateRequest) -> Dict[str, Any]:
    """Update configuration values.

    Currently supports updating the "ai" section (thresholds for AI prediction).

    Example payload:
    {
      "ai": {
        "entry_threshold": 0.6,
        "exit_threshold": 0.45,
        "min_confidence": 0.65
      }
    }
    """
    try:
        partial: Dict[str, Any] = {}
        if payload.ai is not None:
            partial["ai"] = payload.ai

        if not partial:
            return load_config()

        cfg = update_config(partial)
        return cfg
    except Exception as e:
        logger.error(f"Config update error: {e}")
        raise HTTPException(status_code=500, detail="Unable to update config")
