"""
NSE Service - Fetch data from NSE using nsepython
"""

from typing import Optional, Dict, Any
from loguru import logger
from nsepython import nse_eq, nse_get_index_quote


class NSEService:
    """Service for fetching data from NSE"""
    
    # List of known indices
    INDICES = {
        'NIFTY50', 'NIFTY 50', 'NIFTY', 
        'BANKNIFTY', 'BANK NIFTY',
        'NIFTYIT', 'FINNIFTY', 'MIDCPNIFTY'
    }
    
    def __init__(self):
        logger.info("NSEService initialized")
    
    def _is_index(self, symbol: str) -> bool:
        """Check if symbol is an index"""
        return symbol.upper().replace('.NS', '').replace('_', ' ') in self.INDICES
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get live quote for a symbol from NSE
        
        Args:
            symbol: Stock symbol or index (e.g., "TCS", "NIFTY50")
            
        Returns:
            Dict with quote data or None if failed
        """
        try:
            logger.info(f"Fetching NSE quote for {symbol}")
            
            # Remove .NS suffix if present (NSE symbols don't need it)
            clean_symbol = symbol.replace(".NS", "").upper()
            
            # Check if it's an index
            if self._is_index(clean_symbol):
                return self._get_index_quote(clean_symbol)
            else:
                return self._get_equity_quote(clean_symbol)
                
        except Exception as e:
            logger.error(f"Error fetching NSE quote for {symbol}: {str(e)}")
            return None
    
    def _get_index_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote for an index"""
        try:
            # Map common index names
            index_map = {
                'NIFTY50': 'NIFTY 50',
                'NIFTY': 'NIFTY 50',
                'BANKNIFTY': 'NIFTY BANK',
                'BANK NIFTY': 'NIFTY BANK',
            }
            
            index_name = index_map.get(symbol, symbol)
            
            # Fetch quote using nsepython index function
            quote_data = nse_get_index_quote(index_name)
            
            if not quote_data:
                logger.warning(f"No data returned from NSE for index {index_name}")
                return None
            
            # Parse the index response
            # Note: Index data format is different from equity
            last_price = float(str(quote_data.get('last', 0)).replace(',', ''))
            prev_close = float(str(quote_data.get('previousClose', 0)).replace(',', ''))
            
            change = last_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close != 0 else 0
            
            result = {
                'symbol': symbol,
                'lastPrice': last_price,
                'change': change,
                'pChange': change_percent,
                'previousClose': prev_close,
                'open': float(str(quote_data.get('open', 0)).replace(',', '')),
                'close': last_price,
                'high': float(str(quote_data.get('high', 0)).replace(',', '')),
                'low': float(str(quote_data.get('low', 0)).replace(',', '')),
                'yearHigh': quote_data.get('yearHigh', ''),
                'yearLow': quote_data.get('yearLow', ''),
                'timeVal': quote_data.get('timeVal', ''),
                'raw': quote_data
            }
            
            logger.info(f"Successfully fetched NSE index quote for {symbol}: ₹{result['lastPrice']}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching index quote for {symbol}: {str(e)}")
            return None
    
    def _get_equity_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get quote for an equity stock"""
        try:
            # Fetch quote using nsepython
            quote_data = nse_eq(symbol)
            
            if not quote_data:
                logger.warning(f"No data returned from NSE for {symbol}")
                return None
            
            # Extract price info
            price_info = quote_data.get('priceInfo', {})
            
            if not price_info:
                logger.warning(f"No priceInfo in NSE response for {symbol}")
                return None
            
            # Parse the response into a standardized format
            result = {
                'symbol': symbol,
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
            
            logger.info(f"Successfully fetched NSE quote for {symbol}: ₹{result['lastPrice']}")
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
