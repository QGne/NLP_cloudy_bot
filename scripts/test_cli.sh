#!/bin/bash

echo "🧪 Testing CLI Interface..."

# Check if CLI dependencies are installed
cd cli
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run test
echo "🔧 Running CLI test..."
python3 chatbot_cli.py --test-mode

if [ $? -eq 0 ]; then
    echo "✅ CLI test passed!"
else
    echo "❌ CLI test failed!"
    exit 1
fi