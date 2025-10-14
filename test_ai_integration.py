#!/usr/bin/env python3
"""
Test AI Integration

Tests the integrated AI-powered content selection in the main ClipSense pipeline.
"""

import requests
import json
import time
import os
from pathlib import Path

def test_ai_integration():
    """Test the integrated AI selection system"""
    
    print("🤖 Testing AI Integration with ClipSense")
    print("=" * 50)
    
    # Test data
    base_url = "http://127.0.0.1:8123"
    video_dir = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video"
    music_path = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/music/weddingmusic.mp3"
    
    # Get first 5 wedding clips
    video_paths = []
    for i in range(1, 6):
        clip_path = f"{video_dir}/000{i:02d}wedding.mov"
        if os.path.exists(clip_path):
            video_paths.append(clip_path)
    
    if not video_paths:
        print("❌ No wedding clips found for testing")
        return
    
    print(f"📹 Testing with {len(video_paths)} wedding clips")
    print(f"🎵 Music: {os.path.basename(music_path)}")
    print()
    
    # Test 1: Health check
    print("🔍 Test 1: Health Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Worker is healthy: {health_data.get('status', 'unknown')}")
            print(f"✅ FFmpeg available: {health_data.get('ffmpeg_available', False)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    print()
    
    # Test 2: AI Autocut with different styles
    print("🎬 Test 2: AI Autocut with Different Styles")
    print("-" * 40)
    
    styles_to_test = [
        {"story_style": "traditional", "style_preset": "romantic", "name": "Traditional Romantic"},
        {"story_style": "modern", "style_preset": "energetic", "name": "Modern Energetic"},
        {"story_style": "intimate", "style_preset": "cinematic", "name": "Intimate Cinematic"},
        {"story_style": "destination", "style_preset": "documentary", "name": "Destination Documentary"}
    ]
    
    for style_config in styles_to_test:
        print(f"\n🎨 Testing {style_config['name']} style...")
        
        try:
            # Prepare request
            request_data = {
                "clips": video_paths,
                "music_path": music_path,
                "target_duration": 30,
                "story_style": style_config["story_style"],
                "style_preset": style_config["style_preset"],
                "use_ai_selection": True
            }
            
            # Make request
            start_time = time.time()
            response = requests.post(f"{base_url}/ai_autocut", json=request_data)
            request_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("ok", False):
                    print(f"  ✅ Success in {request_time:.2f}s")
                    print(f"  📊 Selected clips: {len(result.get('selected_clips', []))}")
                    print(f"  🎭 Story breakdown: {result.get('story_breakdown', {})}")
                    
                    # Show quality metrics
                    quality = result.get('quality_metrics', {})
                    if quality:
                        print(f"  📈 Quality: avg={quality.get('average_score', 0):.2f}, high_quality={quality.get('high_quality_clips', 0)}")
                    
                    # Show top selected clips
                    selected_clips = result.get('selected_clips', [])
                    if selected_clips:
                        print(f"  🏆 Top clips:")
                        for i, clip in enumerate(selected_clips[:3]):
                            print(f"    {i+1}. {Path(clip['path']).name} (score: {clip['score']:.2f})")
                else:
                    print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()
    
    # Test 3: Compare AI vs Non-AI selection
    print("🔄 Test 3: AI vs Non-AI Comparison")
    print("-" * 40)
    
    try:
        # AI selection
        print("🤖 AI Selection:")
        ai_request = {
            "clips": video_paths,
            "music_path": music_path,
            "target_duration": 30,
            "story_style": "traditional",
            "style_preset": "romantic",
            "use_ai_selection": True
        }
        
        ai_response = requests.post(f"{base_url}/ai_autocut", json=ai_request)
        if ai_response.status_code == 200:
            ai_result = ai_response.json()
            if ai_result.get("ok", False):
                ai_clips = len(ai_result.get('selected_clips', []))
                ai_quality = ai_result.get('quality_metrics', {}).get('average_score', 0)
                print(f"  ✅ AI selected {ai_clips} clips (avg quality: {ai_quality:.2f})")
            else:
                print(f"  ❌ AI selection failed: {ai_result.get('error')}")
        else:
            print(f"  ❌ AI request failed: {ai_response.status_code}")
        
        # Non-AI selection
        print("📹 Non-AI Selection:")
        non_ai_request = {
            "clips": video_paths,
            "music_path": music_path,
            "target_duration": 30,
            "story_style": "traditional",
            "style_preset": "romantic",
            "use_ai_selection": False
        }
        
        non_ai_response = requests.post(f"{base_url}/ai_autocut", json=non_ai_request)
        if non_ai_response.status_code == 200:
            non_ai_result = non_ai_response.json()
            if non_ai_result.get("ok", False):
                non_ai_clips = len(non_ai_result.get('selected_clips', []))
                non_ai_quality = non_ai_result.get('quality_metrics', {}).get('average_score', 0)
                print(f"  ✅ Non-AI used {non_ai_clips} clips (avg quality: {non_ai_quality:.2f})")
            else:
                print(f"  ❌ Non-AI selection failed: {non_ai_result.get('error')}")
        else:
            print(f"  ❌ Non-AI request failed: {non_ai_response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Comparison error: {e}")
    
    print()
    print("✅ AI Integration Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_ai_integration()
