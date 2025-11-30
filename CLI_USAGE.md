# Data Ingestion CLI - Usage Guide

## Overview

The enhanced `data_ingest.py` module provides a complete CLI interface for fetching Indian stock indices data with robust error handling, timezone management, and efficient parquet storage.

## Features

✓ **CLI Interface** - Full argparse-based command-line interface
✓ **Parquet Support** - Efficient columnar storage with snappy compression
✓ **Timezone Handling** - Automatic IST timezone conversion
✓ **Retry Logic** - 3 automatic retries with 5-second delays
✓ **Incremental Updates** - Only fetches new data since last update
✓ **Error Handling** - Comprehensive exception handling with fallbacks
✓ **Caching** - Smart caching to minimize API calls

## CLI Usage

### Basic Commands

#### Fetch All Indices
```bash
python -m src.data_ingest --all
```

#### Fetch Specific Index
```bash
python -m src.data_ingest --index NIFTY50
```

#### Fetch with Summary Statistics
```bash
python -m src.data_ingest --index BANKNIFTY --summary
```

### Advanced Options

#### Custom Date Range
```bash
python -m src.data_ingest --all --start 2023-01-01 --end 2024-01-01
```

#### Force Refresh (Ignore Cache)
```bash
python -m src.data_ingest --all --force
```

#### Different Intervals
```bash
# Hourly data
python -m src.data_ingest --index NIFTYIT --interval 1h

# Weekly data
python -m src.data_ingest --all --interval 1wk

# Monthly data
python -m src.data_ingest --all --interval 1mo
```

#### CSV Format Instead of Parquet
```bash
python -m src.data_ingest --all --format csv
```

#### Custom Output Directory
```bash
python -m src.data_ingest --all --output-dir /path/to/data
```

### Combined Examples

#### Production Data Fetch
```bash
# Fetch all indices from 2020, save as parquet, show summary
python -m src.data_ingest --all --start 2020-01-01 --summary
```

#### Quick Update
```bash
# Update NIFTY50 with latest data (uses cache)
python -m src.data_ingest --index NIFTY50
```

#### Full Refresh
```bash
# Force download all data, ignore cache
python -m src.data_ingest --all --force --summary
```

## Python API Usage

### Basic Usage

```python
from src.data_ingest import DataIngestor

# Initialize
ingestor = DataIngestor(
    raw_data_dir="data/raw",
    start_date="2020-01-01",
    file_format="parquet"
)

# Fetch specific index
df = ingestor.get_index_data("NIFTY50")
print(f"Fetched {len(df)} records")

# Fetch all indices
all_data = ingestor.fetch_all_indices()
```

### Advanced Usage

```python
from src.data_ingest import DataIngestor

# Initialize with custom settings
ingestor = DataIngestor(
    raw_data_dir="data/raw",
    start_date="2023-01-01",
    end_date="2024-01-01",
    interval="1d",
    file_format="parquet"
)

# Fetch with force refresh
df = ingestor.get_index_data("BANKNIFTY", force_refresh=True)

# Get latest price
price = ingestor.get_latest_price("NIFTYIT")
print(f"Latest NIFTY IT price: ₹{price:,.2f}")

# Get summary statistics
summary = ingestor.get_data_summary("NIFTY50")
print(f"Records: {summary['records']}")
print(f"Date range: {summary['start_date']} to {summary['end_date']}")
print(f"Latest close: ₹{summary['latest_close']:,.2f}")
```

### Direct Ticker Fetch

```python
from src.data_ingest import DataIngestor

ingestor = DataIngestor()

# Fetch any ticker directly
df = ingestor.fetch_index_data(
    ticker="^NSEI",
    start="2024-01-01",
    end="2024-12-31"
)
```

## Supported Indices

| Index Name | Ticker Symbol | Description |
|------------|---------------|-------------|
| NIFTY50 | ^NSEI | NIFTY 50 - India's benchmark index |
| BANKNIFTY | ^NSEBANK | Bank NIFTY - Banking sector index |
| NIFTYIT | ^CNXIT | NIFTY IT - Information Technology sector |

## File Formats

### Parquet (Default)
- **Pros**: Faster read/write, smaller file size, preserves data types
- **Compression**: Snappy compression
- **Use case**: Production, large datasets

### CSV
- **Pros**: Human-readable, universal compatibility
- **Use case**: Data inspection, sharing with non-Python tools

## Error Handling

The module includes comprehensive error handling:

1. **Network Failures**: Automatic retry with exponential backoff
2. **Invalid Tickers**: Clear error messages
3. **Empty Data**: Graceful handling with warnings
4. **Cache Corruption**: Falls back to fresh download
5. **Timezone Issues**: Automatic conversion to IST

## Timezone Management

All timestamps are automatically converted to IST (Asia/Kolkata):
- Downloaded data is converted from UTC to IST
- Cached data maintains timezone information
- Date comparisons account for market hours

