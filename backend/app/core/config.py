"""
Application Configuration
Environment-based settings using Pydantic
"""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Stock Predictor AI Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Allow Flutter web, Android, iOS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://localhost",
        "*"  # For development - restrict in production
    ]
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    MODELS_DIR: Path = BASE_DIR / "app" / "ml" / "models"
    
    # API Keys (load from .env in production)
    ALPHA_VANTAGE_API_KEY: str = ""
    
    # ML Model Config
    MODEL_UPDATE_INTERVAL: int = 3600  # seconds
    PREDICTION_CACHE_TTL: int = 300  # seconds
    
    # WebSocket Config
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # Database (Optional)
    DATABASE_URL: str = "sqlite:///./stock_predictor.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
