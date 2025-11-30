#!/usr/bin/env python3
"""
Quick test script to verify the stock predictor platform setup.

Tests:
1. Module imports
2. Data ingestion
3. Feature engineering
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)
    
    try:
        from src import DataIngestor, FeatureEngine, setup_logger, load_config
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_data_ingestion():
    """Test data ingestion from yfinance."""
    print("\n" + "=" * 60)
    print("Testing Data Ingestion")
    print("=" * 60)
    
    try:
        from src.data_ingest import DataIngestor
        
        # Initialize with small date range for quick test
        ingestor = DataIngestor(
            raw_data_dir="data/raw",
            start_date="2024-01-01"
        )
        
        # Fetch NIFTY50 data
        print("\nFetching NIFTY50 data...")
        df = ingestor.fetch_index_data("NIFTY50")
        
        if df.empty:
            print("✗ No data fetched")
            return False
        
        print(f"✓ Fetched {len(df)} records")
        print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"  Columns: {list(df.columns)}")
        
        # Get summary
        summary = ingestor.get_data_summary("NIFTY50")
        print(f"\n  Latest close: ₹{summary['latest_close']:,.2f}")
        print(f"  Mean close: ₹{summary['mean_close']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_engineering():
    """Test feature engineering."""
    print("\n" + "=" * 60)
    print("Testing Feature Engineering")
    print("=" * 60)
    
    try:
        from src.data_ingest import DataIngestor
        from src.features import FeatureEngine
        
        # Get data
        ingestor = DataIngestor(raw_data_dir="data/raw", start_date="2024-01-01")
        df = ingestor.fetch_index_data("NIFTY50")
        
        # Create features
        print("\nCreating features...")
        fe = FeatureEngine()
        df_features = fe.create_all_features(df)
        
        print(f"✓ Created {len(df_features.columns)} features")
        print(f"  Original records: {len(df)}")
        print(f"  After feature engineering: {len(df_features)}")
        
        # Show some feature groups
        groups = fe.get_feature_importance_groups()
        print("\n  Feature groups:")
        for group_name, patterns in groups.items():
            matching_cols = [col for col in df_features.columns 
                           if any(pattern in col for pattern in patterns)]
            print(f"    {group_name:12s}: {len(matching_cols)} features")
        
        return True
        
    except Exception as e:
        print(f"✗ Feature engineering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STOCK PREDICTOR PLATFORM - VERIFICATION TEST")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Data Ingestion", test_data_ingestion()))
    results.append(("Feature Engineering", test_feature_engineering()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:25s}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nThe platform is ready to use!")
        print("\nNext steps:")
        print("1. Create conda environment: conda env create -f environment.yml")
        print("2. Activate environment: conda activate stock_predictor")
        print("3. Explore notebooks: jupyter lab")
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        print("=" * 60)
        print("\nPlease check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
