#!/usr/bin/env python3
"""
Test script for background processing functionality

Demonstrates how to use the background processing API to handle large clip sets
with real-time progress updates.
"""

import asyncio
import httpx
import time
import json
from typing import List, Dict, Any

async def test_background_processing():
    """Test the background processing with 10 clips"""
    print("🚀 Testing Background Processing with 10 Clips")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8123"
    
    # Test data
    video_dir = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video"
    music_path = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/music/weddingmusic.mp3"
    
    # Get 10 wedding clips
    video_paths = []
    for i in range(1, 11):
        clip_path = f"{video_dir}/000{i:02d}wedding.mov"
        video_paths.append(clip_path)
    
    print(f"📹 Testing with {len(video_paths)} wedding clips")
    print(f"🎵 Music: {music_path}")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Start background job
        print("\n🔄 Step 1: Starting background job...")
        start_request = {
            "clips": video_paths,
            "music_path": music_path,
            "target_duration": 60,
            "story_style": "traditional",
            "style_preset": "romantic"
        }
        
        try:
            response = await client.post(f"{base_url}/background/start", json=start_request)
            response.raise_for_status()
            result = response.json()
            
            if not result.get("ok"):
                print(f"❌ Failed to start job: {result.get('error')}")
                return
            
            job_id = result["job_id"]
            print(f"✅ Job started: {job_id}")
            
        except httpx.RequestError as e:
            print(f"❌ Failed to start job: {e}")
            return
        
        # Step 2: Monitor progress
        print("\n📊 Step 2: Monitoring progress...")
        start_time = time.time()
        
        while True:
            try:
                response = await client.get(f"{base_url}/background/status/{job_id}")
                response.raise_for_status()
                status = response.json()
                
                if not status.get("ok"):
                    print(f"❌ Failed to get status: {status.get('error')}")
                    break
                
                # Display progress
                progress = status["progress"]
                current_step = status["current_step"]
                status_name = status["status"]
                elapsed = time.time() - start_time
                
                print(f"⏱️  [{elapsed:6.1f}s] {status_name.upper():8} | {progress:5.1%} | {current_step}")
                
                # Check if completed
                if status_name == "completed":
                    print(f"✅ Job completed in {elapsed:.1f} seconds!")
                    
                    # Show results
                    if status.get("results"):
                        print(f"\n🎯 Selected {len(status['results'])} best clips:")
                        for i, result in enumerate(status["results"][:5]):
                            print(f"  {i+1}. {result['clip_path'].split('/')[-1]} (score: {result['final_score']:.2f})")
                    
                    break
                elif status_name == "failed":
                    print(f"❌ Job failed: {status.get('error', 'Unknown error')}")
                    break
                elif status_name == "cancelled":
                    print("⚠️  Job was cancelled")
                    break
                
                # Wait before next check
                await asyncio.sleep(2)
                
            except httpx.RequestError as e:
                print(f"❌ Error checking status: {e}")
                break
        
        # Step 3: Get detailed results
        print("\n📋 Step 3: Getting detailed results...")
        try:
            response = await client.get(f"{base_url}/background/results/{job_id}")
            response.raise_for_status()
            results = response.json()
            
            if results.get("ok") and results.get("results"):
                print(f"✅ Retrieved {len(results['results'])} detailed results")
                
                # Show detailed analysis
                for i, result in enumerate(results["results"][:3]):
                    print(f"\n🎬 Clip {i+1}: {result['clip_path'].split('/')[-1]}")
                    print(f"   Score: {result['final_score']:.2f}")
                    print(f"   Reason: {result['selection_reason']}")
                    print(f"   Scene: {result['story_arc']['scene_classification']}")
                    print(f"   Tone: {result['story_arc']['emotional_tone']}")
                    print(f"   Importance: {result['story_arc']['story_importance']:.2f}")
            else:
                print("❌ No results available")
                
        except httpx.RequestError as e:
            print(f"❌ Error getting results: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Background processing test completed!")

async def test_progress_monitoring():
    """Test real-time progress monitoring"""
    print("\n🔄 Testing Real-time Progress Monitoring")
    print("=" * 40)
    
    base_url = "http://127.0.0.1:8123"
    
    # Start a job
    video_paths = [
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00001wedding.mov",
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00002wedding.mov",
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00003wedding.mov",
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00004wedding.mov",
        "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video/00005wedding.mov"
    ]
    music_path = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/music/weddingmusic.mp3"
    
    async with httpx.AsyncClient() as client:
        # Start job
        start_request = {
            "clips": video_paths,
            "music_path": music_path,
            "target_duration": 30,
            "story_style": "traditional",
            "style_preset": "romantic"
        }
        
        response = await client.post(f"{base_url}/background/start", json=start_request)
        result = response.json()
        
        if not result.get("ok"):
            print(f"❌ Failed to start job: {result.get('error')}")
            return
        
        job_id = result["job_id"]
        print(f"🚀 Started job: {job_id}")
        
        # Monitor with detailed updates
        start_time = time.time()
        last_progress = -1
        
        while True:
            response = await client.get(f"{base_url}/background/status/{job_id}")
            status = response.json()
            
            if not status.get("ok"):
                break
            
            progress = status["progress"]
            current_step = status["current_step"]
            status_name = status["status"]
            elapsed = time.time() - start_time
            
            # Only print when progress changes significantly
            if abs(progress - last_progress) > 0.05 or status_name != "running":
                print(f"⏱️  [{elapsed:6.1f}s] {status_name.upper():8} | {progress:5.1%} | {current_step}")
                last_progress = progress
            
            if status_name in ["completed", "failed", "cancelled"]:
                break
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    print("🎬 ClipSense Background Processing Test")
    print("=" * 50)
    
    # Test 1: Full background processing with 10 clips
    asyncio.run(test_background_processing())
    
    # Test 2: Progress monitoring
    asyncio.run(test_progress_monitoring())
