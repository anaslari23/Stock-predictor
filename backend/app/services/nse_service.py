"""
NSE Service - Fetch data from NSE using nsepython
"""

from typing import Optional, Dict, Any
from loguru import logger
from nsepython import nse_eq


class NSEService:
    """Service for fetching data from NSE"""
    
    def __init__(self):
        logger.info("NSEService initialized")
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get live quote for a symbol from NSE
        
        Args:
            symbol: Stock symbol (e.g., "TCS", "RELIANCE")
            
        Returns:
            Dict with quote data or None if failed
        """
        try:
            logger.info(f"Fetching NSE quote for {symbol}")
            
            # Remove .NS suffix if present (NSE symbols don't need it)
            clean_symbol = symbol.replace(".NS", "").upper()
            
            # Fetch quote using nsepython
            quote_data = nse_eq(clean_symbol)
            
            if not quote_data:
                logger.warning(f"No data returned from NSE for {clean_symbol}")
                return None
            
            # Extract price info
            price_info = quote_data.get('priceInfo', {})
            
            if not price_info:
                logger.warning(f"No priceInfo in NSE response for {clean_symbol}")
                return None
            
            # Parse the response into a standardized format
            result = {
                'symbol': clean_symbol,
                'lastPrice': price_info.get('lastPrice'),
                'change': price_info.get('change'),
                'pChange': price_info.get('pChange'),
                'previousClose': price_info.get('previousClose'),
                'open': price_info.get('open'),
                'close': price_info.get('close'),
                'vwap': price_info.get('vwap'),
                'lowerCP': price_info.get('lowerCP'),
                'upperCP': price_info.get('upperCP'),
                'intraDayHighLow': price_info.get('intraDayHighLow', {}),
                'weekHighLow': price_info.get('weekHighLow', {}),
                'raw': quote_data  # Keep full response for debugging
            }
            
            logger.info(f"Successfully fetched NSE quote for {clean_symbol}: ₹{result['lastPrice']}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching NSE quote for {symbol}: {str(e)}")
            return None
    
    def is_market_open(self) -> bool:
        """
        Check if NSE market is currently open
        This is a simple heuristic - can be improved
        """
        from datetime import datetime
        import pytz
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        # Market hours: Monday-Friday, 9:15 AM - 3:30 PM IST
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
