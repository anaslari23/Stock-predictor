#!/bin/bash
# Setup script for stock predictor environment using pip

echo "=========================================================================="
echo "STOCK PREDICTOR - ENVIRONMENT SETUP"
echo "=========================================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================================================="
echo "✓ SETUP COMPLETE"
echo "=========================================================================="
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the data ingestion:"
echo "  python -m src.data_ingest --all --summary"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
echo ""
