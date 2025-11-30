"""
API Router - Main router that includes all sub-routers
"""

from fastapi import APIRouter
from app.api.endpoints import predictions, stocks, websocket, screener, search, price, ohlcv, predict, ai_screener, ws_prices

router = APIRouter()

# Include all endpoint routers
router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
router.include_router(screener.router, prefix="/screener", tags=["Screener"])
router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
router.include_router(ws_prices.router, prefix="/ws", tags=["WebSocket"])
router.include_router(search.router, tags=["Search"])
router.include_router(price.router, tags=["Price"])
router.include_router(ohlcv.router, tags=["OHLCV"])
router.include_router(predict.router, tags=["ML Prediction"])
router.include_router(ai_screener.router, prefix="/ai", tags=["AI Screener"])

