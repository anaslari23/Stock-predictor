"""
Screener Service - Handles stock screening and filtering
"""

from typing import List, Dict
import random
from loguru import logger

class ScreenerService:
    def __init__(self):
        logger.info("ScreenerService initialized")
    
    async def get_filtered_stocks(self, filter_type: str, page: int) -> List[Dict]:
        """Get stocks based on filter criteria"""
        stocks = []
        page_size = 10
        
        for i in range(page_size):
            symbol = f"STOCK{(page - 1) * page_size + i + 1}"
            base_price = 100 + random.random() * 900
            
            if filter_type == "bullish":
                change = random.uniform(5, 50)
                confidence = 0.7 + random.random() * 0.25
            elif filter_type == "bearish":
                change = -random.uniform(5, 50)
                confidence = 0.7 + random.random() * 0.25
            else:
                change = random.uniform(-50, 50)
                confidence = 0.6 + random.random() * 0.35
            
            stocks.append({
                "symbol": symbol,
                "name": f"{symbol} Ltd",
                "price": round(base_price + change, 2),
                "change": round(change, 2),
                "percentChange": round((change / base_price) * 100, 2),
                "prediction": "UP" if change > 0 else "DOWN",
                "confidence": round(confidence, 2)
            })
        
        return stocks
    
    async def get_ai_picks(self) -> List[Dict]:
        """Get AI-recommended stocks"""
        return await self.get_filtered_stocks("bullish", 1)
