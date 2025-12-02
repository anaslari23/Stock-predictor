"""
NSE API Endpoints
"""

from fastapi import APIRouter, HTTPException
from app.services.nse_service import NSEService

router = APIRouter(tags=["NSE"])

# Initialize NSE service
nse_service = NSEService()


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """
    Get live quote for a symbol from NSE
    
    Args:
        symbol: Stock symbol (e.g., "TCS", "RELIANCE", "TCS.NS")
        
    Returns:
        Quote data from NSE
    """
    quote = nse_service.get_quote(symbol)
    
    if not quote:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for symbol {symbol}"
        )
    
    return quote


@router.get("/market-status")
async def get_market_status():
    """
    Check if NSE market is currently open
    
    Returns:
        Market status
    """
    is_open = nse_service.is_market_open()
    
    return {
        "market": "NSE",
        "isOpen": is_open,
        "status": "OPEN" if is_open else "CLOSED"
    }
