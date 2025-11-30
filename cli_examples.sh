#!/bin/bash
# Demo script showing CLI usage examples for data_ingest.py
# This script demonstrates the various CLI commands available

echo "=========================================================================="
echo "DATA INGESTION CLI - USAGE EXAMPLES"
echo "=========================================================================="
echo ""
echo "Note: These commands require the environment to be set up first."
echo "Run: conda env create -f environment.yml && conda activate stock_predictor"
echo ""
echo "=========================================================================="
echo "BASIC COMMANDS"
echo "=========================================================================="
echo ""

echo "1. Fetch all indices (default settings):"
echo "   $ python -m src.data_ingest --all"
echo ""

echo "2. Fetch specific index:"
echo "   $ python -m src.data_ingest --index NIFTY50"
echo ""

echo "3. Fetch with summary statistics:"
echo "   $ python -m src.data_ingest --index BANKNIFTY --summary"
echo ""

echo "=========================================================================="
echo "ADVANCED OPTIONS"
echo "=========================================================================="
echo ""

echo "4. Custom date range:"
echo "   $ python -m src.data_ingest --all --start 2023-01-01 --end 2024-01-01"
echo ""

echo "5. Force refresh (ignore cache):"
echo "   $ python -m src.data_ingest --all --force"
echo ""

echo "6. Different intervals:"
echo "   $ python -m src.data_ingest --index NIFTYIT --interval 1h"
echo "   $ python -m src.data_ingest --all --interval 1wk"
echo ""

echo "7. CSV format instead of parquet:"
echo "   $ python -m src.data_ingest --all --format csv"
echo ""

echo "8. Custom output directory:"
echo "   $ python -m src.data_ingest --all --output-dir /path/to/data"
echo ""

echo "=========================================================================="
echo "PRODUCTION EXAMPLES"
echo "=========================================================================="
echo ""

echo "9. Full production fetch:"
echo "   $ python -m src.data_ingest --all --start 2020-01-01 --summary"
echo ""

echo "10. Quick daily update:"
echo "    $ python -m src.data_ingest --all"
echo ""

echo "11. Complete refresh with summary:"
echo "    $ python -m src.data_ingest --all --force --summary"
echo ""

echo "=========================================================================="
echo "HELP"
echo "=========================================================================="
echo ""

echo "12. View all options:"
echo "    $ python -m src.data_ingest --help"
echo ""

echo "=========================================================================="
echo "SUPPORTED INDICES"
echo "=========================================================================="
echo ""
echo "  NIFTY50    - ^NSEI    - NIFTY 50 benchmark index"
echo "  BANKNIFTY  - ^NSEBANK - Banking sector index"
echo "  NIFTYIT    - ^CNXIT   - Information Technology sector"
echo ""

echo "=========================================================================="
echo "FILE FORMATS"
echo "=========================================================================="
echo ""
echo "  parquet (default) - Faster, smaller, preserves types"
echo "  csv              - Human-readable, universal"
echo ""

echo "=========================================================================="
echo "For detailed documentation, see: CLI_USAGE.md"
echo "=========================================================================="
