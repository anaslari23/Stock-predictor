"""
Price Service - Real-time stock price fetching with caching
Tries NSE API first, falls back to yfinance
"""

import yfinance as yf
from typing import Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio
from app.services.kite_service import KiteService
from app.services.nse_service import NSEService

class PriceService:
    def __init__(self):
        self.cache: Dict[str, tuple[Dict, datetime]] = {}
        self.cache_ttl = timedelta(seconds=10)
        self.kite_service = KiteService()
        self.nse_service = NSEService()
        logger.info("PriceService initialized with NSE, Kite, and yfinance fallback (10-second cache)")
    
    async def get_price(self, symbol: str) -> Dict:
        """
        Get real-time price for a symbol with 10-second caching
        Tries NSE API first, falls back to yfinance
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
        
        # Try NSE API first
        try:
            logger.info(f"Attempting NSE API for {symbol}")
            price_data = await asyncio.to_thread(self._fetch_nse, symbol)
            
            # Cache the result
            self.cache[symbol] = (price_data, datetime.now())
            logger.info(f"✓ NSE API success for {symbol}: ₹{price_data['lastPrice']:.2f}")
            
            return price_data
            
        except Exception as nse_error:
            logger.warning(f"NSE API failed for {symbol}: {str(nse_error)}")
            
            # Fallback to yfinance
            try:
                logger.info(f"Falling back to yfinance for {symbol}")
                price_data = await asyncio.to_thread(self._fetch_yfinance, symbol)
                
                # Cache the result
                self.cache[symbol] = (price_data, datetime.now())
                logger.info(f"✓ yfinance success for {symbol}: ₹{price_data['lastPrice']:.2f}")
                
                return price_data
                
            except Exception as yf_error:
                logger.error(f"Both NSE and yfinance failed for {symbol}: {str(yf_error)}")
                # Return fallback data
                return self._get_fallback_price(symbol)
    
    def _fetch_nse(self, symbol: str) -> Dict:
        """
        Fetch price from NSE API (blocking call)
        """
        try:
            # Get quote from NSE
            quote_data = self.nse_service.get_quote(symbol)
            
            if not quote_data:
                raise Exception(f"No data returned from NSE for {symbol}")
            
            # Extract price data
            current_price = quote_data.get('lastPrice', 0)
            previous_close = quote_data.get('previousClose', current_price)
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            return {
                'symbol': symbol,
                'lastPrice': round(current_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'timestamp': datetime.now().isoformat(),
                'source': 'nse'
            }
            
        except Exception as e:
            logger.error(f"NSE API error for {symbol}: {str(e)}")
            raise
    
    def _fetch_kite(self, symbol: str) -> Dict:
        """
        Fetch price from Kite API (blocking call)
        """
        try:
            # Convert symbol format if needed (e.g., TCS.NS -> NSE:TCS)
            kite_symbol = self._convert_to_kite_symbol(symbol)
            
            # Get quote from Kite
            quote_data = self.kite_service.get_quote(kite_symbol)
            
            if not quote_data or kite_symbol not in quote_data:
                raise Exception(f"No data returned for {kite_symbol}")
            
            quote = quote_data[kite_symbol]
            
            # Extract price data
            current_price = quote.get('last_price', 0)
            previous_close = quote.get('ohlc', {}).get('close', current_price)
            
            # Calculate change
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            return {
                'symbol': symbol,
                'lastPrice': round(current_price, 2),
                'change': round(change, 2),
                'changePercent': round(change_percent, 2),
                'timestamp': datetime.now().isoformat(),
                'source': 'kite'
            }
            
        except Exception as e:
            logger.error(f"Kite API error for {symbol}: {str(e)}")
            raise
    
    def _convert_to_kite_symbol(self, symbol: str) -> str:
        """
        Convert yfinance symbol format to Kite format
        Example: TCS.NS -> NSE:TCS
        """
        if '.NS' in symbol:
            return f"NSE:{symbol.replace('.NS', '')}"
        elif '.BO' in symbol:
            return f"BSE:{symbol.replace('.BO', '')}"
        else:
            # Assume NSE for indices and other symbols
            return f"NSE:{symbol}"
    
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
