"""Health API Endpoint"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.ml.predictor import Predictor

router = APIRouter()

START_TIME = datetime.now(timezone.utc)

predictor = Predictor()


@router.get("/health")
async def health() -> Dict[str, Any]:
    """Application health status with uptime and model status.

    Example response:
    {
      "status": "ok",
      "uptime": "1234.56s",
      "models_loaded": true
    }
    """
    try:
        now = datetime.now(timezone.utc)
        uptime_seconds = (now - START_TIME).total_seconds()

        models_loaded = predictor.model_loader.is_ready()

        return {
            "status": "ok",
            "uptime": f"{uptime_seconds:.2f}s",
            "models_loaded": bool(models_loaded),
        }
    except Exception as e:
        logger.error(f"Health endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
