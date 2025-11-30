# Stock Predictor Platform

A professional stock prediction platform for Indian stock market indices (NIFTY 50, BANKNIFTY, NIFTY IT).

## Features

- **Data Ingestion**: Automated fetching of historical data from Yahoo Finance
- **Feature Engineering**: Comprehensive technical indicators and transformations
- **Model Training**: Support for multiple ML/DL frameworks (TensorFlow, XGBoost, LightGBM, CatBoost)
- **Backtesting**: Strategy validation framework
- **Deployment**: FastAPI-based REST API for predictions

## Supported Indices

- **NIFTY 50** (^NSEI) - India's benchmark stock market index
- **BANKNIFTY** (^NSEBANK) - Banking sector index
- **NIFTY IT** (^CNXIT) - Information Technology sector index

## Project Structure

```
StockPredictor/
├── data/
│   ├── raw/              # Raw data from yfinance
│   └── processed/        # Processed features
├── notebooks/            # Jupyter notebooks for exploration
├── src/
│   ├── __init__.py
│   ├── data_ingest.py   # Data fetching and caching
│   ├── features.py      # Feature engineering
│   └── utils.py         # Utility functions
├── models/              # Trained model artifacts
├── backtests/           # Backtesting results
├── deployment/          # Deployment scripts
├── logs/                # Application logs
├── config.json          # Configuration file
├── environment.yml      # Conda environment
└── requirements.txt     # Pip requirements
```

## Installation

### Using Conda (Recommended)

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate stock_predictor
```

### Using Pip

```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Fetch Data

```python
from src.data_ingest import DataIngestor

# Initialize ingestor
ingestor = DataIngestor(
    raw_data_dir="data/raw",
    start_date="2020-01-01"
)

# Fetch all indices
data = ingestor.fetch_all_indices()

# Get summary
summary = ingestor.get_data_summary("NIFTY50")
print(summary)
```

### 2. Create Features

```python
from src.features import FeatureEngine

# Initialize feature engine
fe = FeatureEngine()

# Create all features
df_features = fe.create_all_features(data['NIFTY50'])

# Save processed data
df_features.to_csv('data/processed/NIFTY50_features.csv')
```

### 3. Explore in Jupyter

```bash
jupyter lab
```

Create a new notebook in the `notebooks/` directory to explore the data and build models.

## Configuration

Edit `config.json` to customize:

- **Indices**: Add or remove indices
- **Data parameters**: Date ranges, intervals
- **Features**: Technical indicators, lag periods
- **Model settings**: Train/test split, random seed

## Technical Indicators

The platform includes:

- **Trend**: SMA, EMA, MACD
- **Momentum**: RSI, MACD Histogram
- **Volatility**: Bollinger Bands, ATR
- **Volume**: Volume MA, Price-Volume Trend
- **Price Transformations**: Returns, Log Returns, Price Changes
- **Lag Features**: Historical values
- **Rolling Statistics**: Mean, Std, Min, Max

## Data Source

Data is fetched from Yahoo Finance using the `yfinance` library:
- **NIFTY 50**: ^NSEI
- **BANKNIFTY**: ^NSEBANK
- **NIFTY IT**: ^CNXIT

Data is cached locally and incrementally updated to minimize API calls.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black src/

# Lint
flake8 src/
```

## Timezone

All timestamps are handled in IST (Asia/Kolkata) timezone to match Indian market hours.

## License

MIT License

## Disclaimer

This platform is for educational and research purposes only. Stock market predictions are inherently uncertain. Always consult with financial advisors before making investment decisions.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For questions or issues, please open a GitHub issue.
