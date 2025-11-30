"""
Feature engineering module for stock prediction.

Implements technical indicators, lag features, and rolling statistics
for time series forecasting.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from src.utils import setup_logger


class FeatureEngine:
    """
    Feature engineering for stock market time series data.
    
    Generates:
    - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
    - Lag features
    - Rolling statistics
    - Price transformations
    """
    
    def __init__(self):
        """Initialize FeatureEngine."""
        self.logger = setup_logger("FeatureEngine")
    
    def add_sma(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        windows: List[int] = [20, 50, 200]
    ) -> pd.DataFrame:
        """
        Add Simple Moving Average features.
        
        Args:
            df: Input DataFrame
            column: Column to calculate SMA on
            windows: List of window sizes
            
        Returns:
            DataFrame with SMA columns added
        """
        for window in windows:
            df[f'SMA_{window}'] = df[column].rolling(window=window).mean()
        return df
    
    def add_ema(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        spans: List[int] = [12, 26, 50]
    ) -> pd.DataFrame:
        """
        Add Exponential Moving Average features.
        
        Args:
            df: Input DataFrame
            column: Column to calculate EMA on
            spans: List of span values
            
        Returns:
            DataFrame with EMA columns added
        """
        for span in spans:
            df[f'EMA_{span}'] = df[column].ewm(span=span, adjust=False).mean()
        return df
    
    def add_rsi(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        period: int = 14
    ) -> pd.DataFrame:
        """
        Add Relative Strength Index.
        
        Args:
            df: Input DataFrame
            column: Column to calculate RSI on
            period: RSI period
            
        Returns:
            DataFrame with RSI column added
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
        return df
    
    def add_macd(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence) indicator.
        
        Args:
            df: Input DataFrame
            column: Column to calculate MACD on
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            DataFrame with MACD columns added
        """
        ema_fast = df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[column].ewm(span=slow, adjust=False).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        return df
    
    def add_bollinger_bands(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        window: int = 20,
        num_std: float = 2.0
    ) -> pd.DataFrame:
        """
        Add Bollinger Bands.
        
        Args:
            df: Input DataFrame
            column: Column to calculate bands on
            window: Moving average window
            num_std: Number of standard deviations
            
        Returns:
            DataFrame with Bollinger Band columns added
        """
        sma = df[column].rolling(window=window).mean()
        std = df[column].rolling(window=window).std()
        
        df['BB_Middle'] = sma
        df['BB_Upper'] = sma + (std * num_std)
        df['BB_Lower'] = sma - (std * num_std)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df[column] - df['BB_Lower']) / df['BB_Width']
        return df
    
    def add_atr(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.DataFrame:
        """
        Add Average True Range (volatility indicator).
        
        Args:
            df: Input DataFrame with High, Low, Close
            period: ATR period
            
        Returns:
            DataFrame with ATR column added
        """
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df[f'ATR_{period}'] = true_range.rolling(window=period).mean()
        return df
    
    def add_lag_features(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        lags: List[int] = [1, 2, 3, 5, 10]
    ) -> pd.DataFrame:
        """
        Add lagged values of a column.
        
        Args:
            df: Input DataFrame
            column: Column to create lags for
            lags: List of lag periods
            
        Returns:
            DataFrame with lag columns added
        """
        for lag in lags:
            df[f'{column}_Lag_{lag}'] = df[column].shift(lag)
        return df
    
    def add_rolling_stats(
        self,
        df: pd.DataFrame,
        column: str = 'Close',
        windows: List[int] = [5, 10, 20]
    ) -> pd.DataFrame:
        """
        Add rolling statistics (mean, std, min, max).
        
        Args:
            df: Input DataFrame
            column: Column to calculate statistics on
            windows: List of window sizes
            
        Returns:
            DataFrame with rolling statistics columns added
        """
        for window in windows:
            df[f'{column}_RollingMean_{window}'] = df[column].rolling(window).mean()
            df[f'{column}_RollingStd_{window}'] = df[column].rolling(window).std()
            df[f'{column}_RollingMin_{window}'] = df[column].rolling(window).min()
            df[f'{column}_RollingMax_{window}'] = df[column].rolling(window).max()
        return df
    
    def add_price_transforms(
        self,
        df: pd.DataFrame,
        column: str = 'Close'
    ) -> pd.DataFrame:
        """
        Add price transformation features.
        
        Args:
            df: Input DataFrame
            column: Price column
            
        Returns:
            DataFrame with transformation columns added
        """
        # Returns
        df['Returns'] = df[column].pct_change()
        df['Log_Returns'] = np.log(df[column] / df[column].shift(1))
        
        # Price changes
        df['Price_Change'] = df[column].diff()
        df['Price_Change_Pct'] = df['Price_Change'] / df[column].shift(1) * 100
        
        # High-Low range
        df['HL_Range'] = df['High'] - df['Low']
        df['HL_Range_Pct'] = df['HL_Range'] / df['Close'] * 100
        
        # Close position in daily range
        df['Close_Position'] = (df['Close'] - df['Low']) / df['HL_Range']
        
        return df
    
    def add_volume_features(
        self,
        df: pd.DataFrame,
        windows: List[int] = [5, 20]
    ) -> pd.DataFrame:
        """
        Add volume-based features.
        
        Args:
            df: Input DataFrame
            windows: List of window sizes
            
        Returns:
            DataFrame with volume features added
        """
        # Volume moving averages
        for window in windows:
            df[f'Volume_MA_{window}'] = df['Volume'].rolling(window).mean()
        
        # Volume ratio
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_20']
        
        # Price-Volume trend
        df['PV_Trend'] = df['Returns'] * df['Volume']
        
        return df
    
    def create_all_features(
        self,
        df: pd.DataFrame,
        config: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Create all features at once.
        
        Args:
            df: Input DataFrame with OHLCV data
            config: Optional configuration dictionary
            
        Returns:
            DataFrame with all features added
        """
        self.logger.info("Creating all features...")
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Technical indicators
        df = self.add_sma(df, windows=[20, 50, 200])
        df = self.add_ema(df, spans=[12, 26, 50])
        df = self.add_rsi(df, period=14)
        df = self.add_macd(df)
        df = self.add_bollinger_bands(df)
        df = self.add_atr(df, period=14)
        
        # Price transformations
        df = self.add_price_transforms(df)
        
        # Lag features
        df = self.add_lag_features(df, lags=[1, 2, 3, 5, 10])
        
        # Rolling statistics
        df = self.add_rolling_stats(df, windows=[5, 10, 20])
        
        # Volume features
        df = self.add_volume_features(df, windows=[5, 20])
        
        # Drop NaN rows created by rolling operations
        initial_rows = len(df)
        df = df.dropna()
        dropped_rows = initial_rows - len(df)
        
        self.logger.info(
            f"Feature engineering complete. "
            f"Created {len(df.columns)} columns. "
            f"Dropped {dropped_rows} rows with NaN values."
        )
        
        return df
    
    def get_feature_importance_groups(self) -> Dict[str, List[str]]:
        """
        Get feature groups for analysis.
        
        Returns:
            Dictionary mapping group names to feature patterns
        """
        return {
            "trend": ["SMA_", "EMA_", "MACD"],
            "momentum": ["RSI_", "MACD_Hist"],
            "volatility": ["BB_", "ATR_", "RollingStd"],
            "volume": ["Volume_", "PV_Trend"],
            "price": ["Returns", "Price_Change", "Close_Position"],
            "lag": ["_Lag_"]
        }
