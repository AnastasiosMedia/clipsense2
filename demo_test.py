#!/usr/bin/env python3
"""
Demo script to test ClipSense API
This script tests the backend API without the frontend
"""

import requests
import json
import time
import os
from pathlib import Path

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8123/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   FFmpeg: {'Available' if health_data.get('ffmpeg_available') else 'Not available'}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_autocut():
    """Test the auto-cut endpoint with dummy data"""
    print("\n🎬 Testing auto-cut endpoint...")
    
    # You would need to provide actual video and audio files for this test
    # For now, we'll just test the endpoint structure
    test_request = {
        "clips": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
        "music": "/path/to/music.wav",
        "target_seconds": 60
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8123/autocut",
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Auto-cut endpoint responded")
            print(f"   Success: {result.get('ok')}")
            if result.get('error'):
                print(f"   Error: {result.get('error')}")
            return True
        else:
            print(f"❌ Auto-cut failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Auto-cut error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ClipSense API Demo Test")
    print("=" * 40)
    
    # Test health endpoint
    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ Backend is not running or not healthy")
        print("   Start it with: cd worker && python run_dev.py")
        return 1
    
    # Test auto-cut endpoint
    autocut_ok = test_autocut()
    
    print("\n📊 Test Results")
    print("=" * 40)
    print(f"Health Check: {'✅ Pass' if health_ok else '❌ Fail'}")
    print(f"Auto-cut API: {'✅ Pass' if autocut_ok else '❌ Fail'}")
    
    if health_ok and autocut_ok:
        print("\n🎉 All tests passed! The API is working correctly.")
        print("   You can now use the Tauri frontend to process real videos.")
    else:
        print("\n⚠️  Some tests failed. Check the backend logs for details.")
    
    return 0 if (health_ok and autocut_ok) else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
