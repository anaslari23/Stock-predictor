"""
Price API Endpoint
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import PriceResponse
from app.services.price_service import PriceService
from loguru import logger

router = APIRouter()
price_service = PriceService()

@router.get("/price", response_model=PriceResponse)
async def get_price(
    symbol: str = Query(..., description="Stock symbol (e.g., TCS.NS, RELIANCE.NS)")
):
    """
    Get real-time stock price
    
    - **symbol**: Stock symbol with exchange suffix (e.g., TCS.NS for NSE)
    - Returns current price, change, and percentage change
    - Data cached for 10 seconds for performance
    - Falls back to mock data if live fetch fails
    
    Example: GET /price?symbol=TCS.NS
    """
    try:
        logger.info(f"Price request for: {symbol}")
        price_data = await price_service.get_price(symbol)
        return price_data
        
    except Exception as e:
        logger.error(f"Price endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Price service temporarily unavailable"
        )

@router.get("/price/cache/stats")
async def get_cache_stats():
    """
    Get price cache statistics (admin endpoint)
    """
    try:
        stats = price_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Cache stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/price/cache/clear")
async def clear_cache():
    """
    Clear price cache (admin endpoint)
    """
    try:
        price_service.clear_cache()
        return {"message": "Price cache cleared successfully"}
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
