#!/usr/bin/env python3
"""
ClipSense E2E Test Asset Generation Script (Python fallback)
Generates synthetic test media using FFmpeg
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🎬 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ FFmpeg not found. Please install FFmpeg first.")
        sys.exit(1)

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg found")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ FFmpeg not found. Please install FFmpeg first.")
    return False

def generate_clip1():
    """Generate clip1.mp4 - Color bars with timecode overlay and 1kHz sine wave"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc=duration=10:size=1280x720:rate=25",
        "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*1000*t):duration=10:sample_rate=48000",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-filter_complex", "[0:v]drawtext=text='%{eif\\:t\\:d\\:2}':fontsize=24:fontcolor=white:x=10:y=10[v]",
        "-map", "[v]", "-map", "1:a",
        "-shortest",
        "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact",
        "-map_metadata", "-1", "-movflags", "+faststart+use_metadata_tags",
        "-metadata", "title=ClipSense Test Clip 1",
        "tests/media/clip1.mp4"
    ]
    run_command(cmd, "Generating clip1.mp4 (10s, color bars, timecode, 1kHz sine)")

def generate_clip2():
    """Generate clip2.mp4 - Solid color with moving box and 1kHz sine wave"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=blue:size=1280x720:duration=12:rate=25",
        "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*1000*t):duration=12:sample_rate=48000",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-filter_complex", "[0:v]drawbox=x='t*50':y='t*30':w=100:h=100:color=red:t=5[v]",
        "-map", "[v]", "-map", "1:a",
        "-shortest",
        "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact",
        "-map_metadata", "-1", "-movflags", "+faststart+use_metadata_tags",
        "-metadata", "title=ClipSense Test Clip 2",
        "tests/media/clip2.mp4"
    ]
    run_command(cmd, "Generating clip2.mp4 (12s, solid color, moving box, 1kHz sine)")

def generate_music():
    """Generate music.wav - Pink noise at approximately -18 LUFS"""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=duration=60:color=pink:seed=424242",
        "-c:a", "pcm_s16le",
        "-af", "loudnorm=I=-18:TP=-1.5:LRA=11",
        "-fflags", "+bitexact", "-map_metadata", "-1",
        "tests/media/music.wav"
    ]
    run_command(cmd, "Generating music.wav (60s pink noise at -18 LUFS)")

def verify_assets():
    """Verify generated assets"""
    print("🔍 Verifying generated assets...")
    
    media_dir = Path("tests/media")
    required_files = ["clip1.mp4", "clip2.mp4", "music.wav"]
    
    for filename in required_files:
        filepath = media_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"✅ {filename} - {size_mb:.1f}MB")
        else:
            print(f"❌ {filename} not found")
            sys.exit(1)

def get_asset_info():
    """Get detailed information about generated assets"""
    print("📊 Asset details:")
    
    media_dir = Path("tests/media")
    for filepath in media_dir.glob("*"):
        if filepath.is_file():
            print(f"File: {filepath.name}")
            
            # Get basic info
            cmd = [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration,size",
                "-show_entries", "stream=codec_name,width,height,sample_rate",
                "-of", "csv=p=0",
                str(filepath)
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            duration, size, codec = parts[0], parts[1], parts[2] if len(parts) > 2 else ""
                            print(f"  Duration: {duration}s")
                            print(f"  Size: {int(size)/1024/1024:.1f}MB")
                            if codec:
                                print(f"  Codec: {codec}")
                            
                            if len(parts) > 3:
                                width, height = parts[3], parts[4] if len(parts) > 4 else ""
                                if width and height:
                                    print(f"  Resolution: {width}x{height}")
                            
                            if len(parts) > 5:
                                sample_rate = parts[5]
                                if sample_rate:
                                    print(f"  Sample Rate: {sample_rate}Hz")
            except subprocess.CalledProcessError:
                print(f"  Could not get detailed info for {filepath.name}")
            
            print()

def main():
    """Main function"""
    print("🎬 Generating ClipSense E2E test assets...")
    
    # Check FFmpeg
    if not check_ffmpeg():
        sys.exit(1)
    
    # Create directories
    os.makedirs("tests/media", exist_ok=True)
    os.makedirs("tests/.tmp", exist_ok=True)
    
    print("📁 Using media directory: tests/media")
    
    # Generate assets
    generate_clip1()
    generate_clip2()
    generate_music()
    
    # Verify and show info
    verify_assets()
    get_asset_info()
    
    print("🎉 Test assets generated successfully!")
    print("📁 Assets location: tests/media")
    print("📁 Temp directory: tests/.tmp")

if __name__ == "__main__":
    main()
