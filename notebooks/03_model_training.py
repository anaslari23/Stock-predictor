"""
Model Training Script
Trains XGBoost and LSTM models for stock price prediction.
Saves models to backend/app/ml/models/ for use by the API.
"""

import sys
import os
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime

# Add project root to path
sys.path.append('..')

from src.data_ingest import DataIngestor
from src.features import FeatureEngine

# Configuration
MODEL_DIR = "../backend/app/ml/models"
SEQ_LENGTH = 5  # Sequence length for LSTM (reduced for small dataset)
TEST_SIZE = 0.2
TARGET_COL = 'Close'

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def prepare_lstm_data(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length)])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=50, num_layers=2, output_size=1):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

def train_models():
    print("="*50)
    print("Starting Model Training Pipeline")
    print("="*50)

    # 1. Data Ingestion
    print("\n1. Fetching Data...")
    ingestor = DataIngestor(raw_data_dir="../data/raw")
    # Fetch NIFTY50 as primary dataset
    # get_index_data handles ticker mapping (NIFTY50 -> ^NSEI) and caching
    df = ingestor.get_index_data("NIFTY50")
    print(f"Loaded {len(df)} records for NIFTY50")

    # 2. Feature Engineering
    print("\n2. Engineering Features...")
    fe = FeatureEngine()
    df_features = fe.create_all_features(df)
    
    # Drop NaN values created by lag features
    df_features.dropna(inplace=True)
    print(f"Features shape after cleaning: {df_features.shape}")

    # Prepare Target (Next Day Close)
    # For this example, we'll predict the Close price itself based on past data
    # Ideally, we shift the target for next-day prediction
    # df_features['Target'] = df_features['Close'].shift(-1)
    # df_features.dropna(inplace=True)
    
    # Use all columns except Target as features
    feature_cols = [c for c in df_features.columns if c != 'Target']
    
    # 3. Data Scaling
    print("\n3. Scaling Data...")
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df_features[feature_cols])
    
    # Save Scaler
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    print(f"Saved scaler to {scaler_path}")

    # 4. Train/Test Split
    train_size = int(len(scaled_data) * (1 - TEST_SIZE))
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]
    
    # ---------------------------------------------------------
    # XGBoost Training
    # ---------------------------------------------------------
    print("\n4. Training XGBoost Model...")
    
    # Prepare X, y for XGBoost (using previous day to predict today)
    X_train_xgb = train_data[:-1]
    y_train_xgb = train_data[1:, 0] # Assuming Close is at index 0
    X_test_xgb = test_data[:-1]
    y_test_xgb = test_data[1:, 0]

    xgb_model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    
    xgb_model.fit(X_train_xgb, y_train_xgb)
    
    # Evaluate
    preds_xgb = xgb_model.predict(X_test_xgb)
    rmse_xgb = np.sqrt(mean_squared_error(y_test_xgb, preds_xgb))
    print(f"XGBoost RMSE: {rmse_xgb:.4f}")
    
    # Save XGBoost Model
    xgb_path = os.path.join(MODEL_DIR, "xgboost_model.pkl")
    joblib.dump(xgb_model, xgb_path)
    print(f"Saved XGBoost model to {xgb_path}")

    # ---------------------------------------------------------
    # LSTM Training
    # ---------------------------------------------------------
    print("\n5. Training LSTM Model...")
    
    # Prepare Sequences
    # We use the Close price column (index 0) for LSTM sequence prediction for simplicity
    # Or use all features. Let's use all features.
    
    X_train_lstm, y_train_lstm = prepare_lstm_data(train_data, SEQ_LENGTH)
    X_test_lstm, y_test_lstm = prepare_lstm_data(test_data, SEQ_LENGTH)
    
    # prepare_lstm_data returns y as full feature vectors (2D array)
    # Extract Close price (index 0) as target
    if y_train_lstm.ndim > 1:
        y_train_lstm = y_train_lstm[:, 0]
        y_test_lstm = y_test_lstm[:, 0]

    # Convert to PyTorch tensors
    X_train_tensor = torch.FloatTensor(X_train_lstm)
    y_train_tensor = torch.FloatTensor(y_train_lstm)
    X_test_tensor = torch.FloatTensor(X_test_lstm)
    y_test_tensor = torch.FloatTensor(y_test_lstm)

    # Initialize Model
    input_size = X_train_lstm.shape[2]
    lstm_model = LSTMModel(input_size=input_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.001)

    # Training Loop
    epochs = 50 # Reduced for speed
    batch_size = 32
    
    lstm_model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = lstm_model(X_train_tensor)
        loss = criterion(outputs.squeeze(), y_train_tensor)
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")

    # Evaluate
    lstm_model.eval()
    with torch.no_grad():
        preds_lstm = lstm_model(X_test_tensor).squeeze()
        rmse_lstm = np.sqrt(mean_squared_error(y_test_tensor.numpy(), preds_lstm.numpy()))
    print(f"LSTM RMSE: {rmse_lstm:.4f}")

    # Save LSTM Model
    lstm_path = os.path.join(MODEL_DIR, "lstm_model.pth")
    torch.save(lstm_model.state_dict(), lstm_path)
    print(f"Saved LSTM model to {lstm_path}")

    # ---------------------------------------------------------
    # Ensemble Weights
    # ---------------------------------------------------------
    print("\n6. Saving Ensemble Weights...")
    # Simple weighting based on inverse RMSE (better model gets higher weight)
    total_inv_rmse = (1/rmse_xgb) + (1/rmse_lstm)
    xgb_weight = (1/rmse_xgb) / total_inv_rmse
    lstm_weight = (1/rmse_lstm) / total_inv_rmse
    
    weights = {
        'xgboost': xgb_weight,
        'lstm': lstm_weight
    }
    
    weights_path = os.path.join(MODEL_DIR, "ensemble_weights.pkl")
    joblib.dump(weights, weights_path)
    print(f"Saved ensemble weights: {weights}")
    print(f"Saved to {weights_path}")

    print("\n" + "="*50)
    print("Training Complete!")
    print("="*50)

if __name__ == "__main__":
    train_models()
