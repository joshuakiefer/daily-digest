#!/bin/bash

# Quick start script for Daily Digest API

echo "🚀 Starting Daily Digest API Setup..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists, create minimal one if needed
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating minimal .env..."
    # Create minimal .env - many keys are already in config.py
    cat > .env << 'EOF'
# Daily Digest API Configuration
# Note: Many API keys are already set in config.py
# Google OAuth tokens will auto-load from setup/google_credentials/tokens.json

# Add any custom overrides here
EOF
    echo "✅ Created minimal .env file"
    echo "📝 Note: API keys in config.py will be used by default"
fi

# Start the server
echo "✅ Starting FastAPI server..."
echo "📍 Server will be available at http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo ""
uvicorn main:app --reload
