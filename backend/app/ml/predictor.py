"""
Predictor - ML prediction pipeline
"""

import numpy as np
from typing import Dict, List
from datetime import datetime
from loguru import logger

from app.ml.feature_engineering import FeatureEngineer
from app.ml.model_loader import ModelLoader

class Predictor:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.model_loader = ModelLoader()
        
        # Load models on initialization
        self.model_loader.load_all()
        
        logger.info("Predictor initialized")
    
    async def predict(self, df, symbol: str) -> Dict:
        """
        Make prediction from OHLCV data
        """
        try:
            # Generate features
            df_features = self.feature_engineer.generate_features(df)
            
            if df_features.empty:
                raise ValueError("No valid features generated")
            
            # Get normalized feature vector for latest data
            feature_vector = self.feature_engineer.get_last_feature_row(df_features, normalize=True)
            
            logger.info(f"Feature vector shape: {feature_vector.shape}, Features: {len(self.feature_engineer.feature_names)}")
            
            # Make predictions
            predictions = {}
            
            # XGBoost prediction
            if self.model_loader.xgboost_model is not None:
                xgb_prob = self._predict_xgboost(feature_vector)
                predictions['xgboost'] = xgb_prob
                logger.info(f"XGBoost prediction: {xgb_prob:.4f}")
            
            # LSTM prediction (if available)
            if self.model_loader.lstm_model is not None:
                lstm_prob = self._predict_lstm(df_features)
                predictions['lstm'] = lstm_prob
                logger.info(f"LSTM prediction: {lstm_prob:.4f}")
            
            # Ensemble prediction
            if not predictions:
                # No models loaded - use mock prediction
                logger.warning("No models loaded, using mock prediction")
                probability = self._mock_prediction(symbol)
            else:
                probability = self._ensemble_predict(predictions)
            
            # Determine direction
            direction = "UP" if probability >= 0.5 else "DOWN"
            confidence = probability if probability >= 0.5 else (1 - probability)
            
            return {
                'symbol': symbol,
                'prediction': direction,
                'probability': round(probability, 4),
                'confidence': round(confidence, 4),
                'features_used': self.feature_engineer.feature_names,
                'timestamp': datetime.now().isoformat(),
                'models_used': list(predictions.keys()) if predictions else ['mock']
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def _predict_xgboost(self, features: np.ndarray) -> float:
        """XGBoost prediction"""
        try:
            # Reshape for single prediction
            features_2d = features.reshape(1, -1)
            
            # Get probability for class 1 (UP)
            prob = self.model_loader.xgboost_model.predict_proba(features_2d)[0][1]
            return float(prob)
            
        except Exception as e:
            logger.error(f"XGBoost prediction error: {str(e)}")
            return 0.5
    
    def _predict_lstm(self, df_features) -> float:
        """LSTM prediction"""
        try:
            # LSTM would use sequence of features
            # This is a placeholder
            logger.warning("LSTM prediction not implemented")
            return 0.5
            
        except Exception as e:
            logger.error(f"LSTM prediction error: {str(e)}")
            return 0.5
    
    def _ensemble_predict(self, predictions: Dict[str, float]) -> float:
        """Ensemble prediction using weighted average"""
        weights = self.model_loader.ensemble_weights
        
        total_weight = 0
        weighted_sum = 0
        
        for model_name, prob in predictions.items():
            weight = weights.get(model_name, 0.5)
            weighted_sum += prob * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        ensemble_prob = weighted_sum / total_weight
        logger.info(f"Ensemble prediction: {ensemble_prob:.4f}")
        
        return ensemble_prob
    
    def _mock_prediction(self, symbol: str) -> float:
        """Mock prediction when no models are loaded"""
        import random
        random.seed(hash(symbol) % 10000)
        return 0.5 + random.uniform(-0.3, 0.3)
