"""
OHLCV API Endpoint
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.ohlcv_service import OHLCVService
from loguru import logger

router = APIRouter()
ohlcv_service = OHLCVService()

@router.get("/ohlcv")
async def get_ohlcv(
    symbol: str = Query(..., description="Stock symbol (e.g., TCS.NS)"),
    range: str = Query("1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$", description="Time range")
):
    """
    Get OHLCV data with technical indicators
    
    - **symbol**: Stock symbol with exchange suffix
    - **range**: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    **Technical Indicators Included:**
    - MA20, MA50: Moving averages
    - RSI(14): Relative Strength Index
    - MACD: Moving Average Convergence Divergence
    - Bollinger Bands: Upper, Middle, Lower
    - ATR(14): Average True Range
    
    **Caching**: Data cached in pickle format for 1 hour
    
    Example: GET /ohlcv?symbol=TCS.NS&range=1y
    """
    try:
        logger.info(f"OHLCV request for {symbol} ({range})")
        data = await ohlcv_service.get_ohlcv(symbol, range)
        return data
        
    except ValueError as e:
        logger.error(f"Invalid request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"OHLCV endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="OHLCV service temporarily unavailable"
        )

@router.post("/ohlcv/cache/clear")
async def clear_cache(symbol: str = Query(None, description="Symbol to clear (or all if not specified)")):
    """
    Clear OHLCV cache (admin endpoint)
    """
    try:
        ohlcv_service.clear_cache(symbol)
        message = f"Cache cleared for {symbol}" if symbol else "All OHLCV cache cleared"
        return {"message": message}
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
