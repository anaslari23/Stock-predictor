"""
ML Prediction API Endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ml.predictor import Predictor
from app.services.ohlcv_service import OHLCVService
from loguru import logger
import asyncio

router = APIRouter()
predictor = Predictor()
ohlcv_service = OHLCVService()

class PredictRequest(BaseModel):
    symbol: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "TCS.NS"
            }
        }

class PredictResponse(BaseModel):
    symbol: str
    prediction: str
    probability: float
    confidence: float
    features_used: list
    timestamp: str
    models_used: list

@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Make ML prediction for a stock
    
    **Pipeline:**
    1. Fetch 180 days of OHLCV data
    2. Generate features (identical to training)
    3. Load XGBoost + LSTM models
    4. Compute ensemble prediction
    5. Return probability and direction
    
    **Input:**
    - symbol: Stock symbol (e.g., TCS.NS)
    
    **Output:**
    - prediction: UP or DOWN
    - probability: 0.0 to 1.0
    - confidence: Confidence level
    - features_used: List of features
    - models_used: Which models were used
    
    Example: POST /predict with {"symbol": "TCS.NS"}
    """
    try:
        symbol = request.symbol
        logger.info(f"Prediction request for {symbol}")
        
        # Step 1: Fetch 180 days OHLCV data
        logger.info("Fetching 180 days of OHLCV data...")
        ohlcv_data = await ohlcv_service.get_ohlcv(symbol, "6mo")
        
        if not ohlcv_data or not ohlcv_data.get('candles'):
            raise ValueError(f"No data available for {symbol}")
        
        # Convert to DataFrame
        import pandas as pd
        candles = ohlcv_data['candles']
        df = pd.DataFrame(candles)
        df['time'] = pd.to_datetime(df['t'])
        df = df.set_index('time')
        df = df.rename(columns={'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'})
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        logger.info(f"Loaded {len(df)} candles for {symbol}")
        
        # Step 2-5: Generate features and predict
        prediction = await predictor.predict(df, symbol)
        
        logger.info(f"Prediction for {symbol}: {prediction['prediction']} ({prediction['probability']:.2%})")
        return prediction
        
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Prediction service error: {str(e)}"
        )

@router.get("/predict/models/status")
async def get_models_status():
    """
    Get status of loaded models (admin endpoint)
    """
    try:
        return {
            'xgboost_loaded': predictor.model_loader.xgboost_model is not None,
            'lstm_loaded': predictor.model_loader.lstm_model is not None,
            'ensemble_weights': predictor.model_loader.ensemble_weights,
            'feature_count': len(predictor.feature_engineer.feature_names) if predictor.feature_engineer.feature_names else 0
        }
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
