#!/usr/bin/env python3
"""
Comprehensive Export Video Validation Test

Tests the exported video to verify:
- Video plays correctly
- Scene detection and changes
- Audio/music presence and quality
- Duration and timing
- Visual quality and resolution
- Frame analysis
"""

import os
import subprocess
import json
import cv2
import numpy as np
from pathlib import Path

def test_video_basic_info(video_path):
    """Test basic video information"""
    print("📊 BASIC VIDEO INFORMATION")
    print("-" * 40)
    
    try:
        # Get basic info with ffprobe
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ FFprobe failed: {result.stderr}")
            return False
        
        data = json.loads(result.stdout)
        
        # Format info
        format_info = data['format']
        duration = float(format_info['duration'])
        size = int(format_info['size'])
        
        print(f"✅ File exists: {os.path.exists(video_path)}")
        print(f"📁 File size: {size / (1024*1024):.2f} MB")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🎬 Format: {format_info['format_name']}")
        print(f"📊 Bitrate: {int(format_info.get('bit_rate', 0)) / 1000:.0f} kbps")
        
        # Stream info
        video_stream = None
        audio_stream = None
        
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                video_stream = stream
            elif stream['codec_type'] == 'audio':
                audio_stream = stream
        
        if video_stream:
            print(f"🎥 Video: {video_stream['codec_name']} {video_stream['width']}x{video_stream['height']}")
            print(f"🎞️  FPS: {eval(video_stream['r_frame_rate']):.2f}")
            print(f"🎨 Pixel format: {video_stream['pix_fmt']}")
        
        if audio_stream:
            print(f"🎵 Audio: {audio_stream['codec_name']} {audio_stream['sample_rate']}Hz")
            print(f"🔊 Channels: {audio_stream['channels']}")
            print(f"📊 Audio bitrate: {int(audio_stream.get('bit_rate', 0)) / 1000:.0f} kbps")
        else:
            print("❌ No audio stream found!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing video: {e}")
        return False

def test_video_playback(video_path):
    """Test if video can be opened and played"""
    print("\n🎬 VIDEO PLAYBACK TEST")
    print("-" * 40)
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print("❌ Cannot open video file")
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Video opens successfully")
        print(f"📐 Resolution: {width}x{height}")
        print(f"🎞️  FPS: {fps:.2f}")
        print(f"📊 Total frames: {frame_count}")
        
        # Test reading frames
        frames_read = 0
        frame_times = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frames_read += 1
            if frames_read % 10 == 0:  # Every 10th frame
                current_time = frames_read / fps
                frame_times.append(current_time)
        
        cap.release()
        
        print(f"✅ Successfully read {frames_read} frames")
        print(f"⏱️  Actual duration: {frames_read / fps:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing playback: {e}")
        return False

def test_scene_detection(video_path):
    """Test scene detection and changes"""
    print("\n🎭 SCENE DETECTION TEST")
    print("-" * 40)
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video for scene analysis")
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample every 0.5 seconds for scene analysis
        sample_interval = int(fps * 0.5)
        if sample_interval == 0:
            sample_interval = 1
        
        prev_frame = None
        scene_changes = []
        brightness_changes = []
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                current_time = frame_idx / fps
                
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Calculate brightness
                brightness = np.mean(gray)
                brightness_changes.append((current_time, brightness))
                
                # Detect scene changes
                if prev_frame is not None:
                    # Calculate difference
                    diff = cv2.absdiff(prev_frame, gray)
                    diff_score = np.mean(diff)
                    
                    # Threshold for scene change
                    if diff_score > 30:  # Adjust threshold as needed
                        scene_changes.append((current_time, diff_score))
                        print(f"🎬 Scene change at {current_time:.2f}s (diff: {diff_score:.1f})")
                
                prev_frame = gray.copy()
            
            frame_idx += 1
        
        cap.release()
        
        print(f"✅ Analyzed {len(brightness_changes)} sample frames")
        print(f"🎭 Found {len(scene_changes)} scene changes")
        
        # Analyze brightness variation
        if brightness_changes:
            brightness_values = [b[1] for b in brightness_changes]
            avg_brightness = np.mean(brightness_values)
            brightness_std = np.std(brightness_values)
            
            print(f"💡 Average brightness: {avg_brightness:.1f}")
            print(f"📊 Brightness variation: {brightness_std:.1f}")
            
            if brightness_std > 20:
                print("✅ Good brightness variation (indicates different scenes)")
            else:
                print("⚠️  Low brightness variation (might be similar scenes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in scene detection: {e}")
        return False

