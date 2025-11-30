"""
Stock Predictor - A professional platform for Indian stock indices prediction.

This package provides tools for:
- Data ingestion from yfinance
- Feature engineering for time series
- Model training and evaluation
- Backtesting strategies
- Deployment utilities
"""

__version__ = "0.1.0"
__author__ = "Stock Predictor Team"

from src.data_ingest import DataIngestor
from src.features import FeatureEngine
from src.utils import setup_logger, load_config

__all__ = [
    "DataIngestor",
    "FeatureEngine",
    "setup_logger",
    "load_config",
]
