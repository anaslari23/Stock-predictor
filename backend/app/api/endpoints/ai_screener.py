"""
AI Screener API Endpoint
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.ai_screener_service import AIScreenerService
from loguru import logger

router = APIRouter()
ai_screener = AIScreenerService()

@router.get("/screener")
async def ai_screener_endpoint(
    filter: str = Query(
        "high_confidence",
        regex="^(high_confidence|bearish|trending|oversold_up|all)$",
        description="Filter type"
    ),
    limit: int = Query(50, ge=1, le=200, description="Maximum results")
):
    """
    AI-powered stock screener
    
    **Filters:**
    - **high_confidence**: UP predictions with probability > 0.7
    - **bearish**: DOWN predictions with probability < 0.3
    - **trending**: Positive MACD + UP prediction (p > 0.6)
    - **oversold_up**: RSI < 30 + UP prediction (p > 0.55)
    - **all**: All stocks with confidence > 0.6
    
    **Process:**
    1. Runs predictions on top 200 stocks (NIFTY + FNO)
    2. Applies filter criteria
    3. Sorts by confidence
    4. Returns top matches
    
    **Performance:**
    - Uses async parallel processing
    - Caches OHLCV data (1 hour)
    - Typically completes in 10-30 seconds
    
    Example: GET /ai/screener?filter=high_confidence&limit=20
    """
    try:
        logger.info(f"AI screener request: filter={filter}, limit={limit}")
        
        results = await ai_screener.screen_stocks(filter, limit)
        
        return {
            'filter': filter,
            'count': len(results),
            'stocks': results
        }
        
    except Exception as e:
        logger.error(f"AI screener error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"AI screener service error: {str(e)}"
        )

@router.get("/screener/universe")
async def get_stock_universe():
    """
    Get list of stocks in the screener universe
    """
    try:
        return {
            'count': len(ai_screener.stock_universe),
            'stocks': ai_screener.stock_universe
        }
    except Exception as e:
        logger.error(f"Error getting stock universe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
