#!/usr/bin/env python3
"""
Test AI-Powered Content Selection

Demonstrates the new AI-powered content selection system with:
- Object detection for wedding elements
- Emotion analysis for emotional moments
- Story arc creation for narrative flow
- Style presets for consistent editing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add worker directory to path
sys.path.append('worker')

from ai_content_selector import AIContentSelector

async def test_ai_content_selection():
    """Test the AI-powered content selection system"""
    
    print("🤖 Testing AI-Powered Content Selection")
    print("=" * 50)
    
    # Initialize AI content selector
    selector = AIContentSelector()
    
    # Test with wedding clips
    video_dir = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/video"
    video_paths = []
    
    # Get first 5 wedding clips for testing
    for i in range(1, 6):
        clip_path = f"{video_dir}/000{i:02d}wedding.mov"
        if os.path.exists(clip_path):
            video_paths.append(clip_path)
    
    if not video_paths:
        print("❌ No wedding clips found for testing")
        return
    
    print(f"📹 Testing with {len(video_paths)} wedding clips")
    print()
    
    # Test 1: Analyze individual clips
    print("🎬 Test 1: Individual Clip Analysis")
    print("-" * 40)
    
    for i, video_path in enumerate(video_paths[:3]):  # Test first 3 clips
        print(f"Analyzing clip {i+1}: {Path(video_path).name}")
        
        try:
            result = await selector.analyze_clip(
                video_path, 
                story_style='traditional', 
                style_preset='romantic'
            )
            
            print(f"  📊 Final Score: {result.final_score:.2f}")
            print(f"  🎭 Scene: {result.story_arc.scene_classification}")
            print(f"  💝 Tone: {result.story_arc.emotional_tone}")
            print(f"  ⭐ Importance: {result.story_arc.story_importance:.2f}")
            print(f"  🎨 Style: {result.style_preset.applied_style}")
            print(f"  💭 Reason: {result.selection_reason}")
            print()
            
        except Exception as e:
            print(f"  ❌ Error analyzing clip: {e}")
            print()
    
    # Test 2: Select best clips
    print("🎯 Test 2: Best Clip Selection")
    print("-" * 40)
    
    try:
        selected_clips = await selector.select_best_clips(
            video_paths,
            target_count=3,
            story_style='traditional',
            style_preset='romantic'
        )
        
        print(f"Selected {len(selected_clips)} best clips:")
        for i, clip in enumerate(selected_clips):
            print(f"  {i+1}. {Path(clip.clip_path).name}")
            print(f"     Score: {clip.final_score:.2f}")
            print(f"     Scene: {clip.story_arc.scene_classification}")
            print(f"     Reason: {clip.selection_reason}")
            print()
        
    except Exception as e:
        print(f"❌ Error selecting clips: {e}")
        return
    
    # Test 3: Create intelligent highlight
    print("🎬 Test 3: Intelligent Highlight Creation")
    print("-" * 40)
    
    try:
        highlight_summary = await selector.create_intelligent_highlight(
            video_paths,
            music_path="/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/music/weddingmusic.mp3",
            target_duration=30,
            story_style='traditional',
            style_preset='romantic'
        )
        
        print("📋 Highlight Summary:")
        print(f"  Total clips analyzed: {highlight_summary['total_clips_analyzed']}")
        print(f"  Clips selected: {highlight_summary['clips_selected']}")
        print(f"  Story style: {highlight_summary['story_style']}")
        print(f"  Style preset: {highlight_summary['style_preset']}")
        print()
        
        print("🎭 Story Breakdown:")
        story_breakdown = highlight_summary['story_breakdown']
        print(f"  Scenes: {story_breakdown['scenes']}")
        print(f"  Tones: {story_breakdown['tones']}")
        print(f"  Positions: {story_breakdown['positions']}")
        print()
        
        print("📊 Quality Metrics:")
        quality_metrics = highlight_summary['quality_metrics']
        print(f"  Average score: {quality_metrics['average_score']:.2f}")
        print(f"  High quality clips: {quality_metrics['high_quality_clips']}")
        print(f"  Story importance avg: {quality_metrics['story_importance_avg']:.2f}")
        print()
        
        print("🎬 Selected Clips:")
        for i, clip_info in enumerate(highlight_summary['selected_clips']):
            print(f"  {i+1}. {Path(clip_info['path']).name}")
            print(f"     Score: {clip_info['score']:.2f}")
            print(f"     Scene: {clip_info['scene']}")
            print(f"     Tone: {clip_info['tone']}")
            print(f"     Importance: {clip_info['importance']:.2f}")
            print(f"     Reason: {clip_info['reason']}")
            print()
        
    except Exception as e:
        print(f"❌ Error creating highlight: {e}")
        return
    
    print("✅ AI Content Selection Test Complete!")
    print("=" * 50)

async def main():
    """Main test function"""
    print("🚀 Starting AI Content Selection Test")
    print("=" * 50)
    
    try:
        await test_ai_content_selection()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
