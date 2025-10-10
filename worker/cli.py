"""
ClipSense CLI Entrypoint

Command-line interface for offline timeline processing and conforming.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conform import ConformProcessor
from timeline import read_timeline, validate_timeline_sources


async def main():
    """Main CLI entrypoint"""
    parser = argparse.ArgumentParser(description="ClipSense CLI - Process timeline files")
    parser.add_argument("--timeline", required=True, help="Path to timeline.json file")
    parser.add_argument("--out", required=True, help="Output path for conformed video")
    parser.add_argument("--music", help="Override music path")
    parser.add_argument("--no-audio", action="store_true", help="Skip audio overlay")
    parser.add_argument("--temp-dir", help="Temporary directory for processing")
    
    args = parser.parse_args()
    
    # Validate timeline file
    if not os.path.exists(args.timeline):
        print(f"❌ Timeline file not found: {args.timeline}")
        sys.exit(1)
    
    try:
        # Read and validate timeline
        timeline = read_timeline(args.timeline)
        print(f"📋 Loaded timeline: {len(timeline['clips'])} clips, {timeline['target_seconds']}s target")
        
        if not validate_timeline_sources(timeline):
            print("⚠️  Warning: Timeline source files have changed or are missing")
            print("   Some clips may not conform correctly")
        
        # Set temp directory if provided
        if args.temp_dir:
            os.environ["CLIPSENSE_TMP_DIR"] = args.temp_dir
        
        # Create conform processor
        processor = ConformProcessor()
        
        # Conform timeline
        print("🎬 Starting conform process...")
        result = await processor.conform_from_timeline(
            timeline_path=args.timeline,
            output_path=args.out,
            music_path=args.music,
            no_audio=args.no_audio
        )
        
        print(f"✅ Conform completed successfully!")
        print(f"   Output: {result['output']}")
        print(f"   Conform time: {result['conform_time']:.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
