#!/usr/bin/env python3
"""
Test script to verify ClipSense setup
Checks all dependencies and components
"""

import subprocess
import sys
import os
import requests
import json
from pathlib import Path

def check_command(command, name):
    """Check if a command is available"""
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ {name}: {version}")
            return True
        else:
            print(f"❌ {name}: Not found")
            return False
    except FileNotFoundError:
        print(f"❌ {name}: Not found")
        return False

def check_python_packages():
    """Check if required Python packages are installed"""
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "python-multipart", 
        "opencv-python", "scenedetect", "numpy"
    ]
    
    print("\n🐍 Checking Python packages...")
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Not installed")
            all_installed = False
    
    return all_installed

def check_node_packages():
    """Check if Node.js packages are installed"""
    print("\n⚛️  Checking Node.js packages...")
    
    app_dir = Path("app")
    if not app_dir.exists():
        print("❌ app/ directory not found")
        return False
    
    node_modules = app_dir / "node_modules"
    if not node_modules.exists():
        print("❌ node_modules not found. Run 'cd app && pnpm install'")
        return False
    
    print("✅ Node.js packages: Installed")
    return True

def test_backend_connection():
    """Test if the backend is running"""
    print("\n🔌 Testing backend connection...")
    
    try:
        # Test ping endpoint first
        ping_response = requests.get("http://127.0.0.1:8123/ping", timeout=5)
        if ping_response.status_code == 200:
            print("✅ Backend: Ping successful")
        else:
            print(f"⚠️  Backend: Ping failed (HTTP {ping_response.status_code})")
        
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8123/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend: Connected")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   FFmpeg: {'Available' if health_data.get('ffmpeg_available') else 'Not available'}")
            
            if health_data.get('ffmpeg_version'):
                print(f"   Version: {health_data.get('ffmpeg_version')}")
            
            if health_data.get('ffmpeg_path'):
                print(f"   Path: {health_data.get('ffmpeg_path')}")
            
            if not health_data.get('ffmpeg_available') and health_data.get('installation_instructions'):
                print(f"   Installation help available")
            
            return health_data.get('ffmpeg_available', False)
        else:
            print(f"❌ Backend: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend: Not running (start with 'cd worker && python run_dev.py')")
        return False
    except Exception as e:
        print(f"❌ Backend: Error - {e}")
        return False

def main():
    """Run all checks"""
    print("🧪 ClipSense Setup Test")
    print("=" * 50)
    
    # Check system dependencies
    print("\n🔧 Checking system dependencies...")
    ffmpeg_ok = check_command("ffmpeg", "FFmpeg")
    node_ok = check_command("node", "Node.js")
    pnpm_ok = check_command("pnpm", "pnpm")
    python_ok = check_command("python3", "Python 3")
    
    # Check Python packages
    python_packages_ok = check_python_packages()
    
    # Check Node.js packages
    node_packages_ok = check_node_packages()
    
    # Test backend connection
    backend_ok = test_backend_connection()
    
    # Summary
    print("\n📊 Summary")
    print("=" * 50)
    
    all_good = (
        ffmpeg_ok and node_ok and pnpm_ok and python_ok and 
        python_packages_ok and node_packages_ok
    )
    
    if all_good:
        print("✅ All dependencies are properly installed!")
        if backend_ok:
            print("✅ Backend is running and ready!")
            print("\n🚀 You can now run: cd app && pnpm tauri dev")
        else:
            print("⚠️  Backend is not running. Start it with:")
            print("   cd worker && python run_dev.py")
    else:
        print("❌ Some dependencies are missing. Please install them first.")
        print("\n📖 See README.md for installation instructions.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
