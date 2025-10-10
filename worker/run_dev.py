#!/usr/bin/env python3
"""
Development runner for ClipSense worker
Starts the FastAPI server with auto-reload
"""

import subprocess
import sys
import os

def main():
    """Run the FastAPI development server"""
    print("🚀 Starting ClipSense worker...")
    print("📍 Server will be available at: http://127.0.0.1:8123")
    print("🔄 Auto-reload enabled for development")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        # Run uvicorn with auto-reload
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1",
            "--port", "8123", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Worker stopped")
    except Exception as e:
        print(f"❌ Error starting worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
