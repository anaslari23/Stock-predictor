"""
Predictions API Endpoints
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService
from loguru import logger

router = APIRouter()
prediction_service = PredictionService()

@router.post("/predict/{symbol}", response_model=PredictionResponse)
async def get_prediction(symbol: str):
    """
    Get AI prediction for a stock symbol
    """
    try:
        logger.info(f"Prediction requested for {symbol}")
        prediction = await prediction_service.predict(symbol)
        return prediction
    except Exception as e:
        logger.error(f"Prediction error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{symbol}", response_model=PredictionResponse)
async def get_prediction_get(symbol: str):
    """
    Get AI prediction for a stock symbol (GET method)
    """
    return await get_prediction(symbol)
