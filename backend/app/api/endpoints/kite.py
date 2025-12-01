"""
Kite API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from app.services.kite_service import KiteService
from loguru import logger
from typing import Dict, List

router = APIRouter()
kite_service = KiteService()

@router.get("/login")
async def login():
    """
    Get Kite Connect login URL
    """
    try:
        login_url = kite_service.get_login_url()
        return {"login_url": login_url}
    except Exception as e:
        logger.error(f"Error getting login URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def callback(request_token: str = Query(..., description="Request token from Kite")):
    """
    Handle Kite Connect redirect callback
    Exchanges request token for access token
    """
    try:
        data = kite_service.generate_session(request_token)
        return {
            "message": "Login successful",
            "access_token": data.get("access_token"),
            "public_token": data.get("public_token"),
            "user_id": data.get("user_id")
        }
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """
    Get live quote for a symbol
    Example: TCS.NS -> NSE:TCS
    """
    try:
        quote = kite_service.get_quote(symbol)
        return quote
    except Exception as e:
        logger.error(f"Error fetching quote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instruments")
async def get_instruments(exchange: str = "NSE"):
    """
    Get list of instruments for an exchange
    """
    try:
        instruments = kite_service.get_instruments(exchange)
        # Return simplified list to avoid massive JSON
        return [
            {
                "instrument_token": i["instrument_token"],
                "tradingsymbol": i["tradingsymbol"],
                "name": i["name"],
                "last_price": 0, # Not available in instrument list
                "expiry": i["expiry"]
            }
            for i in instruments
        ]
    except Exception as e:
        logger.error(f"Error fetching instruments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
