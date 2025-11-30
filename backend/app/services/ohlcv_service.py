"""
OHLCV Service - Historical data with technical indicators and pickle caching
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import asyncio

class OHLCVService:
    def __init__(self):
        self.cache_dir = Path("data/ohlcv_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=1)  # Cache for 1 hour
        logger.info(f"OHLCVService initialized with cache at {self.cache_dir}")
    
    async def get_ohlcv(self, symbol: str, range_period: str = "1y") -> Dict:
        """
        Get OHLCV data with technical indicators
        """
        try:
            # Check cache first
            cached_data = self._load_from_cache(symbol, range_period)
            if cached_data is not None:
                logger.info(f"Cache hit for {symbol} ({range_period})")
                return cached_data
            
            # Fetch from yfinance (run in thread pool)
            df = await asyncio.to_thread(self._fetch_yfinance, symbol, range_period)
            
            # Calculate technical indicators
            df = self._calculate_indicators(df)
            
            # Convert to JSON format
            result = self._format_response(symbol, range_period, df)
            
            # Save to cache
            self._save_to_cache(symbol, range_period, df)
            
            logger.info(f"Fetched and cached {len(df)} candles for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {str(e)}")
            raise
    
    def _fetch_yfinance(self, symbol: str, range_period: str) -> pd.DataFrame:
        """
        Fetch OHLCV data from yfinance
        """
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=range_period)
        
        if df.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Rename columns to lowercase
        df.columns = [col.lower() for col in df.columns]
        
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        """
        # Moving Averages
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        
        # RSI (14)
        df['rsi'] = self._calculate_rsi(df['close'], period=14)
        
        # MACD
        macd_data = self._calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']
        
        # Bollinger Bands
        bb_data = self._calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_data['upper']
        df['bb_middle'] = bb_data['middle']
        df['bb_lower'] = bb_data['lower']
        
        # ATR (14)
        df['atr'] = self._calculate_atr(df, period=14)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast=12, slow=26, signal=9) -> Dict:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        
        return {
            'macd': macd,
            'signal': macd_signal,
            'histogram': macd_hist
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period=20, std_dev=2) -> Dict:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def _format_response(self, symbol: str, range_period: str, df: pd.DataFrame) -> Dict:
        """
        Format DataFrame to JSON response
        """
        candles = []
        
        for idx, row in df.iterrows():
            candle = {
                't': idx.isoformat(),
                'o': round(row['open'], 2),
                'h': round(row['high'], 2),
                'l': round(row['low'], 2),
                'c': round(row['close'], 2),
                'v': int(row['volume']),
            }
            
            # Add indicators (handle NaN values)
            if pd.notna(row.get('ma20')):
                candle['ma20'] = round(row['ma20'], 2)
            if pd.notna(row.get('ma50')):
                candle['ma50'] = round(row['ma50'], 2)
            if pd.notna(row.get('rsi')):
                candle['rsi'] = round(row['rsi'], 2)
            if pd.notna(row.get('macd')):
                candle['macd'] = round(row['macd'], 2)
            if pd.notna(row.get('macd_signal')):
                candle['macd_signal'] = round(row['macd_signal'], 2)
            if pd.notna(row.get('macd_hist')):
                candle['macd_hist'] = round(row['macd_hist'], 2)
            if pd.notna(row.get('bb_upper')):
                candle['bb_upper'] = round(row['bb_upper'], 2)
            if pd.notna(row.get('bb_middle')):
                candle['bb_middle'] = round(row['bb_middle'], 2)
            if pd.notna(row.get('bb_lower')):
                candle['bb_lower'] = round(row['bb_lower'], 2)
            if pd.notna(row.get('atr')):
                candle['atr'] = round(row['atr'], 2)
            
            candles.append(candle)
        
        return {
            'symbol': symbol,
            'range': range_period,
            'candles': candles,
            'count': len(candles)
        }
    
    def _get_cache_path(self, symbol: str, range_period: str) -> Path:
        """Get cache file path"""
        safe_symbol = symbol.replace('.', '_')
        return self.cache_dir / f"{safe_symbol}_{range_period}.pkl"
    
    def _load_from_cache(self, symbol: str, range_period: str) -> Dict:
        """Load data from pickle cache"""
        cache_path = self._get_cache_path(symbol, range_period)
        
        if not cache_path.exists():
            return None
        
        # Check if cache is expired
        cache_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if cache_age > self.cache_ttl:
            logger.info(f"Cache expired for {symbol} ({range_period})")
            cache_path.unlink()
            return None
        
        try:
            df = pd.read_pickle(cache_path)
            return self._format_response(symbol, range_period, df)
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return None
    
    def _save_to_cache(self, symbol: str, range_period: str, df: pd.DataFrame):
        """Save data to pickle cache"""
        cache_path = self._get_cache_path(symbol, range_period)
        
        try:
            df.to_pickle(cache_path)
            logger.info(f"Saved to cache: {cache_path}")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def clear_cache(self, symbol: str = None):
        """Clear cache for a symbol or all symbols"""
        if symbol:
            for file in self.cache_dir.glob(f"{symbol.replace('.', '_')}_*.pkl"):
                file.unlink()
                logger.info(f"Deleted cache: {file}")
        else:
            for file in self.cache_dir.glob("*.pkl"):
                file.unlink()
            logger.info("Cleared all OHLCV cache")
