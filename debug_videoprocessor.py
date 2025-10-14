#!/usr/bin/env python3
"""
Debug VideoProcessor issue
"""

import sys
import os
sys.path.append('/Users/anastasiosk/Documents/devprojects/OS/clipsense2/worker')

from video_processor import VideoProcessor

def test_videoprocessor():
    print("🔍 Debugging VideoProcessor...")
    
    # Create instance
    vp = VideoProcessor()
    
    # Check methods
    print(f"✅ VideoProcessor created: {type(vp)}")
    print(f"✅ Has _check_ffmpeg: {hasattr(vp, '_check_ffmpeg')}")
    
    if hasattr(vp, '_check_ffmpeg'):
        print(f"✅ Method type: {type(vp._check_ffmpeg)}")
        print(f"✅ Method callable: {callable(vp._check_ffmpeg)}")
        
        # Try to call it
        try:
            import asyncio
            result = asyncio.run(vp._check_ffmpeg())
            print(f"✅ Method call result: {result}")
        except Exception as e:
            print(f"❌ Method call error: {e}")
    else:
        print("❌ Method not found!")
        print("Available methods:")
        for method in dir(vp):
            if not method.startswith('__'):
                print(f"  - {method}")

if __name__ == "__main__":
    test_videoprocessor()
