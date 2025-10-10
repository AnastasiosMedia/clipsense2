#!/bin/bash

# ClipSense Quick Start Script
echo "🎬 ClipSense Quick Start"
echo "======================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "app" ] || [ ! -d "worker" ]; then
    echo "❌ Please run this script from the ClipSense root directory"
    exit 1
fi

echo "🚀 Starting ClipSense development environment..."
echo ""

# Start backend in background
echo "🐍 Starting Python backend..."
cd worker
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Start backend in background
python run_dev.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting Tauri frontend..."
cd ../app

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    pnpm install
fi

echo ""
echo "🎉 Both services are starting up!"
echo "📍 Backend: http://127.0.0.1:8123"
echo "📍 Frontend: Tauri app will open shortly"
echo ""
echo "⏹️  Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Start Tauri dev
pnpm tauri dev

# Cleanup when Tauri exits
cleanup
