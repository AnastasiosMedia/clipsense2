#!/bin/bash

# ClipSense E2E Test Asset Generation Script
# Generates synthetic test media using FFmpeg

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MEDIA_DIR="tests/media"
TEMP_DIR="tests/.tmp"

# Create directories
mkdir -p "$MEDIA_DIR" "$TEMP_DIR"

echo -e "${GREEN}🎬 Generating ClipSense E2E test assets...${NC}"

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}❌ FFmpeg not found. Please install FFmpeg first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📁 Using media directory: $MEDIA_DIR${NC}"

# Generate clip1.mp4 - Color bars with timecode overlay and 1kHz sine wave
echo -e "${YELLOW}🎥 Generating clip1.mp4 (10s, color bars, timecode, 1kHz sine)...${NC}"
ffmpeg -y \
    -f lavfi -i "testsrc=duration=10:size=1280x720:rate=25" \
    -f lavfi -i "aevalsrc=sin(2*PI*1000*t):duration=10:sample_rate=48000" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 128k \
    -filter_complex "[0:v]drawtext=text='%{eif\\:t\\:d\\:2}':fontsize=24:fontcolor=white:x=10:y=10[v]" \
    -map "[v]" -map 1:a \
    -shortest \
    -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
    -map_metadata -1 -movflags +faststart+use_metadata_tags \
    -metadata title="ClipSense Test Clip 1" \
    "$MEDIA_DIR/clip1.mp4"

# Generate clip2.mp4 - Solid color with moving box and 1kHz sine wave
echo -e "${YELLOW}🎥 Generating clip2.mp4 (12s, solid color, moving box, 1kHz sine)...${NC}"
ffmpeg -y \
    -f lavfi -i "color=c=blue:size=1280x720:duration=12:rate=25" \
    -f lavfi -i "aevalsrc=sin(2*PI*1000*t):duration=12:sample_rate=48000" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 128k \
    -filter_complex "[0:v]drawbox=x='t*50':y='t*30':w=100:h=100:color=red:t=5[v]" \
    -map "[v]" -map 1:a \
    -shortest \
    -fflags +bitexact -flags:v +bitexact -flags:a +bitexact \
    -map_metadata -1 -movflags +faststart+use_metadata_tags \
    -metadata title="ClipSense Test Clip 2" \
    "$MEDIA_DIR/clip2.mp4"

# Generate music.wav - Pink noise at approximately -18 LUFS
echo -e "${YELLOW}🎵 Generating music.wav (60s pink noise at -18 LUFS)...${NC}"
ffmpeg -y \
    -f lavfi -i "anoisesrc=duration=60:color=pink:seed=424242" \
    -c:a pcm_s16le \
    -af "loudnorm=I=-18:TP=-1.5:LRA=11" \
    -fflags +bitexact -map_metadata -1 \
    "$MEDIA_DIR/music.wav"

# Verify generated files
echo -e "${YELLOW}🔍 Verifying generated assets...${NC}"

for file in "$MEDIA_DIR/clip1.mp4" "$MEDIA_DIR/clip2.mp4" "$MEDIA_DIR/music.wav"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo -e "${GREEN}✅ $(basename "$file") - $size${NC}"
    else
        echo -e "${RED}❌ $(basename "$file") not found${NC}"
        exit 1
    fi
done

# Get detailed info about generated files
echo -e "${YELLOW}📊 Asset details:${NC}"
for file in "$MEDIA_DIR"/*; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}File: $(basename "$file")${NC}"
        ffprobe -v quiet -show_entries format=duration,size -show_entries stream=codec_name,width,height,sample_rate -of csv=p=0 "$file" | while IFS=',' read -r duration size codec width height sample_rate; do
            echo "  Duration: ${duration}s"
            echo "  Size: $((size/1024/1024))MB"
            echo "  Codec: $codec"
            if [ ! -z "$width" ]; then
                echo "  Resolution: ${width}x${height}"
            fi
            if [ ! -z "$sample_rate" ]; then
                echo "  Sample Rate: ${sample_rate}Hz"
            fi
        done
        echo
    fi
done

echo -e "${GREEN}🎉 Test assets generated successfully!${NC}"
echo -e "${YELLOW}📁 Assets location: $MEDIA_DIR${NC}"
echo -e "${YELLOW}📁 Temp directory: $TEMP_DIR${NC}"
