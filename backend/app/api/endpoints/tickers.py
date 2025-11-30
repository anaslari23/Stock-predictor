"""Tickers API Endpoint"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.utils.ticker_loader import load_tickers

router = APIRouter()


@router.get("/tickers")
async def get_tickers(
    market: str = Query(
        "ALL",
        regex=r"^(ALL|NSE|BSE|NASDAQ|NYSE|FX|CRYPTO)$",
        description="Market filter (ALL, NSE, BSE, NASDAQ, NYSE, FX, CRYPTO)",
    )
) -> Dict[str, Any]:
    """Get list of tickers from the global database.

    Example: GET /tickers?market=NSE
    """
    try:
        logger.info(f"Tickers request: market={market}")
        market_filter = None if market.upper() == "ALL" else market
        data = load_tickers(market_filter)
        return {
            "market": market.upper(),
            "count": len(data),
            "tickers": data,
        }
    except Exception as e:
        logger.error(f"Tickers endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Tickers service temporarily unavailable")
