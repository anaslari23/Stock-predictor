from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

from loguru import logger

from app.services.backtest_service import BacktestService

router = APIRouter()
backtest_service = BacktestService()


@router.get("/backtest")
async def run_backtest(
    symbol: str = Query(..., description="Stock symbol (e.g., TCS.NS)"),
    entry_threshold: float = Query(0.55, ge=0.0, le=1.0, description="Entry threshold for p_up"),
    exit_threshold: float = Query(0.5, ge=0.0, le=1.0, description="Exit threshold for p_up"),
    fee_bps: float = Query(10.0, ge=0.0, description="Fee per trade in basis points"),
    slippage_bps: float = Query(5.0, ge=0.0, description="Slippage per trade in basis points"),
    range_period: str = Query("1y", description="History range period (e.g., 6mo, 1y, 5y)"),
) -> Dict[str, Any]:
    """Run a simple long-only backtest for a symbol.

    Process:
    1. Load historical OHLCV data via OHLCVService.
    2. Construct a probability-like signal p_up from price vs MA20.
    3. Run backtest with:
       - Entry when p_up > entry_threshold
       - Exit when p_up < exit_threshold
       - Includes slippage and fees
    4. Return portfolio metrics and equity curve points.
    """
    try:
        logger.info(
            f"Backtest request symbol={symbol} range={range_period} "
            f"entry={entry_threshold} exit={exit_threshold} "
            f"fee_bps={fee_bps} slippage_bps={slippage_bps}"
        )

        result = await backtest_service.run_backtest(
            symbol=symbol,
            range_period=range_period,
            entry_threshold=entry_threshold,
            exit_threshold=exit_threshold,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )
        return result

    except ValueError as e:
        logger.error(f"Backtest invalid request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Backtest service error: {str(e)}",
        )
