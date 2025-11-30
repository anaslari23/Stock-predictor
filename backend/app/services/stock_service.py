"""
Stock Service - Handles stock data fetching
"""

from typing import List, Dict
import random
from datetime import datetime, timedelta
from loguru import logger

class StockService:
    def __init__(self):
        logger.info("StockService initialized")
        self.stock_symbols = [
            "NIFTY50", "BANKNIFTY", "NIFTYIT", "RELIANCE.NS", "TCS.NS",
            "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS"
        ]
    
    async def search(self, query: str) -> List[str]:
        """Search stocks by query"""
        return [s for s in self.stock_symbols if query.upper() in s.upper()]
    
    async def get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        # TODO: Integrate with yfinance or real data source
        base_prices = {
            "NIFTY50": 22000.0,
            "BANKNIFTY": 46000.0,
            "TCS.NS": 4000.0,
            "RELIANCE.NS": 2900.0,
        }
        base = base_prices.get(symbol, 1000.0)
        return base + random.uniform(-20, 20)
    
    async def get_ohlcv(self, symbol: str, timeframe: str) -> List[Dict]:
        """Get OHLCV data for charting"""
        # TODO: Integrate with yfinance
        candles = []
        count = {"1D": 75, "1W": 100, "1M": 90, "1Y": 250}.get(timeframe, 100)
        base_price = await self.get_current_price(symbol)
        
        for i in range(count):
            time = datetime.now() - timedelta(hours=i)
            open_price = base_price + random.uniform(-50, 50)
            close_price = open_price + random.uniform(-20, 20)
            high_price = max(open_price, close_price) + random.uniform(0, 10)
            low_price = min(open_price, close_price) - random.uniform(0, 10)
            
            candles.append({
                "time": time.isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(10000, 100000)
            })
        
        return list(reversed(candles))
    
    async def get_details(self, symbol: str) -> Dict:
        """Get detailed stock information"""
        price = await self.get_current_price(symbol)
        change = random.uniform(-50, 50)
        
        return {
            "symbol": symbol,
            "name": f"{symbol} Ltd",
            "price": price,
            "change": change,
            "percentChange": (change / price) * 100,
            "prediction": "UP" if change > 0 else "DOWN",
            "confidence": 0.7 + random.random() * 0.25
        }
