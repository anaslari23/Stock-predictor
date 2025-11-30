"""
Feature Engineering Module
Generates features identical to the training pipeline with normalization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from loguru import logger
import pickle

class FeatureEngineer:
    def __init__(self):
        self.feature_names = []
        self.scaler = None
        self.scaler_path = Path("app/ml/models/scaler.pkl")
        self._load_scaler()
        logger.info("FeatureEngineer initialized")
    
    def _load_scaler(self):
        """Load saved scaler from training"""
        try:
            if self.scaler_path.exists():
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {self.scaler_path}")
            else:
                logger.warning(f"Scaler not found at {self.scaler_path}, will skip normalization")
        except Exception as e:
            logger.error(f"Error loading scaler: {str(e)}")
            self.scaler = None
    
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate all features from OHLCV data
        Must match training pipeline exactly
        """
        df = df.copy()
        
        # 1. Returns features
        df = self._add_returns(df)
        
        # 2. Moving averages
        df = self._add_moving_averages(df)
        
        # 3. Technical indicators
        df = self._add_technical_indicators(df)
        
        # 4. Volatility features
        df = self._add_volatility_features(df)
        
        # 5. Volume features
        df = self._add_volume_features(df)
        
        # Drop NaN rows
        df = df.dropna()
        
        # Store feature names (exclude OHLCV columns)
        self.feature_names = [col for col in df.columns 
                             if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        logger.info(f"Generated {len(self.feature_names)} features from {len(df)} rows")
        return df
    
    def _add_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate return features"""
        # Simple returns
        df['ret1'] = df['close'].pct_change(1)
        df['ret5'] = df['close'].pct_change(5)
        df['ret10'] = df['close'].pct_change(10)
        
        # Log returns
        df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
        
        return df
    
    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate moving averages"""
        for period in [5, 10, 20, 50]:
            # Simple Moving Average
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
            
            # Exponential Moving Average
            df[f'ema{period}'] = df['close'].ewm(span=period, adjust=False).mean()
            
            # Price relative to MA
            df[f'close_ma{period}_ratio'] = df['close'] / df[f'ma{period}']
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # RSI (14)
        df['rsi'] = self._calculate_rsi(df['close'], period=14)
        
        # MACD
        macd_data = self._calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']
        
        # Bollinger Bands
        bb = self._calculate_bollinger_bands(df['close'], period=20, std_dev=2)
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']
        df['bb_width'] = (bb['upper'] - bb['lower']) / bb['middle']
        df['bb_position'] = (df['close'] - bb['lower']) / (bb['upper'] - bb['lower'])
        
        # ATR (14)
        df['atr'] = self._calculate_atr(df, period=14)
        df['atr_ratio'] = df['atr'] / df['close']
        
        # Stochastic Oscillator
        stoch = self._calculate_stochastic(df, period=14)
        df['stoch_k'] = stoch['k']
        df['stoch_d'] = stoch['d']
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility features"""
        # Rolling standard deviation
        df['std_5'] = df['ret1'].rolling(window=5).std()
        df['std_10'] = df['ret1'].rolling(window=10).std()
        df['std_20'] = df['ret1'].rolling(window=20).std()
        
        # Volatility ratio
        df['vol_ratio'] = df['std_5'] / df['std_20']
        
        # High-Low range
        df['hl_range'] = (df['high'] - df['low']) / df['close']
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume features"""
        # Volume moving averages
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma20'] = df['volume'].rolling(window=20).mean()
        
        # Volume ratio
        df['volume_ratio'] = df['volume'] / df['volume_ma20']
        
        # Volume change
        df['volume_change'] = df['volume'].pct_change()
        
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
    
    def _calculate_stochastic(self, df: pd.DataFrame, period=14) -> Dict:
        """Calculate Stochastic Oscillator"""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()
        
        return {'k': k, 'd': d}
    
    def get_last_feature_row(self, df: pd.DataFrame, normalize: bool = True) -> np.ndarray:
        """
        Get the last valid feature row for prediction
        
        Args:
            df: DataFrame with features
            normalize: Whether to apply normalization using saved scaler
            
        Returns:
            Feature vector as numpy array
        """
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        # Get only feature columns
        feature_cols = [col for col in df.columns 
                       if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        # Get last row
        last_row = df[feature_cols].iloc[-1:].copy()
        
        # Check for NaN values
        if last_row.isnull().any().any():
            logger.warning("Last row contains NaN values, using second-to-last row")
            last_row = df[feature_cols].iloc[-2:-1].copy()
        
        # Normalize if scaler is available
        if normalize and self.scaler is not None:
            try:
                last_row_normalized = self.scaler.transform(last_row)
                logger.info("Applied normalization using saved scaler")
                return last_row_normalized[0]
            except Exception as e:
                logger.error(f"Error applying scaler: {str(e)}, returning unnormalized features")
                return last_row.values[0]
        else:
            if normalize:
                logger.warning("Scaler not available, returning unnormalized features")
            return last_row.values[0]
    
    def get_feature_vector(self, df: pd.DataFrame) -> np.ndarray:
        """
        Alias for get_last_feature_row for backward compatibility
        """
        return self.get_last_feature_row(df, normalize=True)

