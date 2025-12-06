"""
Market Status Service - Check if NSE market is open
"""

from datetime import datetime, time
import pytz
from typing import Dict
from loguru import logger


class MarketStatusService:
    """Service to check NSE market status"""
    
    # NSE market hours (IST)
    MARKET_OPEN_TIME = time(9, 15)  # 9:15 AM
    MARKET_CLOSE_TIME = time(15, 30)  # 3:30 PM
    
    # NSE timezone
    IST = pytz.timezone('Asia/Kolkata')
    
    @classmethod
    def is_market_open(cls) -> bool:
        """Check if NSE market is currently open"""
        now = datetime.now(cls.IST)
        
        # Check if weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if within market hours
        current_time = now.time()
        return cls.MARKET_OPEN_TIME <= current_time <= cls.MARKET_CLOSE_TIME
    
    @classmethod
    def get_market_status(cls) -> Dict:
        """Get detailed market status"""
        now = datetime.now(cls.IST)
        is_open = cls.is_market_open()
        
        # Calculate next market open/close time
        if is_open:
            next_change = "Market closes"
            next_time = datetime.combine(now.date(), cls.MARKET_CLOSE_TIME)
        else:
            next_change = "Market opens"
            # If after market hours today, next open is tomorrow
            if now.time() > cls.MARKET_CLOSE_TIME:
                next_day = now.date().replace(day=now.day + 1)
                next_time = datetime.combine(next_day, cls.MARKET_OPEN_TIME)
            else:
                next_time = datetime.combine(now.date(), cls.MARKET_OPEN_TIME)
        
        next_time = cls.IST.localize(next_time)
        
        return {
            "is_open": is_open,
            "status": "OPEN" if is_open else "CLOSED",
            "current_time": now.isoformat(),
            "next_change": next_change,
            "next_change_time": next_time.isoformat(),
            "market_hours": f"{cls.MARKET_OPEN_TIME.strftime('%H:%M')} - {cls.MARKET_CLOSE_TIME.strftime('%H:%M')} IST"
        }
    
    @classmethod
    def get_data_freshness_message(cls) -> str:
        """Get a user-friendly message about data freshness"""
        if cls.is_market_open():
            return "Live market data"
        else:
            return "Showing previous close (Market closed)"


# Global instance
market_status_service = MarketStatusService()
