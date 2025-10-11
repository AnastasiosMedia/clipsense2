#!/usr/bin/env python3
"""
Debug script for visual analysis API
"""

import asyncio
import sys
import os
from pathlib import Path

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from visual_analyzer import VisualAnalyzer

async def debug_visual_analysis():
    """Debug the visual analysis with detailed error handling"""
    
    print("🔍 Debugging Visual Analysis API")
    print("=" * 50)
    
    video_path = "tests/media/clip1.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    print(f"📹 Testing with: {video_path}")
    
    try:
        analyzer = VisualAnalyzer()
        print("✅ VisualAnalyzer created successfully")
        
        result = await analyzer.analyze_clip(video_path, sample_rate=1.0)
        print("✅ Analysis completed successfully")
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_visual_analysis())
