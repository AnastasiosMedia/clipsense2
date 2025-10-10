"""
Conform Stage for ClipSense

Handles re-rendering the final cut from original sources using timeline.json
to create high-quality master output files.
"""

import os
import tempfile
import subprocess
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from video_processor import VideoProcessor
from timeline import read_timeline, validate_timeline_sources


class ConformProcessor:
    """Handles conforming timeline to master quality output"""
    
    def __init__(self):
        self.temp_dir = None
    
    async def conform_from_timeline(
        self,
        timeline_path: str,
        output_path: Optional[str] = None,
        music_path: Optional[str] = None,
        no_audio: bool = False
    ) -> Dict[str, Any]:
        """
        Conform a timeline to master quality output using original sources.
        
        Args:
            timeline_path: Path to timeline.json
            output_path: Output path for master file (optional)
            music_path: Override music path (optional)
            no_audio: Skip audio overlay if True
            
        Returns:
            Dict with output path and timing metrics
        """
        # Read and validate timeline
        timeline = read_timeline(timeline_path)
        
        if not validate_timeline_sources(timeline):
            raise ValueError("Timeline source files have changed or are missing")
        
        # Setup temp directory
        base_temp_dir = os.getenv("CLIPSENSE_TMP_DIR")
        if base_temp_dir:
            os.makedirs(base_temp_dir, exist_ok=True)
            self.temp_dir = tempfile.mkdtemp(prefix="conform_", dir=base_temp_dir)
        else:
            self.temp_dir = tempfile.mkdtemp(prefix="conform_")
        
        try:
            # Determine output path
            if not output_path:
                output_path = os.path.join(self.temp_dir, "highlight_master.mp4")
            else:
                output_path = os.path.abspath(output_path)
            
            # Use timeline music or override
            music = music_path if music_path else timeline['music']
            
            # Conform the timeline
            start_time = asyncio.get_event_loop().time()
            
            if no_audio:
                await self._conform_video_only(timeline, output_path)
            else:
                await self._conform_with_audio(timeline, output_path, music)
            
            conform_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "output": output_path,
                "conform_time": conform_time,
                "temp_dir": self.temp_dir
            }
            
        except Exception as e:
            print(f"❌ Error in conform: {e}")
            raise
    
    async def _conform_video_only(self, timeline: Dict[str, Any], output_path: str):
        """Conform video only without audio overlay"""
        clips = timeline['clips']
        fps = timeline['fps']
        
        # Create file list for FFmpeg concat with precise timecodes
        filelist_path = os.path.join(self.temp_dir, "conform_filelist.txt")
        with open(filelist_path, 'w') as f:
            for clip in clips:
                # Use inpoint and duration for precise cutting
                duration = clip['out'] - clip['in']
                f.write(f"file '{os.path.abspath(clip['src'])}'\n")
                f.write(f"inpoint {clip['in']:.3f}\n")
                f.write(f"duration {duration:.3f}\n")
        
        # Conform using original sources with accurate seeking
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", filelist_path,
            "-c:v", "libx264",
            "-preset", "medium",  # Higher quality than fast
            "-crf", "18",  # Lower CRF for better quality
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            output_path
        ]
        
        print("🎬 Conforming video from original sources...")
        await self._run_ffmpeg(cmd)
    
    async def _conform_with_audio(self, timeline: Dict[str, Any], output_path: str, music_path: str):
        """Conform video with audio overlay using original sources"""
        clips = timeline['clips']
        fps = timeline['fps']
        
        # First create video-only conform
        video_path = os.path.join(self.temp_dir, "conform_video.mp4")
        await self._conform_video_only(timeline, video_path)
        
        # Then overlay music using the same robust chain as assemble stage
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-stream_loop", "-1", "-i", os.path.abspath(music_path),
            "-filter_complex", 
            "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,pan=stereo|FL=c0|FR=c1[a]",
            "-map", "0:v:0",
            "-map", "[a]",
            "-c:v", "copy",  # Copy video since it's already conformed
            "-c:a", "aac",
            "-ac", "2",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
        
        print("🎵 Overlaying music on conformed video...")
        await self._run_ffmpeg(cmd)
    
    async def _run_ffmpeg(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run FFmpeg command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            stderr_text = stderr.decode('utf-8') if stderr else ""
            stdout_text = stdout.decode('utf-8') if stdout else ""
            raise subprocess.CalledProcessError(
                process.returncode, cmd, stdout_text, stderr_text
            )
        
        return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
