"""
Video Processing Module for ClipSense

Handles FFmpeg operations for creating highlight videos:
- Creating 720p proxies
- Trimming equal segments from clips
- Concatenating segments
- Overlaying and normalizing music
"""

import os
import tempfile
import subprocess
import math
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any
import asyncio
from config import Config
from timeline import write_timeline
from simple_beat_detector import SimpleBeatDetector
from visual_analyzer import VisualAnalyzer

class VideoProcessor:
    """Handles all video processing operations using FFmpeg"""
    
    def __init__(self):
        self.temp_dir = None
        self.proxy_dir = None
        self.beat_detector = SimpleBeatDetector()
        self.visual_analyzer = VisualAnalyzer()
    
    async def process_highlight(
        self, 
        clips: List[str], 
        music_path: str, 
        target_duration: int = 60
    ) -> Dict[str, Any]:
        """
        Main processing function - now creates both proxy and timeline
        
        If target_duration is 0, calculates dynamic duration based on number of clips
        """
        # Calculate dynamic duration if target_duration is 0
        if target_duration == 0:
            # Dynamic duration: number of clips × 3 seconds per clip
            target_duration = len(clips) * 3
            print(f"🎯 Dynamic duration calculated: {len(clips)} clips × 3 seconds = {target_duration} seconds")
        
        return await self.assemble_from_sources(clips, music_path, target_duration)
    
    async def assemble_from_sources(
        self, 
        clips: List[str], 
        music_path: str, 
        target_duration: int = 60
    ) -> Dict[str, Any]:
        """
        Assemble stage: Create proxy video and timeline from source clips
        
        Args:
            clips: List of video file paths
            music_path: Path to music file
            target_duration: Target duration in seconds
            
        Returns:
            Dict containing proxy output, timeline path, and timing metrics
        """
        proxy_start_time = time.time()
        
        try:
            # Create temporary directories
            base_temp_dir = os.getenv("CLIPSENSE_TMP_DIR")
            if base_temp_dir:
                # Use specified temp directory for testing
                os.makedirs(base_temp_dir, exist_ok=True)
                self.temp_dir = tempfile.mkdtemp(prefix="clipsense_", dir=base_temp_dir)
            else:
                # Use system temp directory
                self.temp_dir = tempfile.mkdtemp(prefix="clipsense_")
            self.proxy_dir = os.path.join(self.temp_dir, "proxies")
            os.makedirs(self.proxy_dir, exist_ok=True)
            
            if Config.ENABLE_TIMING_LOGS:
                print(f"📁 Temp directory: {self.temp_dir}")
                print(f"🕐 [TIMING] Proxy creation started at {time.strftime('%H:%M:%S')}")
            
            # Step 1: Create 720p proxies for all clips
            print(f"🎬 Creating 720p proxies for {len(clips)} clips...")
            proxy_paths = await self._create_proxies(clips)
            proxy_time = time.time() - proxy_start_time
            
            if Config.ENABLE_TIMING_LOGS:
                print(f"⏱️  Proxy creation took {proxy_time:.2f} seconds")
                print(f"🕐 [TIMING] Proxy creation completed at {time.strftime('%H:%M:%S')}")
            
            # Step 2: Analyze music for tempo, beats, and bars
            print("🎵 Analyzing music for tempo and bar detection...")
            music_analysis = await self.beat_detector.analyze_music(music_path, target_duration)
            
            tempo = music_analysis["tempo"]
            beat_times = music_analysis["beat_times"]
            bar_times = music_analysis["bar_times"]
            
            print(f"🎼 Music analysis complete:")
            print(f"   Tempo: {tempo:.1f} BPM")
            print(f"   Beats: {len(beat_times)}")
            print(f"   Bars: {len(bar_times)}")
            print(f"   First bar: {bar_times[0]:.3f}s")
            print(f"   Time signature: {music_analysis.get('time_signature', '4/4')}")
            
            # Use bar times for clip alignment if we have enough bars
            if len(bar_times) >= len(proxy_paths):
                print(f"🎯 Using {len(bar_times)} detected bars for clip alignment")
                trimmed_segments = await self._trim_segments_with_bars(proxy_paths, bar_times, target_duration)
            elif len(beat_times) >= len(proxy_paths):
                print(f"🎯 Using {len(beat_times)} detected beats for timing")
                trimmed_segments = await self._trim_segments_with_beats(proxy_paths, beat_times, target_duration)
            else:
                print(f"⚠️  Not enough beats/bars found for {len(proxy_paths)} clips")
                print("🔄 Using regular timing as fallback")
                segment_duration = target_duration / len(proxy_paths)
                trimmed_segments = await self._trim_segments(proxy_paths, segment_duration)
            
            # Step 4: Check if we need to loop segments to reach target duration
            actual_duration = 0.0
            for seg in trimmed_segments:
                actual_duration += await self._get_video_duration(seg)
            
            if actual_duration < target_duration * 0.9:  # If we're significantly short
                print(f"⚠️  Actual duration {actual_duration:.2f}s is shorter than target {target_duration}s")
                print("🔄 Will loop segments to reach target duration")
                trimmed_segments = await self._loop_segments_to_duration(trimmed_segments, target_duration)
            
            # Step 4: Concatenate all segments
            print("🔗 Concatenating segments...")
            concatenated_video = await self._concatenate_segments(trimmed_segments)
            
            # Step 5: Overlay and normalize music
            render_start_time = time.time()
            print("🎵 Overlaying music and normalizing audio...")
            
            if Config.ENABLE_TIMING_LOGS:
                print(f"🕐 [TIMING] Final render started at {time.strftime('%H:%M:%S')}")
            
            final_output = await self._overlay_music(concatenated_video, music_path)
            render_time = time.time() - render_start_time
            
            if Config.ENABLE_TIMING_LOGS:
                print(f"⏱️  Render took {render_time:.2f} seconds")
                print(f"🕐 [TIMING] Final render completed at {time.strftime('%H:%M:%S')}")
            
            print(f"✅ Proxy video created: {final_output}")
            
            # Generate timeline data with music analysis
            timeline_data = await self._generate_timeline_data(clips, trimmed_segments, target_duration, music_path, beat_times, bar_times)
            timeline_path = os.path.join(self.temp_dir, "timeline.json")
            
            print(f"📝 Writing timeline with bar markers starting at {bar_times[0]:.3f}s")
            
            write_timeline(
                clips=timeline_data,
                target_seconds=target_duration,
                music_path=music_path,
                output_path=timeline_path,
                used_scene_detect=False,  # We're using music analysis instead
                used_beat_snapping=True,  # We're using music-based timing
                bar_markers=bar_times,
                tempo=tempo,
                time_signature=music_analysis.get('time_signature', '4/4')
            )
            
            # Rename proxy output
            proxy_output = os.path.join(self.temp_dir, "highlight_proxy.mp4")
            os.rename(final_output, proxy_output)
            
            return {
                "proxy_output": proxy_output,
                "timeline_path": timeline_path,
                "timeline_hash": self._calculate_timeline_hash(timeline_path),
                "proxy_time": proxy_time,
                "render_time": render_time,
                "temp_dir": self.temp_dir
            }
            
        except Exception as e:
            print(f"❌ Error in process_highlight: {e}")
            raise
        finally:
            # Cleanup temporary files (optional - keep for debugging)
            # self._cleanup_temp_files()
            pass
    
    async def _create_proxies(self, clips: List[str]) -> List[str]:
        """Create optimized 720p proxies for all input clips"""
        proxy_paths = []
        ffmpeg_settings = Config.get_ffmpeg_proxy_settings()
        
        for i, clip_path in enumerate(clips):
            proxy_path = os.path.join(self.proxy_dir, f"proxy_{i:03d}.mp4")
            
            # Optimized FFmpeg command for fast proxy creation
            cmd = [
                "ffmpeg", "-y",  # -y to overwrite output files
                "-i", clip_path,
                "-vf", ffmpeg_settings["scale_filter"],
                "-c:v", "libx264",
                "-preset", ffmpeg_settings["preset"],
                "-crf", ffmpeg_settings["crf"],
                "-c:a", "aac",
                "-b:a", ffmpeg_settings["audio_bitrate"],
                "-movflags", "+faststart",  # Optimize for streaming
                proxy_path
            ]
            
            print(f"🎬 Creating proxy for: {os.path.basename(clip_path)}")
            await self._run_ffmpeg(cmd)
            proxy_paths.append(proxy_path)
        
        return proxy_paths
    
    async def _trim_segments(self, proxy_paths: List[str], segment_duration: float) -> List[str]:
        """Trim equal segments from each proxy clip"""
        trimmed_segments = []
        
        for i, proxy_path in enumerate(proxy_paths):
            # Get video duration first
            duration = await self._get_video_duration(proxy_path)
            
            # Calculate start time (use middle portion of video)
            start_time = max(0, (duration - segment_duration) / 2)
            
            trimmed_path = os.path.join(self.temp_dir, f"trimmed_{i:03d}.mp4")
            
            cmd = [
                "ffmpeg", "-y",
                "-i", proxy_path,
                "-ss", str(start_time),
                "-t", str(segment_duration),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-crf", "23",
                "-r", "25",  # Force 25fps for consistency
                "-vf", "scale=1280:720",  # Ensure consistent resolution
                trimmed_path
            ]
            
            print(f"Trimming segment {i+1}/{len(proxy_paths)}")
            await self._run_ffmpeg(cmd)
            trimmed_segments.append(trimmed_path)
        
        return trimmed_segments
    
    async def _trim_segments_with_beats(self, proxy_paths: List[str], beat_times: List[float], target_duration: float) -> List[str]:
        """Trim segments using beat detection for precise timing"""
        trimmed_segments = []
        
        # Calculate segment durations based on beat intervals
        beat_intervals = []
        for i in range(len(beat_times) - 1):
            beat_intervals.append(beat_times[i + 1] - beat_times[i])
        
        # If we have more clips than beats, extend the last interval
        if len(proxy_paths) > len(beat_intervals):
            last_interval = beat_intervals[-1] if beat_intervals else 2.0
            while len(beat_intervals) < len(proxy_paths):
                beat_intervals.append(last_interval)
        
        print(f"🎵 Beat intervals: {[f'{bi:.2f}s' for bi in beat_intervals[:len(proxy_paths)]]}")
        
        for i, proxy_path in enumerate(proxy_paths):
            # Get video duration first
            duration = await self._get_video_duration(proxy_path)
            
            # Use beat-based segment duration
            segment_duration = beat_intervals[i] if i < len(beat_intervals) else beat_intervals[-1]
            
            # Calculate start time based on beat timing
            # Try to find interesting content around the beat time
            beat_time = beat_times[i] if i < len(beat_times) else beat_times[-1]
            
            # Look for the best moment around this beat time
            # Use the beat time as a guide, but ensure we don't go out of bounds
            start_time = max(0, min(beat_time, duration - segment_duration))
            
            # If the beat time is too close to the end, use the middle
            if start_time + segment_duration > duration:
                start_time = max(0, (duration - segment_duration) / 2)
            
            trimmed_path = os.path.join(self.temp_dir, f"trimmed_beat_{i:03d}.mp4")
            
            cmd = [
                "ffmpeg", "-y",
                "-i", proxy_path,
                "-ss", str(start_time),
                "-t", str(segment_duration),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-crf", "23",
                "-r", "25",  # Force 25fps for consistency
                "-vf", "scale=1280:720",  # Ensure consistent resolution
                trimmed_path
            ]
            
            print(f"🎵 Trimming segment {i+1}/{len(proxy_paths)} (beat at {beat_time:.2f}s, duration {segment_duration:.2f}s)")
            await self._run_ffmpeg(cmd)
            trimmed_segments.append(trimmed_path)
        
        return trimmed_segments
    
    async def _trim_segments_with_bars(self, proxy_paths: List[str], bar_times: List[float], target_duration: float) -> List[str]:
        """Trim segments using bar detection and visual analysis for optimal clip selection"""
        trimmed_segments = []
        
        # Calculate segment durations based on bar intervals
        bar_intervals = []
        for i in range(len(bar_times) - 1):
            bar_intervals.append(bar_times[i + 1] - bar_times[i])
        
        # If we have more clips than bars, extend the last interval
        if len(proxy_paths) > len(bar_intervals):
            last_interval = bar_intervals[-1] if bar_intervals else 2.0
            while len(bar_intervals) < len(proxy_paths):
                bar_intervals.append(last_interval)
        
        print(f"🎼 Bar intervals: {[f'{bi:.2f}s' for bi in bar_intervals[:len(proxy_paths)]]}")
        
        for i, proxy_path in enumerate(proxy_paths):
            # Get video duration first
            duration = await self._get_video_duration(proxy_path)
            
            # Use bar-based segment duration
            segment_duration = bar_intervals[i] if i < len(bar_intervals) else bar_intervals[-1]
            
            # Calculate start time based on bar timing
            # The bar times are absolute music times, but we need relative video times
            # Use the bar time as a guide for interesting content, but map it to video time
            bar_time = bar_times[i] if i < len(bar_times) else bar_times[-1]
            
            # Map bar time to video time (use modulo to cycle through video)
            # This ensures we get interesting content at the right musical moment
            video_time = bar_time % duration
            
            # 🎨 VISUAL INTELLIGENCE: Find the best moment using visual analysis
            print(f"🎬 Analyzing clip {i+1}/{len(proxy_paths)} for best moments...")
            
            # Define search window around the bar-suggested time
            search_window = min(10.0, duration * 0.3)  # Search up to 10s or 30% of video
            search_start = max(0, video_time - search_window / 2)
            search_end = min(duration, search_start + search_window)
            
            # Find best moments within the search window
            best_moments = await self.visual_analyzer.find_best_moments_in_duration(
                proxy_path, search_start, search_end - search_start
            )
            
            if best_moments:
                # Use the best moment, adjusted for search window
                best_moment = best_moments[0] - search_start  # Convert back to relative time
                start_time = max(0, min(best_moment, duration - segment_duration))
                print(f"🎯 Found best moment at {start_time:.2f}s (quality-based selection)")
            else:
                # Fallback to bar-based timing
                start_time = max(0, min(video_time, duration - segment_duration))
                print(f"🎵 Using bar-based timing at {start_time:.2f}s (fallback)")
            
            # If the selected time is too close to the end, use the middle
            if start_time + segment_duration > duration:
                start_time = max(0, (duration - segment_duration) / 2)
                print(f"⚠️  Adjusted to middle of clip: {start_time:.2f}s")
            
            trimmed_path = os.path.join(self.temp_dir, f"trimmed_bar_{i:03d}.mp4")
            
            cmd = [
                "ffmpeg", "-y",
                "-i", proxy_path,
                "-ss", str(start_time),
                "-t", str(segment_duration),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-preset", "fast",
                "-crf", "23",
                "-r", "25",  # Force 25fps for consistency
                "-vf", "scale=1280:720",  # Ensure consistent resolution
                trimmed_path
            ]
            
            print(f"🎼 Trimming segment {i+1}/{len(proxy_paths)} (bar at {bar_time:.2f}s, duration {segment_duration:.2f}s)")
            await self._run_ffmpeg(cmd)
            trimmed_segments.append(trimmed_path)
        
        return trimmed_segments
    
    async def _loop_segments_to_duration(self, segments: List[str], target_duration: float) -> List[str]:
        """Loop segments to reach target duration"""
        looped_segments = []
        current_duration = 0.0
        
        while current_duration < target_duration:
            for segment in segments:
                if current_duration >= target_duration:
                    break
                    
                segment_duration = await self._get_video_duration(segment)
                remaining_needed = target_duration - current_duration
                
                if segment_duration <= remaining_needed:
                    # Use entire segment
                    looped_segments.append(segment)
                    current_duration += segment_duration
                else:
                    # Trim segment to fit remaining duration
                    trimmed_path = os.path.join(self.temp_dir, f"looped_trimmed_{len(looped_segments):03d}.mp4")
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", segment,
                        "-t", str(remaining_needed),
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        "-preset", "fast",
                        "-crf", "23",
                        trimmed_path
                    ]
                    await self._run_ffmpeg(cmd)
                    looped_segments.append(trimmed_path)
                    current_duration += remaining_needed
                    break
        
        print(f"🔄 Created {len(looped_segments)} segments totaling {current_duration:.2f}s")
        return looped_segments
    
    async def _concatenate_segments(self, segments: List[str]) -> str:
        """Concatenate all trimmed segments into one video"""
        concatenated_path = os.path.join(self.temp_dir, "concatenated.mp4")
        
        # Create file list for FFmpeg concat (use absolute paths)
        filelist_path = os.path.abspath(os.path.join(self.temp_dir, "filelist.txt"))
        with open(filelist_path, "w") as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", filelist_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            "-crf", "23",
            os.path.abspath(concatenated_path)
        ]
        
        print("Concatenating segments...")
        await self._run_ffmpeg(cmd)
        return concatenated_path
    
    async def _overlay_music(self, video_path: str, music_path: str) -> str:
        """Overlay music and normalize audio to -14 LUFS"""
        final_path = os.path.abspath(os.path.join(self.temp_dir, "highlight_final.mp4"))
        
        cmd = [
            "ffmpeg", "-y",
            "-i", os.path.abspath(video_path),
            "-stream_loop", "-1", "-i", os.path.abspath(music_path),
            "-filter_complex", 
            "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,pan=stereo|FL=c0|FR=c1[a]",
            "-map", "0:v:0",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-ac", "2",
            "-b:a", "192k",
            "-shortest",
            final_path
        ]
        
        print("Overlaying music and normalizing audio...")
        await self._run_ffmpeg(cmd)
        return final_path
    
    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration using ffprobe"""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            video_path
        ]
        
        result = await self._run_ffmpeg(cmd, capture_output=True)
        return float(result.stdout.strip())
    
    async def _run_ffmpeg(self, cmd: List[str], capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run FFmpeg command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            # Always capture stderr for better error reporting
            stderr_text = stderr.decode('utf-8') if stderr else ""
            stdout_text = stdout.decode('utf-8') if stdout else ""
            raise subprocess.CalledProcessError(
                process.returncode, cmd, stdout_text, stderr_text
            )
        
        return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
    
    async def _generate_timeline_data(self, original_clips: List[str], trimmed_segments: List[str], target_duration: int, music_path: str, beat_times: List[float] = None, bar_times: List[float] = None) -> List[Dict[str, Any]]:
        """Generate timeline data from trimmed segments with beat/bar detection"""
        timeline_clips = []
        
        # Use bar times if available, otherwise fall back to beat times
        timing_markers = bar_times if bar_times else beat_times
        
        for i, (original_clip, trimmed_segment) in enumerate(zip(original_clips, trimmed_segments)):
            # Get duration of trimmed segment
            duration = await self._get_video_duration(trimmed_segment)
            
            # Calculate in/out points for original clip
            original_duration = await self._get_video_duration(original_clip)
            
            if timing_markers and i < len(timing_markers):
                # Use timing markers: find the best moment around the marker time
                marker_time = timing_markers[i]
                # Look for interesting content around this marker time
                start_time = max(0, min(marker_time, original_duration - duration))
            else:
                # Fallback: use middle portion
                start_time = max(0, (original_duration - duration) / 2)
            
            timeline_clips.append({
                "src": os.path.abspath(original_clip),
                "in": round(start_time, 3),
                "out": round(start_time + duration, 3)
            })
        
        return timeline_clips
    
    def _calculate_timeline_hash(self, timeline_path: str) -> str:
        """Calculate SHA256 hash of timeline file"""
        import hashlib
        with open(timeline_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _cleanup_temp_files(self):
        """Clean up temporary files and directories"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up temporary directory: {self.temp_dir}")