def test_audio_analysis(video_path):
    """Test audio presence and quality"""
    print("\n🎵 AUDIO ANALYSIS TEST")
    print("-" * 40)
    
    try:
        # Extract audio and analyze
        cmd = [
            'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '44100', '-ac', '2', '-f', 'wav', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            print(f"❌ Audio extraction failed: {result.stderr.decode()}")
            return False
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(result.stdout, dtype=np.int16)
        
        if len(audio_data) == 0:
            print("❌ No audio data found")
            return False
        
        # Reshape for stereo
        if len(audio_data) % 2 == 0:
            audio_data = audio_data.reshape(-1, 2)
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
        else:
            left_channel = audio_data
            right_channel = audio_data
        
        # Calculate audio metrics
        sample_rate = 44100
        duration = len(audio_data) / sample_rate
        
        # RMS (Root Mean Square) - indicates audio level
        rms_left = np.sqrt(np.mean(left_channel**2))
        rms_right = np.sqrt(np.mean(right_channel**2))
        
        # Peak levels
        peak_left = np.max(np.abs(left_channel))
        peak_right = np.max(np.abs(right_channel))
        
        print(f"✅ Audio extracted successfully")
        print(f"⏱️  Audio duration: {duration:.2f} seconds")
        print(f"📊 Sample rate: {sample_rate} Hz")
        print(f"🔊 RMS Left: {rms_left:.0f}, Right: {rms_right:.0f}")
        print(f"📈 Peak Left: {peak_left}, Right: {peak_right}")
        
        # Check if audio is not silent
        if rms_left < 100 and rms_right < 100:
            print("⚠️  Very low audio levels (might be silent)")
        else:
            print("✅ Good audio levels detected")
        
        # Check for stereo
        if len(audio_data.shape) == 2:
            print("✅ Stereo audio detected")
        else:
            print("ℹ️  Mono audio detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in audio analysis: {e}")
        return False

def test_video_quality(video_path):
    """Test video quality metrics"""
    print("\n🎨 VIDEO QUALITY TEST")
    print("-" * 40)
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video for quality analysis")
            return False
        
        # Sample frames for quality analysis
        fps = cap.get(cv2.CAP_PROP_FPS)
        sample_interval = int(fps * 1.0)  # Every second
        if sample_interval == 0:
            sample_interval = 1
        
        sharpness_scores = []
        contrast_scores = []
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Sharpness (Laplacian variance)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                sharpness_scores.append(laplacian_var)
                
                # Contrast (standard deviation)
                contrast = np.std(gray)
                contrast_scores.append(contrast)
            
            frame_idx += 1
        
        cap.release()
        
        if sharpness_scores:
            avg_sharpness = np.mean(sharpness_scores)
            avg_contrast = np.mean(contrast_scores)
            
            print(f"✅ Quality analysis completed")
            print(f"🔍 Average sharpness: {avg_sharpness:.1f}")
            print(f"🎨 Average contrast: {avg_contrast:.1f}")
            
            # Quality assessment
            if avg_sharpness > 100:
                print("✅ Good sharpness")
            elif avg_sharpness > 50:
                print("⚠️  Moderate sharpness")
            else:
                print("❌ Low sharpness (blurry)")
            
            if avg_contrast > 50:
                print("✅ Good contrast")
            elif avg_contrast > 30:
                print("⚠️  Moderate contrast")
            else:
                print("❌ Low contrast (washed out)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in quality analysis: {e}")
        return False

def main():
    """Run comprehensive video validation test"""
    print("🎬 EXPORT VIDEO VALIDATION TEST")
    print("=" * 60)
    
    # Find the most recent export file
    export_dir = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/Export"
    
    if not os.path.exists(export_dir):
        print(f"❌ Export directory not found: {export_dir}")
        return
    
    # Get all video files
    video_files = []
    for file in os.listdir(export_dir):
        if file.endswith('.mp4'):
            file_path = os.path.join(export_dir, file)
            mtime = os.path.getmtime(file_path)
            video_files.append((file_path, mtime))
    
    if not video_files:
        print("❌ No video files found in export directory")
        return
    
    # Sort by modification time (newest first)
    video_files.sort(key=lambda x: x[1], reverse=True)
    latest_video = video_files[0][0]
    
    print(f"📁 Testing: {os.path.basename(latest_video)}")
    print(f"📂 Path: {latest_video}")
    print()
    
    # Run all tests
    tests = [
        ("Basic Info", test_video_basic_info),
        ("Playback", test_video_playback),
        ("Scene Detection", test_scene_detection),
        ("Audio Analysis", test_audio_analysis),
        ("Video Quality", test_video_quality)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(latest_video)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Video is working correctly.")
    else:
        print("⚠️  Some tests failed. Video may have issues.")

if __name__ == "__main__":
    main()
