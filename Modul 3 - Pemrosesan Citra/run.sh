#!/bin/bash

echo ""
echo "========================================"
echo "  Smart Document Scanner - Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 tidak terinstall!"
    echo "Install dengan: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Mengaktifkan virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Menginstall dependencies..."
pip install -r requirements.txt

# Run the application
echo ""
echo "Menjalankan Smart Document Scanner..."
echo ""
python3 scanner_gui.py
