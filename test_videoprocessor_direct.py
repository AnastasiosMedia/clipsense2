#!/usr/bin/env python3
"""
Test VideoProcessor directly to debug the shutil issue
"""

import sys
import os
sys.path.append('/Users/anastasiosk/Documents/devprojects/OS/clipsense2/worker')

async def test_videoprocessor():
    print("🔍 Testing VideoProcessor directly...")
    
    try:
        from video_processor import VideoProcessor
        
        # Create instance
        vp = VideoProcessor()
        print(f"✅ VideoProcessor created: {type(vp)}")
        
        # Test the method that's failing
        print("🧪 Testing assemble_with_ai_selection...")
        
        result = await vp.assemble_with_ai_selection(
            clips=["/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00001wedding.mov"],
            music_path="/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/music/weddingmusic.mp3",
            target_duration=30,
            story_style="traditional",
            style_preset="romantic",
            use_ai_selection=True
        )
        
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_videoprocessor())
