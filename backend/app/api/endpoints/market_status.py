"""
Market Status Endpoint
"""

from fastapi import APIRouter
from app.services.market_status_service import market_status_service

router = APIRouter()


@router.get("/market-status")
async def get_market_status():
    """
    Get current NSE market status
    
    Returns:
        - is_open: boolean
        - status: "OPEN" or "CLOSED"
        - current_time: current IST time
        - next_change: description of next status change
        - next_change_time: time of next status change
        - market_hours: market operating hours
    """
    return market_status_service.get_market_status()
