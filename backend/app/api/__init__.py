"""API Router - Main router that includes all sub-routers"""

from fastapi import APIRouter
from app.api.endpoints import predictions, stocks, websocket, screener, search, price, ohlcv, predict, ai_screener, ws_prices, backtest, tickers, health, config, kite, nse

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
router.include_router(backtest.router, tags=["Backtest"])
router.include_router(tickers.router, tags=["Tickers"])
router.include_router(health.router, tags=["Health"])
router.include_router(config.router, tags=["Config"])
router.include_router(kite.router, prefix="/kite", tags=["Kite Zerodha"])
router.include_router(nse.router, prefix="/nse", tags=["NSE"])