## Caching Strategy

### Smart Caching
- Data is cached after first download
- Subsequent calls check if cache is up-to-date
- Only fetches new data since last update

### Cache Invalidation
- Automatic: If data is older than 1 day
- Manual: Use `--force` flag

### Cache Files
- Location: `data/raw/`
- Naming: `{INDEX}_{INTERVAL}.{FORMAT}`
- Example: `NIFTY50_1d.parquet`

## Performance Tips

1. **Use Parquet**: 3-5x faster than CSV for large datasets
2. **Leverage Cache**: Don't use `--force` unless necessary
3. **Batch Fetching**: Use `--all` instead of multiple single fetches
4. **Appropriate Intervals**: Use daily data unless you need intraday

## Troubleshooting

### Issue: "No module named 'pyarrow'"
**Solution**: Install parquet support
```bash
pip install pyarrow
# or
conda install pyarrow
```

### Issue: Network timeout
**Solution**: The module automatically retries 3 times. If it still fails, check your internet connection.

### Issue: Empty data returned
**Solution**: 
- Check if the date range is valid
- Verify ticker symbol is correct
- Try with `--force` to bypass cache

### Issue: Timezone warnings
**Solution**: The module handles this automatically. Warnings can be ignored.

## Output Examples

### Successful Fetch
```
======================================================================
INDIAN STOCK INDICES DATA INGESTION
======================================================================
Start Date    : 2020-01-01
End Date      : today
Interval      : 1d
Format        : parquet
Output Dir    : data/raw
Force Refresh : False
======================================================================

Fetching all indices...

======================================================================
RESULTS
======================================================================
✓ NIFTY50    :   1234 records (2020-01-01 to 2024-11-30)
✓ BANKNIFTY  :   1234 records (2020-01-01 to 2024-11-30)
✓ NIFTYIT    :   1234 records (2020-01-01 to 2024-11-30)

======================================================================
✓ DATA INGESTION COMPLETE
======================================================================
```

### With Summary Statistics
```
======================================================================
SUMMARY STATISTICS
======================================================================

NIFTY50:
  Latest Close : ₹21,731.40
  Mean Close   : ₹17,245.82
  Std Dev      : ₹2,891.34
  Min Close    : ₹12,456.70
  Max Close    : ₹22,124.15

BANKNIFTY:
  Latest Close : ₹46,523.85
  Mean Close   : ₹38,912.45
  Std Dev      : ₹6,234.91
  Min Close    : ₹28,345.20
  Max Close    : ₹48,765.30
```

## Integration with Other Modules

### With Feature Engineering
```python
from src.data_ingest import DataIngestor
from src.features import FeatureEngine

# Fetch data
ingestor = DataIngestor()
df = ingestor.get_index_data("NIFTY50")

# Create features
fe = FeatureEngine()
df_features = fe.create_all_features(df)

# Save processed data
df_features.to_parquet("data/processed/NIFTY50_features.parquet")
```

### Automated Pipeline
```python
from src.data_ingest import DataIngestor
from src.features import FeatureEngine

def update_all_data():
    """Update all indices and create features."""
    ingestor = DataIngestor(file_format="parquet")
    fe = FeatureEngine()
    
    for index_name in DataIngestor.INDICES.keys():
        # Fetch data (uses cache if up-to-date)
        df = ingestor.get_index_data(index_name)
        
        # Create features
        df_features = fe.create_all_features(df)
        
        # Save
        output_path = f"data/processed/{index_name}_features.parquet"
        df_features.to_parquet(output_path)
        print(f"✓ Updated {index_name}")

# Run daily
update_all_data()
```

## Best Practices

1. **Daily Updates**: Run without `--force` to get incremental updates
2. **Use Parquet**: Default format for better performance
3. **Check Logs**: Monitor `logs/DataIngestor_*.log` for issues
4. **Validate Data**: Use `--summary` to verify data quality
5. **Backup**: Keep backups before using `--force`

## API Reference

### DataIngestor Class

#### Methods

- `get_index_data(index_name, force_refresh=False)` - Get data for specific index
- `fetch_index_data(ticker, start, end)` - Fetch data for any ticker
- `fetch_all_indices(force_refresh=False)` - Fetch all supported indices
- `get_latest_price(index_name)` - Get latest closing price
- `get_data_summary(index_name)` - Get summary statistics

#### Attributes

- `INDICES` - Dictionary of supported indices
- `IST` - IST timezone object
- `raw_data_dir` - Data storage directory
- `file_format` - Storage format (parquet/csv)

## Changelog

### Version 2.0 (Current)
- ✓ Added CLI interface with argparse
- ✓ Implemented parquet support
- ✓ Added timezone handling (IST)
- ✓ Implemented retry logic
- ✓ Enhanced error handling
- ✓ Added incremental updates
- ✓ Improved caching strategy

### Version 1.0
- Basic data fetching
- CSV storage
- Simple caching
