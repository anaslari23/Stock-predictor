"""
Screener API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.screener_service import ScreenerService
from loguru import logger

router = APIRouter()
screener_service = ScreenerService()

@router.get("/")
async def get_screener_stocks(
    filter: str = Query("bullish", regex="^(bullish|bearish|trending)$"),
    page: int = Query(1, ge=1)
):
    """
    Get filtered stocks based on criteria
    """
    try:
        stocks = await screener_service.get_filtered_stocks(filter, page)
        return {"filter": filter, "page": page, "stocks": stocks}
    except Exception as e:
        logger.error(f"Screener error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-picks")
async def get_ai_picks():
    """
    Get AI-recommended stocks
    """
    try:
        picks = await screener_service.get_ai_picks()
        return {"picks": picks}
    except Exception as e:
        logger.error(f"AI picks error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
