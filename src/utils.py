"""
Utility functions for the stock predictor platform.

Provides logging setup, configuration management, and common helper functions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import pytz


def setup_logger(
    name: str,
    log_dir: str = "logs",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = Path(log_dir) / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        # Return default configuration
        return get_default_config()
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for the platform.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "indices": {
            "NIFTY50": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "NIFTYIT": "^CNXIT"
        },
        "data": {
            "start_date": "2020-01-01",
            "interval": "1d",
            "raw_dir": "data/raw",
            "processed_dir": "data/processed"
        },
        "features": {
            "technical_indicators": [
                "SMA_20", "SMA_50", "SMA_200",
                "EMA_12", "EMA_26",
                "RSI_14", "MACD",
                "BB_UPPER", "BB_LOWER",
                "ATR_14", "ADX_14"
            ],
            "lag_periods": [1, 2, 3, 5, 10, 20],
            "rolling_windows": [5, 10, 20, 50]
        },
        "model": {
            "test_size": 0.2,
            "validation_size": 0.1,
            "random_state": 42
        },
        "timezone": "Asia/Kolkata"
    }


def save_config(config: Dict[str, Any], config_path: str = "config.json") -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


def get_ist_time() -> datetime:
    """
    Get current time in IST timezone.
    
    Returns:
        Current datetime in IST
    """
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def ensure_dir(directory: str) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.2f}"
    return f"{currency} {amount:,.2f}"
