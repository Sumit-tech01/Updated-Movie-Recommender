#!/bin/bash
# Movie Recommender System - Startup Script

echo "=========================================="
echo "   MOVIE RECOMMENDER SYSTEM"
echo "=========================================="
echo ""

# Check if virtual environment should be used
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask; import pandas; import numpy; import matplotlib; import seaborn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting Flask server..."
echo "----------------------------------------"
echo "The app will run at:"
echo "  http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"
echo ""

# Start the server
python3 app.py
