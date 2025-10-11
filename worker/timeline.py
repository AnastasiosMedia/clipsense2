"""
Timeline Management for ClipSense

Handles generation and processing of deterministic timeline artifacts
that describe the final edit with precise timecodes and metadata.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


def write_timeline(
    clips: List[Dict[str, Any]], 
    target_seconds: int,
    music_path: str,
    output_path: str,
    fps: int = 25,
    used_scene_detect: bool = False,
    used_beat_snapping: bool = False,
    bar_markers: Optional[List[float]] = None,
    tempo: Optional[float] = None,
    time_signature: Optional[str] = None
) -> str:
    """
    Write a deterministic timeline.json file with clip timecodes and metadata.
    
    Args:
        clips: List of clip info with 'src', 'in', 'out' timecodes
        target_seconds: Target duration in seconds
        music_path: Path to music file
        output_path: Where to write timeline.json
        fps: Frame rate
        used_scene_detect: Whether scene detection was used
        used_beat_snapping: Whether beat snapping was used
        
    Returns:
        Path to written timeline file
    """
    # Ensure all paths are absolute
    clips_absolute = []
    for clip in clips:
        clip_abs = clip.copy()
        clip_abs['src'] = os.path.abspath(clip['src'])
        clips_absolute.append(clip_abs)
    
    music_absolute = os.path.abspath(music_path)
    
    # Create timeline structure
    timeline = {
        "clips": clips_absolute,
        "fps": fps,
        "target_seconds": target_seconds,
        "music": music_absolute,
        "used_scene_detect": used_scene_detect,
        "used_beat_snapping": used_beat_snapping,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    # Add music analysis data if provided
    if bar_markers is not None:
        timeline["bar_markers"] = bar_markers
    if tempo is not None:
        timeline["tempo"] = tempo
    if time_signature is not None:
        timeline["time_signature"] = time_signature
    
    # Calculate file hashes for source files
    timeline["source_hashes"] = {}
    for clip in clips_absolute:
        src_path = clip['src']
        if os.path.exists(src_path):
            timeline["source_hashes"][src_path] = _calculate_file_hash(src_path)
    
    if os.path.exists(music_absolute):
        timeline["source_hashes"][music_absolute] = _calculate_file_hash(music_absolute)
    
    # Write timeline with sorted keys for deterministic output
    timeline_path = os.path.abspath(output_path)
    with open(timeline_path, 'w') as f:
        json.dump(timeline, f, indent=2, sort_keys=True)
    
    # Calculate timeline hash
    timeline_hash = _calculate_file_hash(timeline_path)
    
    # Add hash to timeline and rewrite
    timeline["timeline_hash"] = timeline_hash
    with open(timeline_path, 'w') as f:
        json.dump(timeline, f, indent=2, sort_keys=True)
    
    return timeline_path


def read_timeline(timeline_path: str) -> Dict[str, Any]:
    """
    Read and validate a timeline.json file.
    
    Args:
        timeline_path: Path to timeline.json
        
    Returns:
        Timeline data dictionary
        
    Raises:
        FileNotFoundError: If timeline file doesn't exist
        json.JSONDecodeError: If timeline is invalid JSON
        ValueError: If timeline is missing required fields
    """
    if not os.path.exists(timeline_path):
        raise FileNotFoundError(f"Timeline file not found: {timeline_path}")
    
    with open(timeline_path, 'r') as f:
        timeline = json.load(f)
    
    # Validate required fields
    required_fields = ['clips', 'fps', 'target_seconds', 'music', 'timeline_hash']
    for field in required_fields:
        if field not in timeline:
            raise ValueError(f"Timeline missing required field: {field}")
    
    # Validate clips structure
    for i, clip in enumerate(timeline['clips']):
        if not all(key in clip for key in ['src', 'in', 'out']):
            raise ValueError(f"Clip {i} missing required fields: src, in, out")
        
        if not isinstance(clip['in'], (int, float)) or not isinstance(clip['out'], (int, float)):
            raise ValueError(f"Clip {i} timecodes must be numeric")
        
        if clip['in'] >= clip['out']:
            raise ValueError(f"Clip {i} invalid timecode: in >= out")
    
    return timeline


def _calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of a file including mtime and size."""
    stat = os.stat(file_path)
    file_info = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
    return hashlib.sha256(file_info.encode()).hexdigest()


def validate_timeline_sources(timeline: Dict[str, Any]) -> bool:
    """
    Validate that all source files in timeline exist and hashes match.
    
    Args:
        timeline: Timeline data dictionary
        
    Returns:
        True if all sources are valid, False otherwise
    """
    for file_path, expected_hash in timeline.get('source_hashes', {}).items():
        if not os.path.exists(file_path):
            return False
        
        actual_hash = _calculate_file_hash(file_path)
        if actual_hash != expected_hash:
            return False
    
    return True


def format_timecode(seconds: float, fps: int = 25) -> str:
    """
    Format timecode as HH:MM:SS:FF for display purposes.
    
    Args:
        seconds: Time in seconds
        fps: Frame rate
        
    Returns:
        Formatted timecode string
    """
    total_frames = int(seconds * fps)
    hours = total_frames // (fps * 3600)
    minutes = (total_frames % (fps * 3600)) // (fps * 60)
    secs = (total_frames % (fps * 60)) // fps
    frames = total_frames % fps
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"
