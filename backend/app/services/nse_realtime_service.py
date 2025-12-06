"""
NSE Real-Time Polling Service
Polls NSE every 1-2 seconds to provide near-real-time data
"""

import asyncio
from typing import Dict, Set, Optional
from datetime import datetime
from loguru import logger
from nsepython import nse_eq, nse_get_index_quote
import time


class NSERealTimeService:
    """
    High-frequency polling service for near-real-time NSE data
    Polls every 1-2 seconds during market hours
    """
    
    def __init__(self, poll_interval: float = 1.5):
        self.poll_interval = poll_interval  # seconds
        self.subscribed_symbols: Set[str] = set()
        self.latest_prices: Dict[str, dict] = {}
        self.is_running = False
        self.poll_task = None
        
        # Indices list
        self.indices = {'NIFTY50', 'NIFTY 50', 'NIFTY', 'BANKNIFTY', 'BANK NIFTY', 'NIFTYIT'}
        
        logger.info(f"NSERealTimeService initialized with {poll_interval}s poll interval")
    
    def subscribe(self, symbol: str):
        """Subscribe to a symbol for real-time updates"""
        clean_symbol = symbol.replace('.NS', '').upper()
        self.subscribed_symbols.add(clean_symbol)
        logger.info(f"Subscribed to {clean_symbol}")
    
    def unsubscribe(self, symbol: str):
        """Unsubscribe from a symbol"""
        clean_symbol = symbol.replace('.NS', '').upper()
        self.subscribed_symbols.discard(clean_symbol)
        logger.info(f"Unsubscribed from {clean_symbol}")
    
    def get_latest_price(self, symbol: str) -> Optional[dict]:
        """Get the latest cached price for a symbol"""
        clean_symbol = symbol.replace('.NS', '').upper()
        return self.latest_prices.get(clean_symbol)
    
    def _is_index(self, symbol: str) -> bool:
        """Check if symbol is an index"""
        return symbol.upper() in self.indices
    
    async def _fetch_symbol_data(self, symbol: str) -> Optional[dict]:
        """Fetch data for a single symbol"""
        try:
            if self._is_index(symbol):
                # Map to NSE index names
                index_map = {
                    'NIFTY50': 'NIFTY 50',
                    'NIFTY': 'NIFTY 50',
                    'BANKNIFTY': 'NIFTY BANK',
                    'BANK NIFTY': 'NIFTY BANK',
                }
                index_name = index_map.get(symbol, symbol)
                
                # Fetch index data
                data = await asyncio.to_thread(nse_get_index_quote, index_name)
                
                if data:
                    last_price = float(str(data.get('last', 0)).replace(',', ''))
                    prev_close = float(str(data.get('previousClose', 0)).replace(',', ''))
                    
                    return {
                        'symbol': symbol,
                        'lastPrice': last_price,
                        'change': last_price - prev_close,
                        'changePercent': ((last_price - prev_close) / prev_close * 100) if prev_close else 0,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'nse_realtime'
                    }
            else:
                # Fetch stock data
                data = await asyncio.to_thread(nse_eq, symbol)
                
                if data and 'priceInfo' in data:
                    price_info = data['priceInfo']
                    return {
                        'symbol': symbol,
                        'lastPrice': price_info.get('lastPrice', 0),
                        'change': price_info.get('change', 0),
                        'changePercent': price_info.get('pChange', 0),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'nse_realtime'
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    async def _poll_loop(self):
        """Main polling loop"""
        logger.info("Starting real-time polling loop")
        
        while self.is_running:
            start_time = time.time()
            
            if self.subscribed_symbols:
                # Fetch all subscribed symbols concurrently
                tasks = [
                    self._fetch_symbol_data(symbol)
                    for symbol in self.subscribed_symbols
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update cache
                for symbol, result in zip(self.subscribed_symbols, results):
                    if isinstance(result, dict) and result:
                        self.latest_prices[symbol] = result
                        logger.debug(f"Updated {symbol}: ₹{result['lastPrice']}")
                
                logger.info(f"Polled {len(self.subscribed_symbols)} symbols in {time.time() - start_time:.2f}s")
            
            # Wait for next poll interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.poll_interval - elapsed)
            await asyncio.sleep(sleep_time)
    
    async def start(self):
        """Start the polling service"""
        if self.is_running:
            logger.warning("Service already running")
            return
        
        self.is_running = True
        self.poll_task = asyncio.create_task(self._poll_loop())
        logger.info("Real-time polling service started")
    
    async def stop(self):
        """Stop the polling service"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.poll_task:
            self.poll_task.cancel()
            try:
                await self.poll_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Real-time polling service stopped")


# Global instance
_realtime_service: Optional[NSERealTimeService] = None


def get_realtime_service() -> NSERealTimeService:
    """Get or create the global real-time service instance"""
    global _realtime_service
    if _realtime_service is None:
        _realtime_service = NSERealTimeService(poll_interval=1.5)
    return _realtime_service
