"""
Kite Service - Zerodha Kite Connect Integration
"""

from kiteconnect import KiteConnect
from app.core.config import settings
from loguru import logger
from typing import Dict, List, Optional
import pandas as pd

class KiteService:
    def __init__(self):
        self.api_key = settings.KITE_API_KEY
        self.api_secret = settings.KITE_API_SECRET
        self.access_token = settings.KITE_ACCESS_TOKEN
        
        self.kite = KiteConnect(api_key=self.api_key)
        
        if self.access_token:
            self.kite.set_access_token(self.access_token)
            logger.info("KiteService initialized with access token")
        else:
            logger.warning("KiteService initialized without access token. Login required.")
            
        self.instruments_cache = {}
        
    def get_login_url(self) -> str:
        """Get the login URL for Kite Connect"""
        return self.kite.login_url()
    
    def generate_session(self, request_token: str) -> Dict:
        """Exchange request token for access token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            
            # Update settings (in memory only, won't persist to .env automatically)
            settings.KITE_ACCESS_TOKEN = self.access_token
            
            logger.info("Kite session generated successfully")
            return data
        except Exception as e:
            logger.error(f"Error generating Kite session: {str(e)}")
            raise

    def get_quote(self, symbol: str) -> Dict:
        """
        Get live quote for a symbol
        Symbol format: 'NSE:TCS', 'BSE:INFY'
        """
        try:
            # If symbol doesn't have exchange, default to NSE
            if ':' not in symbol:
                symbol = f"NSE:{symbol.replace('.NS', '')}"
                
            quotes = self.kite.quote(symbol)
            return quotes.get(symbol, {})
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {str(e)}")
            raise

    def get_ohlc(self, symbol: str) -> Dict:
        """Get OHLC data"""
        try:
            if ':' not in symbol:
                symbol = f"NSE:{symbol.replace('.NS', '')}"
            return self.kite.ohlc(symbol)
        except Exception as e:
            logger.error(f"Error fetching OHLC for {symbol}: {str(e)}")
            raise

    def get_instruments(self, exchange: str = "NSE") -> List[Dict]:
        """Get list of instruments"""
        try:
            if exchange in self.instruments_cache:
                return self.instruments_cache[exchange]
                
            instruments = self.kite.instruments(exchange)
            self.instruments_cache[exchange] = instruments
            logger.info(f"Fetched {len(instruments)} instruments for {exchange}")
            return instruments
        except Exception as e:
            logger.error(f"Error fetching instruments: {str(e)}")
            raise
            
    def get_instrument_token(self, symbol: str) -> Optional[int]:
        """
        Get instrument token for a symbol (e.g., 'TCS')
        """
        try:
            # Normalize symbol
            clean_symbol = symbol.replace('.NS', '').upper()
            
            instruments = self.get_instruments("NSE")
            for instrument in instruments:
                if instrument['tradingsymbol'] == clean_symbol:
                    return instrument['instrument_token']
            
            logger.warning(f"Instrument token not found for {symbol}")
            return None
        except Exception as e:
            logger.error(f"Error finding instrument token: {str(e)}")
            return None
