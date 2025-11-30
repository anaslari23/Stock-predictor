"""
Pydantic Models for Request/Response Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# ============================================================================
# PREDICTION MODELS
# ============================================================================

class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")

class PredictionResponse(BaseModel):
    symbol: str
    price: float
    trend: str = Field(..., description="UP or DOWN")
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "TCS.NS",
                "price": 4000.50,
                "trend": "UP",
                "confidence": 0.85,
                "timestamp": "2024-01-01T12:00:00"
            }
        }

# ============================================================================
# STOCK MODELS
# ============================================================================

class StockData(BaseModel):
    symbol: str
    name: Optional[str] = None
    price: float
    change: float
    percent_change: float

class OHLCVData(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

# ============================================================================
# SCREENER MODELS
# ============================================================================

class ScreenerStock(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    percent_change: float
    prediction: str
    confidence: float

# ============================================================================
# SEARCH MODELS
# ============================================================================

class SearchResult(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    type: Optional[str] = Field(None, description="Security type (EQUITY, ETF, INDEX)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "TCS.NS",
                "name": "Tata Consultancy Services",
                "exchange": "NSI",
                "type": "EQUITY"
            }
        }

# ============================================================================
# PRICE MODELS
# ============================================================================

class PriceResponse(BaseModel):
    symbol: str
    lastPrice: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change from previous close")
    changePercent: float = Field(..., description="Percentage change")
    timestamp: str = Field(..., description="Timestamp of price data")
    source: str = Field(..., description="Data source (yfinance or fallback)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "TCS.NS",
                "lastPrice": 4000.50,
                "change": 25.30,
                "changePercent": 0.64,
                "timestamp": "2024-01-01T12:00:00",
                "source": "yfinance"
            }
        }

