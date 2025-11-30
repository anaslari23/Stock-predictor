"""
Data ingestion module for fetching Indian stock indices data.

Uses yfinance to download historical data for NIFTY 50, BANKNIFTY, and NIFTY IT.
Supports CLI interface, parquet storage, and robust error handling.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import time
import pandas as pd
import pytz
import yfinance as yf


# Conditional import for utils (allows standalone usage)
try:
    from src.utils import setup_logger, ensure_dir
except ImportError:
    import logging
    
    def setup_logger(name: str, log_dir: str = "logs", level: int = logging.INFO):
        """Fallback logger setup."""
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def ensure_dir(directory: str) -> Path:
        """Fallback directory creation."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path


class DataIngestor:
    """
    Handles data ingestion from yfinance for Indian stock indices.
    
    Supports downloading, caching, and updating historical data for:
    - NIFTY 50 (^NSEI)
    - BANKNIFTY (^NSEBANK)
    - NIFTY IT (^CNXIT)
    
    Features:
    - Automatic timezone handling (IST)
    - Parquet file format for efficient storage
    - Incremental updates
    - Retry logic for network failures
    - Comprehensive error handling
    """
    
    # Indian index ticker mappings
    INDICES = {
        "NIFTY50": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "NIFTYIT": "^CNXIT"
    }
    
    # IST timezone
    IST = pytz.timezone('Asia/Kolkata')
    
    def __init__(
        self,
        raw_data_dir: str = "data/raw",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
        file_format: str = "parquet"
    ):
        """
        Initialize DataIngestor.
        
        Args:
            raw_data_dir: Directory to store raw data
            start_date: Start date for data download (YYYY-MM-DD)
            end_date: End date for data download (YYYY-MM-DD)
            interval: Data interval (1d, 1h, etc.)
            file_format: Storage format ('parquet' or 'csv')
        """
        self.raw_data_dir = ensure_dir(raw_data_dir)
        self.start_date = start_date or "2020-01-01"
        self.end_date = end_date or self._get_ist_date()
        self.interval = interval
        self.file_format = file_format
        self.logger = setup_logger("DataIngestor")
        
    def _get_ist_date(self) -> str:
        """Get current date in IST timezone."""
        return datetime.now(self.IST).strftime("%Y-%m-%d")
    
    def _get_cache_file(self, index_name: str) -> Path:
        """Get cache file path for an index."""
        extension = "parquet" if self.file_format == "parquet" else "csv"
        return self.raw_data_dir / f"{index_name}_{self.interval}.{extension}"
    
    def _load_cached_data(self, cache_file: Path) -> Optional[pd.DataFrame]:
        """
        Load data from cache file.
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            DataFrame or None if file doesn't exist or error occurs
        """
        if not cache_file.exists():
            return None
        
        try:
            if cache_file.suffix == ".parquet":
                df = pd.read_parquet(cache_file)
            else:
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            
            # Ensure timezone-aware index
            if df.index.tz is None:
                df.index = df.index.tz_localize('UTC').tz_convert(self.IST)
            
            self.logger.info(f"Loaded {len(df)} records from cache: {cache_file.name}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading cached data from {cache_file}: {e}")
            return None
    
    def _save_data(self, df: pd.DataFrame, cache_file: Path) -> bool:
        """
        Save DataFrame to cache file.
        
        Args:
            df: DataFrame to save
            cache_file: Path to cache file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if cache_file.suffix == ".parquet":
                df.to_parquet(cache_file, compression='snappy')
            else:
                df.to_csv(cache_file)
            
            self.logger.info(f"Saved {len(df)} records to {cache_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving data to {cache_file}: {e}")
            return False
    
    def fetch_index_data(
        self,
        ticker: str,
        start: str,
        end: str,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> pd.DataFrame:
        """
        Fetch historical data for a specific ticker with retry logic.
        
        Args:
            ticker: Yahoo Finance ticker symbol (e.g., '^NSEI')
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            ValueError: If ticker is invalid
            RuntimeError: If all retry attempts fail
        """
        for attempt in range(max_retries):
            try:
                self.logger.info(
                    f"Fetching {ticker} from {start} to {end} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                
                # Download data
                data = yf.download(
                    ticker,
                    start=start,
                    end=end,
                    interval=self.interval,
                    progress=False,
                    auto_adjust=True  # Adjust for splits and dividends
                )
                
                if data.empty:
                    self.logger.warning(f"No data returned for {ticker}")
                    return pd.DataFrame()
                
                # Clean column names (handle multi-index from yfinance)
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = [col[0] for col in data.columns]
                
                # Ensure timezone-aware index
                if data.index.tz is None:
                    data.index = data.index.tz_localize('UTC').tz_convert(self.IST)
                elif data.index.tz != self.IST:
                    data.index = data.index.tz_convert(self.IST)
                
                # Sort by date
                data = data.sort_index()
                
                self.logger.info(
                    f"Successfully fetched {len(data)} records for {ticker}"
                )
                
                return data
                
            except Exception as e:
                self.logger.error(
                    f"Error fetching {ticker} (attempt {attempt + 1}/{max_retries}): {e}"
                )
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(
                        f"Failed to fetch data for {ticker} after {max_retries} attempts"
                    )
        
        return pd.DataFrame()
    
    def get_index_data(
        self,
        index_name: str,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Get historical data for a specific index with caching.
        
        Args:
            index_name: Name of the index (NIFTY50, BANKNIFTY, NIFTYIT)
            force_refresh: Force download even if cached data exists
            
        Returns:
            DataFrame with OHLCV data
            
        Raises:
            ValueError: If index_name is invalid
        """
        if index_name not in self.INDICES:
            raise ValueError(
                f"Invalid index name '{index_name}'. "
                f"Choose from: {list(self.INDICES.keys())}"
            )
        
        ticker = self.INDICES[index_name]
        cache_file = self._get_cache_file(index_name)
        
        # Try to load cached data
        if not force_refresh:
            cached_df = self._load_cached_data(cache_file)
            
            if cached_df is not None and not cached_df.empty:
                # Check if cache is up to date
                last_date = cached_df.index[-1]
                current_date = datetime.now(self.IST)
                
                # If last date is today or yesterday (accounting for market hours), use cache
                days_diff = (current_date.date() - last_date.date()).days
                
                if days_diff <= 1:
                    self.logger.info(f"Cache is up to date for {index_name}")
                    return cached_df
                
                # Otherwise, fetch incremental data
                self.logger.info(f"Updating {index_name} with new data...")
                new_start = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
                
                try:
                    new_data = self.fetch_index_data(ticker, new_start, self.end_date)
                    
                    if not new_data.empty:
                        # Combine old and new data
                        combined_df = pd.concat([cached_df, new_data])
                        combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
                        combined_df = combined_df.sort_index()
                        
                        # Save updated data
                        self._save_data(combined_df, cache_file)
                        return combined_df
                    else:
                        # No new data available, return cached data
                        return cached_df
                        
                except Exception as e:
                    self.logger.warning(
                        f"Failed to fetch incremental data: {e}. Using cached data."
                    )
                    return cached_df
        
        # Download fresh data
        self.logger.info(f"Downloading fresh data for {index_name}")
        df = self.fetch_index_data(ticker, self.start_date, self.end_date)
        
        if not df.empty:
            self._save_data(df, cache_file)
        
        return df
    
    def fetch_all_indices(
        self,
        force_refresh: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all supported indices.
        
        Args:
            force_refresh: Force download even if cached data exists
            
        Returns:
            Dictionary mapping index names to DataFrames
        """
        results = {}
        
        for index_name in self.INDICES.keys():
            try:
                self.logger.info(f"Processing {index_name}...")
                df = self.get_index_data(index_name, force_refresh)
                results[index_name] = df
            except Exception as e:
                self.logger.error(f"Failed to fetch {index_name}: {e}")
                results[index_name] = pd.DataFrame()
        
        successful = sum(1 for df in results.values() if not df.empty)
        self.logger.info(
            f"Completed fetching indices: {successful}/{len(self.INDICES)} successful"
        )
        
        return results
    
    def get_latest_price(self, index_name: str) -> Optional[float]:
        """
        Get the latest closing price for an index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Latest closing price or None
        """
        try:
            df = self.get_index_data(index_name)
            if df.empty:
                return None
            return float(df['Close'].iloc[-1])
        except Exception as e:
            self.logger.error(f"Error getting latest price for {index_name}: {e}")
            return None
    
    def get_data_summary(self, index_name: str) -> Dict:
        """
        Get summary statistics for an index.
        
        Args:
            index_name: Name of the index
            
        Returns:
            Dictionary with summary statistics
        """
        try:
            df = self.get_index_data(index_name)
            
            if df.empty:
                return {"error": "No data available"}
            
            return {
                "index": index_name,
                "ticker": self.INDICES[index_name],
                "records": len(df),
                "start_date": str(df.index[0].date()),
                "end_date": str(df.index[-1].date()),
                "latest_close": float(df['Close'].iloc[-1]),
                "mean_close": float(df['Close'].mean()),
                "std_close": float(df['Close'].std()),
                "min_close": float(df['Close'].min()),
                "max_close": float(df['Close'].max()),
                "mean_volume": float(df['Volume'].mean()) if 'Volume' in df.columns else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting summary for {index_name}: {e}")
            return {"error": str(e)}


def main():
    """CLI interface for data ingestion."""
    parser = argparse.ArgumentParser(
        description="Fetch Indian stock indices data from Yahoo Finance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all indices with default settings
  python -m src.data_ingest --all
  
  # Fetch specific index
  python -m src.data_ingest --index NIFTY50
  
  # Fetch with custom date range
  python -m src.data_ingest --all --start 2023-01-01 --end 2024-01-01
  
  # Force refresh (ignore cache)
  python -m src.data_ingest --all --force
  
  # Save as CSV instead of parquet
  python -m src.data_ingest --all --format csv
  
  # Show summary statistics
  python -m src.data_ingest --index BANKNIFTY --summary
        """
    )
    
    parser.add_argument(
        '--index',
        type=str,
        choices=list(DataIngestor.INDICES.keys()),
        help='Specific index to fetch'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Fetch all supported indices'
    )
    
    parser.add_argument(
        '--start',
        type=str,
        default='2020-01-01',
        help='Start date (YYYY-MM-DD), default: 2020-01-01'
    )
    
    parser.add_argument(
        '--end',
        type=str,
        help='End date (YYYY-MM-DD), default: today'
    )
    
    parser.add_argument(
        '--interval',
        type=str,
        default='1d',
        choices=['1d', '1h', '1wk', '1mo'],
        help='Data interval, default: 1d'
    )
    
    parser.add_argument(
        '--format',
        type=str,
        default='parquet',
        choices=['parquet', 'csv'],
        help='Output file format, default: parquet'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory, default: data/raw'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh (ignore cached data)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary statistics'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.index:
        parser.error("Either --all or --index must be specified")
    
    # Initialize ingestor
    ingestor = DataIngestor(
        raw_data_dir=args.output_dir,
        start_date=args.start,
        end_date=args.end,
        interval=args.interval,
        file_format=args.format
    )
    
    print("=" * 70)
    print("INDIAN STOCK INDICES DATA INGESTION")
    print("=" * 70)
    print(f"Start Date    : {args.start}")
    print(f"End Date      : {args.end or 'today'}")
    print(f"Interval      : {args.interval}")
    print(f"Format        : {args.format}")
    print(f"Output Dir    : {args.output_dir}")
    print(f"Force Refresh : {args.force}")
    print("=" * 70)
    
    try:
        if args.all:
            # Fetch all indices
            print("\nFetching all indices...\n")
            results = ingestor.fetch_all_indices(force_refresh=args.force)
            
            # Display results
            print("\n" + "=" * 70)
            print("RESULTS")
            print("=" * 70)
            
            for index_name, df in results.items():
                if not df.empty:
                    print(f"✓ {index_name:12s}: {len(df):6d} records "
                          f"({df.index[0].date()} to {df.index[-1].date()})")
                else:
                    print(f"✗ {index_name:12s}: Failed to fetch data")
            
            if args.summary:
                print("\n" + "=" * 70)
                print("SUMMARY STATISTICS")
                print("=" * 70)
                
                for index_name in results.keys():
                    if not results[index_name].empty:
                        summary = ingestor.get_data_summary(index_name)
                        print(f"\n{index_name}:")
                        print(f"  Latest Close : ₹{summary['latest_close']:,.2f}")
                        print(f"  Mean Close   : ₹{summary['mean_close']:,.2f}")
                        print(f"  Std Dev      : ₹{summary['std_close']:,.2f}")
                        print(f"  Min Close    : ₹{summary['min_close']:,.2f}")
                        print(f"  Max Close    : ₹{summary['max_close']:,.2f}")
        
        else:
            # Fetch specific index
            print(f"\nFetching {args.index}...\n")
            df = ingestor.get_index_data(args.index, force_refresh=args.force)
            
            if not df.empty:
                print("\n" + "=" * 70)
                print("RESULTS")
                print("=" * 70)
                print(f"✓ Successfully fetched {len(df)} records")
                print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
                print(f"  Columns: {', '.join(df.columns)}")
                
                if args.summary:
                    summary = ingestor.get_data_summary(args.index)
                    print("\n" + "=" * 70)
                    print("SUMMARY STATISTICS")
                    print("=" * 70)
                    print(f"Latest Close : ₹{summary['latest_close']:,.2f}")
                    print(f"Mean Close   : ₹{summary['mean_close']:,.2f}")
                    print(f"Std Dev      : ₹{summary['std_close']:,.2f}")
                    print(f"Min Close    : ₹{summary['min_close']:,.2f}")
                    print(f"Max Close    : ₹{summary['max_close']:,.2f}")
            else:
                print("\n✗ Failed to fetch data")
                return 1
        
        print("\n" + "=" * 70)
        print("✓ DATA INGESTION COMPLETE")
        print("=" * 70)
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
