#!/usr/bin/env python3
"""
Test script for Visual Analysis functionality

This script tests the visual analysis features without requiring the full API server.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from visual_analyzer import VisualAnalyzer

async def test_visual_analysis():
    """Test the visual analyzer with sample videos"""
    
    print("🎬 Testing Visual Analysis Module")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = VisualAnalyzer()
    
    # Test with sample videos from our test suite
    test_videos = [
        "tests/media/clip1.mp4",
        "tests/media/clip2.mp4"
    ]
    
    for video_path in test_videos:
        if os.path.exists(video_path):
            print(f"\n📹 Analyzing: {Path(video_path).name}")
            print("-" * 30)
            
            try:
                result = await analyzer.analyze_clip(video_path, sample_rate=0.5)
                
                print(f"✅ Analysis completed in {result.analysis_duration:.2f}s")
                print(f"📊 Duration: {result.duration:.2f}s")
                print(f"👥 Face Count: {result.face_count}")
                print(f"🎯 Face Confidence: {result.face_confidence:.2f}")
                print(f"🏃 Motion Score: {result.motion_score:.2f}")
                print(f"💡 Brightness Score: {result.brightness_score:.2f}")
                print(f"🎨 Contrast Score: {result.contrast_score:.2f}")
                print(f"📐 Stability Score: {result.stability_score:.2f}")
                print(f"⭐ Overall Quality: {result.overall_quality:.2f}")
                print(f"🎯 Best Moments: {[f'{m:.2f}s' for m in result.best_moments[:3]]}")
                
            except Exception as e:
                print(f"❌ Analysis failed: {e}")
        else:
            print(f"⚠️  Video not found: {video_path}")
    
    # Test best moments in duration
    print(f"\n🎯 Testing Best Moments Detection")
    print("-" * 30)
    
    for video_path in test_videos:
        if os.path.exists(video_path):
            print(f"\n📹 Finding best moments in: {Path(video_path).name}")
            
            try:
                # Test finding best moments in first 10 seconds
                best_moments = await analyzer.find_best_moments_in_duration(
                    video_path, start_time=0.0, duration=10.0
                )
                
                print(f"🎯 Best moments in first 10s: {[f'{m:.2f}s' for m in best_moments]}")
                
            except Exception as e:
                print(f"❌ Best moments detection failed: {e}")

async def test_face_detection():
    """Test face detection specifically"""
    
    print(f"\n👥 Testing Face Detection")
    print("-" * 30)
    
    analyzer = VisualAnalyzer()
    
    # Test with a simple synthetic image
    import cv2
    import numpy as np
    
    # Create a simple test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    test_image[:] = (128, 128, 128)  # Gray background
    
    # Test face detection
    face_score = analyzer._detect_faces(test_image)
    print(f"📊 Face detection on empty image: {face_score:.2f}")
    
    # Test with a more complex image (just for testing the function)
    test_image2 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    face_score2 = analyzer._detect_faces(test_image2)
    print(f"📊 Face detection on random image: {face_score2:.2f}")

async def main():
    """Main test function"""
    
    print("🚀 ClipSense Visual Analysis Test Suite")
    print("=" * 60)
    
    # Test basic visual analysis
    await test_visual_analysis()
    
    # Test face detection
    await test_face_detection()
    
    print(f"\n✅ Visual Analysis Test Suite Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
