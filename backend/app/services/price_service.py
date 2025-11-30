"""
Price Service - Real-time stock price fetching with caching
"""

import yfinance as yf
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio

class PriceService:
    def __init__(self):
        self.cache: Dict[str, tuple[Dict, datetime]] = {}
        self.cache_ttl = timedelta(seconds=10)
        logger.info("PriceService initialized with 10-second cache")
    
    async def get_price(self, symbol: str) -> Dict:
        """
        Get real-time price for a symbol with 10-second caching
        """
        # Check cache first
        if symbol in self.cache:
            data, timestamp = self.cache[symbol]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info(f"Cache hit for {symbol}")
                return data
            else:
                logger.info(f"Cache expired for {symbol}")
                del self.cache[symbol]
        
        try:
            # Fetch from yfinance (run in thread pool to avoid blocking)
            price_data = await asyncio.to_thread(self._fetch_yfinance, symbol)
            
            # Cache the result
            self.cache[symbol] = (price_data, datetime.now())
            logger.info(f"Cached price for {symbol}: ₹{price_data['lastPrice']:.2f}")
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            # Return fallback data
            return self._get_fallback_price(symbol)
    
    def _fetch_yfinance(self, symbol: str) -> Dict:
        """
        Fetch price from yfinance (blocking call)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose', 0)
            previous_close = info.get('previousClose', current_price)
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            return {
                'symbol': symbol,
                'lastPrice': round(current_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'timestamp': datetime.now().isoformat(),
                'source': 'yfinance'
            }
            
        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {str(e)}")
            raise
    
    def _get_fallback_price(self, symbol: str) -> Dict:
        """
        Fallback price data when live fetch fails
        """
        import random
        
        # Base prices for common symbols
        base_prices = {
            'TCS.NS': 4000.0,
            'RELIANCE.NS': 2900.0,
            'INFY.NS': 1600.0,
            'HDFCBANK.NS': 1450.0,
            'SBIN.NS': 750.0,
            'NIFTY50': 22000.0,
            'BANKNIFTY': 46000.0,
        }
        
        base_price = base_prices.get(symbol, 1000.0)
        change = random.uniform(-20, 20)
        change_percent = (change / base_price) * 100
        
        logger.warning(f"Using fallback price for {symbol}")
        
        return {
            'symbol': symbol,
            'lastPrice': round(base_price + change, 2),
            'change': round(change, 2),
            'changePercent': round(change_percent, 2),
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def clear_cache(self):
        """Clear all cached prices"""
        self.cache.clear()
        logger.info("Price cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = sum(
            1 for _, (_, timestamp) in self.cache.items()
            if datetime.now() - timestamp < self.cache_ttl
        )
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_ttl_seconds': self.cache_ttl.total_seconds()
        }
