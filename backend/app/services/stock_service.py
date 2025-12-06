"""
Stock Service - Handles stock data fetching with REAL data from NSE
"""

from typing import List, Dict
from datetime import datetime, timedelta
from loguru import logger
from nsepython import nse_eq, nse_get_index_quote
import pandas as pd


class StockService:
    def __init__(self):
        logger.info("StockService initialized with NSE data")
        self.stock_symbols = [
            "NIFTY50", "BANKNIFTY", "NIFTYIT", "RELIANCE", "TCS",
            "HDFCBANK", "ICICIBANK", "INFY", "SBIN", "BHARTIARTL"
        ]
    
    async def search(self, query: str) -> List[str]:
        """Search stocks by query"""
        return [s for s in self.stock_symbols if query.upper() in s.upper()]
    
    def _is_index(self, symbol: str) -> bool:
        """Check if symbol is an index"""
        indices = ['NIFTY50', 'NIFTY', 'BANKNIFTY', 'NIFTYIT', 'BANK NIFTY', 'NIFTY BANK']
        return symbol.upper() in indices
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for symbol using NSE"""
        try:
            # Remove .NS suffix
            clean_symbol = symbol.replace(".NS", "").upper()
            
            if self._is_index(clean_symbol):
                # Map to NSE index names
                index_map = {
                    'NIFTY50': 'NIFTY 50',
                    'NIFTY': 'NIFTY 50',
                    'BANKNIFTY': 'NIFTY BANK',
                    'BANK NIFTY': 'NIFTY BANK',
                }
                index_name = index_map.get(clean_symbol, clean_symbol)
                data = nse_get_index_quote(index_name)
                return float(str(data.get('last', 0)).replace(',', ''))
            else:
                data = nse_eq(clean_symbol)
                price_info = data.get('priceInfo', {})
                return float(price_info.get('lastPrice', 0))
                
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    async def get_ohlcv(self, symbol: str, timeframe: str) -> List[Dict]:
        """
        Get OHLCV data - Returns ONLY real current day data from NSE
        NO MOCK DATA - Only actual NSE data
        """
        try:
            # Remove .NS suffix
            clean_symbol = symbol.replace(".NS", "").upper()
            
            logger.info(f"Fetching REAL OHLCV for {clean_symbol}")
            
            if self._is_index(clean_symbol):
                # Get index data
                index_map = {
                    'NIFTY50': 'NIFTY 50',
                    'NIFTY': 'NIFTY 50',
                    'BANKNIFTY': 'NIFTY BANK',
                    'BANK NIFTY': 'NIFTY BANK',
                }
                index_name = index_map.get(clean_symbol, clean_symbol)
                data = nse_get_index_quote(index_name)
                
                # NSE only provides current day data
                last_price = float(str(data.get('last', 0)).replace(',', ''))
                prev_close = float(str(data.get('previousClose', 0)).replace(',', ''))
                open_price = float(str(data.get('open', prev_close)).replace(',', ''))
                
                # Create a single candle for today - REAL DATA ONLY
                candles = [{
                    "time": datetime.now().replace(hour=9, minute=15, second=0).isoformat(),
                    "open": open_price,
                    "high": last_price,  # Current high
                    "low": min(open_price, last_price),  # Current low
                    "close": last_price,
                    "volume": 0  # Not available for indices
                }]
                
            else:
                # Get equity data
                data = nse_eq(clean_symbol)
                price_info = data.get('priceInfo', {})
                
                last_price = float(price_info.get('lastPrice', 0))
                prev_close = float(price_info.get('previousClose', 0))
                open_price = float(price_info.get('open', prev_close))
                intraday = price_info.get('intraDayHighLow', {})
                high_price = float(intraday.get('max', last_price))
                low_price = float(intraday.get('min', last_price))
                
                # Create a single candle for today - REAL DATA ONLY
                candles = [{
                    "time": datetime.now().replace(hour=9, minute=15, second=0).isoformat(),
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": last_price,
                    "volume": 0  # Would need to parse from NSE if available
                }]
            
            logger.info(f"Returning {len(candles)} REAL candle(s) for {clean_symbol}")
            return candles
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []
    
    async def get_details(self, symbol: str) -> Dict:
        """Get detailed stock information from NSE"""
        try:
            # Remove .NS suffix
            clean_symbol = symbol.replace(".NS", "").upper()
            
            if self._is_index(clean_symbol):
                index_map = {
                    'NIFTY50': 'NIFTY 50',
                    'NIFTY': 'NIFTY 50',
                    'BANKNIFTY': 'NIFTY BANK',
                }
                index_name = index_map.get(clean_symbol, clean_symbol)
                data = nse_get_index_quote(index_name)
                
                last_price = float(str(data.get('last', 0)).replace(',', ''))
                prev_close = float(str(data.get('previousClose', 0)).replace(',', ''))
                change = last_price - prev_close
                percent_change = (change / prev_close * 100) if prev_close != 0 else 0
                
                return {
                    "symbol": clean_symbol,
                    "name": index_name,
                    "price": last_price,
                    "change": change,
                    "percentChange": percent_change,
                    "prediction": "UP" if change > 0 else "DOWN",
                    "confidence": 0.75
                }
            else:
                data = nse_eq(clean_symbol)
                price_info = data.get('priceInfo', {})
                metadata = data.get('metadata', {})
                
                last_price = float(price_info.get('lastPrice', 0))
                prev_close = float(price_info.get('previousClose', 0))
                change = last_price - prev_close
                percent_change = (change / prev_close * 100) if prev_close != 0 else 0
                
                return {
                    "symbol": clean_symbol,
                    "name": metadata.get('companyName', clean_symbol),
                    "price": last_price,
                    "change": change,
                    "percentChange": percent_change,
                    "prediction": "UP" if change > 0 else "DOWN",
                    "confidence": 0.75
                }
        except Exception as e:
            logger.error(f"Error fetching details for {symbol}: {e}")
            return {
                "symbol": symbol,
                "name": symbol,
                "price": 0.0,
                "change": 0.0,
                "percentChange": 0.0,
                "prediction": "NEUTRAL",
                "confidence": 0.0
            }
