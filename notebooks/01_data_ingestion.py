"""
Example notebook for data ingestion and exploration.

This notebook demonstrates:
1. Fetching data for Indian indices
2. Basic data exploration
3. Visualization of price trends
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

# Initialize data ingestor
print("Initializing Data Ingestor...")
ingestor = DataIngestor(
    raw_data_dir="../data/raw",
    start_date="2020-01-01"
)

# Fetch all indices
print("\nFetching data for all indices...")
data = ingestor.fetch_all_indices()

# Display summaries
for index_name in data.keys():
    print(f"\n{'='*60}")
    print(f"Summary for {index_name}")
    print('='*60)
    summary = ingestor.get_data_summary(index_name)
    for key, value in summary.items():
        print(f"{key:20s}: {value}")

# Plot closing prices
print("\nPlotting closing prices...")
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

for idx, (index_name, df) in enumerate(data.items()):
    axes[idx].plot(df.index, df['Close'], label=index_name, linewidth=2)
    axes[idx].set_title(f'{index_name} Closing Price', fontsize=14, fontweight='bold')
    axes[idx].set_xlabel('Date')
    axes[idx].set_ylabel('Price (INR)')
    axes[idx].legend()
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../notebooks/price_trends.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nData ingestion complete!")
