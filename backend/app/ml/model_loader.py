"""
Model Loader - Load trained ML models
"""

from pathlib import Path
from typing import Optional
from loguru import logger
import pickle

class ModelLoader:
    def __init__(self):
        self.models_dir = Path("app/ml/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.xgboost_model = None
        self.lstm_model = None
        self.ensemble_weights = None
        
        logger.info(f"ModelLoader initialized with models dir: {self.models_dir}")
    
    def load_xgboost(self, model_path: Optional[str] = None) -> bool:
        """Load XGBoost model"""
        if model_path is None:
            model_path = self.models_dir / "xgboost_model.pkl"
        else:
            model_path = Path(model_path)
        
        try:
            if not model_path.exists():
                logger.warning(f"XGBoost model not found at {model_path}")
                return False
            
            with open(model_path, 'rb') as f:
                self.xgboost_model = pickle.load(f)
            
            logger.info(f"Loaded XGBoost model from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading XGBoost model: {str(e)}")
            return False
    
    def load_lstm(self, model_path: Optional[str] = None) -> bool:
        """Load LSTM PyTorch model"""
        if model_path is None:
            model_path = self.models_dir / "lstm_model.pth"
        else:
            model_path = Path(model_path)
        
        try:
            if not model_path.exists():
                logger.warning(f"LSTM model not found at {model_path}")
                return False
            
            # PyTorch loading would go here
            # import torch
            # self.lstm_model = torch.load(model_path)
            # self.lstm_model.eval()
            
            logger.info(f"LSTM model path exists: {model_path}")
            logger.warning("PyTorch not installed - LSTM model loading skipped")
            return False
            
        except Exception as e:
            logger.error(f"Error loading LSTM model: {str(e)}")
            return False
    
    def load_ensemble_weights(self, weights_path: Optional[str] = None) -> bool:
        """Load ensemble weights"""
        if weights_path is None:
            weights_path = self.models_dir / "ensemble_weights.pkl"
        else:
            weights_path = Path(weights_path)
        
        try:
            if not weights_path.exists():
                logger.warning(f"Ensemble weights not found at {weights_path}")
                # Use default weights
                self.ensemble_weights = {'xgboost': 0.6, 'lstm': 0.4}
                logger.info("Using default ensemble weights")
                return True
            
            with open(weights_path, 'rb') as f:
                self.ensemble_weights = pickle.load(f)
            
            logger.info(f"Loaded ensemble weights from {weights_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading ensemble weights: {str(e)}")
            self.ensemble_weights = {'xgboost': 0.6, 'lstm': 0.4}
            return True
    
    def load_all(self) -> Dict[str, bool]:
        """Load all models"""
        results = {
            'xgboost': self.load_xgboost(),
            'lstm': self.load_lstm(),
            'ensemble': self.load_ensemble_weights()
        }
        
        logger.info(f"Model loading results: {results}")
        return results
    
    def is_ready(self) -> bool:
        """Check if at least one model is loaded"""
        return self.xgboost_model is not None or self.lstm_model is not None
