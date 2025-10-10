#!/bin/bash

# ClipSense Setup Script
echo "🎬 Setting up ClipSense..."

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Please install FFmpeg first:"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    echo "   Windows: Download from https://ffmpeg.org/"
    exit 1
fi

echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"

# Setup Python backend
echo "🐍 Setting up Python backend..."
cd worker
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Python backend ready"

# Setup Node.js frontend
echo "⚛️  Setting up React frontend..."
cd ../app
if [ ! -d "node_modules" ]; then
    pnpm install
fi
echo "✅ React frontend ready"

echo ""
echo "🚀 Setup complete! To start development:"
echo ""
echo "1. Start the backend worker:"
echo "   cd worker && source venv/bin/activate && uvicorn main:app --port 8123 --reload"
echo ""
echo "2. Start the Tauri app (in a new terminal):"
echo "   cd app && pnpm tauri dev"
echo ""
echo "Happy video editing! 🎥"
