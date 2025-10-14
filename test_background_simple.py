#!/usr/bin/env python3
"""
Simple test for background processing functionality
"""

import asyncio
import sys
import os

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from background_processor import background_processor, ProcessingStatus

async def test_background_processor():
    """Test the background processor directly"""
    print("🚀 Testing Background Processor Directly")
    print("=" * 50)
    
    # Test data
    video_paths = [
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00001wedding.mov",
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00002wedding.mov",
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00003wedding.mov"
    ]
    music_path = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/music/weddingmusic.mp3"
    
    print(f"📹 Testing with {len(video_paths)} clips")
    
    # Create job
    job_id = background_processor.create_job(
        clips=video_paths,
        music_path=music_path,
        target_duration=20,
        story_style="traditional",
        style_preset="romantic"
    )
    
    print(f"✅ Job created: {job_id}")
    
    # Start processing
    print("🔄 Starting processing...")
    await background_processor.start_processing(job_id)
    
    # Check results
    job = background_processor.get_job_status(job_id)
    if job:
        print(f"📊 Final status: {job.status.value}")
        print(f"📈 Progress: {job.progress:.1%}")
        print(f"⏱️  Duration: {job.completed_at - job.started_at:.1f}s" if job.completed_at and job.started_at else "N/A")
        
        if job.results:
            print(f"🎯 Selected {len(job.results)} clips:")
            for i, result in enumerate(job.results[:3]):
                print(f"  {i+1}. {os.path.basename(result.clip_path)} (score: {result.final_score:.2f})")
        else:
            print("❌ No results available")
    else:
        print("❌ Job not found")

if __name__ == "__main__":
    asyncio.run(test_background_processor())
