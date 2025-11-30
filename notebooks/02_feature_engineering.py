"""
Example notebook for feature engineering.

This notebook demonstrates:
1. Loading raw data
2. Creating technical indicators
3. Feature analysis and visualization
"""

# Import libraries
import sys
sys.path.append('..')

from src.data_ingest import DataIngestor
from src.features import FeatureEngine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style('darkgrid')
plt.rcParams['figure.figsize'] = (14, 7)

# Load data
print("Loading NIFTY50 data...")
ingestor = DataIngestor(raw_data_dir="../data/raw")
df = ingestor.fetch_index_data("NIFTY50")

print(f"Loaded {len(df)} records")
print(f"Date range: {df.index[0]} to {df.index[-1]}")

# Create features
print("\nCreating features...")
fe = FeatureEngine()
df_features = fe.create_all_features(df)

print(f"\nFeature engineering complete!")
print(f"Original columns: {len(df.columns)}")
print(f"Feature columns: {len(df_features.columns)}")
print(f"Records after cleaning: {len(df_features)}")

# Display feature groups
print("\nFeature groups:")
groups = fe.get_feature_importance_groups()
for group_name, patterns in groups.items():
    matching_cols = [col for col in df_features.columns 
                    if any(pattern in col for pattern in patterns)]
    print(f"{group_name:15s}: {len(matching_cols)} features")

# Save processed data
output_path = "../data/processed/NIFTY50_features.csv"
df_features.to_csv(output_path)
print(f"\nSaved features to {output_path}")

# Visualize some key indicators
print("\nPlotting technical indicators...")
fig, axes = plt.subplots(4, 1, figsize=(14, 16))

# Price with moving averages
axes[0].plot(df_features.index, df_features['Close'], label='Close', linewidth=2)
axes[0].plot(df_features.index, df_features['SMA_20'], label='SMA 20', alpha=0.7)
axes[0].plot(df_features.index, df_features['SMA_50'], label='SMA 50', alpha=0.7)
axes[0].plot(df_features.index, df_features['SMA_200'], label='SMA 200', alpha=0.7)
axes[0].set_title('Price with Moving Averages', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# RSI
axes[1].plot(df_features.index, df_features['RSI_14'], label='RSI', color='purple', linewidth=2)
axes[1].axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
axes[1].axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
axes[1].set_title('Relative Strength Index (RSI)', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# MACD
axes[2].plot(df_features.index, df_features['MACD'], label='MACD', linewidth=2)
axes[2].plot(df_features.index, df_features['MACD_Signal'], label='Signal', linewidth=2)
axes[2].bar(df_features.index, df_features['MACD_Hist'], label='Histogram', alpha=0.3)
axes[2].set_title('MACD', fontsize=14, fontweight='bold')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Bollinger Bands
axes[3].plot(df_features.index, df_features['Close'], label='Close', linewidth=2)
axes[3].plot(df_features.index, df_features['BB_Upper'], label='Upper Band', alpha=0.7, linestyle='--')
axes[3].plot(df_features.index, df_features['BB_Middle'], label='Middle Band', alpha=0.7)
axes[3].plot(df_features.index, df_features['BB_Lower'], label='Lower Band', alpha=0.7, linestyle='--')
axes[3].fill_between(df_features.index, df_features['BB_Lower'], df_features['BB_Upper'], alpha=0.1)
axes[3].set_title('Bollinger Bands', fontsize=14, fontweight='bold')
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../notebooks/technical_indicators.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nFeature engineering complete!")
