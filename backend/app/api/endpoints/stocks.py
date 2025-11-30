"""
Stocks API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.schemas import StockData, OHLCVData
from app.services.stock_service import StockService
from loguru import logger

router = APIRouter()
stock_service = StockService()

@router.get("/search")
async def search_stocks(q: str = Query(..., min_length=1)):
    """
    Search for stocks by symbol or name
    """
    try:
        results = await stock_service.search(q)
        return {"results": results}
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """
    Get current price for a symbol
    """
    try:
        price = await stock_service.get_current_price(symbol)
        return {"symbol": symbol, "price": price}
    except Exception as e:
        logger.error(f"Price fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ohlcv/{symbol}", response_model=dict)
async def get_ohlcv(symbol: str, timeframe: str = "1D"):
    """
    Get OHLCV data for charting
    """
    try:
        candles = await stock_service.get_ohlcv(symbol, timeframe)
        return {"symbol": symbol, "timeframe": timeframe, "candles": candles}
    except Exception as e:
        logger.error(f"OHLCV fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details/{symbol}")
async def get_stock_details(symbol: str):
    """
    Get detailed stock information
    """
    try:
        details = await stock_service.get_details(symbol)
        return details
    except Exception as e:
        logger.error(f"Details fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
