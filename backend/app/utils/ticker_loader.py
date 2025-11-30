import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger


TICKERS_PATH = Path("data/tickers.json")


def load_tickers(market: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load tickers from the JSON database.

    Args:
        market: Optional market filter (e.g., "NSE", "BSE", "NASDAQ", "NYSE", "FX", "CRYPTO").
                If None or "ALL", returns all tickers.

    Returns:
        List of ticker dictionaries.
    """
    if not TICKERS_PATH.exists():
        logger.warning(f"Tickers file not found at {TICKERS_PATH}, returning empty list")
        return []

    try:
        with TICKERS_PATH.open("r", encoding="utf-8") as f:
            tickers: List[Dict[str, Any]] = json.load(f)
    except Exception as e:
        logger.error(f"Error loading tickers from {TICKERS_PATH}: {e}")
        return []

    if market is None or market.upper() == "ALL":
        return tickers

    market_upper = market.upper()
    filtered = [t for t in tickers if t.get("market", "").upper() == market_upper]
    return filtered


def update_tickers(new_tickers: List[Dict[str, Any]]) -> int:
    """Update the tickers database by merging new entries.

    Existing tickers are preserved; entries are de-duplicated on the `symbol` field.

    Args:
        new_tickers: List of ticker dicts to add or update.

    Returns:
        Total number of tickers after the update.
    """
    existing: List[Dict[str, Any]] = []
    if TICKERS_PATH.exists():
        try:
            with TICKERS_PATH.open("r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception as e:
            logger.error(f"Error reading existing tickers, starting fresh: {e}")
            existing = []

    by_symbol: Dict[str, Dict[str, Any]] = {t["symbol"]: t for t in existing if "symbol" in t}

    for t in new_tickers:
        symbol = t.get("symbol")
        if not symbol:
            continue
        by_symbol[symbol] = t

    merged = list(by_symbol.values())

    TICKERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with TICKERS_PATH.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        logger.info(f"Updated tickers database at {TICKERS_PATH} with {len(merged)} entries")
    except Exception as e:
        logger.error(f"Error writing updated tickers to {TICKERS_PATH}: {e}")

    return len(merged)
