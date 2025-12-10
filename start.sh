#!/bin/bash
# ProTrader Terminal Backend Startup Script

echo "=========================================="
echo "🚀 ProTrader Terminal Backend"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Starting ProTrader Terminal Backend..."
echo "📡 Server will be available at: http://0.0.0.0:8000"
echo "📊 API Documentation at: http://0.0.0.0:8000/docs"
echo ""

# Run the application
python app.py
